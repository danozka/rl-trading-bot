from ..domain.logging_level import LoggingLevel
from ..settings.logging_settings import LoggingSettings


class LoggingLevelGetter:
    _logging_settings: LoggingSettings

    def __init__(self, logging_settings: LoggingSettings = LoggingSettings()) -> None:
        self._logging_settings = logging_settings

    def get_logging_level(self) -> LoggingLevel:
        return self._logging_settings.logging_level
