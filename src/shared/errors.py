"""Custom exception classes and error handling utilities."""

from typing import Any, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the platform."""
    
    # Client errors (4xx)
    INVALID_REQUEST = "INVALID_REQUEST"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    VOICE_PROFILE_NOT_FOUND = "VOICE_PROFILE_NOT_FOUND"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TRANSCRIPTION_FAILED = "TRANSCRIPTION_FAILED"
    TRANSLATION_FAILED = "TRANSLATION_FAILED"
    VOICE_CLONING_FAILED = "VOICE_CLONING_FAILED"
    STORAGE_ERROR = "STORAGE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


class UniVoiceError(Exception):
    """Base exception for all UniVoice errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details,
            }
        }


class ValidationError(UniVoiceError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_REQUEST,
            status_code=400,
            details=details,
        )


class AuthenticationError(UniVoiceError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            status_code=401,
        )


class AuthorizationError(UniVoiceError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHORIZATION_FAILED,
            status_code=403,
        )


class ResourceNotFoundError(UniVoiceError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class RateLimitError(UniVoiceError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details={"retry_after": retry_after},
        )


class ServiceUnavailableError(UniVoiceError):
    """Raised when a service is temporarily unavailable."""
    
    def __init__(self, service_name: str, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            status_code=503,
            details={"service": service_name},
        )


class TranscriptionError(UniVoiceError):
    """Raised when speech-to-text transcription fails."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.TRANSCRIPTION_FAILED,
            status_code=500,
            details=details,
        )


class TranslationError(UniVoiceError):
    """Raised when translation fails."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.TRANSLATION_FAILED,
            status_code=500,
            details=details,
        )


class VoiceCloningError(UniVoiceError):
    """Raised when voice cloning or synthesis fails."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VOICE_CLONING_FAILED,
            status_code=500,
            details=details,
        )


class StorageError(UniVoiceError):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.STORAGE_ERROR,
            status_code=500,
            details=details,
        )
