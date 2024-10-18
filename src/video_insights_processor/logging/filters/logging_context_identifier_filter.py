from logging import Filter, LogRecord

from ..services.i_logging_context_identifier import ILoggingContextIdentifier


class LoggingContextIdentifierFilter(Filter):
    _logging_context_identifier: ILoggingContextIdentifier

    def __init__(self, logging_context_identifier: ILoggingContextIdentifier) -> None:
        super().__init__()
        self._logging_context_identifier = logging_context_identifier

    def filter(self, record: LogRecord) -> bool:
        setattr(record, 'context', self._logging_context_identifier.get_logging_context_id())
        return True
