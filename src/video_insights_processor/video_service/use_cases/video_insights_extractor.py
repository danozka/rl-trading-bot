import logging
from logging import Logger
from pathlib import Path

from dependency_injector.wiring import inject, Provide
from starlette.concurrency import run_in_threadpool

from ..domain.video import Video
from ..domain.video_insights_state import VideoInsightsState
from ..exceptions.video_file_not_found_exception import VideoFileNotFoundException
from ..persistence.i_videos_repository import IVideosRepository
from ..services.i_computer_vision_model import IComputerVisionModel
from ..settings.i_files_settings import IFilesSettings


class VideoInsightsExtractor:
    _log: Logger = logging.getLogger(__name__)
    _videos_repository: IVideosRepository
    _computer_vision_model: IComputerVisionModel
    _files_settings: IFilesSettings

    @inject
    def __init__(
        self,
        videos_repository: IVideosRepository = Provide['videos_repository'],
        computer_vision_model: IComputerVisionModel = Provide['computer_vision_model'],
        files_settings: IFilesSettings = Provide['files_settings']
    ) -> None:
        self._videos_repository = videos_repository
        self._computer_vision_model = computer_vision_model
        self._files_settings = files_settings

    async def extract_video_insights(self, video: Video) -> None:
        self._log.info(f'Extracting insights from {video}...')
        try:
            video_file_path: Path = self._files_settings.get_file_path(video.file)
            if not video_file_path.is_file():
                raise VideoFileNotFoundException(video_file_path)
            video.insights_state = VideoInsightsState.extracting
            await self._videos_repository.update_video(video)
            video.insights = await run_in_threadpool(self._computer_vision_model.extract_video_insights,video)
            video.insights_state = VideoInsightsState.completed
            await self._videos_repository.update_video(video)
            self._log.info(f'Insights from {video} extracted')
        except VideoFileNotFoundException as exception:
            video.insights_state = VideoInsightsState.video_file_not_found
            await self._videos_repository.update_video(video)
            self._log.error(f'Exception found while extracting insights from {video}: {exception}')
        except Exception as exception:
            video.insights_state = VideoInsightsState.error_during_extraction
            await self._videos_repository.update_video(video)
            self._log.error(f'Exception found while extracting insights from {video}: {exception}')
