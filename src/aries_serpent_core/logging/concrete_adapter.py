"""Concrete logger adapter wrapping codex.logging.

This module provides a concrete implementation of LoggerAdapter that wraps
the actual codex.logging.structured_logger.StandardLogger, enabling
dependency injection patterns while preserving full logging functionality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from codex.logging.adapter import LoggerAdapter

if TYPE_CHECKING:
    from codex.logging.structured_logger import StandardLogger


class ConcreteLoggerAdapter(LoggerAdapter):
    """Production adapter wrapping actual codex.logging.

    This adapter bridges the abstract LoggerAdapter interface with the
    concrete StandardLogger implementation from codex.logging, enabling
    full structured logging functionality while supporting dependency injection.

    Args:
        logger: The underlying StandardLogger instance to wrap
    """

    def __init__(self, logger: StandardLogger) -> None:
        """Initialize the concrete adapter.

        Args:
            logger: A StandardLogger instance from codex.logging
        """
        self._logger = logger

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """
        self._logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an exception with traceback.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """
        self._logger.exception(msg, *args, **kwargs)


def create_logger_adapter(name: str) -> ConcreteLoggerAdapter:
    """Create a concrete logger adapter for the given name.

    This factory function creates a ConcreteLoggerAdapter wrapping a
    StandardLogger from codex.logging.

    Args:
        name: Logger name (typically __name__ or a module name)

    Returns:
        A ConcreteLoggerAdapter instance wrapping a StandardLogger

    Example:
        >>> logger = create_logger_adapter(__name__)
        >>> logger.info("Application started")
    """
    from codex.logging.structured_logger import StandardLogger

    return ConcreteLoggerAdapter(StandardLogger(name))


__all__ = [
    "ConcreteLoggerAdapter",
    "create_logger_adapter",
]
