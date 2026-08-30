"""
Errors Module

This module provides functionality for errors.

Usage:
    from utils.errors import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import json
import time
from pathlib import Path


def record_error(step_number: str, step_desc: str, error_msg: str, context: str = ""):
    """Append a structured error record to ``.codex/status/errors.ndjson``.

    Each call writes one JSON line to the NDJSON error log and appends a
    human-readable block to ``.codex/status/ERROR_CAPTURE_BLOCKS.md`` to help
    with async debugging (e.g. pasting into a chat assistant).

    Args:
        step_number: Short identifier for the pipeline step (e.g. ``"02"``).
        step_desc: Human-readable description of the step.
        error_msg: The error message or exception string to record.
        context: Optional extra context (environment, inputs, etc.).
    """
    p = Path(".codex/status")
    p.mkdir(parents=True, exist_ok=True)
    with (p / "errors.ndjson").open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "ts": time.time(),
                    "step": step_number,
                    "desc": step_desc,
                    "error": error_msg,
                    "context": context,
                }
            )
            + "\n"
        )
    blk = (
        ":::\n"
        f"Question for ChatGPT @codex {int(time.time())}:\n"
        f"While performing [{step_number}:{step_desc}], encountered the following error: {error_msg}\n"  # noqa: E501
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"  # noqa: E501
        ":::\n"
    )
    with (p / "ERROR_CAPTURE_BLOCKS.md").open("a", encoding="utf-8") as f:
        f.write(blk + "\n")
