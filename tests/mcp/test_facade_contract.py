"""
Test Facade Contract

Test module for facade contract.
"""

import importlib

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")

from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def fake_adapter_loader(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_RATE", "1000")
    monkeypatch.setenv("RATE_LIMIT_BURST", "1000")

    class FakeAdapter:
        def __init__(self):
            self.query_calls = []
            self.upsert_calls = []
            self.delete_calls = []

        def connect(self):
            return None

        def query_top_k(self, namespace, query_embedding, top_k=5, filters=None):
            self.query_calls.append(
                {
                    "namespace": namespace,
                    "query_embedding": query_embedding,
                    "top_k": top_k,
                    "filters": filters,
                }
            )
            return [{"id": "x", "score": 0.9, "content": "", "metadata": {}}]

        def upsert_batch(self, namespace, items):
            self.upsert_calls.append({"namespace": namespace, "items": list(items)})

        def delete(self, namespace, id):
            self.delete_calls.append({"namespace": namespace, "id": id})
            return True

        def health_check(self):
            return {"status": "ok", "adapter": "fake"}

    fake = FakeAdapter()
    try:
        from src.mcp.middleware.rate_limit_middleware import clear_buckets

        clear_buckets()
    except ImportError:
        _ = None  # suppressed: no action needed
    monkeypatch.setattr("mcp.server.adapter_loader.load_adapter", lambda: (fake, "fake.adapter"))
    try:
        from mcp.server import jsonrpc_adapter

        monkeypatch.setattr(jsonrpc_adapter, "_ADAPTER_LOADER", lambda: (fake, "fake.adapter"))
        jsonrpc_adapter.clear_adapter_cache()
    except ImportError:
        _ = None  # suppressed: no action needed
    return fake


def _load_app():
    module = importlib.import_module("src.mcp.server.facade_fastapi")
    app = importlib.reload(module).APP
    try:
        import mcp.server.adapter_loader as adapter_loader
        from mcp.server import jsonrpc_adapter

        jsonrpc_adapter.clear_adapter_cache()
        jsonrpc_adapter._ADAPTER_LOADER = adapter_loader.load_adapter
    except ImportError:
        _ = None  # suppressed: no action needed
    return app


def test_calltool_invokes_adapter_query_top_k(fake_adapter_loader):
    app = _load_app()
    client = TestClient(app)
    payload = {
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {
            "tool_id": "mcp.tool.query",
            "input": {"embedding": [1.0, 0.0], "filters": {"tag": "x"}},
            "top_k": 3,
            "tenant": "tenant-1",
        },
        "id": "test1",
    }
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200, "status_code is not valid"
    body = resp.json()
    assert "result" in body, "Result must not be empty"
    fake = fake_adapter_loader
    assert len(fake.query_calls) >= 1, "Collection must not be empty"
    first = fake.query_calls[0]
    assert first["namespace"] == "tenant-1", "Condition must be true"
    assert first["query_embedding"] == [1.0, 0.0]
    assert first["top_k"] == 3, "Condition must be true"
    assert first["filters"] == {"tag": "x"}, "Condition must be true"
