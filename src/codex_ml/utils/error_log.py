from __future__ import annotations

import json
from pathlib import Path

ERROR_PATH = Path(".codex/errors.ndjson")


def log_error(step: str, err: str, ctx: str) -> None:
    """Append an error record to ``.codex/errors.ndjson``."""
    entry = {"step": step, "err": err, "ctx": ctx}
    try:
        ERROR_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ERROR_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        pass
