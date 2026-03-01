"""
Cognitive Brain — CLI & API Gateway Server
==========================================
FastAPI server that exposes two capabilities to the React frontend:

  WebSocket  /ws/cli          — real-time bidirectional terminal (PTY)
  REST       /api/request     — HTTP proxy (GET/POST/PUT/PATCH/DELETE)
  REST       /api/cli/run     — one-shot command execution (stdout + stderr)
  REST       /api/cli/history — last N commands with results
  GET        /api/health      — liveness check

Run:
    uvicorn cognitive_app.src.server.cli_api_server:app --host 0.0.0.0 --port 8765 --reload
"""

from __future__ import annotations

import asyncio
import fcntl
import json
import logging
import os
import pty
import re
import select
import sqlite3
import struct
import subprocess
import termios
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Sprint 3: cognitive orchestrator — module-level import with env-safe fallback ──
# REPO_ROOT computed later; sys.path extended once here so OODA endpoints don't
# modify sys.path on every request (avoids reviewer concern about per-request mutation).
import sys as _sys
def _find_repo_root() -> str:
    """Walk up from this file until we find a pyproject.toml or .git — repo root marker."""
    from pathlib import Path  # noqa: PLC0415 (module-level import order doesn't matter here)
    candidate = Path(__file__).resolve()
    for _ in range(8):  # max 8 levels up; avoids infinite loop on broken installs
        candidate = candidate.parent
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return str(candidate)
    # Fallback: 4 levels up from this file (cognitive_app/src/server/ → repo root)
    return str(Path(__file__).resolve().parents[3])

_repo_root_for_import = _find_repo_root()
if _repo_root_for_import not in _sys.path:
    _sys.path.insert(0, _repo_root_for_import)
try:
    from cognitive_app.src.orchestrator import get_cognitive_app as _get_cognitive_app
    _OODA_AVAILABLE = True
except ImportError:
    _get_cognitive_app = None  # type: ignore[assignment]
    _OODA_AVAILABLE = False

# Also try to import Planner/MemoryInterface at module level for auto-init
try:
    from cognitive_brain.base import MemoryInterface as _MemoryInterface  # noqa: E402
    from cognitive_brain.base import Planner as _Planner  # noqa: E402
    _BRAIN_BASE_AVAILABLE = True
except ImportError:
    _Planner = None  # type: ignore[assignment,misc]
    _MemoryInterface = None  # type: ignore[assignment,misc]
    _BRAIN_BASE_AVAILABLE = False

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cli_api_server")


# ── Sprint 2: CORS allowlist helper ──────────────────────────────────────────
def _build_cors_origins() -> list[str]:
    """Read CODEX_ALLOWED_ORIGINS (comma-separated) from env; fall back to dev defaults."""
    env_val = os.environ.get("CODEX_ALLOWED_ORIGINS", "").strip()
    if env_val:
        origins = [o.strip() for o in env_val.split(",") if o.strip()]
        log.info("CORS origins from CODEX_ALLOWED_ORIGINS: %s", origins)
        return origins
    return ["http://localhost:5173", "http://127.0.0.1:5173"]


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Cognitive Brain CLI & API Gateway",
    description="Real-time terminal + HTTP proxy for the Cognitive Brain console",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    # Sprint 2: CORS allowlist from CODEX_ALLOWED_ORIGINS env var (comma-separated).
    # Falls back to localhost dev origins when the env var is absent.
    allow_origins=_build_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sprint 2: SQLite-backed command history ───────────────────────────────────
MAX_HISTORY = 200

# DB path: CODEX_DB_PATH env var → default ~/.codex/cli_history.db
_DB_PATH = os.environ.get(
    "CODEX_DB_PATH",
    os.path.join(os.path.expanduser("~"), ".codex", "cli_history.db"),
)


def _init_history_db() -> sqlite3.Connection:
    """Open (or create) the SQLite history database and return a connection."""
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # enables named column access
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cli_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            command   TEXT NOT NULL,
            stdout    TEXT,
            stderr    TEXT,
            returncode INTEGER,
            duration_ms REAL,
            cwd       TEXT,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


_db: sqlite3.Connection = _init_history_db()
_db_lock = threading.Lock()  # SQLite single-writer guard for async/multi-thread safety

# In-memory mirror for O(1) recent-N access (still capped at MAX_HISTORY)
_history: Deque[Dict[str, Any]] = deque(maxlen=MAX_HISTORY)

# Pre-load last MAX_HISTORY records from DB so history survives server restarts
try:
    _rows = _db.execute(
        "SELECT command,stdout,stderr,returncode,duration_ms,cwd,timestamp "
        "FROM cli_history ORDER BY id DESC LIMIT ?",
        (MAX_HISTORY,),
    ).fetchall()
    for _r in reversed(_rows):
        _history.append({
            "command": _r["command"], "stdout": _r["stdout"], "stderr": _r["stderr"],
            "returncode": _r["returncode"], "duration_ms": _r["duration_ms"],
            "cwd": _r["cwd"], "timestamp": _r["timestamp"],
        })
    log.info("Loaded %d history entries from SQLite (%s)", len(_rows), _DB_PATH)
except sqlite3.OperationalError as _e:
    log.warning("SQLite schema error pre-loading history (DB corrupt or schema mismatch?): %s", _e)
except sqlite3.DatabaseError as _e:
    log.warning("SQLite database error pre-loading history (connection failure?): %s", _e)
except Exception as _e:
    log.warning("Unexpected error pre-loading history from SQLite: %s", _e)

# Repo root (4 levels up from this file: server/ → src/ → cognitive_app/ → repo/)
REPO_ROOT = str(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))))

# ── Schemas ───────────────────────────────────────────────────────────────────

class CliRunRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    timeout: Optional[int] = 30
    env: Optional[Dict[str, str]] = None


class ApiProxyRequest(BaseModel):
    method: str           # GET POST PUT PATCH DELETE HEAD OPTIONS
    url: str              # full URL or path (resolved against base_url if relative)
    headers: Optional[Dict[str, str]] = None
    params:  Optional[Dict[str, str]] = None
    body:    Optional[Any] = None
    base_url: Optional[str] = None
    timeout: Optional[int] = 30


class CliRunResponse(BaseModel):
    command:     str
    stdout:      str
    stderr:      str
    returncode:  int
    duration_ms: float
    cwd:         str
    timestamp:   str


class ApiProxyResponse(BaseModel):
    status_code: int
    headers:     Dict[str, str]
    body:        Any
    duration_ms: float
    url:         str
    method:      str


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "repo_root": REPO_ROOT,
        "timestamp": datetime.utcnow().isoformat(),
        "history_db": _DB_PATH,
    }


# ── Sprint 3: OODA loop endpoints — wire CognitiveAppMain to the React frontend
# The orchestrator.py global instance is imported lazily to avoid import errors
# when the cognitive_brain.base deps are not installed (CI environment).

@app.post("/api/ooda/process")
async def ooda_process(req: Dict[str, Any]):
    """
    Route input through the real CognitiveAppMain.process() OODA loop.
    Sprint 3: replaces mock-api-client in AgentOrchestrationPanel.

    Request body: { "input": {...}, "context": {...} }
    Response: ActionResult serialized as JSON.
    """
    if not _OODA_AVAILABLE or _get_cognitive_app is None:
        return {
            "success": False,
            "output": None,
            "metrics": {},
            "errors": ["Cognitive orchestrator not available in this environment"],
        }
    try:
        app_instance = _get_cognitive_app()
        if not app_instance._orchestrator:
            # Auto-initialize with lightweight stubs when not yet wired
            if _BRAIN_BASE_AVAILABLE and _Planner and _MemoryInterface:
                app_instance.initialize(_Planner(), _MemoryInterface())
        result = app_instance.process(
            input_data=req.get("input", {}),
            context=req.get("context"),
        )
        return {
            "success": result.success,
            "output": result.output,
            "metrics": result.metrics,
            "errors": result.errors,
        }
    except Exception as exc:
        log.warning("OODA process error (returning graceful fallback): %s", exc)
        return {
            "success": False,
            "output": None,
            "metrics": {},
            "errors": [str(exc)],
        }


@app.get("/api/ooda/metrics")
async def ooda_metrics():
    """
    Return aggregated OODA execution metrics.
    Sprint 3: drives MetricsDashboard K1 factor display.
    """
    if not _OODA_AVAILABLE or _get_cognitive_app is None:
        return {"metrics": {}, "timestamp": datetime.utcnow().isoformat(),
                "error": "Cognitive orchestrator not available"}
    try:
        metrics = _get_cognitive_app().get_metrics()
        return {"metrics": metrics, "timestamp": datetime.utcnow().isoformat()}
    except Exception as exc:
        log.warning("OODA metrics error: %s", exc)
        return {"metrics": {}, "timestamp": datetime.utcnow().isoformat(), "error": str(exc)}


# ── CLI one-shot endpoint ─────────────────────────────────────────────────────

# Commands that are never allowed (safety boundary)
_BLOCKED = re.compile(
    r'\b(rm\s+-rf\s+/|mkfs|dd\s+if=|shutdown|reboot|:(){ :|:& };:)\b'
)


@app.post("/api/cli/run", response_model=CliRunResponse)
async def cli_run(req: CliRunRequest):
    """Execute a shell command and return stdout/stderr/returncode."""
    if _BLOCKED.search(req.command):
        raise HTTPException(status_code=400, detail="Command blocked by safety filter")

    cwd = req.cwd or REPO_ROOT
    env = {**os.environ, **(req.env or {})}

    t0 = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_shell(
            req.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=req.timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            stdout, stderr = b"", b"[timeout after %ds]" % req.timeout
            proc.returncode = -1
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    duration_ms = (time.monotonic() - t0) * 1000
    record: Dict[str, Any] = {
        "command":     req.command,
        "stdout":      stdout.decode(errors="replace"),
        "stderr":      stderr.decode(errors="replace"),
        "returncode":  proc.returncode or 0,
        "duration_ms": round(duration_ms, 1),
        "cwd":         cwd,
        "timestamp":   datetime.utcnow().isoformat(),
    }
    _history.append(record)
    # Sprint 2: persist to SQLite for cross-session history
    try:
        with _db_lock:
            _db.execute(
                "INSERT INTO cli_history (command,stdout,stderr,returncode,duration_ms,cwd,timestamp) "
                "VALUES (?,?,?,?,?,?,?)",
                (record["command"], record["stdout"], record["stderr"],
                 record["returncode"], record["duration_ms"], record["cwd"], record["timestamp"]),
            )
            _db.commit()
    except Exception as _e:
        log.debug("SQLite history write failed (non-blocking): %s", _e)
    log.info("cli_run rc=%s %.0fms cmd=%r", record["returncode"], duration_ms, req.command[:80])
    return record


@app.get("/api/cli/history")
async def cli_history(limit: int = 50):
    """Return the last N command executions (in-memory mirror; survives restarts via SQLite)."""
    items = list(_history)
    return {"items": items[-limit:], "total": len(items)}


@app.delete("/api/cli/history")
async def cli_clear_history():
    """Clear command history (both in-memory and SQLite)."""
    _history.clear()
    try:
        with _db_lock:
            _db.execute("DELETE FROM cli_history")
            _db.commit()
    except Exception as _e:
        log.debug("SQLite history clear failed (non-blocking): %s", _e)
    return {"cleared": True}


# ── HTTP API proxy endpoint ───────────────────────────────────────────────────

@app.post("/api/request", response_model=ApiProxyResponse)
async def api_proxy(req: ApiProxyRequest):
    """
    Proxy an HTTP request to any URL and return the response.
    Supports GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.
    """
    method = req.method.upper()
    allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
    if method not in allowed_methods:
        raise HTTPException(status_code=400, detail=f"Unsupported method: {method!r}")

    # Resolve relative URLs against base_url
    url = req.url
    if req.base_url and not url.startswith(("http://", "https://")):
        url = req.base_url.rstrip("/") + "/" + url.lstrip("/")

    headers = dict(req.headers or {})
    # Auto Content-Type for JSON body
    if req.body is not None and "content-type" not in {k.lower() for k in headers}:
        headers["Content-Type"] = "application/json"

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=req.timeout, follow_redirects=True) as client:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=req.params,
                json=req.body if isinstance(req.body, (dict, list)) else None,
                content=req.body.encode() if isinstance(req.body, str) else None,
            )
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=502, detail=f"Connection error: {exc}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    duration_ms = (time.monotonic() - t0) * 1000

    # Parse response body — JSON preferred, fall back to text
    try:
        body = resp.json()
    except Exception:
        body = resp.text

    log.info("api_proxy %s %s → %s (%.0fms)", method, url, resp.status_code, duration_ms)
    return {
        "status_code": resp.status_code,
        "headers":     dict(resp.headers),
        "body":        body,
        "duration_ms": round(duration_ms, 1),
        "url":         str(resp.url),
        "method":      method,
    }


# ── WebSocket PTY terminal ────────────────────────────────────────────────────

@app.websocket("/ws/cli")
async def ws_cli(ws: WebSocket):
    """
    Real-time PTY terminal over WebSocket.

    Client → Server JSON messages:
      { "type": "input",  "data": "<keystrokes>" }
      { "type": "resize", "cols": N, "rows": N }

    Server → Client JSON messages:
      { "type": "output", "data": "<terminal output>" }
      { "type": "exit",   "code": N }
    """
    await ws.accept()
    log.info("WS PTY session opened")

    master_fd, slave_fd = pty.openpty()
    shell = os.environ.get("SHELL", "/bin/bash")

    proc = subprocess.Popen(
        [shell, "--login"],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=REPO_ROOT,
        env={**os.environ, "TERM": "xterm-256color", "COLORTERM": "truecolor"},
        close_fds=True,
    )
    os.close(slave_fd)
    loop = asyncio.get_event_loop()

    async def read_pty() -> None:
        """Drain PTY output and forward to WebSocket."""
        try:
            while True:
                r, _, _ = await loop.run_in_executor(
                    None, select.select, [master_fd], [], [], 0.05
                )
                if r:
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if data:
                        await ws.send_json({
                            "type": "output",
                            "data": data.decode(errors="replace"),
                        })
                if proc.poll() is not None:
                    # Drain remaining output
                    try:
                        while select.select([master_fd], [], [], 0)[0]:
                            chunk = os.read(master_fd, 4096)
                            if not chunk:
                                break
                            await ws.send_json({
                                "type": "output",
                                "data": chunk.decode(errors="replace"),
                            })
                    except OSError as exc:
                        # Best-effort drain: PTY may already be closed; ignore and exit.
                        log.debug("Ignoring OSError while draining PTY output: %s", exc)
                    await ws.send_json({"type": "exit", "code": proc.returncode or 0})
                    break
        except WebSocketDisconnect:
            # Client disconnected — normal control flow; stop reading silently.
            pass
        except RuntimeError as exc:
            log.debug("Unexpected RuntimeError in read_pty: %s", exc)

    async def write_pty() -> None:
        """Forward WebSocket keystrokes to the PTY."""
        try:
            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                kind = msg.get("type")
                if kind == "input":
                    os.write(master_fd, msg["data"].encode())
                elif kind == "resize":
                    cols = max(1, int(msg.get("cols", 80)))
                    rows = max(1, int(msg.get("rows", 24)))
                    winsize = struct.pack("HHHH", rows, cols, 0, 0)
                    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
        except WebSocketDisconnect:
            # Client disconnected — normal control flow; stop writing silently.
            pass
        except RuntimeError as exc:
            log.debug("Unexpected RuntimeError in write_pty: %s", exc)

    try:
        await asyncio.gather(read_pty(), write_pty())
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        try:
            os.close(master_fd)
        except OSError as exc:
            # Best-effort cleanup: master_fd may already be closed or invalid.
            log.debug("Error while closing PTY master_fd: %s", exc)
        log.info("WS PTY session closed (pid=%s rc=%s)", proc.pid, proc.returncode)
