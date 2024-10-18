from pathlib import Path
from uuid import UUID

from .base_json_dto import BaseJsonDto


class VideoDto(BaseJsonDto):
    id: UUID
    file: Path
