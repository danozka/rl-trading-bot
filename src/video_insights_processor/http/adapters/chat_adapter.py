import logging
from logging import Logger

from ..dtos.chat_dto import ChatDto
from ..dtos.chat_message_dto import ChatMessageDto
from ..dtos.chat_message_role_type_dto import ChatMessageRoleTypeDto
from ..dtos.video_chat_message_dto import VideoChatMessageDto
from ...chatbot.domain.chat import Chat
from ...chatbot.domain.chat_message import ChatMessage
from ...chatbot.domain.chat_message_role_type import ChatMessageRoleType


class ChatAdapter:
    _log: Logger = logging.getLogger(__name__)

    def adapt_chat(self, chat: Chat) -> ChatDto:
        self._log.debug(f'Adapting {chat}...')
        result: ChatDto = ChatDto(id=chat.id, messages=[self.adapt_chat_message(message) for message in chat.messages])
        self._log.debug(f'{chat} adapted')
        return result

    def adapt_chat_message(self, chat_message: ChatMessage) -> ChatMessageDto:
        self._log.debug(f'Adapting {chat_message}...')
        result: ChatMessageDto = ChatMessageDto(
            id=chat_message.id,
            content=chat_message.content,
            role_type=ChatMessageRoleTypeDto(chat_message.role_type.value),
            chat_id=chat_message.chat_id,
            timestamp=chat_message.timestamp
        )
        self._log.debug(f'{chat_message} adapted')
        return result

    def adapt_video_chat_message_dto(self, video_chat_message_dto: VideoChatMessageDto) -> ChatMessage:
        self._log.debug(f'Adapting {video_chat_message_dto}...')
        result: ChatMessage = ChatMessage(
            id=video_chat_message_dto.id,
            content=video_chat_message_dto.content,
            role_type=ChatMessageRoleType(video_chat_message_dto.role_type.value),
            chat_id=video_chat_message_dto.chat_id,
            timestamp=video_chat_message_dto.timestamp
        )
        self._log.debug(f'{video_chat_message_dto} adapted')
        return result
