"""Tests for configuration management."""

import pytest
from src.shared.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Test that settings have correct default values."""
    settings = Settings()
    
    assert settings.environment == "development"
    assert settings.aws_region == "us-east-1"
    assert settings.log_level == "INFO"
    assert settings.enable_xray is True


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that settings can be loaded from environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    
    settings = Settings()
    
    assert settings.environment == "production"
    assert settings.aws_region == "eu-west-1"
    assert settings.log_level == "ERROR"


def test_get_settings_cached() -> None:
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
