from enum import Enum

from ..exceptions.unknown_chat_message_role_type_exception import UnknownChatMessageRoleTypeException


class ChatMessageRoleType(Enum):
    system = 'system'
    assistant = 'assistant'
    user = 'user'

    @classmethod
    def _missing_(cls, value: str) -> None:
        raise UnknownChatMessageRoleTypeException(value)
