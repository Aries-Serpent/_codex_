"""Tests for the Codespace Cognitive Brain MCP stdio bridge."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from scripts.autonomous.mcp_server import TOOLS, approved_api_base, handle_message


class FakeTransport:
    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        return {"method": method, "path": path, "body": body}


def test_initialize_and_list_tools() -> None:
    initialized = asyncio.run(
        handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            transport_factory=FakeTransport,
        )
    )
    listed = asyncio.run(
        handle_message(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            transport_factory=FakeTransport,
        )
    )

    assert initialized is not None
    assert initialized["result"]["protocolVersion"] == "2024-11-05"
    assert listed is not None
    assert [tool["name"] for tool in listed["result"]["tools"]] == [tool["name"] for tool in TOOLS]
    execute_schema = next(
        tool["inputSchema"] for tool in TOOLS if tool["name"] == "cognitive_brain_route_execute"
    )
    assert "allow_write" not in execute_schema["properties"]


def test_route_plan_tool_uses_local_middleware() -> None:
    response = asyncio.run(
        handle_message(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "cognitive_brain_route_plan",
                    "arguments": {
                        "capability": "github.read",
                        "action": "get_repository",
                        "target": "Aries-Serpent/_codex_",
                    },
                },
            },
            transport_factory=FakeTransport,
        )
    )

    assert response is not None
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["method"] == "POST"
    assert payload["path"] == "/api/routes/plan"


def test_unknown_tool_returns_json_rpc_error() -> None:
    response = asyncio.run(
        handle_message(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "unknown", "arguments": {}},
            },
            transport_factory=FakeTransport,
        )
    )

    assert response is not None
    assert response["error"]["code"] == -32000
    assert response["error"]["message"] == "Cognitive Brain tool failed"
    assert "unknown" not in response["error"]["message"]


def test_tool_error_does_not_expose_exception_text() -> None:
    class FailingTransport:
        def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
            raise RuntimeError("secret bootstrap path and token")

    response = asyncio.run(
        handle_message(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "cognitive_brain_capabilities", "arguments": {}},
            },
            transport_factory=FailingTransport,
        )
    )

    assert response is not None
    assert response["error"]["message"] == "Cognitive Brain tool failed"
    assert "secret" not in response["error"]["message"]


def test_api_base_rejects_non_loopback_dynamic_origins(monkeypatch) -> None:
    monkeypatch.delenv("CODEX_ALLOWED_CLI_API_ORIGINS", raising=False)

    with pytest.raises(ValueError):
        approved_api_base("file:///etc/passwd")
    with pytest.raises(ValueError):
        approved_api_base("https://attacker.example")
