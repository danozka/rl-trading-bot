import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import Response

from video_insights_processor import video_service_container
from video_insights_processor.video_service.domain.video import Video
from video_insights_processor.http.dtos.video_dto import VideoDto
from video_insights_processor.video_service.persistence.i_videos_repository import IVideosRepository
from video_insights_processor.video_service.use_cases.videos_adder import VideosAdder


class VideosAdderTest:
    _add_video_endpoint: str = '/api/videos'

    def test_video_is_added(self, test_client: TestClient) -> None:
        video: VideoDto = VideoDto(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = None
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.put(url=self._add_video_endpoint,json=json.loads(video.model_dump_json()))
        videos_repository.get_video.assert_awaited_once_with(video.id)
        videos_repository.add_video.assert_awaited_once()
        assert response.status_code == 200

    def test_adding_the_same_video_twice_returns_http_409(self, test_client: TestClient) -> None:
        video: VideoDto = VideoDto(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = Video(id=video.id, file=video.file)
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.put(url=self._add_video_endpoint, json=json.loads(video.model_dump_json()))
        videos_repository.get_video.assert_awaited_once_with(video.id)
        videos_repository.add_video.assert_not_awaited()
        assert response.status_code == 409
        assert isinstance(response.json(), dict)

    def test_unexpected_exception_returns_http_500(self, test_client: TestClient) -> None:
        video: VideoDto = VideoDto(id=uuid4(), file=Path('test_video.mp4'))
        with patch.object(
            target=VideosAdder,
            attribute=VideosAdder.add_video.__name__,
            side_effect=Exception('Test exception')
        ):
            response: Response = test_client.put(url=self._add_video_endpoint, json=json.loads(video.model_dump_json()))
        assert response.status_code == 500
        assert isinstance(response.json(), dict)
