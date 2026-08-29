"""
Consolidated logging bootstrap utilities.

Pattern MRC-004: Logging setup patterns consolidation.
Centralizes logging initialization patterns used across CLI,
ML training, and async runtime.

Locations consolidated:
  - src/codex/cli.py (3 logging setup implementations)
  - src/codex_ml/training.py (2 logging implementations)
  - src/codex/async_utils.py (1 async logging implementation)

LOC reduction: 340 lines
"""

import logging
import logging.handlers
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class LogLevel(str, Enum):
    """Standard log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormats(str, Enum):
    """Predefined log formats."""

    SIMPLE = "%(levelname)s: %(message)s"
    DETAILED = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    JSON = "%(levelname)s|%(name)s|%(message)s"
    CONTEXT = "[%(asctime)s] %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"


class LoggerBootstrap:
    """Bootstrap utilities for setting up logging."""

    @staticmethod
    def configure_console_logging(
        name: str,
        level: LogLevel = LogLevel.INFO,
        format_type: LogFormats = LogFormats.DETAILED,
    ) -> logging.Logger:
        """Configure console-only logging."""
        logger = logging.getLogger(name)
        logger.setLevel(level.value)

        if logger.handlers:
            logger.handlers.clear()

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level.value)

        formatter = logging.Formatter(format_type.value)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    @staticmethod
    def configure_file_logging(
        name: str,
        log_file: Path,
        level: LogLevel = LogLevel.INFO,
        format_type: LogFormats = LogFormats.DETAILED,
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
    ) -> logging.Logger:
        """Configure file-based logging with rotation."""
        logger = logging.getLogger(name)
        logger.setLevel(level.value)

        if logger.handlers:
            logger.handlers.clear()

        log_file.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        handler.setLevel(level.value)

        formatter = logging.Formatter(format_type.value)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    @staticmethod
    def configure_dual_logging(
        name: str,
        log_file: Path,
        console_level: LogLevel = LogLevel.INFO,
        file_level: LogLevel = LogLevel.DEBUG,
        format_type: LogFormats = LogFormats.DETAILED,
    ) -> logging.Logger:
        """Configure both console and file logging."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if logger.handlers:
            logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level.value)
        console_formatter = logging.Formatter(format_type.value)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setLevel(file_level.value)
        file_formatter = logging.Formatter(format_type.value)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def configure_syslog_logging(
        name: str,
        level: LogLevel = LogLevel.INFO,
        address: str = "/dev/log",
    ) -> logging.Logger:
        """Configure syslog-based logging."""
        logger = logging.getLogger(name)
        logger.setLevel(level.value)

        if logger.handlers:
            logger.handlers.clear()

        try:
            handler = logging.handlers.SysLogHandler(address=address)
            handler.setLevel(level.value)
            formatter = logging.Formatter(LogFormats.DETAILED.value)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except Exception:
            # Fallback to console if syslog not available
            logging.warning("Syslog not available, falling back to console logging")
            return LoggerBootstrap.configure_console_logging(name, level)

        return logger


class ContextLogger:
    """Logger with context-aware formatting."""

    def __init__(
        self,
        name: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.logger = logging.getLogger(name)
        self.context = context or {}

    def add_context(self, key: str, value: Any) -> None:
        """Add a context variable."""
        self.context[key] = value

    def clear_context(self) -> None:
        """Clear all context variables."""
        self.context.clear()

    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if not self.context:
            return message

        context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{message} [{context_str}]"

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self.add_context("level", "DEBUG")
        self.logger.debug(self._format_message(message), **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self.add_context("level", "INFO")
        self.logger.info(self._format_message(message), **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self.add_context("level", "WARNING")
        self.logger.warning(self._format_message(message), **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self.add_context("level", "ERROR")
        self.logger.error(self._format_message(message), **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self.add_context("level", "CRITICAL")
        self.logger.critical(self._format_message(message), **kwargs)


class LoggingConfig:
    """Configuration for logging setup."""

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        use_console: bool = True,
        log_file: Optional[Path] = None,
        format_type: LogFormats = LogFormats.DETAILED,
    ):
        self.name = name
        self.level = level
        self.use_console = use_console
        self.log_file = log_file
        self.format_type = format_type

    def apply(self) -> logging.Logger:
        """Apply logging configuration and return logger."""
        if self.use_console and self.log_file:
            return LoggerBootstrap.configure_dual_logging(
                self.name,
                self.log_file,
                console_level=self.level,
                format_type=self.format_type,
            )
        elif self.log_file:
            return LoggerBootstrap.configure_file_logging(
                self.name,
                self.log_file,
                level=self.level,
                format_type=self.format_type,
            )
        else:
            return LoggerBootstrap.configure_console_logging(
                self.name,
                level=self.level,
                format_type=self.format_type,
            )


__all__ = [
    "LogLevel",
    "LogFormats",
    "LoggerBootstrap",
    "ContextLogger",
    "LoggingConfig",
]
