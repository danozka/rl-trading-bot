from pathlib import Path


class VideoFileNotFoundException(Exception):

    def __init__(self, video_file_path: Path) -> None:
        super().__init__(f'Video file \'{video_file_path}\' does not exist')
