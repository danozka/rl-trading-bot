from abc import ABC, abstractmethod
from uuid import UUID


class ILoggingContextIdentifier(ABC):

    @abstractmethod
    def get_logging_context_id(self) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def set_logging_context_id(self, logging_context_id: UUID) -> None:
        raise NotImplementedError
