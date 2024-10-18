from pathlib import Path
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from video_insights_processor import video_service_container
from video_insights_processor.video_service.domain.video_insights import VideoInsights
from video_insights_processor.video_service.exceptions.video_not_found_exception import VideoNotFoundException
from video_insights_processor.video_service.exceptions.video_insights_not_found_exception import (
    VideoInsightsNotFoundException
)
from video_insights_processor.video_service.domain.video import Video
from video_insights_processor.video_service.domain.video_insights_state import VideoInsightsState
from video_insights_processor.video_service.persistence.i_videos_repository import IVideosRepository
from video_insights_processor.video_service.use_cases.video_insights_getter import VideoInsightsGetter


class VideosInsightsGetterTest:

    @staticmethod
    async def test_video_insights_are_returned_as_string() -> None:
        expected_string_result: str = 'Test string'
        video: Video = Video(
            id=uuid4(),
            file=Path('test_video.mp4'),
            insights=Mock(spec=VideoInsights),
            insights_state=VideoInsightsState.completed
        )
        video.insights.model_dump_json.return_value = expected_string_result
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = video
        with video_service_container.videos_repository.override(videos_repository):
            result: str = await VideoInsightsGetter().get_video_insights_as_string(video.id)
        videos_repository.get_video.assert_awaited_once_with(video.id)
        assert isinstance(result, str)
        assert result == expected_string_result

    @staticmethod
    async def test_exception_is_raised_if_video_does_not_exist() -> None:
        video_id: UUID = uuid4()
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = None
        with video_service_container.videos_repository.override(videos_repository):
            with pytest.raises(VideoNotFoundException):
                await VideoInsightsGetter().get_video_insights_as_string(video_id)
        videos_repository.get_video.assert_awaited_once_with(video_id)

    @staticmethod
    async def test_exception_is_raised_if_insights_extraction_is_not_completed() -> None:
        video: Video = Video(
            id=uuid4(),
            file=Path('test_video.mp4'),
            insights=None,
            insights_state=VideoInsightsState.extracting
        )
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = video
        with video_service_container.videos_repository.override(videos_repository):
            with pytest.raises(VideoInsightsNotFoundException):
                await VideoInsightsGetter().get_video_insights_as_string(video.id)
        videos_repository.get_video.assert_awaited_once_with(video.id)
