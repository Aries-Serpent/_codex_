"""
Test Server Smoke

Test module for server smoke.
"""

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")

from fastapi.testclient import TestClient

from mcp.server.facade_fastapi import APP


@pytest.mark.integration
def test_health_endpoint():
    client = TestClient(APP)
    resp = client.get("/health")
    assert resp.status_code == 200, "status_code is not valid"
    payload = resp.json()
    for key in ("service", "status", "adapter", "adapter_status"):
        assert key in payload, "Condition must be true"


@pytest.mark.integration
def test_jsonrpc_endpoints():
    client = TestClient(APP)
    resp = client.post(
        "/jsonrpc",
        json={"jsonrpc": "2.0", "method": "mcp.listTools", "params": {}, "id": "1"},
    )
    assert resp.status_code == 200, "status_code is not valid"
    body = resp.json()
    assert body.get("jsonrpc") == "2.0", "Condition must be true"
    assert isinstance(body.get("result"), list)

    resp = client.post(
        "/jsonrpc",
        json={
            "jsonrpc": "2.0",
            "method": "mcp.callTool",
            "params": {"tool_id": "mock.tool.echo", "input": {"text": "hello"}},
            "id": "2",
        },
    )
    assert resp.status_code == 200, "status_code is not valid"
    body = resp.json()
    assert body.get("result", {}).get("output", {}).get("text") == "hello"
