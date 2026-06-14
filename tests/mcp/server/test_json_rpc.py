"""Tests for mcp.server.json_rpc — JSON-RPC 2.0 handler."""

from __future__ import annotations

import asyncio

import pytest

from mcp.server.json_rpc import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    JsonRpcError,
    JsonRpcHandler,
    JsonRpcRequest,
    JsonRpcResponse,
)


# ---------------------------------------------------------------------------
# JsonRpcRequest
# ---------------------------------------------------------------------------


def test_request_is_notification_when_no_id():
    req = JsonRpcRequest(method="ping")
    assert req.is_notification is True


def test_request_not_notification_when_id_is_zero():
    req = JsonRpcRequest(method="ping", id=0)
    assert req.is_notification is False


def test_request_not_notification_with_string_id():
    req = JsonRpcRequest(method="ping", id="abc")
    assert req.is_notification is False


def test_request_defaults():
    req = JsonRpcRequest(method="tools.list")
    assert req.jsonrpc == "2.0"
    assert req.params is None
    assert req.id is None


# ---------------------------------------------------------------------------
# JsonRpcResponse
# ---------------------------------------------------------------------------


def test_response_to_dict_with_result():
    resp = JsonRpcResponse(id=1, result={"ok": True})
    d = resp.to_dict()
    assert d["jsonrpc"] == "2.0"
    assert d["id"] == 1
    assert d["result"] == {"ok": True}
    assert "error" not in d


def test_response_to_dict_with_error():
    err = {"code": -32600, "message": "Bad request"}
    resp = JsonRpcResponse(id=2, error=err)
    d = resp.to_dict()
    assert d["error"] == err
    assert "result" not in d


def test_response_to_dict_no_id():
    resp = JsonRpcResponse(id=None, result=None)
    d = resp.to_dict()
    assert d["id"] is None
    assert d["result"] is None


# ---------------------------------------------------------------------------
# JsonRpcError
# ---------------------------------------------------------------------------


def test_error_to_dict_without_data():
    err = JsonRpcError(code=INTERNAL_ERROR, message="oops")
    d = err.to_dict()
    assert d == {"code": INTERNAL_ERROR, "message": "oops"}
    assert "data" not in d


def test_error_to_dict_with_data():
    err = JsonRpcError(code=INVALID_PARAMS, message="bad", data={"field": "x"})
    d = err.to_dict()
    assert d["data"] == {"field": "x"}


def test_error_code_constants():
    assert PARSE_ERROR == -32700
    assert INVALID_REQUEST == -32600
    assert METHOD_NOT_FOUND == -32601
    assert INVALID_PARAMS == -32602
    assert INTERNAL_ERROR == -32603


# ---------------------------------------------------------------------------
# JsonRpcHandler — registration
# ---------------------------------------------------------------------------


def test_register_and_get_methods():
    handler = JsonRpcHandler()

    async def ping(params):
        return "pong"

    handler.register_method("ping", ping)
    assert "ping" in handler.get_registered_methods()


def test_unregister_existing_method():
    handler = JsonRpcHandler()

    async def noop(params):
        return None

    handler.register_method("noop", noop)
    result = handler.unregister_method("noop")
    assert result is True
    assert "noop" not in handler.get_registered_methods()


def test_unregister_nonexistent_method():
    handler = JsonRpcHandler()
    result = handler.unregister_method("does_not_exist")
    assert result is False


def test_method_decorator_registers():
    handler = JsonRpcHandler()

    @handler.method("echo")
    async def echo(params):
        return params

    assert "echo" in handler.get_registered_methods()


def test_get_registered_methods_empty():
    handler = JsonRpcHandler()
    assert handler.get_registered_methods() == []


# ---------------------------------------------------------------------------
# JsonRpcHandler — handle_request (async)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_request_success():
    handler = JsonRpcHandler()

    @handler.method("add")
    async def add(params):
        return params["a"] + params["b"]

    resp = await handler.handle_request(
        {"jsonrpc": "2.0", "method": "add", "params": {"a": 3, "b": 4}, "id": 1}
    )
    assert resp["result"] == 7
    assert resp["id"] == 1


@pytest.mark.asyncio
async def test_handle_request_method_not_found():
    handler = JsonRpcHandler()
    resp = await handler.handle_request({"jsonrpc": "2.0", "method": "unknown", "id": 2})
    assert resp["error"]["code"] == METHOD_NOT_FOUND
    assert resp["id"] == 2


@pytest.mark.asyncio
async def test_handle_request_invalid_jsonrpc_version():
    handler = JsonRpcHandler()
    resp = await handler.handle_request({"jsonrpc": "1.0", "method": "ping", "id": 3})
    assert resp["error"]["code"] == INVALID_REQUEST


@pytest.mark.asyncio
async def test_handle_request_missing_method():
    handler = JsonRpcHandler()
    resp = await handler.handle_request({"jsonrpc": "2.0", "id": 4})
    assert resp["error"]["code"] == INVALID_REQUEST


@pytest.mark.asyncio
async def test_handle_request_notification_returns_none():
    handler = JsonRpcHandler()

    @handler.method("notify.me")
    async def notif(params):
        return "ignored"

    result = await handler.handle_request({"jsonrpc": "2.0", "method": "notify.me"})
    assert result is None


@pytest.mark.asyncio
async def test_handle_request_handler_raises_exception():
    handler = JsonRpcHandler()

    @handler.method("boom")
    async def boom(params):
        raise RuntimeError("explosion")

    resp = await handler.handle_request({"jsonrpc": "2.0", "method": "boom", "id": 5})
    assert resp["error"]["code"] == INTERNAL_ERROR


@pytest.mark.asyncio
async def test_handle_request_array_params_ignored():
    """Array-style params are logged but method still dispatched with None params."""
    handler = JsonRpcHandler()

    @handler.method("arr")
    async def arr(params):
        return params

    resp = await handler.handle_request(
        {"jsonrpc": "2.0", "method": "arr", "params": [1, 2, 3], "id": 6}
    )
    # Handler receives None because array params aren't mapped
    assert resp["result"] is None


# ---------------------------------------------------------------------------
# JsonRpcHandler — handle_batch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_batch_empty_returns_error():
    handler = JsonRpcHandler()
    responses = await handler.handle_batch([])
    assert len(responses) == 1
    assert responses[0]["error"]["code"] == INVALID_REQUEST


@pytest.mark.asyncio
async def test_handle_batch_multiple_requests():
    handler = JsonRpcHandler()

    @handler.method("double")
    async def double(params):
        return params["x"] * 2

    responses = await handler.handle_batch(
        [
            {"jsonrpc": "2.0", "method": "double", "params": {"x": 5}, "id": 1},
            {"jsonrpc": "2.0", "method": "double", "params": {"x": 10}, "id": 2},
        ]
    )
    results = {r["id"]: r["result"] for r in responses}
    assert results[1] == 10
    assert results[2] == 20


@pytest.mark.asyncio
async def test_handle_batch_excludes_notifications():
    handler = JsonRpcHandler()

    @handler.method("fire_and_forget")
    async def faf(params):
        return None

    responses = await handler.handle_batch(
        [
            {"jsonrpc": "2.0", "method": "fire_and_forget"},  # notification
            {"jsonrpc": "2.0", "method": "fire_and_forget", "id": 99},
        ]
    )
    # Only the non-notification should appear in responses
    assert len(responses) == 1
    assert responses[0]["id"] == 99


# ---------------------------------------------------------------------------
# JsonRpcHandler — handle (dispatch wrapper)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_single_request():
    handler = JsonRpcHandler()

    @handler.method("greet")
    async def greet(params):
        return f"Hello, {params['name']}!"

    result = await handler.handle(
        {"jsonrpc": "2.0", "method": "greet", "params": {"name": "World"}, "id": 7}
    )
    assert isinstance(result, dict)
    assert result["result"] == "Hello, World!"


@pytest.mark.asyncio
async def test_handle_batch_list():
    handler = JsonRpcHandler()

    @handler.method("noop2")
    async def noop2(params):
        return "ok"

    result = await handler.handle(
        [{"jsonrpc": "2.0", "method": "noop2", "id": 1}]
    )
    assert isinstance(result, list)
    assert len(result) == 1
