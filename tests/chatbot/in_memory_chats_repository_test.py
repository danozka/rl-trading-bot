from uuid import uuid4

from video_insights_processor.chatbot.domain.chat import Chat
from video_insights_processor.chatbot.domain.chat_message import ChatMessage
from video_insights_processor.chatbot.domain.chat_message_role_type import ChatMessageRoleType
from video_insights_processor.chatbot.persistence.in_memory_chats_repository import InMemoryChatsRepository


class InMemoryChatsRepositoryTest:

    @staticmethod
    async def test_all_chats_are_returned() -> None:
        chat: Chat = Chat(uuid4())
        chats_repository: InMemoryChatsRepository = InMemoryChatsRepository()
        await chats_repository.add_chat(chat)
        result: list[Chat] = await chats_repository.get_all_chats()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == chat.id

    @staticmethod
    async def test_chat_is_returned() -> None:
        chat: Chat = Chat(uuid4())
        chats_repository: InMemoryChatsRepository = InMemoryChatsRepository()
        await chats_repository.add_chat(chat)
        result: Chat | None = await chats_repository.get_chat(chat.id)
        assert result is not None
        assert isinstance(result, Chat)
        assert result.id == chat.id

    @staticmethod
    async def test_null_is_returned_for_non_existing_chat() -> None:
        chats_repository: InMemoryChatsRepository = InMemoryChatsRepository()
        result: Chat | None = await chats_repository.get_chat(uuid4())
        assert result is None

    @staticmethod
    async def test_chat_is_deleted() -> None:
        chat: Chat = Chat(uuid4())
        chats_repository: InMemoryChatsRepository = InMemoryChatsRepository()
        await chats_repository.add_chat(chat)
        await chats_repository.delete_chat(chat.id)
        result: list[Chat] = await chats_repository.get_all_chats()
        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    async def test_chat_is_updated() -> None:
        chat: Chat = Chat(uuid4())
        chats_repository: InMemoryChatsRepository = InMemoryChatsRepository()
        await chats_repository.add_chat(chat)
        chat.messages.append(ChatMessage(role_type=ChatMessageRoleType.user, chat_id=chat.id))
        await chats_repository.update_chat(chat)
        result: Chat | None = await chats_repository.get_chat(chat.id)
        assert result is not None
        assert isinstance(result, Chat)
        assert result.id == chat.id
        assert result.messages == chat.messages
