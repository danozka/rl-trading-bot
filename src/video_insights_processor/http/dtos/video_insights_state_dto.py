from uuid import UUID

from .base_json_dto import BaseJsonDto


class VideoInsightsStateDto(BaseJsonDto):
    video_id: UUID
    video_insights_state: str
