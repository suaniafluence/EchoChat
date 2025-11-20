"""Centralized logging configuration."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.config import settings


def setup_logger(name: str = "echochat") -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler with rotation
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Buffer handler for UI display
    try:
        from app.utils.log_buffer import get_log_handler, LogBufferHandler
        buffer_handler = get_log_handler()
        buffer_handler.setLevel(logging.DEBUG)
        buffer_handler.setFormatter(console_format)
        logger.addHandler(buffer_handler)

        # Also attach buffer handler to root logger to capture all logs (including uvicorn)
        root_logger = logging.getLogger()
        # Check if LogBufferHandler is already attached to root logger
        has_buffer_handler = any(isinstance(h, LogBufferHandler) for h in root_logger.handlers)
        if not has_buffer_handler:
            root_buffer_handler = get_log_handler()
            root_buffer_handler.setLevel(logging.INFO)
            root_buffer_handler.setFormatter(console_format)
            root_logger.addHandler(root_buffer_handler)
            root_logger.setLevel(logging.INFO)
    except Exception as e:
        print(f"Warning: Could not setup log buffer handler: {e}")

    return logger


# Global logger instance
logger = setup_logger()
