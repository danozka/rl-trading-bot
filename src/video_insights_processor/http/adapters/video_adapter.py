import logging
from logging import Logger

from ..dtos.video_dto import VideoDto
from ...video_service.domain.video import Video


class VideoAdapter:
    _log: Logger = logging.getLogger(__name__)

    def adapt_video(self, video: Video) -> VideoDto:
        self._log.debug(f'Adapting {video}...')
        result: VideoDto = VideoDto(id=video.id, file=video.file)
        self._log.debug(f'{video} adapted')
        return result

    def adapt_video_dto(self, video_dto: VideoDto) -> Video:
        self._log.debug(f'Adapting {video_dto}...')
        result: Video = Video(id=video_dto.id, file=video_dto.file)
        self._log.debug(f'{video_dto} adapted')
        return result
