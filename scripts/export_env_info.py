#!/usr/bin/env python3
"""Export environment and version info as JSON."""
from __future__ import annotations

import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

CODEX = Path(__file__).resolve().parents[1] / ".codex"
ERRORS = CODEX / "errors.ndjson"
CODEX.mkdir(parents=True, exist_ok=True)


def ts() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_error(step: str, err: str, ctx: str) -> None:
    """Append a formatted error entry and emit a research question."""
    message = (
        f"Question for ChatGPT @codex {ts()}:\n"
        f"While performing [{step}], encountered the following error:\n"
        f"{err}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?"
    )
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx})
            + "\n"
        )
    sys.stderr.write(message + "\n")


def collect_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "env": {k: v for k, v in os.environ.items() if k.startswith("CODEX_")},
    }
    try:
        import torch  # type: ignore

        info["torch"] = torch.__version__
        info["cuda"] = torch.version.cuda if torch.cuda.is_available() else None
    except Exception as exc:  # noqa: BLE001
        log_error("1: import torch", repr(exc), "collecting torch and cuda versions")
        info["torch"] = None
        info["cuda"] = None
    return info


def main() -> None:
    try:
        print(json.dumps(collect_info(), indent=2))  # noqa: T201
    except Exception as exc:  # noqa: BLE001
        log_error("2: export info", repr(exc), "serialising environment info")
        raise


if __name__ == "__main__":
    main()
