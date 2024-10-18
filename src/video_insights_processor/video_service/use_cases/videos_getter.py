import logging
from logging import Logger

from dependency_injector.wiring import inject, Provide

from ..domain.video import Video
from ..persistence.i_videos_repository import IVideosRepository


class VideosGetter:
    _log: Logger = logging.getLogger(__name__)
    _videos_repository: IVideosRepository

    @inject
    def __init__(self, videos_repository: IVideosRepository = Provide['videos_repository']) -> None:
        self._videos_repository = videos_repository

    async def get_all_videos(self) -> list[Video]:
        self._log.info('Getting all videos...')
        result: list[Video] = await self._videos_repository.get_all_videos()
        self._log.info('All videos retrieved')
        return result
