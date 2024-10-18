import logging
from logging import Logger
from uuid import UUID

from ..domain.chat import Chat
from .i_chats_repository import IChatsRepository


class InMemoryChatsRepository(IChatsRepository):
    _log: Logger = logging.getLogger(__name__)
    _chats: list[Chat]

    def __init__(self) -> None:
        self._chats = []

    async def get_all_chats(self) -> list[Chat]:
        self._log.debug('Getting all chats...')
        result: list[Chat] = self._chats
        self._log.debug('All chats retrieved')
        return result

    async def get_chat(self, chat_id: UUID) -> Chat | None:
        self._log.debug(f'Getting chat \'{chat_id}\'...')
        result: Chat | None = next((x for x in self._chats if x.id == chat_id), None)
        self._log.debug(f'Chat \'{chat_id}\' retrieved')
        return result

    async def add_chat(self, chat: Chat) -> None:
        self._log.debug(f'Adding {chat}...')
        self._chats.append(chat)
        self._log.debug(f'{chat} added')

    async def delete_chat(self, chat_id: UUID) -> None:
        self._log.debug(f'Deleting chat \'{chat_id}\'...')
        self._chats = [x for x in self._chats if x.id != chat_id]
        self._log.debug(f'Chat \'{chat_id}\' deleted')

    async def update_chat(self, chat: Chat) -> None:
        self._log.debug(f'Updating {chat}...')
        self._chats = [x if x.id != chat.id else chat for x in self._chats]
        self._log.debug(f'{chat} updated')
