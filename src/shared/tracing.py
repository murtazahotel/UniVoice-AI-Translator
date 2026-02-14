"""AWS X-Ray distributed tracing configuration."""

from typing import Any, Callable
from functools import wraps
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.core.context import Context

from .config import get_settings
from .logging import get_logger

logger = get_logger(__name__)


def setup_xray() -> None:
    """Configure AWS X-Ray tracing."""
    settings = get_settings()
    
    if not settings.enable_xray:
        logger.info("X-Ray tracing disabled")
        return
    
    # Set service name
    xray_recorder.configure(
        service=settings.service_name,
        context=Context(),
        sampling=True,
    )
    
    # Patch AWS SDK and other libraries
    patch_all()
    
    logger.info("X-Ray tracing enabled", service=settings.service_name)


def trace_function(name: str | None = None) -> Callable:
    """
    Decorator to trace function execution with X-Ray.
    
    Args:
        name: Custom subsegment name (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            subsegment_name = name or func.__name__
            
            try:
                with xray_recorder.capture(subsegment_name):
                    return await func(*args, **kwargs)
            except Exception as e:
                xray_recorder.current_subsegment().put_annotation("error", str(e))
                raise
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            subsegment_name = name or func.__name__
            
            try:
                with xray_recorder.capture(subsegment_name):
                    return func(*args, **kwargs)
            except Exception as e:
                xray_recorder.current_subsegment().put_annotation("error", str(e))
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def add_trace_annotation(key: str, value: Any) -> None:
    """
    Add annotation to current X-Ray segment.
    
    Args:
        key: Annotation key
        value: Annotation value
    """
    try:
        xray_recorder.current_subsegment().put_annotation(key, value)
    except Exception as e:
        logger.warning("Failed to add X-Ray annotation", key=key, error=str(e))


def add_trace_metadata(namespace: str, key: str, value: Any) -> None:
    """
    Add metadata to current X-Ray segment.
    
    Args:
        namespace: Metadata namespace
        key: Metadata key
        value: Metadata value
    """
    try:
        xray_recorder.current_subsegment().put_metadata(key, value, namespace)
    except Exception as e:
        logger.warning("Failed to add X-Ray metadata", key=key, error=str(e))
