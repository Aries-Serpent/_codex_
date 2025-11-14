"""Centralized error handling with logging and graceful degradation.

Provides:
- Structured error logging with context
- Decorator for automatic error logging
- Fatal error handling with proper exit codes
- Integration with .codex/logs/ directory structure
"""

from __future__ import annotations

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional


class CodexErrorHandler:
    """Centralized error handling with logging and graceful degradation.

    Usage:
        handler = CodexErrorHandler()

        @handler.log_errors
        def risky_function():
            ...
    """

    def __init__(self, log_dir: Optional[Path] = None) -> None:
        """Initialize error handler.

        Args:
            log_dir: Directory for error logs (default: .codex/logs)
        """
        self.log_dir = log_dir or Path(".codex/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.error_log = (
            self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        )

        # Configure logger
        self.logger = logging.getLogger("codex.errors")
        self.logger.setLevel(logging.ERROR)

        # Clear existing handlers and add our file handler
        # This ensures each instance uses its own log file
        self.logger.handlers.clear()
        
        handler = logging.FileHandler(self.error_log)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        self.logger.addHandler(handler)

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
