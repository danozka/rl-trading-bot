from contextvars import ContextVar
from typing import Optional
from uuid import UUID, uuid4

from .i_logging_context_identifier import ILoggingContextIdentifier


class LoggingContextIdentifier(ILoggingContextIdentifier):
    _logging_context_id: ContextVar[Optional[UUID]] = ContextVar('context', default=None)

    @classmethod
    def get_logging_context_id(cls) -> UUID:
        logging_context_id: UUID | None = cls._logging_context_id.get()
        return logging_context_id if logging_context_id is not None else uuid4()

    @classmethod
    def set_logging_context_id(cls, logging_context_id: UUID) -> None:
        cls._logging_context_id.set(logging_context_id)
