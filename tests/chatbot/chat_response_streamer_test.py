import json
from datetime import datetime
from pathlib import Path
from typing import Iterator
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import Response

from video_insights_processor import chatbot_container
from video_insights_processor import video_service_container
from video_insights_processor.chatbot.domain.chat import Chat
from video_insights_processor.chatbot.domain.chat_message import ChatMessage
from video_insights_processor.chatbot.domain.chat_message_role_type import ChatMessageRoleType
from video_insights_processor.chatbot.persistence.i_chats_repository import IChatsRepository
from video_insights_processor.chatbot.services.i_large_language_model import ILargeLanguageModel
from video_insights_processor.chatbot.use_cases.chat_response_streamer import ChatResponseStreamer
from video_insights_processor.http.dtos.video_chat_message_dto import VideoChatMessageDto
from video_insights_processor.http.dtos.chat_message_role_type_dto import ChatMessageRoleTypeDto
from video_insights_processor.video_service.domain.video import Video
from video_insights_processor.video_service.domain.video_insights import VideoInsights
from video_insights_processor.video_service.domain.video_insights_state import VideoInsightsState
from video_insights_processor.video_service.persistence.i_videos_repository import IVideosRepository


class ChatResponseStreamerTest:
    _stream_chat_response_endpoint: str = '/api/chats/response/stream'

    def test_chat_response_streaming_is_started(self, test_client: TestClient) -> None:
        video: Video = Video(
            id=uuid4(),
            file=Path('test_video.mp4'),
            insights=Mock(spec=VideoInsights),
            insights_state=VideoInsightsState.completed
        )
        video.insights.model_dump_json.return_value = 'Test string'
        video_chat_message: VideoChatMessageDto = VideoChatMessageDto(
            id=uuid4(),
            content='Test content',
            role_type=ChatMessageRoleTypeDto.user,
            chat_id=uuid4(),
            timestamp=datetime.utcnow(),
            video_id=video.id
        )
        large_language_model: Mock = Mock(spec=ILargeLanguageModel)
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = video
        chat_response_streamer: AsyncMock
        with (
            chatbot_container.large_language_model.override(large_language_model),
            video_service_container.videos_repository.override(videos_repository),
            patch.object(
                target=ChatResponseStreamer,
                attribute=ChatResponseStreamer.stream_chat_response_message.__name__
            ) as chat_response_streamer
        ):
            response: Response = test_client.post(
                url=self._stream_chat_response_endpoint,
                json=json.loads(video_chat_message.model_dump_json())
            )
        videos_repository.get_video.assert_awaited_once_with(video.id)
        chat_response_streamer.assert_called_once()
        assert response.status_code == 200

    def test_selecting_a_non_existing_video_returns_http_404(self, test_client: TestClient) -> None:
        video_chat_message: VideoChatMessageDto = VideoChatMessageDto(
            id=uuid4(),
            content='Test content',
            role_type=ChatMessageRoleTypeDto.user,
            chat_id=uuid4(),
            timestamp=datetime.utcnow(),
            video_id=uuid4()
        )
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = None
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.post(
                url=self._stream_chat_response_endpoint,
                json=json.loads(video_chat_message.model_dump_json())
            )
        videos_repository.get_video.assert_awaited_once_with(video_chat_message.video_id)
        assert response.status_code == 404
        assert isinstance(response.json(), dict)

    def test_selecting_an_uncompleted_video_insights_extraction_returns_http_404(self, test_client: TestClient) -> None:
        video: Video = Video(
            id=uuid4(),
            file=Path('test_video.mp4'),
            insights=None,
            insights_state=VideoInsightsState.extracting
        )
        video_chat_message: VideoChatMessageDto = VideoChatMessageDto(
            id=uuid4(),
            content='Test content',
            role_type=ChatMessageRoleTypeDto.user,
            chat_id=uuid4(),
            timestamp=datetime.utcnow(),
            video_id=video.id
        )
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = video
        with video_service_container.videos_repository.override(videos_repository):
            response: Response = test_client.post(
                url=self._stream_chat_response_endpoint,
                json=json.loads(video_chat_message.model_dump_json())
            )
        videos_repository.get_video.assert_awaited_once_with(video_chat_message.video_id)
        assert response.status_code == 404
        assert isinstance(response.json(), dict)

    def test_unexpected_exception_returns_http_500(self, test_client: TestClient) -> None:
        video: Video = Video(
            id=uuid4(),
            file=Path('test_video.mp4'),
            insights=Mock(spec=VideoInsights),
            insights_state=VideoInsightsState.completed
        )
        video.insights.model_dump_json.return_value = 'Test string'
        video_chat_message: VideoChatMessageDto = VideoChatMessageDto(
            id=uuid4(),
            content='Test content',
            role_type=ChatMessageRoleTypeDto.user,
            chat_id=uuid4(),
            timestamp=datetime.utcnow(),
            video_id=video.id
        )
        large_language_model: Mock = Mock(spec=ILargeLanguageModel)
        videos_repository: AsyncMock = AsyncMock(spec=IVideosRepository)
        videos_repository.get_video.return_value = video
        chat_response_streamer: AsyncMock
        with (
            chatbot_container.large_language_model.override(large_language_model),
            video_service_container.videos_repository.override(videos_repository),
            patch.object(
                target=ChatResponseStreamer,
                attribute=ChatResponseStreamer.stream_chat_response_message.__name__,
                side_effect=Exception('Test exception')
            ) as chat_response_streamer
        ):
            response: Response = test_client.post(
                url=self._stream_chat_response_endpoint,
                json=json.loads(video_chat_message.model_dump_json())
            )
        videos_repository.get_video.assert_awaited_once_with(video.id)
        chat_response_streamer.assert_called_once()
        assert response.status_code == 500
        assert isinstance(response.json(), dict)

    @staticmethod
    async def test_chat_response_streaming_is_completed() -> None:
        chat: Chat = Chat(uuid4())
        chat_message: ChatMessage = ChatMessage(
            id=uuid4(),
            content='Test content',
            role_type=ChatMessageRoleType.user,
            chat_id=chat.id,
            timestamp=datetime.utcnow()
        )
        expected_stream: list[str] = ['This', ' is', ' a', ' test', ' response.']

        def large_language_model_stream(system_prompt: str, chat_messages: list[ChatMessage]) -> Iterator[str]:
            stream_chunk: str
            for stream_chunk in expected_stream:
                yield stream_chunk

        chats_repository: AsyncMock = AsyncMock(spec=IChatsRepository)
        chats_repository.get_chat.return_value = chat
        large_language_model: Mock = Mock(spec=ILargeLanguageModel)
        large_language_model.stream_chat_response_message.side_effect = large_language_model_stream
        with (
            chatbot_container.chats_repository.override(chats_repository),
            chatbot_container.large_language_model.override(large_language_model)
        ):
            stream_chunk_counter: int = 0
            stream_chunk_result: str
            async for stream_chunk_result in ChatResponseStreamer().stream_chat_response_message(
                system_prompt='Test system prompt',
                chat_message=chat_message
            ):
                assert stream_chunk_result == expected_stream[stream_chunk_counter]
                stream_chunk_counter += 1
        chats_repository.get_chat.assert_awaited_once_with(chat.id)
        chats_repository.update_chat.assert_awaited_once_with(chat)
        large_language_model.stream_chat_response_message.assert_called_once()
        assert len(chat.messages) == 2
        user_message: ChatMessage = chat.messages[-2]
        assert user_message == chat_message
        assistant_message: ChatMessage = chat.messages[-1]
        assert assistant_message.role_type == ChatMessageRoleType.assistant
        assert assistant_message.chat_id == chat.id
        assert assistant_message.content == ''.join(expected_stream)

    @staticmethod
    async def test_chat_response_streaming_returns_error_message_for_non_existing_chat() -> None:
        chat_message: ChatMessage = ChatMessage(
            id=uuid4(),
            content='Test content',
            role_type=ChatMessageRoleType.user,
            chat_id=uuid4(),
            timestamp=datetime.utcnow()
        )
        chats_repository: AsyncMock = AsyncMock(spec=IChatsRepository)
        chats_repository.get_chat.return_value = None
        large_language_model: Mock = Mock(spec=ILargeLanguageModel)
        with (
            chatbot_container.chats_repository.override(chats_repository),
            chatbot_container.large_language_model.override(large_language_model)
        ):
            stream_result: str
            async for stream_result in ChatResponseStreamer().stream_chat_response_message(
                system_prompt='Test system prompt',
                chat_message=chat_message
            ):
                assert stream_result == '\nWARNING: ERROR FOUND DURING STREAMING.'
