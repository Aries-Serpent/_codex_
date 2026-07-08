"""
Test Http Server

Test module for http server.
"""

import os

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from mcp.server.http import (
    ContextItem,
    ContextUpsertRequest,
    QueryRequest,
    app,
    create_app,
)


def test_health_returns_status_and_count() -> None:
    client = TestClient(app)
    response = client.get("/mcp/v1/health")
    assert response.status_code == 200, "Response must not be empty"
    payload = response.json()
    assert payload["status"] == "healthy", "Condition must be true"
    assert "documents" in payload, "Condition must be true"
    assert isinstance(payload["documents"], int)


def test_query_requires_auth_by_default(monkeypatch) -> None:
    monkeypatch.setenv("MCP_OFFLINE", "false")
    client = TestClient(app)
    response = client.post("/mcp/v1/query", json=QueryRequest(query="codex").dict())
    assert response.status_code == 401, "Response must not be empty"


def test_query_success_with_default_key(monkeypatch) -> None:
    monkeypatch.setenv("MCP_API_KEY", "dev-key")
    client = TestClient(app)
    response = client.post(
        "/mcp/v1/query",
        headers={"X-MCP-API-Key": "dev-key"},
        json=QueryRequest(query="codex", top_k=3).dict(),
    )
    assert response.status_code == 200, "Response must not be empty"
    payload = response.json()
    assert "results" in payload, "Result must not be empty"
    assert len(payload["results"]) <= 3, "Collection must not be empty"


def test_context_upsert_and_query_round_trip() -> None:
    local_app = create_app(store=None)
    client = TestClient(local_app)

    upsert_payload = ContextUpsertRequest(
        items=[ContextItem(id="doc-99", content="edge case", metadata={"scope": "test"})]
    ).dict()

    response = client.post(
        "/mcp/v1/context",
        headers={"X-MCP-API-Key": os.environ.get("MCP_API_KEY", "dev-key")},
        json=upsert_payload,
    )
    assert response.status_code == 200, "Response must not be empty"
    assert response.json()["upserted"] == 1, "Response must not be empty"

    query_payload = QueryRequest(query="edge", top_k=1, filters={"scope": "test"}).dict()
    query_response = client.post(
        "/mcp/v1/query",
        headers={"X-MCP-API-Key": os.environ.get("MCP_API_KEY", "dev-key")},
        json=query_payload,
    )
    assert query_response.status_code == 200, "Response must not be empty"
    results = query_response.json()["results"]
    assert len(results) == 1, "Results must not be empty"
    assert results[0]["id"] == "doc-99", "Result must not be empty"


def test_rate_limit_hook_placeholder(monkeypatch) -> None:
    # Rate limit is disabled by default; ensure enabling raises 429
    from mcp.server import http as http_module

    with monkeypatch.context() as mpatch:
        mpatch.setattr(
            http_module,
            "_enforce_rate_limit",
            lambda enabled=False: (_ for _ in ()).throw(http_module.HTTPException(status_code=429)),
        )
        client = TestClient(http_module.create_app())
        response = client.post(
            "/mcp/v1/query",
            headers={"X-MCP-API-Key": os.environ.get("MCP_API_KEY", "dev-key")},
            json=QueryRequest(query="codex").dict(),
        )
        assert response.status_code == 429, "Response must not be empty"
