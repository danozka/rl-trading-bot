from dependency_injector.wiring import inject, Provide

from .logging_level_getter import LoggingLevelGetter
from ..domain.logging_configuration import LoggingConfiguration
from ..services.i_logging_context_identifier import ILoggingContextIdentifier


class LoggingConfigurationGetter:
    _logging_context_identifier: ILoggingContextIdentifier

    @inject
    def __init__(
        self,
        logging_context_identifier: ILoggingContextIdentifier = Provide['logging_context_identifier']
    ) -> None:
        self._logging_context_identifier = logging_context_identifier

    def get_logging_configuration(self) -> LoggingConfiguration:
        return LoggingConfiguration(
            logging_level=LoggingLevelGetter().get_logging_level(),
            logging_context_identifier=self._logging_context_identifier
        )
