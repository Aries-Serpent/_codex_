"""
Jsonrpc Adapter Module

This module provides functionality for jsonrpc adapter.

Usage:
    from server.jsonrpc_adapter import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from fastapi import Body, FastAPI
from pydantic import ValidationError

from mcp.backends.interface import BackendAdapter
from mcp.observability.metrics import Timer, increment
from mcp.server.adapter_loader import load_adapter

from .schemas import CallToolParams, ListToolsParams, NegotiateParams

logger = logging.getLogger(__name__)

_ADAPTER_CACHE: Optional[tuple[object, str]] = None
_ADAPTER_LOADER = load_adapter


def clear_adapter_cache() -> None:
    global _ADAPTER_CACHE
    _ADAPTER_CACHE = None


def register_jsonrpc_routes(app: FastAPI, adapter_loader_fn=load_adapter) -> None:
    global _ADAPTER_LOADER
    _ADAPTER_LOADER = adapter_loader_fn

    @app.post("/jsonrpc")
    async def jsonrpc_endpoint(payload: Any = Body(...)):
        adapter = _get_adapter()
        return await handle_jsonrpc_request(payload, adapter)


def _get_adapter() -> BackendAdapter:
    global _ADAPTER_CACHE
    if _ADAPTER_CACHE is None:
        _ADAPTER_CACHE = _ADAPTER_LOADER()
    adapter, _ = _ADAPTER_CACHE
    return adapter


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.  # noqa: E501
async def handle_jsonrpc_request(
    payload: Any, adapter: BackendAdapter
) -> dict[str, Any] | list[dict[str, Any]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        return await asyncio.gather(*tasks)
    return await _dispatch_method(payload, adapter)


async def _dispatch_method(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method == "mcp.callTool":
            validated = CallToolParams.model_validate(params or {})
            params = validated.model_dump()
    except ValidationError as ve:
        logger.debug(f"ValidationError: {ve}")
        logger.debug("Exception caught, returning", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Invalid params", "data": ve.errors()},
            "id": req_id,
        }

    if method == "mcp.listTools":
        increment("mcp_list_tools_total")
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "description": "Echoes input"}]
        return {"jsonrpc": "2.0", "result": tools, "id": req_id}

    if method == "mcp.negotiateVersion":
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {
                    "jsonrpc": "2.0",
                    "result": {"output": input_payload},
                    "id": req_id,
                }

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except (ValueError, TypeError) as exc:
                    type(exc).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }
