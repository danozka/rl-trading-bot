from uuid import UUID

from .base_json_dto import BaseJsonDto
from .chat_message_dto import ChatMessageDto


class ChatDto(BaseJsonDto):
    id: UUID
    messages: list[ChatMessageDto]
