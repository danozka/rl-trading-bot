import logging
from logging import Logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..exceptions.video_not_found_exception import VideoNotFoundException
from ..persistence.i_videos_repository import IVideosRepository


class VideosDeleter:
    _log: Logger = logging.getLogger(__name__)
    _videos_repository: IVideosRepository

    @inject
    def __init__(self, videos_repository: IVideosRepository = Provide['videos_repository']) -> None:
        self._videos_repository = videos_repository

    async def delete_video(self, video_id: UUID) -> None:
        self._log.info(f'Deleting video \'{video_id}\'...')
        if await self._videos_repository.get_video(video_id) is None:
            raise VideoNotFoundException(video_id)
        await self._videos_repository.delete_video(video_id)
        self._log.info(f'Video \'{video_id}\' deleted')
