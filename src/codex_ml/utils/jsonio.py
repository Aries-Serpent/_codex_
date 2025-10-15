"""Helpers for CLI JSON stdout discipline."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from typing import Any


def _ensure_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def print_json(payload: Any) -> None:
    """Emit exactly one JSON document to stdout followed by a newline."""

    sys.stdout.write(_ensure_newline(json.dumps(payload)))


def print_error_json(
    message: str,
    *,
    code: int | None = None,
    details: Mapping[str, Any] | None = None,
) -> None:
    """Emit a normalized error envelope suitable for CLI consumption."""

    output: dict[str, Any] = {"ok": False, "error": str(message)}
    if code is not None:
        output["code"] = int(code)
    if details:
        output["details"] = dict(details)
    print_json(output)


__all__ = ["print_json", "print_error_json"]
