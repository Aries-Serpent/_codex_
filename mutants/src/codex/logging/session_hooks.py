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
import logging
import os
import pathlib
import sys
import time
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any, Literal, Optional

logger = logging.getLogger(__name__)

try:  # Prefer DB-backed logging when available
    from .session_logger import log_event
except (IOError, OSError):  # pragma: no cover - best effort fallback

    def log_event(
        session_id: str,
        role: str,
        message: str,
        db_path: pathlib.Path | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Any:
        return None


__all__ = [
    "LOG_DIR",
    "_log_path",
    "_session_id",
    "session",
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
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning("Could not recreate LOG_DIR %s: %s", LOG_DIR, e)
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
    for attempt in range(2):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open(mode, encoding="utf-8", buffering=1) as f:
                f.write(text)
            return
        except OSError as err:
            if attempt == 0:
                logger.debug("write attempt 1 failed for %s: %s — retrying", path, err)
            else:
                logger.warning("write failed after retries for %s: %s", path, err)


def _safe_append_json_line(path: pathlib.Path, obj: dict[str, Any]) -> None:
    """Append a JSON object as a single NDJSON line (best-effort)."""
    line = json.dumps(obj, separators=(",", ":")) + "\n"
    for attempt in range(2):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8", buffering=1) as f:
                f.write(line)
            return
        except (OSError, json.JSONDecodeError) as err:
            if attempt == 0:
                logger.debug("append attempt 1 failed for %s: %s — retrying", path, err)
            else:
                logger.warning("append failed after retries for %s: %s", path, err)


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
    def __enter__(self) -> session:
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
        try:
            log_event(self.sid, "system", "session_start")
        except Exception:  # pragma: no cover - best effort
            logging.exception("session_start DB log failed")
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
        try:
            log_event(self.sid, "system", "session_end")
        except Exception:  # pragma: no cover - best effort
            logging.exception("session_end DB log failed")
