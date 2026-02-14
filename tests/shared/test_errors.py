"""Tests for error handling."""

import pytest
from src.shared.errors import (
    UniVoiceError,
    ValidationError,
    AuthenticationError,
    ResourceNotFoundError,
    ErrorCode,
)


def test_validation_error() -> None:
    """Test ValidationError creation and serialization."""
    error = ValidationError("Invalid input", details={"field": "email"})
    
    assert error.message == "Invalid input"
    assert error.error_code == ErrorCode.INVALID_REQUEST
    assert error.status_code == 400
    assert error.details == {"field": "email"}
    
    error_dict = error.to_dict()
    assert error_dict["error"]["code"] == "INVALID_REQUEST"
    assert error_dict["error"]["message"] == "Invalid input"


def test_authentication_error() -> None:
    """Test AuthenticationError creation."""
    error = AuthenticationError()
    
    assert error.error_code == ErrorCode.AUTHENTICATION_FAILED
    assert error.status_code == 401


def test_resource_not_found_error() -> None:
    """Test ResourceNotFoundError creation."""
    error = ResourceNotFoundError("Session", "session-123")
    
    assert "Session not found: session-123" in error.message
    assert error.error_code == ErrorCode.RESOURCE_NOT_FOUND
    assert error.status_code == 404
    assert error.details["resource_type"] == "Session"
    assert error.details["resource_id"] == "session-123"
