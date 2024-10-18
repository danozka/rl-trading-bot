from abc import ABC, abstractmethod
from pathlib import Path


class IFilesSettings(ABC):

    @abstractmethod
    def get_file_path(self, file: Path) -> Path:
        raise NotImplementedError
