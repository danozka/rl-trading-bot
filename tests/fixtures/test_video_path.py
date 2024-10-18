from pathlib import Path

import pytest


@pytest.fixture(scope='session')
def test_video_path() -> Path:
    return Path(__file__).parent.joinpath('videos/test_video.mp4')
