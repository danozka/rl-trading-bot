from uuid import UUID

from dependency_injector.wiring import inject, Provide

from ..services.i_logging_context_identifier import ILoggingContextIdentifier


class LoggingContextIdSetter:
    _logging_context_identifier: ILoggingContextIdentifier

    @inject
    def __init__(
        self,
        logging_context_identifier: ILoggingContextIdentifier = Provide['logging_context_identifier']
    ) -> None:
        self._logging_context_identifier = logging_context_identifier

    def set_logging_context_id(self, logging_context_id: UUID) -> None:
        return self._logging_context_identifier.set_logging_context_id(logging_context_id)
