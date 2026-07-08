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
    assert req.query == "test", "query is not valid"
    assert req.top_k == 10, "top_k is not valid"
    assert req.filters is None, "filters is not valid"
    assert req.include_metadata is True, "Data must not be empty"


def test_query_response():
    resp = QueryResponse(matches=[{"id": "1"}], query_time_ms=1.5, total_matches=1)
    assert resp.total_matches == 1, "total_matches is not valid"
    assert resp.query_time_ms == 1.5, "query_time_ms is not valid"


def test_upsert_request_defaults():
    req = UpsertRequest(vectors=[{"id": "1", "values": [0.1]}])
    assert req.namespace == "default", "namespace is not valid"


def test_upsert_response():
    resp = UpsertResponse(upserted_count=1, success=True)
    assert resp.upserted_count == 1, "Count must be greater than zero"
    assert resp.success is True, "success is not valid"


def test_health_response():
    resp = HealthResponse(status="healthy")
    assert resp.version == "1.0.0", "version is not valid"


def test_jsonrpc_request():
    req = JSONRPCRequest(method="test_method")
    assert req.jsonrpc == "2.0", "jsonrpc is not valid"
    assert req.method == "test_method", "method is not valid"


def test_jsonrpc_response():
    resp = JSONRPCResponse(result={"ok": True})
    assert resp.jsonrpc == "2.0", "jsonrpc is not valid"
    assert resp.result == {"ok": True}, "Result must not be empty"


def test_jsonrpc_error():
    err = JSONRPCError(code=ErrorCodes.INVALID_PARAMS, message="Invalid")
    assert err.code == -32602, "code is not valid"
    assert err.message == "Invalid", "message is not valid"
