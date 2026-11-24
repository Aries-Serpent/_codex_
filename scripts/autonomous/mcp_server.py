"""Stdio MCP bridge to the Codespace Cognitive Brain middleware."""

from __future__ import annotations

import asyncio
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.autonomous.codespace_keepalive import runtime_dir_default, touch_active_marker
from scripts.autonomous.maintainer_control import maintainer_status


def approved_api_base(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.query
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("MCP API origin is invalid")
    if parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}:
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")
    configured = {
        origin.strip().rstrip("/")
        for origin in os.environ.get("CODEX_ALLOWED_CLI_API_ORIGINS", "").split(",")
        if origin.strip()
    }
    normalized = value.rstrip("/")
    if parsed.scheme == "https" and normalized in configured:
        return normalized
    raise ValueError("MCP API origin is not approved")


API_BASE = approved_api_base(os.environ.get("CODEX_CLI_API_URL") or "http://127.0.0.1:8765")
ALLOWED_ORIGIN = os.environ.get("CODEX_MCP_ORIGIN", "http://localhost:5173")
_ALLOWED_PATHS = {
    "/api/session",
    "/api/capabilities",
    "/api/routes/plan",
    "/api/routes/execute",
}

TOOLS = [
    {
        "name": "cognitive_brain_capabilities",
        "description": "Discover server-observed Cognitive Brain routes and adapter states",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "cognitive_brain_route_plan",
        "description": "Plan a server-classified route without executing it",
        "inputSchema": {
            "type": "object",
            "required": ["capability", "action", "target"],
            "properties": {
                "capability": {"type": "string"},
                "action": {"type": "string"},
                "target": {"type": "string"},
                "arguments": {"type": "object"},
                "idempotency_key": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "cognitive_brain_route_execute",
        "description": "Execute an authenticated idempotent Cognitive Brain route",
        "inputSchema": {
            "type": "object",
            "required": ["capability", "action", "target", "idempotency_key"],
            "properties": {
                "capability": {"type": "string"},
                "action": {"type": "string"},
                "target": {"type": "string"},
                "arguments": {"type": "object"},
                "idempotency_key": {"type": "string", "minLength": 1, "maxLength": 256},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "cognitive_brain_maintainer_status",
        "description": "Read the canonical owner, auth, keepalive, and maintainer procedures",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "cognitive_brain_keepalive_touch",
        "description": "Renew the bounded active-agent Codespace keepalive window",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


class BrainTransport:
    """Small cookie-aware client for the local Cognitive Brain API."""

    def __init__(self) -> None:
        self._jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._jar))
        self._session_ready = False

    def bootstrap_capability(self) -> str:
        configured = os.environ.get("CODEX_UI_BOOTSTRAP_MCP", "").strip()
        if configured:
            return configured
        token_file = ROOT / ".codex" / "ui_bootstrap_mcp"
        try:
            return token_file.read_text(encoding="utf-8").strip()
        except OSError:
            return ""

    def request(self, method: str, path: str, body: Mapping[str, Any] | None = None) -> Any:
        if path not in _ALLOWED_PATHS:
            raise RuntimeError("Unsupported Cognitive Brain path")
        if not self._session_ready and path != "/api/session":
            self.request("POST", "/api/session")
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json", "Origin": ALLOWED_ORIGIN}
        if path == "/api/session":
            capability = self.bootstrap_capability()
            if not capability:
                raise RuntimeError("Cognitive Brain session bootstrap unavailable")
            headers["X-Codex-Bootstrap"] = capability
        request = urllib.request.Request(
            f"{API_BASE}{path}",
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with self._opener.open(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Cognitive Brain HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise RuntimeError("Cognitive Brain transport failed") from exc
        if path == "/api/session":
            self._session_ready = True
        return payload


async def call_tool(name: str, arguments: Mapping[str, Any], transport: BrainTransport) -> Any:
    def invoke() -> Any:
        touch_active_marker(runtime_dir_default())
        if name == "cognitive_brain_maintainer_status":
            return maintainer_status()
        if name == "cognitive_brain_keepalive_touch":
            marker = touch_active_marker(runtime_dir_default())
            return {"active": True, "marker": str(marker)}
        if name == "cognitive_brain_capabilities":
            return transport.request("GET", "/api/capabilities")
        if name == "cognitive_brain_route_plan":
            return transport.request("POST", "/api/routes/plan", arguments)
        if name == "cognitive_brain_route_execute":
            payload = dict(arguments)
            payload.pop("allow_write", None)
            return transport.request("POST", "/api/routes/execute", payload)
        raise ValueError(f"Unknown tool: {name}")

    return await asyncio.to_thread(invoke)


def result_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True)


async def handle_message(
    message: Mapping[str, Any],
    transport: Any | None = None,
) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if request_id is None:
        return None
    try:
        if method == "initialize":
            result: Any = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "codex-cognitive-brain", "version": "1.0.0"},
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            name = str(params.get("name", ""))
            arguments = params.get("arguments") or {}
            if not isinstance(arguments, dict):
                raise ValueError("tool arguments must be an object")
            payload = await call_tool(
                name, arguments, transport if transport is not None else BrainTransport()
            )
            result = {"content": [{"type": "text", "text": result_text(payload)}]}
        elif method == "ping":
            result = {}
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": "Cognitive Brain tool failed"},
        }


async def main() -> int:
    transport = BrainTransport()
    while True:
        line = await asyncio.to_thread(sys.stdin.buffer.readline)
        if not line:
            return 0
        try:
            message = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            response: dict[str, Any] | None = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Invalid JSON input"},
            }
        else:
            response = await handle_message(message, transport=transport)
        if response is not None:
            print(json.dumps(response, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
