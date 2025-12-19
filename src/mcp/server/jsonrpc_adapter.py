from __future__ import annotations
import asyncio
import logging
from typing import Any, Dict, List, Union
from pydantic import ValidationError

from src.mcp.backends.interface import BackendAdapter  # type: ignore
from .schemas import CallToolParams, NegotiateParams, ListToolsParams  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore

logger = logging.getLogger(__name__)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def handle_jsonrpc_request(payload: Any, adapter: BackendAdapter) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    if isinstance(payload, list):
        # Dispatch concurrently for a small batch (keeps behavior simple)
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


async def _dispatch_method(p: Dict[str, Any], adapter: BackendAdapter) -> Dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    # Validate with Pydantic where applicable
    try:
        if method == "mcp.listTools":
            ListToolsParams.parse_obj(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.parse_obj(params or {})
        elif method == "mcp.callTool":
            validated = CallToolParams.parse_obj(params or {})
            # convert to simple dict for usage below
            params = validated.dict()
    except ValidationError as ve:
        # Return JSON-RPC invalid params
        return {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params", "data": ve.errors()}, "id": req_id}

    # mcp.listTools
    if method == "mcp.listTools":
        increment("mcp_list_tools_total")
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "description": "Echoes input"}]
        return {"jsonrpc": "2.0", "result": tools, "id": req_id}

    # mcp.negotiateVersion
    if method == "mcp.negotiateVersion":
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "id": req_id}

    # mcp.callTool
    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            # Built-in mock behavior
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            # Example retrieval tool pattern (façade → adapter)
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
                except Exception as exc:
                    logger.exception("Adapter query failed: %s", exc)
                    return {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Adapter query failed"}, "id": req_id}

            return {"jsonrpc": "2.0", "error": {"code": -32000, "message": f"Unknown tool {tool_id}"}, "id": req_id}

    return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": req_id}
