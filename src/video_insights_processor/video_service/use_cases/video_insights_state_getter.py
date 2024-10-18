import logging
from logging import Logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..domain.video import Video
from ..domain.video_insights_state import VideoInsightsState
from ..exceptions.video_not_found_exception import VideoNotFoundException
from ..persistence.i_videos_repository import IVideosRepository


class VideosInsightsStateGetter:
    _log: Logger = logging.getLogger(__name__)
    _videos_repository: IVideosRepository

    @inject
    def __init__(self, videos_repository: IVideosRepository = Provide['videos_repository']) -> None:
        self._videos_repository = videos_repository

    async def get_video_insights_state(self, video_id: UUID) -> Video | VideoInsightsState:
        self._log.info(f'Getting insights state for video \'{video_id}\'...')
        video: Video | None = await self._videos_repository.get_video(video_id)
        if video is None:
            raise VideoNotFoundException(video_id)
        result: VideoInsightsState = video.insights_state
        self._log.info(f'Insights state for video \'{video_id}\' retrieved')
        return result
