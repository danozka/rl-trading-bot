from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import Response

from video_insights_processor import video_service_container
from video_insights_processor.video_service.domain.video import Video
from video_insights_processor.video_service.persistence.i_videos_repository import IVideosRepository
from video_insights_processor.video_service.use_cases.videos_getter import VideosGetter


class VideosGetterTest:
    _get_all_videos_endpoint: str = '/api/videos'

    def test_empty_list_is_returned_if_there_are_no_videos(self, test_client: TestClient) -> None:
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_all_videos.return_value = []
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.get(self._get_all_videos_endpoint)
        videos_repository.get_all_videos.assert_awaited_once()
        assert response.status_code == 200
        result: list[dict[str, Any]] = response.json()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_all_videos_are_returned(self, test_client: TestClient) -> None:
        videos: list[Video] = [Video(id=uuid4(), file=Path(f'test_video_{i}.mp4')) for i in range(1, 4)]
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_all_videos.return_value = videos
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.get(self._get_all_videos_endpoint)
        videos_repository.get_all_videos.assert_awaited_once()
        assert response.status_code == 200
        result: list[dict[str, Any]] = response.json()
        assert isinstance(result, list)
        assert len(result) == 3
        video: Video
        video_result: dict[str, Any]
        for video, video_result in zip(videos, result):
            assert video_result.get('id') == str(video.id)
            assert video_result.get('file') == str(video.file)

    def test_unexpected_exception_returns_http_500(self, test_client: TestClient) -> None:
        with patch.object(
            target=VideosGetter,
            attribute=VideosGetter.get_all_videos.__name__,
            side_effect=Exception('Test exception')
        ):
            response: Response = test_client.get(self._get_all_videos_endpoint)
        assert response.status_code == 500
        assert isinstance(response.json(), dict)
