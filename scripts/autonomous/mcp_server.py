"""Stdio MCP bridge to the Codespace Cognitive Brain middleware."""

from __future__ import annotations

import asyncio
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Callable, Mapping

API_BASE = (os.environ.get("CODEX_CLI_API_URL") or "http://127.0.0.1:8765").rstrip("/")
ALLOWED_ORIGIN = os.environ.get("CODEX_MCP_ORIGIN", "http://localhost:5173")

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
                "allow_write": {"type": "boolean", "default": False},
            },
            "additionalProperties": False,
        },
    },
]


class BrainTransport:
    """Small cookie-aware client for the local Cognitive Brain API."""

    def __init__(self) -> None:
        self._jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._jar))
        self._session_ready = False

    def request(self, method: str, path: str, body: Mapping[str, Any] | None = None) -> Any:
        if not self._session_ready and path != "/api/session":
            self.request("POST", "/api/session")
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            f"{API_BASE}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json", "Origin": ALLOWED_ORIGIN},
        )
        try:
            with self._opener.open(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Cognitive Brain HTTP {exc.code}: {detail[:500]}") from exc
        if path == "/api/session":
            self._session_ready = True
        return payload


async def call_tool(name: str, arguments: Mapping[str, Any], transport: BrainTransport) -> Any:
    def invoke() -> Any:
        if name == "cognitive_brain_capabilities":
            return transport.request("GET", "/api/capabilities")
        if name == "cognitive_brain_route_plan":
            return transport.request("POST", "/api/routes/plan", arguments)
        if name == "cognitive_brain_route_execute":
            payload = dict(arguments)
            payload["allow_write"] = bool(payload.get("allow_write", False))
            return transport.request("POST", "/api/routes/execute", payload)
        raise ValueError(f"Unknown tool: {name}")

    return await asyncio.to_thread(invoke)


def result_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True)


async def handle_message(
    message: Mapping[str, Any],
    transport_factory: Callable[[], BrainTransport] = BrainTransport,
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
            payload = await call_tool(name, arguments, transport_factory())
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
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": f"{type(exc).__name__}: {exc}"},
        }


async def main() -> int:
    while True:
        line = await asyncio.to_thread(sys.stdin.buffer.readline)
        if not line:
            return 0
        try:
            message = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
        else:
            response = await handle_message(message)  # type: ignore[arg-type]
        if response is not None:
            print(json.dumps(response, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
