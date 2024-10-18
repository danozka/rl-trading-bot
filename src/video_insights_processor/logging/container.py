from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton

from . import use_cases
from .services.i_logging_context_identifier import ILoggingContextIdentifier
from .services.logging_context_identifier import LoggingContextIdentifier


class Container(DeclarativeContainer):
    logging_context_identifier: Singleton[ILoggingContextIdentifier] = Singleton(LoggingContextIdentifier)
    wiring_config: WiringConfiguration = WiringConfiguration(packages=[use_cases])
