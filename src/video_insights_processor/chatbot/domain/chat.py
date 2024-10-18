from dataclasses import dataclass, field
from uuid import UUID

from .chat_message import ChatMessage


@dataclass
class Chat:
    id: UUID
    messages: list[ChatMessage] = field(default_factory=list, repr=False)
