import logging
from logging import StreamHandler
from typing import Any

from .logging_level import LoggingLevel
from ..filters.logging_context_identifier_filter import LoggingContextIdentifierFilter
from ..formatters.logging_terminal_formatter import LoggingTerminalFormatter
from ..services.i_logging_context_identifier import ILoggingContextIdentifier


class LoggingConfiguration(dict[str, Any]):

    def __init__(self, logging_level: LoggingLevel, logging_context_identifier: ILoggingContextIdentifier) -> None:
        super().__init__(
            {
                'version': 1,
                'disable_existing_loggers': False,
                'filters': {
                    'logging_context_identifier_filter': {
                        '()': LoggingContextIdentifierFilter,
                        'logging_context_identifier': logging_context_identifier
                    }
                },
                'formatters': {
                    'terminal_formatter': {
                        '()': LoggingTerminalFormatter,
                    }
                },
                'handlers': {
                    'terminal_handler': {
                        'class': '.'.join([StreamHandler.__module__, StreamHandler.__name__]),
                        'level': logging.getLevelName(logging_level.value),
                        'filters': ['logging_context_identifier_filter'],
                        'formatter': 'terminal_formatter'
                    }
                },
                'loggers': {
                    'root': {
                        'level': logging.getLevelName(logging_level.value),
                        'handlers': ['terminal_handler']
                    }
                }
            }
        )
