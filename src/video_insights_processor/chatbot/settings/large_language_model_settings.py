from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LargeLanguageModelSettings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=('settings_',))
    model_path: Path = Field(alias='LARGE_LANGUAGE_MODEL_PATH', default=Path('/app/models/model.gguf'))
    context_length: int = Field(alias='LARGE_LANGUAGE_MODEL_CONTEXT_LENGTH', default=8192)
    number_of_gpu_layers: int = Field(alias='LARGE_LANGUAGE_MODEL_NUMBER_OF_GPU_LAYERS', default=10)
