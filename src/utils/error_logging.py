"""Error logging helpers for Codex tasks.

These utilities append structured entries to ``error_log.md`` whenever
file operations or external API calls fail. The format matches the audit
requirements so downstream tooling can parse remediation steps.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

__all__ = ["append_error"]

_ERROR_LOG_PATH = Path("error_log.md")


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

    timestamp = datetime.utcnow().isoformat()
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
    except Exception:
        # The error log must never raise a secondary exception; downstream
        # callers still need the original error to propagate.
        return
