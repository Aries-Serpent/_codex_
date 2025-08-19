"""Lightweight session logging to newline-delimited JSON files."""

from __future__ import annotations

import atexit
import json
import os
import pathlib
import sys
import time
import uuid
from datetime import UTC, datetime

LOG_DIR = pathlib.Path(os.environ.get("CODEX_SESSION_LOG_DIR", ".codex/sessions"))
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _now():
    """Return current UTC time in ISO-8601 Zulu format."""

    return datetime.utcnow().replace(tzinfo=UTC).isoformat().replace("+00:00", "Z")


def _session_id():
    """Fetch or create a session identifier and cache it in the environment."""

    sid = os.environ.get("CODEX_SESSION_ID")
    if not sid:
        sid = f"{uuid.uuid4()}"
        os.environ["CODEX_SESSION_ID"] = sid
    return sid


def _log(obj: dict):
    """Append a JSON object as a single line to the session log file."""

    sid = _session_id()
    path = LOG_DIR / f"{sid}.ndjson"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


class session:
    """Context manager capturing start and end of a CLI session."""

    def __init__(self, argv=None):
        self.sid = _session_id()
        self.start_ts = time.time()
        self.argv = list(argv) if argv is not None else sys.argv

    def __enter__(self):
        # Write quick meta file and record start event
        (LOG_DIR / f"{self.sid}.meta").write_text(
            f"{_now()} session_start {self.sid}\n"
        )
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

    def _end(self, exit_code: int | None = None):
        """Log session end metadata with duration and exit code."""

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

    def __exit__(self, exc_type, exc, tb):
        # Non-zero exit code indicates an exception occurred
        self._end(1 if exc else 0)
        return False
