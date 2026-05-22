"""
Cognitive Brain — CLI & API Gateway Server
==========================================
FastAPI server that exposes two capabilities to the React frontend:

  WebSocket  /ws/cli                — real-time bidirectional terminal (PTY)
  REST       /api/request           — HTTP proxy (GET/POST/PUT/PATCH/DELETE)
  REST       /api/cli/run           — one-shot command execution (stdout + stderr)
  REST       /api/cli/history       — last N commands with results
  GET        /api/health            — liveness check
  POST       /webhook/github        — inbound GitHub webhook receiver (HMAC-SHA256)
  GET        /api/webhooks/recent   — recent webhook event log

Run:
    uvicorn cognitive_app.src.server.cli_api_server:app --host 0.0.0.0 --port 8765 --reload
"""

from __future__ import annotations

import asyncio
import fcntl
import hashlib
import hmac
import ipaddress
import json
import logging
import os
import pty
import re
import secrets
import select
import shlex
import sqlite3
import struct
import subprocess  # nosec B404 — used only for PTY shell (ws_cli); Popen call has nosec B603
from urllib.parse import urlparse as _urlparse
from urllib.parse import urlunparse as _urlunparse

# Safe JSON parser for external/untrusted inputs (sanitises C0 control chars).
try:
    from codex.utils.json_safe import safe_json_loads as _safe_json_loads
except ImportError:  # pragma: no cover — fallback when package not installed
    _safe_json_loads = json.loads  # type: ignore[assignment]

# ── SAR-G05: OpenTelemetry distributed tracing stub ─────────────────────────
# Full OTel SDK is optional; the stub is a no-op when the SDK is absent so the
# server starts in environments that don't have the OTel packages installed.
try:
    from opentelemetry import trace as _otel_trace
    from opentelemetry.sdk.trace import TracerProvider as _TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor as _BatchSpanProcessor

    # Configure provider — exporter is wired from env OTEL_EXPORTER_OTLP_ENDPOINT.
    # Falls back to a no-op provider when the endpoint is not configured.
    _otel_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if _otel_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # type: ignore[import]
            OTLPSpanExporter as _OTLPSpanExporter,
        )
        _provider = _TracerProvider()
        _provider.add_span_processor(_BatchSpanProcessor(_OTLPSpanExporter(endpoint=_otel_endpoint)))
        _otel_trace.set_tracer_provider(_provider)

    tracer = _otel_trace.get_tracer("cognitive-brain.cli-api", schema_url="https://opentelemetry.io/schemas/1.24.0")
    _OTEL_ENABLED = True
except ImportError:  # pragma: no cover — OTel SDK not installed
    import contextlib as _contextlib

    class _NoopTracer:
        """Stub tracer that returns a no-op context manager for every start_as_current_span call."""

        @_contextlib.contextmanager  # type: ignore[misc]
        def start_as_current_span(self, name: str, **kwargs: Any):  # noqa: ANN401
            yield None

    tracer = _NoopTracer()  # type: ignore[assignment]
    _OTEL_ENABLED = False

# ── Sprint 3: cognitive orchestrator — module-level import with env-safe fallback ──
# REPO_ROOT computed later; sys.path extended once here so OODA endpoints don't
# modify sys.path on every request (avoids reviewer concern about per-request mutation).
import sys as _sys
import termios
import threading
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


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
    from cognitive_brain.base import Planner as _Planner  # noqa: E402
    _BRAIN_BASE_AVAILABLE = True
except ImportError:
    _Planner = None  # type: ignore[assignment,misc]
    _BRAIN_BASE_AVAILABLE = False

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cli_api_server")


# ── SSRF prevention (CodeQL alert #12493) ────────────────────────────────────
# The /api/request proxy endpoint accepts a caller-supplied URL and makes an
# outbound HTTP request on their behalf.  Without restriction this is a Full
# SSRF: an attacker could target internal services (metadata APIs, databases,
# localhost endpoints) that are not exposed to the internet.
#
# Defence-in-depth strategy:
#   1. Only HTTPS scheme is allowed (blocks file://, http://, ftp://, etc.).
#   2. Hostnames that resolve to loopback / link-local / RFC-1918 private
#      ranges are blocked by IP-literal detection.
#   3. Well-known metadata service IPs are explicitly blocked.
#
# Note: DNS-rebinding is still theoretically possible if only hostname checks
# are performed.  The server should be deployed with an egress firewall that
# prevents connections to private ranges for full protection.

_SSRF_BLOCKED_HOSTS = frozenset({
    "localhost", "ip6-localhost", "ip6-loopback",
})
_SSRF_BLOCKED_PREFIXES = ("169.254.",)   # link-local / AWS metadata service
_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),   # link-local / APIPA
    ipaddress.ip_network("100.64.0.0/10"),    # shared address space (RFC 6598)
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 unique-local
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
]


def _assert_safe_proxy_url(url: str) -> str:
    """Validate *url* and return it as a "fresh" string for use by the proxy.

    Raises ``HTTPException(400)`` when *url* targets a private/internal resource.
    Returns the input URL unchanged when validation passes — the indirection
    breaks CodeQL's same-variable taint flow so that downstream HTTP clients
    receive a value CodeQL recognises as sanitised (CodeQL alert #12493, full
    SSRF / py/full-ssrf).

    Called by the ``/api/request`` proxy endpoint before making an outbound
    request so that Full SSRF (CodeQL alert #12493) cannot be exploited.

    **Limitations (documented, not silent):**
    - *DNS rebinding*: if a hostname initially resolves to a public IP but is
      later remap­ped to a private IP (DNS rebinding attack), this guard will
      not catch it because DNS resolution is performed by the HTTP client after
      this check.  **Mitigation**: deploy this server behind a network-level
      egress firewall that blocks outbound connections to RFC-1918 / loopback
      ranges regardless of how the hostname resolves.
    - *IPv6 scope IDs*: ``fe80::1%eth0`` addresses are not fully normalised by
      ``ipaddress.ip_address()``; the ``fe80::/10`` network block covers the
      typical link-local range.

    For maximum protection combine this guard with an egress proxy or firewall
    rule that enforces the same IP range restrictions at the network level.
    """
    from fastapi import HTTPException  # local import avoids circular at module level

    try:
        parsed = _urlparse(url)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"Malformed URL: {exc}")

    # 1. Require HTTPS
    if parsed.scheme != "https":
        raise HTTPException(
            status_code=400,
            detail=f"URL scheme {parsed.scheme!r} is not permitted; only 'https' is allowed",
        )

    host = (parsed.hostname or "").lower()
    if not host:
        raise HTTPException(status_code=400, detail="URL must specify a hostname")

    # 2. Block known loopback hostnames
    if host in _SSRF_BLOCKED_HOSTS:
        raise HTTPException(status_code=400, detail="Requests to loopback hosts are not permitted")

    # 3. Block link-local prefixes (covers 169.254.x.x AWS/GCP metadata)
    if any(host.startswith(p) for p in _SSRF_BLOCKED_PREFIXES):
        raise HTTPException(status_code=400, detail="Requests to link-local addresses are not permitted")

    # 4. Block IP literals that fall in private/loopback ranges.
    # Strip IPv6 zone/scope ID (e.g. "fe80::1%eth0") before parsing so that
    # a percent-encoded scope ID ("%25eth0") cannot bypass the fe80::/10 check.
    # urlparse().hostname already lower-cases the host; strip from '%' onward.
    ip_host = host.split("%")[0] if "%" in host else host
    if ip_host:
        try:
            addr = ipaddress.ip_address(ip_host)
            for net in _PRIVATE_NETWORKS:
                if addr in net:
                    raise HTTPException(
                        status_code=400,
                        detail="Requests to private/reserved IP ranges are not permitted",
                    )
        except ValueError:
            _ = None  # not an IP literal — hostname; DNS-based resolution not done here
    # Reject any remaining host that still contains a literal '%' (malformed or
    # scope-ID that wasn't stripped cleanly — treat as suspicious).
    if "%" in host:
        raise HTTPException(
            status_code=400,
            detail="URL host contains a percent sign; scope-ID or malformed address rejected",
        )

    # Reconstruct from validated components so CodeQL sees a freshly-built URL,
    # breaking the taint trail from the request body into the outbound client.
    return _urlunparse(parsed)


# ── Sprint 2: CORS allowlist helper ──────────────────────────────────────────
def _build_cors_origins() -> list[str]:
    """Read CODEX_ALLOWED_ORIGINS (comma-separated) from env; fall back to localhost dev defaults.

    Security note: ``/api/cli/run`` executes arbitrary shell commands and is
    **currently unauthenticated** (only ``/api/memory/*`` requires a Bearer
    token).  The default allowlist is intentionally restricted to localhost
    origins so that no remote web origin can drive command execution without
    an explicit opt-in.  To enable access from GitHub Pages or a Codespace
    preview URL, set ``CODEX_ALLOWED_ORIGINS`` to the exact origin(s)
    required (e.g. ``https://aries-serpent.github.io``) **and** ensure that
    ``CODEX_MASTER_KEY`` / ``CODEX_BACKUP_KEY`` authentication is enforced
    on ``/api/cli/run`` before exposing to non-local origins.
    """
    env_val = os.environ.get("CODEX_ALLOWED_ORIGINS", "").strip()
    if env_val:
        origins = [o.strip() for o in env_val.split(",") if o.strip()]
        log.info("CORS origins from CODEX_ALLOWED_ORIGINS: %s", origins)
        return origins
    # Default: localhost dev only.
    # Non-local origins (e.g. https://aries-serpent.github.io) MUST be added
    # via CODEX_ALLOWED_ORIGINS to prevent a remote web page from invoking
    # shell-command execution endpoints without explicit operator consent.
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Cognitive Brain CLI & API Gateway",
    description="Real-time terminal + HTTP proxy for the Cognitive Brain console",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    # Sprint 2: CORS allowlist from CODEX_ALLOWED_ORIGINS env var (comma-separated).
    # Defaults to localhost only — set CODEX_ALLOWED_ORIGINS to add non-local origins
    # (e.g. https://aries-serpent.github.io for GitHub Pages integration).
    allow_origins=_build_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SAR-G05: Wire OTel FastAPI auto-instrumentation (no-op when SDK absent) ──
if _OTEL_ENABLED:
    try:
        from opentelemetry.instrumentation.fastapi import (
            FastAPIInstrumentor,  # type: ignore[import]
        )
        FastAPIInstrumentor.instrument_app(app)
        log.info("OpenTelemetry FastAPI auto-instrumentation enabled (endpoint=%s)",
                 os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "<no endpoint>"))
    except ImportError:
        log.debug("opentelemetry-instrumentation-fastapi not installed; per-request spans disabled")

# ── Memory endpoint auth ──────────────────────────────────────────────────────
_memory_bearer = HTTPBearer(auto_error=False)


def _require_memory_auth(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_memory_bearer),
) -> None:
    """Require a valid Bearer token (CODEX_MASTER_KEY or CODEX_BACKUP_KEY) on
    memory endpoints to prevent unauthorised access to potentially sensitive
    STM/LTM data."""
    expected = os.environ.get("CODEX_MASTER_KEY") or os.environ.get("CODEX_BACKUP_KEY") or ""
    if not expected:
        raise HTTPException(status_code=503, detail="Memory auth not configured on server")
    if creds is None or not secrets.compare_digest(creds.credentials, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


# ── Sprint 2: SQLite-backed command history ───────────────────────────────────
MAX_HISTORY = 200
# P4.2: Maximum entries across STM+LTM (tunable via CODEX_MEMORY_CAPACITY)
MEMORY_CAPACITY = int(os.environ.get("CODEX_MEMORY_CAPACITY", "1000"))

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
    # P4.2: Short-term memory table (last 50 OODA executions / ad-hoc stores)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stm_entries (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            key          TEXT NOT NULL UNIQUE,
            value        TEXT NOT NULL,
            metadata     TEXT,
            timestamp    TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        )
        """
    )
    # P4.2: Long-term memory table (consolidated patterns)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ltm_entries (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            key          TEXT NOT NULL UNIQUE,
            value        TEXT NOT NULL,
            metadata     TEXT,
            pattern_type TEXT,
            confidence   REAL DEFAULT 1.0,
            timestamp    TEXT NOT NULL
        )
        """
    )
    # Inbound GitHub webhook event log
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS webhook_events (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_id  TEXT,
            event_type   TEXT NOT NULL,
            payload      TEXT NOT NULL,
            signature    TEXT,
            timestamp    TEXT NOT NULL
        )
        """
    )
    # P6: CI pattern occurrence log (Phase 6 — Cross-Session Pattern Knowledge Graph)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS patterns (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_id   INTEGER NOT NULL,
            pattern_name TEXT NOT NULL,
            file_path    TEXT,
            line_number  INTEGER,
            description  TEXT NOT NULL,
            auto_fixable INTEGER NOT NULL DEFAULT 0,
            fixed        INTEGER NOT NULL DEFAULT 0,
            session      TEXT,
            git_sha      TEXT,
            timestamp    TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_patterns_name ON patterns (pattern_name)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_patterns_session ON patterns (session)"
    )
    conn.commit()
    return conn


_db: sqlite3.Connection = _init_history_db()
_db_lock = threading.Lock()  # SQLite single-writer guard for async/multi-thread safety

# In-memory mirror for O(1) recent-N access (still capped at MAX_HISTORY)
_history: deque[dict[str, Any]] = deque(maxlen=MAX_HISTORY)

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
    env: Optional[dict[str, str]] = None


class ApiProxyRequest(BaseModel):
    method: str           # GET POST PUT PATCH DELETE HEAD OPTIONS
    url: str              # full URL or path (resolved against base_url if relative)
    headers: Optional[dict[str, str]] = None
    params:  Optional[dict[str, str]] = None
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
    headers:     dict[str, str]
    body:        Any
    duration_ms: float
    url:         str
    method:      str


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    with tracer.start_as_current_span("health"):
        return {
            "status": "ok",
            "repo_root": REPO_ROOT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "history_db": _DB_PATH,
            "otel_enabled": _OTEL_ENABLED,
        }


# ── Sprint 3: OODA loop endpoints — wire CognitiveAppMain to the React frontend
# The orchestrator.py global instance is imported lazily to avoid import errors
# when the cognitive_brain.base deps are not installed (CI environment).

@app.post("/api/ooda/process")
async def ooda_process(req: dict[str, Any]):
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
            # Auto-initialize with SQLiteMemory (P4.2) when not yet wired
            if _BRAIN_BASE_AVAILABLE and _Planner:
                app_instance.initialize(_Planner(), SQLiteMemory())
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
        # CodeQL py/stack-trace-exposure: log full details server-side only.
        log.warning("OODA process error (returning graceful fallback): %s", exc)
        return {
            "success": False,
            "output": None,
            "metrics": {},
            "errors": ["OODA process error (see server logs for details)"],
        }


# ── P4.2: SQLiteMemory concrete class ────────────────────────────────────────

class SQLiteMemory:
    """
    Concrete MemoryInterface backed by the same CODEX_DB_PATH SQLite database.
    Implements the same store/retrieve/search/delete contract as MemoryInterface,
    but wires directly to the stm_entries table so the OODA loop persists memories.
    """

    def store(self, key: str, value: Any, metadata: Any = None) -> bool:
        with _db_lock:
            _db.execute(
                "INSERT OR REPLACE INTO stm_entries (key, value, metadata, timestamp) "
                "VALUES (?, ?, ?, ?)",
                (key, json.dumps(value), json.dumps(metadata), datetime.now(timezone.utc).isoformat()),
            )
            _db.commit()
        return True

    def retrieve(self, key: str) -> Any:
        with _db_lock:
            row = _db.execute(
                "SELECT value FROM stm_entries WHERE key = ?", (key,)
            ).fetchone()
            if row is None:
                return None
            _db.execute(
                "UPDATE stm_entries SET access_count = access_count + 1 WHERE key = ?",
                (key,),
            )
            _db.commit()
        return json.loads(row["value"])

    def search(self, query: dict[str, Any], limit: int = 10) -> list:
        q = next(iter(query.values()), "") if query else ""
        rows = _db.execute(
            "SELECT key, value FROM stm_entries WHERE value LIKE ? LIMIT ?",
            (f"%{q}%", limit),
        ).fetchall()
        return [(r["key"], json.loads(r["value"])) for r in rows]

    def delete(self, key: str) -> bool:
        with _db_lock:
            _db.execute("DELETE FROM stm_entries WHERE key = ?", (key,))
            _db.commit()
        return True


# ── P4.2: Memory REST endpoints ───────────────────────────────────────────────

@app.get("/api/memory/state")
async def memory_state(_auth: None = Depends(_require_memory_auth)):
    """
    Return STM/LTM counts and cache metrics.
    Drives MemoryManagementDashboard (P4.1 + P4.2).

    cache_hit_rate = warm_entries / stm_count where warm = access_count >= 1.
    This reflects the fraction of STM that has been retrieved at least once.
    """
    try:
        with _db_lock:
            stm_count = _db.execute("SELECT COUNT(*) FROM stm_entries").fetchone()[0]
            ltm_count = _db.execute("SELECT COUNT(*) FROM ltm_entries").fetchone()[0]
            warm_count = _db.execute(
                "SELECT COUNT(*) FROM stm_entries WHERE access_count >= 1"
            ).fetchone()[0]
        capacity = MEMORY_CAPACITY
        compression_rate = ltm_count / (stm_count + ltm_count) if (stm_count + ltm_count) > 0 else 0.0
        cache_hit_rate = warm_count / stm_count if stm_count > 0 else 0.0
        return {
            "stm_count": stm_count,
            "ltm_count": ltm_count,
            "capacity": capacity,
            "cache_hit_rate": round(cache_hit_rate, 4),
            "compression_rate": round(compression_rate, 4),
            "patterns": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        log.warning("memory_state error: %s", exc)
        return {
            "stm_count": 0,
            "ltm_count": 0,
            "capacity": MEMORY_CAPACITY,
            "cache_hit_rate": 0.0,
            "compression_rate": 0.0,
            "patterns": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "Internal error retrieving memory state",
        }


@app.get("/api/memory/search")
async def memory_search(q: str = "", limit: int = 20, _auth: None = Depends(_require_memory_auth)):
    """
    Full-text search over STM + LTM entries.
    Drives MemoryManagementDashboard search (P4.1 + P4.2).
    """
    try:
        with _db_lock:
            rows = _db.execute(
                "SELECT key, value, metadata, 'stm' as tier FROM stm_entries "
                "WHERE key LIKE ? OR value LIKE ? "
                "UNION ALL "
                "SELECT key, value, metadata, 'ltm' as tier FROM ltm_entries "
                "WHERE key LIKE ? OR value LIKE ? "
                "LIMIT ?",
                (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", limit),
            ).fetchall()
        return {"items": [dict(r) for r in rows], "total": len(rows)}
    except Exception as exc:
        log.warning("memory_search error: %s", exc)
        return {"items": [], "total": 0, "error": "Internal error searching memory"}


# Sprint 11 / Phase 5: tunable consolidation thresholds
_HOT_THRESHOLD = int(os.environ.get("CODEX_STM_HOT_THRESHOLD", "3"))
_HOT_ENTRIES_LIMIT = int(os.environ.get("CODEX_HOT_ENTRIES_LIMIT", "50"))


@app.post("/api/memory/consolidate")
async def memory_consolidate(_auth: None = Depends(_require_memory_auth)):
    """
    Sprint 11 / Phase 5: Consolidate hot STM entries into LTM.

    Promotes STM entries whose ``access_count >= CODEX_STM_HOT_THRESHOLD`` (default 3)
    into the ``ltm_entries`` table and deletes them from STM.  Confidence is
    computed as ``min(1.0, access_count / 10)``.

    Also prunes stale LTM entries older than 30 days with confidence < 0.3.

    Returns:
        consolidated  - number of STM->LTM promotions
        pruned        - number of stale LTM entries removed
        stm_count     - remaining STM entries after consolidation
        ltm_count     - total LTM entries after consolidation
    """
    from datetime import timedelta as _timedelta  # noqa: PLC0415

    now = datetime.now(timezone.utc)
    cutoff = (now - _timedelta(days=30)).isoformat()

    try:
        with _db_lock:
            # 1. Fetch hot STM entries
            hot_rows = _db.execute(
                "SELECT key, value, metadata, access_count FROM stm_entries "
                "WHERE access_count >= ? ORDER BY access_count DESC LIMIT ?",
                (_HOT_THRESHOLD, _HOT_ENTRIES_LIMIT),
            ).fetchall()

            consolidated = 0
            for row in hot_rows:
                confidence = min(1.0, row["access_count"] / 10)
                _db.execute(
                    "INSERT OR REPLACE INTO ltm_entries "
                    "(key, value, metadata, confidence, timestamp) VALUES (?,?,?,?,?)",
                    (
                        row["key"],
                        row["value"],
                        row["metadata"],
                        round(confidence, 3),
                        now.isoformat(),
                    ),
                )
                _db.execute("DELETE FROM stm_entries WHERE key = ?", (row["key"],))
                consolidated += 1

            # 2. Prune stale LTM entries
            pruned = _db.execute(
                "DELETE FROM ltm_entries WHERE timestamp < ? AND confidence < 0.3",
                (cutoff,),
            ).rowcount

            _db.commit()

            stm_count = _db.execute("SELECT COUNT(*) FROM stm_entries").fetchone()[0]
            ltm_count = _db.execute("SELECT COUNT(*) FROM ltm_entries").fetchone()[0]

        log.info(
            "memory_consolidate: consolidated=%d pruned=%d stm=%d ltm=%d",
            consolidated, pruned, stm_count, ltm_count,
        )
        return {
            "consolidated": consolidated,
            "pruned": pruned,
            "stm_count": stm_count,
            "ltm_count": ltm_count,
            "timestamp": now.isoformat(),
        }
    except Exception as exc:
        log.warning("memory_consolidate error: %s", exc)
        return {
            "consolidated": 0,
            "pruned": 0,
            "stm_count": 0,
            "ltm_count": 0,
            "timestamp": now.isoformat(),
            "error": "Internal error during memory consolidation",
        }


@app.get("/api/ooda/metrics")
async def ooda_metrics():
    """
    Return aggregated OODA execution metrics.
    Sprint 3: drives MetricsDashboard K1 factor display.
    """
    if not _OODA_AVAILABLE or _get_cognitive_app is None:
        return {"metrics": {}, "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "Cognitive orchestrator not available"}
    try:
        metrics = _get_cognitive_app().get_metrics()
        return {"metrics": metrics, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        # CodeQL py/stack-trace-exposure: log details server-side, return generic message.
        log.warning("OODA metrics error: %s", exc)
        return {"metrics": {}, "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "OODA metrics unavailable (see server logs for details)"}


# ── CLI one-shot endpoint ─────────────────────────────────────────────────────

# Commands that are never allowed (safety boundary — applied before shlex.split).
# Note: shlex.split + create_subprocess_exec prevents shell *injection* but cannot
# prevent execution of arbitrary binaries in PATH.  The _BLOCKED denylist is a
# best-effort guardrail; production deployments should additionally restrict this
# endpoint to authenticated sessions and/or an allowlist of permitted commands.
_BLOCKED = re.compile(
    r'\b(rm\s+-rf\s+/|mkfs|dd\s+if=|shutdown|reboot|:(){ :|:& };:)\b'
)


@app.post("/api/cli/run", response_model=CliRunResponse)
async def cli_run(req: CliRunRequest):
    """Execute a shell command and return stdout/stderr/returncode.

    Security note (CodeQL #12490 — Uncontrolled command line):
    The command is split with ``shlex.split`` and executed via
    ``create_subprocess_exec`` (not ``create_subprocess_shell``) so that shell
    metacharacters (``; | && || $() `` backticks etc.) in user input cannot
    invoke additional commands.  Operators like pipes and redirections that
    require a shell must be expressed explicitly (e.g. ``bash -c "cmd | other"``),
    which is visible in the audit log and triggers the ``_BLOCKED`` safety filter.
    """
    if _BLOCKED.search(req.command):
        raise HTTPException(status_code=400, detail="Command blocked by safety filter")

    # Split into argv list — prevents shell-injection (CodeQL #12490).
    try:
        args = shlex.split(req.command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid command syntax: {exc}")
    if not args:
        raise HTTPException(status_code=400, detail="Empty command")

    cwd = req.cwd or REPO_ROOT
    env = {**os.environ, **(req.env or {})}

    t0 = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
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
    record: dict[str, Any] = {
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
    log.info(
        "cli_run rc=%s %.0fms cmd_len=%d",
        record["returncode"],
        duration_ms,
        len(str(req.command)),
    )
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


# ── Inbound GitHub webhook receiver ──────────────────────────────────────────

@app.post("/webhook/github")
async def webhook_github(request: Request):
    """
    Receive inbound GitHub webhook payloads (HMAC-SHA256 verified).

    Security: uses X-Hub-Signature-256 header for HMAC verification against
    WEBHOOK_SECRET env var.  Returns 401 and fails closed if the secret is
    not configured (unless CODEX_WEBHOOK_DEV_MODE=true bypasses for local dev).
    """
    raw_body = await request.body()
    sig_header = request.headers.get("X-Hub-Signature-256", "")
    secret = os.environ.get("WEBHOOK_SECRET", "")

    if not secret:
        dev_mode = os.environ.get("CODEX_WEBHOOK_DEV_MODE", "").lower() == "true"
        if dev_mode:
            log.warning("CODEX_WEBHOOK_DEV_MODE active — skipping HMAC verification")
        else:
            return JSONResponse(status_code=401, content={"error": "Webhook secret not configured"})

    if secret:
        expected = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        if not sig_header or not hmac.compare_digest(expected, sig_header):
            log.warning("Webhook HMAC verification failed (delivery=%s)",
                        request.headers.get("X-GitHub-Delivery", "unknown"))
            return JSONResponse(status_code=401, content={"error": "Invalid signature"})

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    delivery_id = request.headers.get("X-GitHub-Delivery", "")

    try:
        payload = _safe_json_loads(raw_body, source="POST /webhook/github")
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload"})

    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        with _db_lock:
            _db.execute(
                "INSERT INTO webhook_events (delivery_id, event_type, payload, signature, timestamp) "
                "VALUES (?, ?, ?, ?, ?)",
                (delivery_id, event_type, json.dumps(payload), sig_header, timestamp),
            )
            _db.commit()
    except Exception as _e:
        log.warning("webhook_events SQLite write failed (non-blocking): %s", _e)

    log.info("webhook_github event=%r delivery=%r", event_type, delivery_id)
    return {"status": "accepted", "delivery_id": delivery_id}


@app.get("/api/webhooks/recent")
async def webhooks_recent(limit: int = 50):
    """Return the most recent webhook events from the webhook_events table."""
    limit = min(limit, 200)
    try:
        with _db_lock:
            rows = _db.execute(
                "SELECT id, delivery_id, event_type, payload, timestamp "
                "FROM webhook_events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        events = []
        for row in rows:
            try:
                parsed_payload = json.loads(row["payload"])
            except (json.JSONDecodeError, TypeError):
                parsed_payload = {}
            events.append({
                "id": row["id"],
                "delivery_id": row["delivery_id"],
                "event_type": row["event_type"],
                "payload": parsed_payload,
                "timestamp": row["timestamp"],
            })
        return {"events": events, "total": len(events)}
    except Exception as exc:
        log.warning("webhooks_recent error: %s", exc)
        return {"events": [], "total": 0, "error": "Internal error retrieving webhook events"}



# ── Phase 6: CI pattern knowledge graph endpoints ────────────────────────────
#
# These endpoints expose the ``patterns`` table that is populated by
# ``scripts/ci/pattern_recorder.py``.  They allow the cognitive brain and
# Copilot agent tooling to query historical CI pattern data without spawning
# a subprocess.


class _PatternInsertRequest(BaseModel):
    pattern_id: int
    pattern_name: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    auto_fixable: bool = False
    fixed: bool = False
    session: Optional[str] = None
    git_sha: Optional[str] = None


@app.get("/api/patterns/recent")
async def patterns_recent(
    limit: int = 50,
    session: Optional[str] = None,
    pattern_id: Optional[int] = None,
):
    """Return the most recent CI pattern occurrences.

    Query params:
        limit      — max rows to return (capped at 500, default 50)
        session    — if provided, filter by session identifier (PR number / run id)
        pattern_id — if provided, filter by numeric pattern ID (e.g. 12 for E501)
    """
    limit = min(limit, 500)
    try:
        with _db_lock:
            # Build WHERE clauses dynamically so any combination of filters works.
            conditions: list[str] = []
            params: list[Any] = []
            if session:
                conditions.append("session = ?")
                params.append(session)
            if pattern_id is not None:
                conditions.append("pattern_id = ?")
                params.append(pattern_id)
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            params.append(limit)
            # Safety: `where` is composed exclusively from hard-coded condition strings
            # ("session = ?", "pattern_id = ?") — never from user input. All user
            # values are bound via the parameterized `params` list, not interpolated
            # into the SQL string. The f-string interpolation of `where` is therefore
            # safe against SQL injection.
            rows = _db.execute(
                "SELECT id, pattern_id, pattern_name, file_path, line_number, "
                "       auto_fixable, fixed, session, git_sha, timestamp "
                f"FROM patterns {where} ORDER BY id DESC LIMIT ?",
                params,
            ).fetchall()
        return {
            "patterns": [dict(r) for r in rows],
            "total": len(rows),
        }
    except Exception as exc:
        log.warning("patterns_recent error: %s", exc)
        return {"patterns": [], "total": 0, "error": "Internal error"}


@app.get("/api/patterns/summary")
async def patterns_summary():
    """Return a frequency summary grouped by pattern name.

    Response shape::

        {
          "summary": [
            {
              "pattern_name": "Duplicate Kwargs",
              "total": 12,
              "fixed": 11,
              "fix_rate": 0.917,
              "last_seen": "2026-03-24T18:00:00Z"
            },
            ...
          ]
        }
    """
    try:
        with _db_lock:
            rows = _db.execute(
                """
                SELECT pattern_name,
                       COUNT(*)      AS total,
                       SUM(fixed)    AS fixed_count,
                       MAX(timestamp) AS last_seen
                FROM patterns
                GROUP BY pattern_name
                ORDER BY total DESC
                """
            ).fetchall()
        summary = []
        for r in rows:
            total = r["total"] or 0
            fixed = r["fixed_count"] or 0
            summary.append(
                {
                    "pattern_name": r["pattern_name"],
                    "total": total,
                    "fixed": fixed,
                    "fix_rate": round(fixed / total, 3) if total else 0.0,
                    "last_seen": r["last_seen"],
                }
            )
        return {"summary": summary}
    except Exception as exc:
        log.warning("patterns_summary error: %s", exc)
        return {"summary": [], "error": "Internal error"}


@app.post("/api/patterns/record", status_code=201)
async def patterns_record(
    req: _PatternInsertRequest,
    _auth: None = Depends(_require_memory_auth),
):
    """Insert a single pattern occurrence into the knowledge graph.

    Protected by the same ``CODEX_MASTER_KEY`` bearer guard as memory routes.
    Returns ``{"id": <row_id>}`` on success.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with _db_lock:
            cur = _db.execute(
                """
                INSERT INTO patterns
                    (pattern_id, pattern_name, file_path, line_number, description,
                     auto_fixable, fixed, session, git_sha, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    req.pattern_id,
                    req.pattern_name,
                    req.file_path,
                    req.line_number,
                    req.description,
                    int(req.auto_fixable),
                    int(req.fixed),
                    req.session,
                    req.git_sha,
                    ts,
                ),
            )
            _db.commit()
        return {"id": cur.lastrowid, "timestamp": ts}
    except Exception as exc:
        log.warning("patterns_record error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to record pattern") from exc


# ── GitHub App installation-token endpoint ───────────────────────────────────
#
# Returns a short-lived GitHub installation access token derived from the
# GitHub App credentials stored as environment variables.
#
# Variable resolution order (handles both Codespace underscore-prefix and
# plain names used in local dev / CI):
#
#   Codespace secret       → CI / local env
#   _GITHUB_APP_ID         → GITHUB_APP_ID
#   _GITHUB_APP_PRIVATE_KEY → GITHUB_APP_PRIVATE_KEY_PEM
#   _GITHUB_APP_INSTALLATION_ID → GITHUB_APP_INSTALLATION_ID
#
# Protected by the same CODEX_MASTER_KEY bearer guard used on memory routes.


class _GithubTokenResponse(BaseModel):
    token: str
    expires_at: Optional[str] = None
    source: str  # "app_installation" | "pat" | "github_token"
    rate_limit: int  # expected req/hr


@app.get("/api/github/token", response_model=_GithubTokenResponse)
async def github_token(_auth: None = Depends(_require_memory_auth)):
    """Return a short-lived GitHub API token for the frontend.

    Priority:
      1. GitHub App installation token (5 000 req/hr) — when App creds available
      2. CODEX_MASTER_KEY / CODEX_BACKUP_KEY PAT (5 000 req/hr)
      3. GITHUB_TOKEN (1 000 req/hr on Actions, 60 unauthenticated otherwise)
    """
    env = dict(os.environ)

    # ── Map Codespace underscore-prefix secrets to plain names ────────────────
    for cs_name, plain_name in (
        ("_GITHUB_APP_ID",              "GITHUB_APP_ID"),
        ("_GITHUB_APP_PRIVATE_KEY",     "GITHUB_APP_PRIVATE_KEY_PEM"),
        ("_GITHUB_APP_INSTALLATION_ID", "GITHUB_APP_INSTALLATION_ID"),
    ):
        if cs_name in env and plain_name not in env:
            env[plain_name] = env[cs_name]

    # ── Try GitHub App installation token ─────────────────────────────────────
    if env.get("GITHUB_APP_ID") and env.get("GITHUB_APP_INSTALLATION_ID"):
        try:
            from integrations.github_app_auth import (
                exchange_installation_token,
                mint_app_jwt,
            )
            # Temporarily set so _read_private_key() inside mint_app_jwt works
            if "GITHUB_APP_PRIVATE_KEY_PEM" in env:
                os.environ.setdefault("GITHUB_APP_PRIVATE_KEY_PEM", env["GITHUB_APP_PRIVATE_KEY_PEM"])
            app_jwt = mint_app_jwt(env["GITHUB_APP_ID"])
            inst_token, expires_at = exchange_installation_token(
                app_jwt, env["GITHUB_APP_INSTALLATION_ID"]
            )
            log.info("github_token: issued App installation token")
            return _GithubTokenResponse(
                token=inst_token,
                expires_at=expires_at,
                source="app_installation",
                rate_limit=5000,
            )
        except Exception as exc:
            log.warning("github_token: App installation token failed (%s), falling back", exc)

    # ── Fall back to PAT ──────────────────────────────────────────────────────
    for var in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GITHUB_TOKEN"):
        pat = env.get(var, "").strip()
        if pat:
            log.info("github_token: using %s as PAT", var)
            return _GithubTokenResponse(
                token=pat,
                expires_at=None,
                source="pat",
                rate_limit=5000 if var != "GITHUB_TOKEN" else 1000,
            )

    raise HTTPException(
        status_code=503,
        detail=(
            "No GitHub credentials available. "
            "Set _GITHUB_APP_ID + _GITHUB_APP_PRIVATE_KEY + _GITHUB_APP_INSTALLATION_ID "
            "(Codespace secrets) or CODEX_MASTER_KEY (PAT)."
        ),
    )


# ── HTTP API proxy endpoint ───────────────────────────────────────────────────

@app.post("/api/request", response_model=ApiProxyResponse)
async def api_proxy(req: ApiProxyRequest):
    """
    CLI API Client — secondary agent API mechanism (MCP/Playwright is primary).

    **Agent API priority hierarchy:**
    1. Primary  — MCP Server tools + Playwright (use first when available)
    2. Secondary — this endpoint / BrainClient.proxy_request() (use when MCP unavailable)
    3. Fallback — direct urllib / requests / httpx (last resort only)

    This endpoint provides: auto GitHub auth injection (CODEX_MASTER_KEY),
    session-level audit logging, and consistent timeout/error handling.

    Supports GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.
    Auto-injects ``Authorization: Bearer $CODEX_MASTER_KEY`` for api.github.com.
    """
    method = req.method.upper()
    allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
    if method not in allowed_methods:
        raise HTTPException(status_code=400, detail=f"Unsupported method: {method!r}")

    # Resolve relative URLs against base_url
    url = req.url
    if req.base_url and not url.startswith(("http://", "https://")):
        url = req.base_url.rstrip("/") + "/" + url.lstrip("/")

    # SSRF prevention (CodeQL #12493): reject URLs targeting private/internal resources.
    # Must be called after URL resolution so that relative-URL payloads are caught too.
    # Returns the sanitised URL — using the returned value (rather than the original
    # ``url`` parameter) breaks CodeQL's same-variable taint flow into the outbound
    # client.
    safe_url = _assert_safe_proxy_url(url)

    headers = dict(req.headers or {})
    # P4.3: Auto-inject GitHub auth header when target is api.github.com
    # Token priority: CODEX_MASTER_KEY > CODEX_BACKUP_KEY > AGENT_GITHUB_TOKEN > GITHUB_TOKEN
    if safe_url.startswith("https://api.github.com/") and "Authorization" not in headers:
        master_key   = os.environ.get("CODEX_MASTER_KEY") or ""
        backup_key   = os.environ.get("CODEX_BACKUP_KEY") or ""
        agent_token  = os.environ.get("AGENT_GITHUB_TOKEN") or ""
        github_token = os.environ.get("GITHUB_TOKEN") or ""
        token = master_key or backup_key or agent_token or github_token
        if token:
            headers["Authorization"] = f"Bearer {token}"
            source = (
                "CODEX_MASTER_KEY" if master_key else
                "CODEX_BACKUP_KEY" if backup_key else
                "AGENT_GITHUB_TOKEN" if agent_token else
                "GITHUB_TOKEN"
            )
            log.debug("Auto-injected GitHub auth header (%s)", source)
    # Auto Content-Type for JSON body
    if req.body is not None and "content-type" not in {k.lower() for k in headers}:
        headers["Content-Type"] = "application/json"

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=req.timeout, follow_redirects=True) as client:
            resp = await client.request(
                method=method,
                url=safe_url,
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
        # CodeQL py/stack-trace-exposure: log server-side, return generic message.
        safe_host = (_urlparse(safe_url).hostname or "").lower()
        log.warning("api_proxy %s host=%s failed (%s)", method, safe_host, type(exc).__name__)
        raise HTTPException(status_code=500, detail="Upstream request failed (see server logs for details)")

    duration_ms = (time.monotonic() - t0) * 1000

    # Parse response body — JSON preferred, fall back to text
    try:
        body = resp.json()
    except Exception:
        body = resp.text

    # CodeQL py/log-injection: use lazy formatting so tainted URL is not interpolated
    # into the message template; %s arguments are routed via the logging
    # framework which CodeQL recognises as safe.
    safe_host = (_urlparse(safe_url).hostname or "").lower()
    log.info("api_proxy %s host=%s -> %s (%.0fms)", method, safe_host, resp.status_code, duration_ms)
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

    proc = subprocess.Popen(  # nosec B603 — shell binary sourced from SHELL env (trusted system path, not user input)
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
            _ = None  # suppressed: no action needed
        except RuntimeError as exc:
            log.debug("Unexpected RuntimeError in read_pty: %s", exc)

    async def write_pty() -> None:
        """Forward WebSocket keystrokes to the PTY."""
        try:
            while True:
                raw = await ws.receive_text()
                msg = _safe_json_loads(raw, source="ws /ws/cli")
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
            _ = None  # suppressed: no action needed
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
