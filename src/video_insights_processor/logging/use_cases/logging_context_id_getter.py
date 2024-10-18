from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..services.i_logging_context_identifier import ILoggingContextIdentifier


class LoggingContextIdGetter:
    _logging_context_identifier: ILoggingContextIdentifier

    @inject
    def __init__(
        self,
        logging_context_identifier: ILoggingContextIdentifier = Provide['logging_context_identifier']
    ) -> None:
        self._logging_context_identifier = logging_context_identifier

    def get_logging_context_id(self) -> UUID:
        return self._logging_context_identifier.get_logging_context_id()
