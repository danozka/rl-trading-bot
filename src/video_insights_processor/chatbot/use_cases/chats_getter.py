import logging
from logging import Logger

from dependency_injector.wiring import inject, Provide

from ..domain.chat import Chat
from ..persistence.i_chats_repository import IChatsRepository


class ChatsGetter:
    _log: Logger = logging.getLogger(__name__)
    _chats_repository: IChatsRepository

    @inject
    def __init__(self, chats_repository: IChatsRepository = Provide['chats_repository']) -> None:
        self._chats_repository = chats_repository

    async def get_all_chats(self) -> list[Chat]:
        self._log.info('Getting all chats...')
        result: list[Chat] = await self._chats_repository.get_all_chats()
        self._log.info('All chats retrieved')
        return result
