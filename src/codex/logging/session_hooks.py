"""Lightweight session logging to newline-delimited JSON files.

This module provides a minimal, dependency‑free session logging facility for
both shell and Python driven CLI executions. It writes two files per session:

  * <SESSION_ID>.meta   – first line contains a quick start marker
  * <SESSION_ID>.ndjson – newline‑delimited JSON events (start, end, etc.)

Merged Features:
- Uses a resilient `_log_path` helper that (re)creates the directory if deleted.
- Retains explicit path `.resolve()` semantics from the alternate branch.
- Adds defensive error handling (graceful fallback; never raises user‑visible
  exceptions during logging).
- Maintains backward compatibility: public behavior and environment variables
  unchanged.

Environment Variables:
  CODEX_SESSION_LOG_DIR  Directory for log files (defaults to .codex/sessions)
  CODEX_SESSION_ID       Optional externally provided session identifier
"""

from __future__ import annotations

import atexit
import json
import os
import pathlib
import sys
import time
import uuid
from datetime import UTC, datetime
from typing import Any, Iterable, Literal, Optional

__all__ = [
    "session",
    "LOG_DIR",
    "_session_id",
    "_log_path",
]

# ---------------------------------------------------------------------------
# Directory resolution (expanded & absolute for stability across cwd changes)
# ---------------------------------------------------------------------------
LOG_DIR = pathlib.Path(os.environ.get("CODEX_SESSION_LOG_DIR", ".codex/sessions"))
LOG_DIR = LOG_DIR.expanduser().resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------
def _log_path(name: str) -> pathlib.Path:
    """Return path under ``LOG_DIR`` (recreating directory if it vanished)."""
    if not LOG_DIR.exists():
        # Directory may have been deleted mid-execution; recreate.
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Last resort: attempt a second time with a short fallback; if this
            # fails we still continue (logging is best-effort).
            try:
                LOG_DIR.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
    return (LOG_DIR / name).resolve()


def _now() -> str:
    """Return current UTC time in ISO-8601 Zulu format."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _session_id() -> str:
    """Fetch or create a session identifier and cache it in the environment."""
    sid = os.environ.get("CODEX_SESSION_ID")
    if not sid:
        sid = f"{uuid.uuid4()}"
        os.environ["CODEX_SESSION_ID"] = sid
    return sid


def _safe_write_text(path: pathlib.Path, text: str, mode: str = "w") -> None:
    """Write text to a file, recreating directory if needed (best-effort)."""
    try:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError:
        # Retry once after ensuring directory exists
        try:
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except OSError:
            # Suppress: logging must not break caller
            pass


def _safe_append_json_line(path: pathlib.Path, obj: dict[str, Any]) -> None:
    """Append a JSON object as a single NDJSON line (best-effort)."""
    line = json.dumps(obj, separators=(",", ":")) + "\n"
    try:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        # Retry once after directory recreation
        try:
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(line)
        except OSError:
            # Suppress to avoid impacting primary program flow
            pass


def _log(obj: dict[str, Any]) -> None:
    """Append a JSON object as a single line to the session log file."""
    sid = _session_id()
    path = _log_path(f"{sid}.ndjson")
    _safe_append_json_line(path, obj)


# ---------------------------------------------------------------------------
# Public session context manager
# ---------------------------------------------------------------------------
class session:
    """Context manager capturing start and end of a CLI session.

    Example:
        from codex.logging.session_logger import session
        with session():
            main()

    Args:
        argv: Iterable of argument strings (defaults to sys.argv)
    """

    def __init__(self, argv: Optional[Iterable[str]] = None):
        self.sid = _session_id()
        self.start_ts = time.time()
        self.argv = list(argv) if argv is not None else sys.argv
        self._ended = False

    # --- context protocol -------------------------------------------------
    def __enter__(self) -> "session":
        # Write quick meta file and record start event
        meta = _log_path(f"{self.sid}.meta")
        _safe_write_text(meta, f"{_now()} session_start {self.sid}\n")
        _log(
            {
                "ts": _now(),
                "type": "session_start",
                "session_id": self.sid,
                "cwd": os.getcwd(),
                "argv": self.argv,
            }
        )
        atexit.register(self._end)  # ensure end event even on abrupt exit
        return self

    def __exit__(self, exc_type, exc, tb) -> Literal[False]:
        # Non-zero exit code indicates an exception occurred
        self._end(1 if exc else 0)
        # Do not suppress exceptions
        return False

    # --- internal ---------------------------------------------------------
    def _end(self, exit_code: int | None = None) -> None:
        """Log session end metadata with duration and exit code."""
        if self._ended:
            return
        self._ended = True
        if exit_code is None:
            exit_code = 0
        dur = max(0, int(time.time() - self.start_ts))
        _log(
            {
                "ts": _now(),
                "type": "session_end",
                "session_id": self.sid,
                "exit_code": exit_code,
                "duration_s": dur,
            }
        )
