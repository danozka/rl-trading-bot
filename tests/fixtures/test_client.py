from typing import Generator

import pytest
from fastapi.testclient import TestClient

from video_insights_processor.http.app import App


@pytest.fixture(scope='session')
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app=App(), raise_server_exceptions=False) as test_client:
        yield test_client
