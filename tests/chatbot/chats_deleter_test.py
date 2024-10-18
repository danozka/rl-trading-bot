from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from httpx import Response

from video_insights_processor import chatbot_container
from video_insights_processor.chatbot.domain.chat import Chat
from video_insights_processor.chatbot.persistence.i_chats_repository import IChatsRepository
from video_insights_processor.chatbot.use_cases.chats_deleter import ChatsDeleter


class ChatsDeleterTest:
    _delete_chat_endpoint: str = '/api/chats/{chat_id}'

    def test_chat_is_deleted(self, test_client: TestClient) -> None:
        chat: Chat = Chat(uuid4())
        chats_repository: AsyncMock = AsyncMock(spec=IChatsRepository)
        chats_repository.get_chat.return_value = chat
        with chatbot_container.chats_repository.override(chats_repository):
            response: Response = test_client.delete(self._delete_chat_endpoint.format(chat_id=chat.id))
        chats_repository.get_chat.assert_awaited_once_with(chat.id)
        chats_repository.delete_chat.assert_awaited_once_with(chat.id)
        assert response.status_code == 200

    def test_deleting_non_existing_chat_returns_http_404(self, test_client: TestClient) -> None:
        chat_id: UUID = uuid4()
        chats_repository: AsyncMock = AsyncMock(spec=IChatsRepository)
        chats_repository.get_chat.return_value = None
        with chatbot_container.chats_repository.override(chats_repository):
            response: Response = test_client.delete(self._delete_chat_endpoint.format(chat_id=chat_id))
        chats_repository.get_chat.assert_awaited_once_with(chat_id)
        chats_repository.add_chat.assert_not_awaited()
        assert response.status_code == 404
        assert isinstance(response.json(), dict)

    def test_unexpected_exception_returns_http_500(self, test_client: TestClient) -> None:
        with patch.object(
            target=ChatsDeleter,
            attribute=ChatsDeleter.delete_chat.__name__,
            side_effect=Exception('Test exception')
        ):
            response: Response = test_client.delete(self._delete_chat_endpoint.format(chat_id=uuid4()))
        assert response.status_code == 500
        assert isinstance(response.json(), dict)
