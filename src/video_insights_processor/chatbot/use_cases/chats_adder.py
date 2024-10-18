import logging
from logging import Logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..domain.chat import Chat
from ..exceptions.chat_already_exists_exception import ChatAlreadyExistsException
from ..persistence.i_chats_repository import IChatsRepository


class ChatsAdder:
    _log: Logger = logging.getLogger(__name__)
    _chats_repository: IChatsRepository

    @inject
    def __init__(self, chats_repository: IChatsRepository = Provide['chats_repository']) -> None:
        self._chats_repository = chats_repository

    async def add_chat(self, chat_id: UUID) -> None:
        self._log.info(f'Adding chat ID \'{chat_id}\'...')
        if await self._chats_repository.get_chat(chat_id) is not None:
            raise ChatAlreadyExistsException(chat_id)
        await self._chats_repository.add_chat(Chat(chat_id))
        self._log.info(f'Chat ID \'{chat_id}\' added')
