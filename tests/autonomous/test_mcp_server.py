"""Tests for the Codespace Cognitive Brain MCP stdio bridge."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from scripts.autonomous import mcp_server
from scripts.autonomous.mcp_server import TOOLS, approved_api_base, handle_message


class FakeTransport:
    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        return {"method": method, "path": path, "body": body}


def test_initialize_and_list_tools() -> None:
    initialized = asyncio.run(
        handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            transport=FakeTransport(),
        )
    )
    listed = asyncio.run(
        handle_message(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            transport=FakeTransport(),
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
            transport=FakeTransport(),
        )
    )

    assert response is not None
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["method"] == "POST"
    assert payload["path"] == "/api/routes/plan"


def test_keepalive_tool_renews_activity_marker(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    monkeypatch.setattr(mcp_server, "runtime_dir_default", lambda: tmp_path)

    response = asyncio.run(
        handle_message(
            {
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {"name": "cognitive_brain_keepalive_touch", "arguments": {}},
            },
            transport=FakeTransport(),
        )
    )

    assert response is not None
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["active"] is True
    assert (tmp_path / "agent-session.active").is_file()


def test_maintainer_tool_uses_single_owner_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "secret-rate-limit-sentinel")
    response = asyncio.run(
        handle_message(
            {
                "jsonrpc": "2.0",
                "id": 21,
                "method": "tools/call",
                "params": {"name": "cognitive_brain_maintainer_status", "arguments": {}},
            },
            transport=FakeTransport(),
        )
    )

    assert response is not None
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["owner"]["human_login"] == "mbaetiong"
    assert payload["owner"]["human_reviewers_required"] == 0
    assert payload["session_liveness"]["max_duration_seconds"] == 28_800
    assert "github_rate_limit" in payload
    assert "credentials" in payload["github_rate_limit"]
    assert "secret-rate-limit-sentinel" not in json.dumps(payload["github_rate_limit"])


def test_unknown_tool_returns_json_rpc_error() -> None:
    response = asyncio.run(
        handle_message(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "unknown", "arguments": {}},
            },
            transport=FakeTransport(),
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
            transport=FailingTransport(),
        )
    )

    assert response is not None
    assert response["error"]["message"] == "Cognitive Brain tool failed"
    assert "secret" not in response["error"]["message"]


def test_stdio_messages_reuse_one_transport_instance() -> None:
    class StatefulTransport(FakeTransport):
        def __init__(self) -> None:
            self.paths: list[str] = []

        def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
            self.paths.append(path)
            return super().request(method, path, body)

    transport = StatefulTransport()
    messages = [
        {
            "jsonrpc": "2.0",
            "id": index,
            "method": "tools/call",
            "params": {"name": "cognitive_brain_capabilities", "arguments": {}},
        }
        for index in (6, 7)
    ]

    for message in messages:
        asyncio.run(handle_message(message, transport=transport))

    assert transport.paths == ["/api/capabilities", "/api/capabilities"]


def test_api_base_rejects_non_loopback_dynamic_origins(monkeypatch) -> None:
    monkeypatch.delenv("CODEX_ALLOWED_CLI_API_ORIGINS", raising=False)

    with pytest.raises(ValueError):
        approved_api_base("file:///etc/passwd")
    with pytest.raises(ValueError):
        approved_api_base("https://attacker.example")
