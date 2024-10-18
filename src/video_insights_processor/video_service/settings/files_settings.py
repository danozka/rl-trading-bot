from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from .i_files_settings import IFilesSettings


class FilesSettings(BaseSettings, IFilesSettings):
    videos_directory_path: Path = Field(alias='VIDEOS_DIRECTORY_PATH', default=Path('/app/videos'))

    def get_file_path(self, file: Path) -> Path:
        return self.videos_directory_path.joinpath(file)
