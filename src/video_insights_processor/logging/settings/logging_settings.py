from pydantic import Field
from pydantic_settings import BaseSettings

from ..domain.logging_level import LoggingLevel


class LoggingSettings(BaseSettings):
    logging_level: LoggingLevel = Field(alias='LOGGING_LEVEL', default=LoggingLevel.info)
