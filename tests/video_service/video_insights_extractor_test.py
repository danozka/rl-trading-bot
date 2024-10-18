from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import Response

from video_insights_processor import video_service_container
from video_insights_processor.video_service.domain.video import Video
from video_insights_processor.video_service.domain.video_insights import VideoInsights
from video_insights_processor.video_service.domain.video_insights_state import VideoInsightsState
from video_insights_processor.video_service.persistence.i_videos_repository import IVideosRepository
from video_insights_processor.video_service.services.i_computer_vision_model import IComputerVisionModel
from video_insights_processor.video_service.settings.i_files_settings import IFilesSettings
from video_insights_processor.video_service.use_cases.video_insights_extractor import VideoInsightsExtractor


class VideosInsightsExtractorTest:
    _extract_video_insights_endpoint: str = '/api/videos/{video_id}/insights'

    def test_video_insights_extractor_background_task_is_started(self, test_client: TestClient) -> None:
        video: Video = Video(id=uuid4(), file=Path('test_video.mp4'))
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_all_videos.return_value = [video]
        video_insights_extractor: AsyncMock
        with (
            video_service_container.videos_repository.override(videos_repository),
            patch.object(
                target=VideoInsightsExtractor,
                attribute=VideoInsightsExtractor.extract_video_insights.__name__
            ) as video_insights_extractor
        ):
            response: Response = test_client.put(self._extract_video_insights_endpoint.format(video_id=video.id))
        videos_repository.get_all_videos.assert_awaited_once()
        video_insights_extractor.assert_awaited_once_with(video=video)
        assert response.status_code == 200

    def test_extracting_insights_from_non_existing_video_returns_http_404(self, test_client: TestClient) -> None:
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_all_videos.return_value = []
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.put(self._extract_video_insights_endpoint.format(video_id=uuid4()))
        videos_repository.get_all_videos.assert_awaited_once()
        assert response.status_code == 404
        assert isinstance(response.json(), dict)

    def test_unexpected_exception_returns_http_500(self, test_client: TestClient) -> None:
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_all_videos.side_effect = Exception('Test exception')
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.put(self._extract_video_insights_endpoint.format(video_id=uuid4()))
        videos_repository.get_all_videos.assert_awaited_once()
        assert response.status_code == 500
        assert isinstance(response.json(), dict)

    @staticmethod
    async def test_video_insights_extraction_is_completed(test_video_path: Path) -> None:
        video: Video = Video(id=uuid4(), file=test_video_path)
        video_insights: Mock = Mock(spec=VideoInsights)
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        computer_vision_model: Mock = Mock(spec=IComputerVisionModel)
        computer_vision_model.extract_video_insights.return_value = video_insights
        files_settings: Mock = Mock(spec=IFilesSettings)
        files_settings.get_file_path.return_value = test_video_path
        with (
            video_service_container.videos_repository.override(videos_repository),
            video_service_container.computer_vision_model.override(computer_vision_model),
            video_service_container.files_settings.override(files_settings)
        ):
            await VideoInsightsExtractor().extract_video_insights(video)
        videos_repository.update_video.assert_awaited_with(video)
        computer_vision_model.extract_video_insights.assert_called_once_with(video)
        files_settings.get_file_path.assert_called_once_with(video.file)
        assert video.insights == video_insights
        assert video.insights_state == VideoInsightsState.completed

    @staticmethod
    async def test_video_insights_extraction_stops_if_there_is_no_video_file() -> None:
        video: Video = Video(id=uuid4(), file=Path(f'{uuid4()}.mp4'))
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        files_settings: Mock = Mock(spec=IFilesSettings)
        files_settings.get_file_path.return_value = video.file
        with (
            video_service_container.videos_repository.override(videos_repository),
            video_service_container.files_settings.override(files_settings)
        ):
            await VideoInsightsExtractor().extract_video_insights(video)
        videos_repository.update_video.assert_awaited_with(video)
        files_settings.get_file_path.assert_called_once_with(video.file)
        assert video.insights is None
        assert video.insights_state == VideoInsightsState.video_file_not_found

    @staticmethod
    async def test_video_insights_extraction_stops_if_there_is_an_unexpected_exception() -> None:
        video: Video = Video(id=uuid4(), file=Path(f'{uuid4()}.mp4'))
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        files_settings: Mock = Mock(spec=IFilesSettings)
        files_settings.get_file_path.side_effect = Exception('Test exception')
        with (
            video_service_container.videos_repository.override(videos_repository),
            video_service_container.files_settings.override(files_settings)
        ):
            await VideoInsightsExtractor().extract_video_insights(video)
        videos_repository.update_video.assert_awaited_with(video)
        files_settings.get_file_path.assert_called_once_with(video.file)
        assert video.insights is None
        assert video.insights_state == VideoInsightsState.error_during_extraction
