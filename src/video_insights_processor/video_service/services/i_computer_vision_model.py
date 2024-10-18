from abc import ABC, abstractmethod

from ..domain.video import Video
from ..domain.video_insights import VideoInsights


class IComputerVisionModel(ABC):

    @abstractmethod
    def extract_video_insights(self, video: Video) -> VideoInsights:
        raise NotImplementedError
