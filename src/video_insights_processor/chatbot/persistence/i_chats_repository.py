from abc import ABC, abstractmethod
from uuid import UUID

from ..domain.chat import Chat


class IChatsRepository(ABC):

    @abstractmethod
    async def get_all_chats(self) -> list[Chat]:
        raise NotImplementedError

    @abstractmethod
    async def get_chat(self, chat_id: UUID) -> Chat | None:
        raise NotImplementedError

    @abstractmethod
    async def add_chat(self, chat: Chat) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_chat(self, chat_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_chat(self, chat: Chat) -> None:
        raise NotImplementedError
