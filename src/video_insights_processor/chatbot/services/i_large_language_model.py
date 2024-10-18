from abc import ABC, abstractmethod
from typing import Iterator

from ..domain.chat_message import ChatMessage


class ILargeLanguageModel(ABC):

    @abstractmethod
    def stream_chat_response_message(self, system_prompt: str, chat_messages: list[ChatMessage]) -> Iterator[str]:
        raise NotImplementedError
