"""Error logging helpers for Codex tasks.

These utilities append structured entries to ``docs/troubleshooting/error_log.md`` whenever
file operations or external API calls fail. The format matches the audit
requirements so downstream tooling can parse remediation steps.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["append_error", "append_error_to_file", "log_error"]

_ERROR_LOG_PATH = Path("docs/troubleshooting/error_log.md")


def append_error(step_number: str, description: str, message: str, context: str) -> None:
    """Record an error using the mandated Codex template.

    Parameters
    ----------
    step_number:
        Identifier for the task step (for example ``"3.1"``).
    description:
        Short human-friendly description of the attempted operation.
    message:
        The raw exception message that was raised.
    context:
        Additional debugging context (such as the file path or
        configuration snippet in use).
    """

    timestamp = datetime.now(UTC).isoformat()
    entry_lines = [
        f"> Question from ChatGPT @codex {timestamp}:",
        (
            "> While performing "
            f"[{step_number}:{description}], encountered the following error: "
            f"{message}. Context: {context}."
        ),
        (
            "> What are the possible causes, and how can this be resolved while "
            "preserving intended functionality?"
        ),
        "",
    ]
    entry = "\n".join(entry_lines) + "\n"
    try:
        _ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _ERROR_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(entry)
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        # The error log must never raise a secondary exception; downstream
        # callers still need the original error to propagate.
        return


def log_error(
    message: str,
    exception: Exception | None = None,
    severity: str = "ERROR",
    context: dict | None = None,
    log_file: str | None = None,
) -> None:
    """Log error with timestamp and optional exception details.

    Parameters
    ----------
    message:
        Error message to log.
    exception:
        Optional exception object to include details.
    severity:
        Log level (ERROR, WARNING, INFO, etc.).
    context:
        Optional dictionary with contextual information.
    log_file:
        Optional custom log file path. Defaults to logs/errors.log.
    """
    timestamp = datetime.now(UTC).isoformat()
    log_path = Path(log_file) if log_file else Path("logs/errors.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_entry = f"[{timestamp}] [{severity}] {message}\n"
    if exception:
        log_entry += f"  Exception: {type(exception).__name__}: {exception}\n"
    if context:
        log_entry += f"  Context: {context}\n"

    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(log_entry)
    except (IOError, OSError):
        logger.warning("Failed to write to error log", exc_info=True)


def append_error_to_file(message: str, file_path: str) -> None:
    """Append error message to specified file.

    Parameters
    ----------
    message:
        Error message to append.
    file_path:
        Path to the log file.
    """
    log_path = Path(file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except (IOError, OSError):
        logger.warning("Failed to append error to file", exc_info=True)
