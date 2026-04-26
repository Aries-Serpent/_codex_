"""Focused tests for mcp.server.jsonrpc_adapter."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp.server import jsonrpc_adapter


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


class _FakeAdapter:
    def __init__(self) -> None:
        self.query_calls: list[dict[str, Any]] = []

    def query_top_k(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "hit-1", "score": 0.9}]


def test_get_adapter_caches_loader_result(monkeypatch) -> None:
    calls = 0
    adapter = _FakeAdapter()

    def _loader() -> tuple[_FakeAdapter, str]:
        nonlocal calls
        calls += 1
        return adapter, "fake.adapter"

    jsonrpc_adapter.clear_adapter_cache()
    monkeypatch.setattr(jsonrpc_adapter, "_ADAPTER_LOADER", _loader)

    first = jsonrpc_adapter._get_adapter()
    second = jsonrpc_adapter._get_adapter()

    assert first is second is adapter
    assert calls == 1
    jsonrpc_adapter.clear_adapter_cache()


def test_handle_jsonrpc_request_supports_batch_calls() -> None:
    adapter = _FakeAdapter()

    payload = [
        {"jsonrpc": "2.0", "id": "list", "method": "mcp.listTools", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": "echo",
            "method": "mcp.callTool",
            "params": {"tool_id": "mock.tool.echo", "input": {"message": "hi"}},
        },
    ]

    result = _run(jsonrpc_adapter.handle_jsonrpc_request(payload, adapter))

    assert [item["id"] for item in result] == ["list", "echo"]
    assert result[0]["result"][0]["id"] == "mock.tool.echo"
    assert result[1]["result"] == {"output": {"message": "hi"}}


def test_dispatch_method_returns_invalid_params_error() -> None:
    adapter = _FakeAdapter()

    result = _run(
        jsonrpc_adapter._dispatch_method(
            {"jsonrpc": "2.0", "id": "bad", "method": "mcp.callTool", "params": {"input": {}}},
            adapter,
        )
    )

    assert result["error"]["code"] == -32602
    assert result["error"]["message"] == "Invalid params"


def test_dispatch_method_handles_query_success_and_failure() -> None:
    adapter = _FakeAdapter()

    success = _run(
        jsonrpc_adapter._dispatch_method(
            {
                "jsonrpc": "2.0",
                "id": "query",
                "method": "mcp.callTool",
                "params": {
                    "tool_id": "mcp.tool.query",
                    "input": {"embedding": [1.0], "filters": {"tag": "x"}},
                    "tenant": "tenant-1",
                    "top_k": 2,
                },
            },
            adapter,
        )
    )

    assert success["result"]["hits"] == [{"id": "hit-1", "score": 0.9}]
    assert adapter.query_calls == [
        {
            "namespace": "tenant-1",
            "query_embedding": [1.0],
            "top_k": 2,
            "filters": {"tag": "x"},
        }
    ]

    class _BrokenAdapter(_FakeAdapter):
        def query_top_k(
            self,
            namespace: str,
            query_embedding: list[float],
            top_k: int = 5,
            filters: dict[str, Any] | None = None,
        ):
            raise RuntimeError("backend unavailable")

    failure = _run(
        jsonrpc_adapter._dispatch_method(
            {
                "jsonrpc": "2.0",
                "id": "query-fail",
                "method": "mcp.callTool",
                "params": {"tool_id": "mcp.tool.query", "input": {"embedding": []}},
            },
            _BrokenAdapter(),
        )
    )

    assert failure["error"] == {"code": -32000, "message": "Adapter query failed"}


def test_dispatch_method_handles_unknown_tool_and_method() -> None:
    adapter = _FakeAdapter()

    unknown_tool = _run(
        jsonrpc_adapter._dispatch_method(
            {
                "jsonrpc": "2.0",
                "id": "tool",
                "method": "mcp.callTool",
                "params": {"tool_id": "unknown.tool", "input": {}},
            },
            adapter,
        )
    )
    unknown_method = _run(
        jsonrpc_adapter._dispatch_method(
            {"jsonrpc": "2.0", "id": "method", "method": "mcp.unknown", "params": {}},
            adapter,
        )
    )

    assert unknown_tool["error"]["message"] == "Unknown tool unknown.tool"
    assert unknown_method["error"] == {"code": -32601, "message": "Method not found"}


def test_register_jsonrpc_routes_uses_supplied_loader() -> None:
    adapter = _FakeAdapter()
    app = FastAPI()
    jsonrpc_adapter.clear_adapter_cache()
    jsonrpc_adapter.register_jsonrpc_routes(app, adapter_loader_fn=lambda: (adapter, "fake.adapter"))
    client = TestClient(app)

    response = client.post(
        "/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "id": "query",
            "method": "mcp.callTool",
            "params": {"tool_id": "mcp.tool.query", "input": {"embedding": [1.0]}},
        },
    )

    assert response.status_code == 200
    assert response.json()["result"]["hits"] == [{"id": "hit-1", "score": 0.9}]
    assert adapter.query_calls[0]["namespace"] == "default"
    jsonrpc_adapter.clear_adapter_cache()
