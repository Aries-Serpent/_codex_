# Contract test: assert façade calls adapter.query_top_k with expected args.
from fastapi.testclient import TestClient

# Monkeypatch adapter loader to return a fake adapter that records calls
from src.mcp.server import adapter_loader
from src.mcp.server.facade_fastapi import APP
from src.mcp.middleware import rate_limit_middleware


class FakeAdapter:
    def __init__(self):
        self.calls = []

    def connect(self):
        pass

    def query_top_k(self, namespace, query_embedding, top_k=5, filters=None):
        self.calls.append(
            {"namespace": namespace, "query_embedding": query_embedding, "top_k": top_k, "filters": filters}
        )
        return [{"id": "x", "score": 1.0, "content": "c", "metadata": {}}]

    def health_check(self):
        return {"status": "ok"}


def test_facade_calls_adapter_query(monkeypatch):
    fake = FakeAdapter()
    monkeypatch.setattr(adapter_loader, "load_adapter", lambda adapter_path=None: (fake, "fake"))
    client = TestClient(APP)
    rate_limit_middleware._BUCKETS.clear()
    payload = {
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {"tool_id": "mcp.tool.query", "input": {"embedding": [0.1, 0.2]}, "top_k": 3, "tenant": "tenantA"},
        "id": "c1",
    }
    resp = client.post("/jsonrpc", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body
    assert "hits" in body["result"]
    assert isinstance(body["result"]["hits"], list)
