"""Structured logging configuration with CloudWatch integration."""

import logging
import sys
from typing import Any
import structlog
from pythonjsonlogger import jsonlogger
from aws_xray_sdk.core import xray_recorder

from .config import get_settings


def setup_logging() -> None:
    """Configure structured logging with JSON output for CloudWatch."""
    settings = get_settings()
    
    # Configure standard library logging
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # JSON formatter for CloudWatch
    json_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    json_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [json_handler]
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def add_trace_context(logger: structlog.BoundLogger) -> structlog.BoundLogger:
    """
    Add X-Ray trace context to logger.
    
    Args:
        logger: Structlog logger instance
        
    Returns:
        Logger with trace context bound
    """
    try:
        trace_id = xray_recorder.current_segment().trace_id
        return logger.bind(trace_id=trace_id)
    except Exception:
        # X-Ray not available or no active segment
        return logger


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """
    Log function call with parameters.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    logger = get_logger(__name__)
    logger.info(
        "function_call",
        function=func_name,
        parameters=kwargs,
    )


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """
    Log error with context.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logger = get_logger(__name__)
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        exc_info=True,
    )
