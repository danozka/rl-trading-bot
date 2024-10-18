from datetime import datetime
from uuid import UUID

from .base_json_dto import BaseJsonDto
from .chat_message_role_type_dto import ChatMessageRoleTypeDto


class ChatMessageDto(BaseJsonDto):
    id: UUID
    content: str | None
    role_type: ChatMessageRoleTypeDto
    chat_id: UUID
    timestamp: datetime
