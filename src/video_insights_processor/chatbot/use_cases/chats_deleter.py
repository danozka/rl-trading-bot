import logging
from logging import Logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..exceptions.chat_not_found_exception import ChatNotFoundException
from ..persistence.i_chats_repository import IChatsRepository


class ChatsDeleter:
    _log: Logger = logging.getLogger(__name__)
    _chats_repository: IChatsRepository

    @inject
    def __init__(self, chats_repository: IChatsRepository = Provide['chats_repository']) -> None:
        self._chats_repository = chats_repository

    async def delete_chat(self, chat_id: UUID) -> None:
        self._log.info(f'Deleting chat \'{chat_id}\'...')
        if await self._chats_repository.get_chat(chat_id) is None:
            raise ChatNotFoundException(chat_id)
        await self._chats_repository.delete_chat(chat_id)
        self._log.info(f'Chat \'{chat_id}\' deleted')
