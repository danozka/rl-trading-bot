import logging
from logging import Logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..domain.video import Video
from ..exceptions.video_insights_not_found_exception import VideoInsightsNotFoundException
from ..exceptions.video_not_found_exception import VideoNotFoundException
from ..persistence.i_videos_repository import IVideosRepository


class VideoInsightsGetter:
    _log: Logger = logging.getLogger(__name__)
    _videos_repository: IVideosRepository

    @inject
    def __init__(self, videos_repository: IVideosRepository = Provide['videos_repository']) -> None:
        self._videos_repository = videos_repository

    async def get_video_insights_as_string(self, video_id: UUID) -> str:
        self._log.info(f'Getting insights for video \'{video_id}\'...')
        video: Video | None = await self._videos_repository.get_video(video_id)
        if video is None:
            raise VideoNotFoundException(video_id)
        if video.insights is None:
            raise VideoInsightsNotFoundException(video_id)
        self._log.info(f'Insights for video \'{video_id}\' retrieved')
        return video.insights.model_dump_json()
