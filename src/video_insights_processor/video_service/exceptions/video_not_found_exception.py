from uuid import UUID


class VideoNotFoundException(Exception):

    def __init__(self, video_id: UUID) -> None:
        super().__init__(f'Video with ID \'{video_id}\' not found')
