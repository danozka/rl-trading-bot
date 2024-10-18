from uuid import UUID


class VideoInsightsNotFoundException(Exception):

    def __init__(self, video_id: UUID) -> None:
        super().__init__(f'Insights for video with ID \'{video_id}\' not found')
