from abc import ABC, abstractmethod
from uuid import UUID

from ..domain.video import Video


class IVideosRepository(ABC):

    @abstractmethod
    async def get_all_videos(self) -> list[Video]:
        raise NotImplementedError

    @abstractmethod
    async def get_video(self, video_id: UUID) -> Video | None:
        raise NotImplementedError

    @abstractmethod
    async def add_video(self, video: Video) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_video(self, video_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_video(self, video: Video) -> None:
        raise NotImplementedError
