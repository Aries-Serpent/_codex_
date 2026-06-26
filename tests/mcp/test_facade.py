"""
Test Facade

Test module for facade.
"""

# Basic façade tests using FastAPI TestClient and the default (mock) adapter
import importlib

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from mcp.server.facade_fastapi import APP

client = TestClient(APP)


def test_list_tools_jsonrpc():
    payload = {"jsonrpc": "2.0", "method": "mcp.listTools", "params": {}, "id": "t1"}
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200, "status_code is not valid"
    body = resp.json()
    assert body.get("jsonrpc") == "2.0", "Condition must be true"
    assert "result" in body, "Result must not be empty"
    assert isinstance(body["result"], list)


def test_call_tool_echo():
    payload = {
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {"tool_id": "mock.tool.echo", "input": {"text": "hello"}, "top_k": 1},
        "id": "t2",
    }
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200, "status_code is not valid"
    body = resp.json()
    assert "result" in body, "Result must not be empty"
    assert body["result"]["output"]["text"] == "hello", "Result must not be empty"


def test_invalid_params_returns_jsonrpc_error():
    payload = {
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {"input": {"text": "missing tool id"}},
        "id": "bad1",
    }
    resp = client.post("/jsonrpc", json=payload)
    body = resp.json()
    assert body["error"]["code"] == -32602, "Error should be raised or set"


def test_health_endpoints():
    r = client.get("/health")
    assert r.status_code == 200, "status_code is not valid"
    j = r.json()
    assert "service" in j and "adapter" in j, "Condition must be true"


def test_rate_limit_429(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_RATE", "0")
    monkeypatch.setenv("RATE_LIMIT_BURST", "0")
    from mcp.middleware import rate_limit_middleware
    from mcp.server import facade_fastapi

    importlib.reload(facade_fastapi)
    rate_limit_middleware._BUCKETS.clear()
    rate_client = TestClient(facade_fastapi.APP)
    resp = rate_client.get("/health")
    assert resp.status_code == 429, "status_code is not valid"
