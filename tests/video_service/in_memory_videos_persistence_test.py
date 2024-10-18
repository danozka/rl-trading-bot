from pathlib import Path
from uuid import uuid4

from video_insights_processor.video_service.domain.video import Video
from video_insights_processor.video_service.domain.video_insights_state import VideoInsightsState
from video_insights_processor.video_service.persistence.in_memory_videos_repository import InMemoryVideosRepository


class InMemoryVideosRepositoryTest:

    @staticmethod
    async def test_all_videos_are_returned() -> None:
        video: Video = Video(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: InMemoryVideosRepository = InMemoryVideosRepository()
        await videos_repository.add_video(video)
        result: list[Video] = await videos_repository.get_all_videos()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == video.id

    @staticmethod
    async def test_video_is_returned() -> None:
        video: Video = Video(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: InMemoryVideosRepository = InMemoryVideosRepository()
        await videos_repository.add_video(video)
        result: Video | None = await videos_repository.get_video(video.id)
        assert result is not None
        assert isinstance(result, Video)
        assert result.id == video.id

    @staticmethod
    async def test_null_is_returned_for_non_existing_video() -> None:
        videos_repository: InMemoryVideosRepository = InMemoryVideosRepository()
        result: Video | None = await videos_repository.get_video(uuid4())
        assert result is None

    @staticmethod
    async def test_video_is_deleted() -> None:
        video: Video = Video(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: InMemoryVideosRepository = InMemoryVideosRepository()
        await videos_repository.add_video(video)
        await videos_repository.delete_video(video.id)
        result: list[Video] = await videos_repository.get_all_videos()
        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    async def test_video_is_updated() -> None:
        video: Video = Video(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: InMemoryVideosRepository = InMemoryVideosRepository()
        await videos_repository.add_video(video)
        video.insights_state = VideoInsightsState.completed
        await videos_repository.update_video(video)
        result: Video | None = await videos_repository.get_video(video.id)
        assert result is not None
        assert isinstance(result, Video)
        assert result.id == video.id
        assert result.insights_state == video.insights_state
