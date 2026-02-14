"""Pytest configuration and fixtures."""

import pytest
from typing import Generator
import os

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["ENABLE_XRAY"] = "false"


@pytest.fixture
def mock_aws_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock AWS credentials for testing."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


@pytest.fixture
def settings() -> Generator:
    """Provide test settings."""
    from src.shared.config import Settings
    
    yield Settings(
        environment="test",
        aws_region="us-east-1",
        log_level="DEBUG",
        enable_xray=False,
    )
