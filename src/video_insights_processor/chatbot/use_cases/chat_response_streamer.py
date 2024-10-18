import logging
from logging import Logger
from typing import AsyncIterator, Iterator

from dependency_injector.wiring import inject, Provide
from starlette.concurrency import run_in_threadpool

from ..domain.chat import Chat
from ..domain.chat_message import ChatMessage
from ..domain.chat_message_role_type import ChatMessageRoleType
from ..exceptions.chat_not_found_exception import ChatNotFoundException
from ..persistence.i_chats_repository import IChatsRepository
from ..services.i_large_language_model import ILargeLanguageModel


class ChatResponseStreamer:
    _log: Logger = logging.getLogger(__name__)
    _chats_repository: IChatsRepository
    _large_language_model: ILargeLanguageModel

    @inject
    def __init__(
        self,
        chats_repository: IChatsRepository = Provide['chats_repository'],
        large_language_model: ILargeLanguageModel = Provide['large_language_model']
    ) -> None:
        self._chats_repository = chats_repository
        self._large_language_model = large_language_model

    async def stream_chat_response_message(self, system_prompt: str, chat_message: ChatMessage) -> AsyncIterator[str]:
        self._log.info(f'Streaming response for {chat_message}...')
        try:
            chat: Chat | None = await self._chats_repository.get_chat(chat_message.chat_id)
            if chat is None:
                raise ChatNotFoundException(chat_message.chat_id)
            chat.messages.append(chat_message)
            chat_response_message_iterator: Iterator[str] = self._large_language_model.stream_chat_response_message(
                system_prompt=system_prompt,
                chat_messages=chat.messages
            )
            result: str | None = None
            chat_response_message_content: str | None = await run_in_threadpool(
                next,
                chat_response_message_iterator,
                None
            )
            while chat_response_message_content is not None:
                result = chat_response_message_content if result is None else result + chat_response_message_content
                yield chat_response_message_content
                chat_response_message_content = await run_in_threadpool(
                    next,
                    chat_response_message_iterator,
                    None
                )
            if result is not None:
                chat.messages.append(
                    ChatMessage(content=result, chat_id=chat.id, role_type=ChatMessageRoleType.assistant)
                )
                await self._chats_repository.update_chat(chat)
            self._log.info(f'Response streaming for {chat_message} completed')
        except Exception as exception:
            self._log.error(
                f'Exception found while streaming response for {chat_message}: {self._format_exception(exception)}'
            )
            yield '\nWARNING: ERROR FOUND DURING STREAMING.'

    @staticmethod
    def _format_exception(exception: Exception) -> str:
        return f'{exception.__class__.__name__} - {exception}'
