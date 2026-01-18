"""Pytest fixtures for backend tests."""

import os

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Ensure Pinecone doesn't try to connect during tests
    os.environ.setdefault("PINECONE_API_KEY", "")
    os.environ.setdefault("PINECONE_INDEX_HOST", "")


@pytest.fixture
def client():
    """Create a test client for the FastAPI app.

    Use context manager to ensure lifespan events (model loading) are triggered.
    """
    with TestClient(app) as client:
        yield client
