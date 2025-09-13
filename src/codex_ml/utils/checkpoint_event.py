from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import IO, Dict, Optional

_ENV_FLAG = "CODEX_EMIT_CHECKPOINT_JSON"


def toggle_checkpoint_json_logging(enable: Optional[bool] = None) -> bool:
    """Enable or disable checkpoint JSON event emission."""

    if enable is None:
        return os.getenv(_ENV_FLAG, "0") == "1"
    os.environ[_ENV_FLAG] = "1" if enable else "0"
    return enable


def _sha256(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for blk in iter(lambda: fh.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def maybe_emit_checkpoint_saved_event(
    path: str | os.PathLike[str],
    *,
    sha256: Optional[str] = None,
    num_bytes: Optional[int] = None,
    extra: Optional[Dict[str, object]] = None,
    stream: Optional[IO[str]] = None,
) -> bool:
    """If enabled, emit one JSON line describing a saved checkpoint."""

    try:
        if not toggle_checkpoint_json_logging(None):
            return False
        p = Path(path)
        nb = num_bytes if num_bytes is not None else (p.stat().st_size if p.exists() else None)
        digest = sha256 if sha256 is not None else (_sha256(p) if p.exists() else None)
        payload: Dict[str, object] = {
            "event": "checkpoint_saved",
            "path": str(p),
            "bytes": nb,
            "sha256": digest,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
        }
        if extra:
            payload.update(extra)
        out = stream or sys.stdout
        out.write(json.dumps(payload, separators=(",", ":")) + "\n")
        out.flush()
        return True
    except Exception:
        return False


__all__ = ["toggle_checkpoint_json_logging", "maybe_emit_checkpoint_saved_event"]
