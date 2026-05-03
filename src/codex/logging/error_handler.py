"""Centralized error handling with logging and graceful degradation.

Provides:
- Structured error logging with context
- Decorator for automatic error logging
- Fatal error handling with proper exit codes
- Integration with .codex/logs/ directory structure
- Log rotation to prevent unbounded growth
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class CodexErrorHandler:
    """Centralized error handling with logging and graceful degradation.

    Usage:
        handler = CodexErrorHandler()

        @handler.log_errors
        def risky_function():
            ...
    """

    def __init__(
        self,
        log_dir: Optional[Path] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB default
        backup_count: int = 5,
    ) -> None:
        """Initialize error handler.

        Args:
            log_dir: Directory for error logs (default: .codex/logs)
            max_bytes: Maximum size of log file before rotation (default: 10MB)
            backup_count: Number of backup files to keep (default: 5)
        """
        self.log_dir = log_dir or Path(".codex/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.error_log = (
            self.log_dir / f"errors_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log"
        )

        # Configure logger - use unique name per instance to avoid conflicts
        # This ensures each instance uses its own log file
        self.logger = logging.getLogger(f"codex.errors.{id(self)}")
        self.logger.setLevel(logging.ERROR)
        self.logger.propagate = False  # Don't propagate to parent loggers

        # Use RotatingFileHandler for automatic log rotation
        handler = logging.handlers.RotatingFileHandler(
            self.error_log,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        self.logger.addHandler(handler)

    def set_log_level(self, level: str) -> None:
        """Set logging level dynamically.

        Args:
            level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL (case-insensitive)

        Raises:
            ValueError: If invalid level provided

        Example:
            handler.set_log_level('DEBUG')
            handler.set_log_level('warning')  # case-insensitive
        """
        level_upper = level.upper()
        if not hasattr(logging, level_upper):
            raise ValueError(
                f"Invalid log level '{level}'. "
                f"Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )
        self.logger.setLevel(getattr(logging, level_upper))

    def log_error(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
        fatal: bool = False,
    ) -> None:
        """Log error with context.

        Args:
            error: Exception to log
            context: Additional context (dict)
            fatal: If True, exit after logging
        """
        error_details = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }

        self.logger.error(
            f"{error_details['type']}: {error_details['message']}\n"
            f"Context: {error_details['context']}\n"
            f"Traceback:\n{error_details['traceback']}"
        )

        # Flush the handler to ensure log is written
        for handler in self.logger.handlers:
            handler.flush()

        if fatal:
            print(f"❌ Fatal error: {error}", file=sys.stderr)
            print(f"See {self.error_log} for details", file=sys.stderr)
            sys.exit(1)

    def log_errors(self, func: Callable) -> Callable:
        """Decorator to log errors from a function.

        Usage:
            @error_handler.log_errors
            def my_function():
                ...
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.debug(f"Exception: {e}")
                self.log_error(
                    e,
                    context={
                        "function": func.__name__,
                        "args": args,
                        "kwargs": kwargs,
                    },
                )
                raise

        return wrapper


# Global instance
error_handler = CodexErrorHandler()
