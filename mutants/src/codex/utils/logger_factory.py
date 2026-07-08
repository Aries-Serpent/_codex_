"""
P006: Logger Factory Utilities

Consolidates 1,446 occurrences of logger initialization patterns.

Example:
    # Instead of: logger = logging.getLogger(__name__)
    logger = get_logger(__name__)
"""

import logging
from typing import Optional

__all__ = [
    "get_logger",
    "configure_logging",
    "LoggerFactory",
]


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get or create a logger.

    Args:
        name: Logger name (usually __name__)
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
    return logger


def configure_logging(
    level: int = logging.INFO,
    format_str: Optional[str] = None,
) -> None:
    """
    Configure root logger.

    Args:
        level: Logging level
        format_str: Log format string
    """
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(level=level, format=format_str)


class LoggerFactory:
    """Singleton logger factory."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "LoggerFactory":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.loggers = {}

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create logger."""
        if name not in self.loggers:
            self.loggers[name] = get_logger(name)
        return self.loggers[name]
