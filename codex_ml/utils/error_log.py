"""Best-effort error logging utility."""

from __future__ import annotations

import json
import sys
from pathlib import Path

__all__ = ["log_error"]


def log_error(kind: str, message: str, context: str | None = None) -> None:
    payload = {"kind": kind, "message": message}
    if context is not None:
        payload["context"] = context
    sys.stderr.write(json.dumps(payload, ensure_ascii=False) + "\n")
