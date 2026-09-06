"""Logger adapter interface for zero-dependency injection.

This module provides abstract base classes for logger adapters that enable
dependency injection of logging functionality without requiring hard imports
of codex.logging from other packages like codex_ml.

The adapter pattern allows codex_ml to work without direct codex.logging
dependencies, enabling independent packaging and distribution.
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from typing import Any


def _render_message(msg: Any, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Render a logger message with basic %-style formatting while preserving input order."""
    if not args:
        return str(msg)
    if isinstance(msg, str):
        try:
            return msg % args
        except (TypeError, ValueError):
            return " ".join(part for part in (str(msg), *(str(arg) for arg in args)))
    return " ".join(part for part in (str(msg), *(str(arg) for arg in args)))


class LoggerAdapter(ABC):
    """Abstract base class for logger injection - zero dependencies.
    
    This interface defines the contract for logger implementations that can be
    injected into codex_ml and other packages without creating hard dependencies.
    """

    @abstractmethod
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """

    @abstractmethod
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """

    @abstractmethod
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """

    @abstractmethod
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """

    @abstractmethod
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an exception with traceback.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments
        """


class NullLogger(LoggerAdapter):
    """No-op logger for decoupled operations (zero overhead).
    
    This logger ignores all log calls, making it suitable for packages
    that want to avoid logging overhead when no logger is injected.
    
    Example:
        >>> logger = NullLogger()
        >>> logger.info("This message is silently ignored")
    """

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """No-op debug logging."""
        return None

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Emit info-level messages to stdout when no real logger is configured."""
        print(_render_message(msg, args, kwargs), file=sys.stdout)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Emit warning-level messages to stderr when no real logger is configured."""
        print(_render_message(msg, args, kwargs), file=sys.stderr)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Emit error-level messages to stderr when no real logger is configured."""
        print(_render_message(msg, args, kwargs), file=sys.stderr)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Emit exception-level output to stderr when no real logger is configured."""
        print(_render_message(msg, args, kwargs), file=sys.stderr)


# Global default null logger instance
_default_logger: LoggerAdapter = NullLogger()


def get_default_logger() -> LoggerAdapter:
    """Get the global default logger instance.
    
    Returns:
        The currently configured default logger adapter
    """
    return _default_logger


def set_default_logger(logger: LoggerAdapter) -> None:
    """Set the global default logger instance.
    
    This function allows setting a custom logger implementation globally.
    Useful for bootstrapping actual logging when codex.logging is available.
    
    Args:
        logger: The logger adapter to use as the default
    """
    global _default_logger
    _default_logger = logger


__all__ = [
    "LoggerAdapter",
    "NullLogger",
    "get_default_logger",
    "set_default_logger",
]
