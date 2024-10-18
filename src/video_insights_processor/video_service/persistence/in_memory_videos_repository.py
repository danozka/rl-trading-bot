import logging
from logging import Logger
from uuid import UUID

from ..domain.video import Video
from .i_videos_repository import IVideosRepository


class InMemoryVideosRepository(IVideosRepository):
    _log: Logger = logging.getLogger(__name__)
    _videos: list[Video]

    def __init__(self) -> None:
        self._videos = []

    async def get_all_videos(self) -> list[Video]:
        self._log.debug('Getting all videos...')
        result: list[Video] = self._videos
        self._log.debug('All videos retrieved')
        return result

    async def get_video(self, video_id: UUID) -> Video | None:
        self._log.debug(f'Getting video \'{video_id}\'...')
        result: Video | None = next((x for x in self._videos if x.id == video_id), None)
        self._log.debug(f'Video \'{video_id}\' retrieved')
        return result

    async def add_video(self, video: Video) -> None:
        self._log.debug(f'Adding {video}...')
        self._videos.append(video)
        self._log.debug(f'{video} added')

    async def delete_video(self, video_id: UUID) -> None:
        self._log.debug(f'Deleting video \'{video_id}\'...')
        self._videos = [x for x in self._videos if x.id != video_id]
        self._log.debug(f'Video \'{video_id}\' deleted')

    async def update_video(self, video: Video) -> None:
        self._log.debug(f'Updating {video}...')
        self._videos = [x if x.id != video.id else video for x in self._videos]
        self._log.debug(f'{video} updated')
