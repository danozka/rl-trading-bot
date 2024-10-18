from enum import Enum


class VideoInsightsState(Enum):
    waiting_extraction = 'WAITING_EXTRACTION'
    extracting = 'EXTRACTING'
    completed = 'COMPLETED'
    error_during_extraction = 'ERROR_DURING_EXTRACTION'
    video_file_not_found = 'VIDEO_FILE_NOT_FOUND'
