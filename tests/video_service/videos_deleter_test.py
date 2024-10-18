from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from httpx import Response

from video_insights_processor import video_service_container
from video_insights_processor.video_service.domain.video import Video
from video_insights_processor.video_service.persistence.i_videos_repository import IVideosRepository
from video_insights_processor.video_service.use_cases.videos_deleter import VideosDeleter


class VideosDeleterTest:
    _delete_video_endpoint: str = '/api/videos/{video_id}'

    def test_video_is_deleted(self, test_client: TestClient) -> None:
        video: Video = Video(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = video
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.delete(self._delete_video_endpoint.format(video_id=video.id))
        videos_repository.get_video.assert_awaited_once_with(video.id)
        videos_repository.delete_video.assert_awaited_once_with(video.id)
        assert response.status_code == 200

    def test_deleting_non_existing_video_returns_http_404(self, test_client: TestClient) -> None:
        video_id: UUID = uuid4()
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = None
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.delete(self._delete_video_endpoint.format(video_id=video_id))
        videos_repository.get_video.assert_awaited_once_with(video_id)
        videos_repository.add_video.assert_not_awaited()
        assert response.status_code == 404
        assert isinstance(response.json(), dict)

    def test_unexpected_exception_returns_http_500(self, test_client: TestClient) -> None:
        with patch.object(
            target=VideosDeleter,
            attribute=VideosDeleter.delete_video.__name__,
            side_effect=Exception('Test exception')
        ):
            response: Response = test_client.delete(self._delete_video_endpoint.format(video_id=uuid4()))
        assert response.status_code == 500
        assert isinstance(response.json(), dict)
