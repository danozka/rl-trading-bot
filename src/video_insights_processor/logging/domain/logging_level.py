from enum import Enum

from ..exceptions.unknown_logging_level_exception import UnknownLoggingLevelException


class LoggingLevel(Enum):
    debug = 'DEBUG'
    info = 'INFO'
    warning = 'WARNING'
    error = 'ERROR'
    critical = 'CRITICAL'

    @classmethod
    def _missing_(cls, value: str) -> None:
        raise UnknownLoggingLevelException(value)
