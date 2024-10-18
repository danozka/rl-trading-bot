from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

from .video_insights import VideoInsights
from .video_insights_state import VideoInsightsState


@dataclass
class Video:
    id: UUID
    file: Path
    insights: VideoInsights | None = field(default=None, repr=False)
    insights_state: VideoInsightsState = field(default=VideoInsightsState.waiting_extraction, repr=False)
