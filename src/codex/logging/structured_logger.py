"""Structured logging system for Codex — replaces print() statements.

This module provides the ``StandardLogger`` class, which offers structured
logging methods (debug, info, warning, error) as a replacement for print()
statements throughout the codebase.

Features:
- Simple debug/info/warning/error() methods matching print() semantics
- Structured JSON-compatible output for programmatic parsing
- Integration with Python's logging module
- Context manager support for operation tracking
- Module-level logger instance for easy importing

Usage::

    from codex.logging.structured_logger import logger

    logger.info("Processing file: %s", filename)
    logger.error("Failed to process: %s", error)
    logger.warning("Using deprecated API")
    logger.debug("Internal state: %s", state)

The logger outputs in a structured format compatible with:
- Python logging handlers (console, file, etc.)
- Downstream log aggregation systems
- JSON parsing for structured analysis
"""

from __future__ import annotations

import json
import logging
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Generator, Optional


@dataclass
class LogContext:
    """Context information for a logging operation."""

    operation: Optional[str] = None
    """Name of the operation being performed."""

    session_id: Optional[str] = None
    """Session ID if applicable."""

    user: Optional[str] = None
    """User information if applicable."""

    extra_fields: dict[str, Any] = field(default_factory=dict)
    """Additional context fields."""

    def to_dict(self) -> dict[str, Any]:
        """Convert context to a dictionary, filtering out None values."""
        data = asdict(self)
        extra = data.pop("extra_fields", {})
        # Filter None values
        context = {k: v for k, v in data.items() if v is not None}
        # Merge extra fields
        context.update(extra)
        return context


class StandardLogger:
    """Structured logger replacing print() statements throughout the codebase.

    This class provides a simple, consistent interface for logging at various
    levels (debug, info, warning, error) with structured output.

    Args:
        name: Logger name (typically __name__ or module name)
        level: Logging level (default: logging.INFO)
        context: Optional LogContext for operation tracking
    """

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        context: Optional[LogContext] = None,
    ) -> None:
        """Initialize the standard logger.

        Args:
            name: Logger name (typically the module name)
            level: Logging level (default: logging.INFO)
            context: Optional LogContext for tracking operations
        """
        self.name = name
        self.level = level
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._context = context or LogContext()

        # Ensure we have at least a console handler
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            self._logger.addHandler(handler)

    def set_context(self, context: LogContext) -> None:
        """Update the logging context.

        Args:
            context: New LogContext to use for all future logging calls.
        """
        self._context = context

    def update_context(self, **kwargs: Any) -> None:
        """Update context fields in-place.

        Args:
            **kwargs: Context fields to update or add.
        """
        if "extra_fields" not in kwargs:
            kwargs = {"extra_fields": kwargs}
        for key, value in kwargs.items():
            if hasattr(self._context, key):
                setattr(self._context, key, value)
            else:
                self._context.extra_fields[key] = value

    def _format_message(self, msg: str, *args: Any) -> str:
        """Format message with arguments, handling both %s and {} style formatting.

        Args:
            msg: The message template
            args: Positional arguments for formatting

        Returns:
            Formatted message string
        """
        if args:
            # Support both %s and .format() style
            try:
                return msg % args
            except (TypeError, ValueError):
                # Fall back to treating args as single string argument
                return msg.format(*args)
        return msg

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments passed to logger
        """
        formatted = self._format_message(msg, *args)
        context = self._context.to_dict()
        if context:
            formatted = f"{formatted} | {json.dumps(context)}"
        self._logger.debug(formatted, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments passed to logger
        """
        formatted = self._format_message(msg, *args)
        context = self._context.to_dict()
        if context:
            formatted = f"{formatted} | {json.dumps(context)}"
        self._logger.info(formatted, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments passed to logger
        """
        formatted = self._format_message(msg, *args)
        context = self._context.to_dict()
        if context:
            formatted = f"{formatted} | {json.dumps(context)}"
        self._logger.warning(formatted, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error-level message.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments passed to logger
        """
        formatted = self._format_message(msg, *args)
        context = self._context.to_dict()
        if context:
            formatted = f"{formatted} | {json.dumps(context)}"
        self._logger.error(formatted, **kwargs)

    @contextmanager
    def operation(self, operation_name: str) -> Generator[None, None, None]:
        """Context manager for tracking operations.

        Logs the start and end of an operation with timing information.

        Args:
            operation_name: Name of the operation

        Yields:
            None

        Example::

            with logger.operation("processing"):
                # Do work here
                pass
        """
        old_operation = self._context.operation
        self._context.operation = operation_name

        start_time = datetime.now(timezone.utc)
        self.info("Starting operation: %s", operation_name)

        try:
            yield
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.error(
                "Operation failed (%0.2fs): %s - %s",
                elapsed,
                operation_name,
                str(e),
            )
            raise
        finally:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.info("Completed operation: %s (%0.2fs)", operation_name, elapsed)
            self._context.operation = old_operation

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an exception with traceback.

        Args:
            msg: Message template (supports %s formatting)
            *args: Positional arguments for message formatting
            **kwargs: Additional keyword arguments passed to logger
        """
        formatted = self._format_message(msg, *args)
        context = self._context.to_dict()
        if context:
            formatted = f"{formatted} | {json.dumps(context)}"
        self._logger.exception(formatted, **kwargs)


# Module-level logger instance for convenient importing
logger = StandardLogger("codex", level=logging.INFO)


def get_logger(name: str, level: int = logging.INFO) -> StandardLogger:
    """Get a StandardLogger instance for a module.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: logging.INFO)

    Returns:
        A StandardLogger instance
    """
    return StandardLogger(name, level=level)


# Convenience function for quick logging without creating a logger
def log_info(msg: str, *args: Any) -> None:
    """Log an info message using the module-level logger.

    Args:
        msg: Message template
        *args: Formatting arguments
    """
    logger.info(msg, *args)


def log_error(msg: str, *args: Any) -> None:
    """Log an error message using the module-level logger.

    Args:
        msg: Message template
        *args: Formatting arguments
    """
    logger.error(msg, *args)


def log_warning(msg: str, *args: Any) -> None:
    """Log a warning message using the module-level logger.

    Args:
        msg: Message template
        *args: Formatting arguments
    """
    logger.warning(msg, *args)


def log_debug(msg: str, *args: Any) -> None:
    """Log a debug message using the module-level logger.

    Args:
        msg: Message template
        *args: Formatting arguments
    """
    logger.debug(msg, *args)


__all__ = [
    "StandardLogger",
    "LogContext",
    "logger",
    "get_logger",
    "log_info",
    "log_error",
    "log_warning",
    "log_debug",
]
