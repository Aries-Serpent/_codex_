from __future__ import annotations

import json
import time
from pathlib import Path

ERROR_PATH = Path(".codex/errors.ndjson")
ROTATE_AFTER = 60 * 60 * 24  # 1 day


def log_error(step: str, err: str, ctx: str) -> None:
    """Append an error record to ``.codex/errors.ndjson``."""
    entry = {"step": step, "err": err, "ctx": ctx}
    try:
        ERROR_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ERROR_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def log(msg: str, path: Path = Path("error.log")) -> None:
    """Append ``msg`` to ``path`` and rotate if the file is old."""
    path = Path(path)
    now = time.time()
    if path.exists():
        try:
            mtime = path.stat().st_mtime
            if now - mtime > ROTATE_AFTER:
                rotated = path.with_name(path.name + f".{int(mtime)}")
                path.rename(rotated)
        except Exception:
            pass
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(msg)
