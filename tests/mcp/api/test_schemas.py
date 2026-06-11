from mcp.api.schemas import (
    ErrorCodes,
    HealthResponse,
    JSONRPCError,
    JSONRPCRequest,
    JSONRPCResponse,
    QueryRequest,
    QueryResponse,
    UpsertRequest,
    UpsertResponse,
)


def test_query_request_defaults():
    req = QueryRequest(query="test")
    assert req.query == "test"
    assert req.top_k == 10
    assert req.filters is None
    assert req.include_metadata is True


def test_query_response():
    resp = QueryResponse(matches=[{"id": "1"}], query_time_ms=1.5, total_matches=1)
    assert resp.total_matches == 1
    assert resp.query_time_ms == 1.5


def test_upsert_request_defaults():
    req = UpsertRequest(vectors=[{"id": "1", "values": [0.1]}])
    assert req.namespace == "default"


def test_upsert_response():
    resp = UpsertResponse(upserted_count=1, success=True)
    assert resp.upserted_count == 1
    assert resp.success is True


def test_health_response():
    resp = HealthResponse(status="healthy")
    assert resp.version == "1.0.0"


def test_jsonrpc_request():
    req = JSONRPCRequest(method="test_method")
    assert req.jsonrpc == "2.0"
    assert req.method == "test_method"


def test_jsonrpc_response():
    resp = JSONRPCResponse(result={"ok": True})
    assert resp.jsonrpc == "2.0"
    assert resp.result == {"ok": True}


def test_jsonrpc_error():
    err = JSONRPCError(code=ErrorCodes.INVALID_PARAMS, message="Invalid")
    assert err.code == -32602
    assert err.message == "Invalid"
