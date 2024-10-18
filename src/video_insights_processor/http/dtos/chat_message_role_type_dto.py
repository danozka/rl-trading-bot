from enum import Enum

from ...chatbot.exceptions.unknown_chat_message_role_type_exception import UnknownChatMessageRoleTypeException


class ChatMessageRoleTypeDto(str, Enum):
    assistant = 'assistant'
    user = 'user'

    @classmethod
    def _missing_(cls, value: str) -> None:
        raise UnknownChatMessageRoleTypeException(value)
