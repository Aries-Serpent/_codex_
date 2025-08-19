# Session logging helper (Python)
from __future__ import annotations
import atexit, json, os, sys, time, uuid, pathlib, datetime as dt

LOG_DIR = pathlib.Path(os.environ.get("CODEX_SESSION_LOG_DIR", ".codex/sessions"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _now():
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat().replace("+00:00","Z")

def _session_id():
    sid = os.environ.get("CODEX_SESSION_ID")
    if not sid:
        sid = f"{uuid.uuid4()}"
        os.environ["CODEX_SESSION_ID"] = sid
    return sid

def _log(obj: dict):
    sid = _session_id()
    with (LOG_DIR / f"{sid}.ndjson").open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")

class session:
    def __init__(self, argv=None):
        self.sid = _session_id()
        self.start_ts = time.time()
        self.argv = list(argv) if argv is not None else sys.argv

    def __enter__(self):
        (LOG_DIR / f"{self.sid}.meta").write_text(f"{_now()} session_start {self.sid}\n")
        _log({"ts": _now(), "type": "session_start", "session_id": self.sid, "cwd": os.getcwd(), "argv": self.argv})
        atexit.register(self._end)
        return self

    def _end(self, exit_code: int | None = None):
        if exit_code is None:
            exit_code = 0
        dur = max(0, int(time.time() - self.start_ts))
        _log({"ts": _now(), "type": "session_end", "session_id": self.sid, "exit_code": exit_code, "duration_s": dur})

    def __exit__(self, exc_type, exc, tb):
        self._end(1 if exc else 0)
        return False
