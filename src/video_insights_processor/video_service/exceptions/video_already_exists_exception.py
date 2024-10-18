from ..domain.video import Video


class VideoAlreadyExistsException(Exception):

    def __init__(self, video: Video) -> None:
        super().__init__(f'Video {video} already exists in the system')
