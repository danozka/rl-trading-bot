import logging
import logging.config

from .logging_configuration_getter import LoggingConfigurationGetter


class LoggingBuilder:

    @staticmethod
    def build() -> None:
        logging.config.dictConfig(LoggingConfigurationGetter().get_logging_configuration())
