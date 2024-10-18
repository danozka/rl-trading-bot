import logging
from logging import Logger

from dependency_injector.wiring import inject, Provide

from ..domain.video import Video
from ..exceptions.video_already_exists_exception import VideoAlreadyExistsException
from ..persistence.i_videos_repository import IVideosRepository


class VideosAdder:
    _log: Logger = logging.getLogger(__name__)
    _videos_repository: IVideosRepository

    @inject
    def __init__(self, videos_repository: IVideosRepository = Provide['videos_repository']) -> None:
        self._videos_repository = videos_repository

    async def add_video(self, video: Video) -> None:
        self._log.info(f'Adding {video}...')
        if await self._videos_repository.get_video(video.id) is not None:
            raise VideoAlreadyExistsException(video)
        await self._videos_repository.add_video(video)
        self._log.info(f'{video} added')
