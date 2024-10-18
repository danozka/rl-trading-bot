from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import Response

from video_insights_processor import chatbot_container
from video_insights_processor.chatbot.domain.chat import Chat
from video_insights_processor.chatbot.persistence.i_chats_repository import IChatsRepository
from video_insights_processor.chatbot.use_cases.chats_getter import ChatsGetter


class ChatsGetterTest:
    _get_all_chats_endpoint: str = '/api/chats'

    def test_empty_list_is_returned_if_there_are_no_chats(self, test_client: TestClient) -> None:
        chats_repository: AsyncMock = AsyncMock(spec=IChatsRepository)
        chats_repository.get_all_chats.return_value = []
        with chatbot_container.chats_repository.override(chats_repository):
            response: Response = test_client.get(self._get_all_chats_endpoint)
        chats_repository.get_all_chats.assert_awaited_once()
        assert response.status_code == 200
        result: list[dict[str, Any]] = response.json()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_all_chats_are_returned(self, test_client: TestClient) -> None:
        chats: list[Chat] = [Chat(uuid4()) for _ in range(3)]
        chats_repository: AsyncMock = AsyncMock(spec=IChatsRepository)
        chats_repository.get_all_chats.return_value = chats
        with chatbot_container.chats_repository.override(chats_repository):
            response: Response = test_client.get(self._get_all_chats_endpoint)
        chats_repository.get_all_chats.assert_awaited_once()
        assert response.status_code == 200
        result: list[dict[str, Any]] = response.json()
        assert isinstance(result, list)
        assert len(result) == 3
        chat: Chat
        chat_result: dict[str, Any]
        for chat, chat_result in zip(chats, result):
            assert chat_result.get('id') == str(chat.id)
            assert len(chat_result.get('messages')) == 0

    def test_unexpected_exception_returns_http_500(self, test_client: TestClient) -> None:
        with patch.object(
            target=ChatsGetter,
            attribute=ChatsGetter.get_all_chats.__name__,
            side_effect=Exception('Test exception')
        ):
            response: Response = test_client.get(self._get_all_chats_endpoint)
        assert response.status_code == 500
        assert isinstance(response.json(), dict)
