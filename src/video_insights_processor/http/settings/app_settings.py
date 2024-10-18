from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    name: str = Field(alias='APP_NAME', default='VideoInsightsProcessor')
    frontend_path: Path = Field(alias='APP_FRONTEND_PATH', default=Path('/app/frontend'))
    host: str = Field(alias='APP_HOST', default='0.0.0.0')
    port: int = Field(alias='APP_PORT', default=8000)
