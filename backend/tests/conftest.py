"""Pytest fixtures for backend tests."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app.

    Use context manager to ensure lifespan events (model loading) are triggered.
    """
    with TestClient(app) as client:
        yield client
