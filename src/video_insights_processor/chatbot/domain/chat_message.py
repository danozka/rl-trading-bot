from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .chat_message_role_type import ChatMessageRoleType


@dataclass
class ChatMessage:
    role_type: ChatMessageRoleType
    chat_id: UUID
    content: str = field(default='', repr=False)
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(repr=False, default_factory=datetime.utcnow)
