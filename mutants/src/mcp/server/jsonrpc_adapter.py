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
from typing import Any, Optional, Union

from fastapi import Body, FastAPI
from pydantic import ValidationError

from src.mcp.backends.interface import BackendAdapter  # type: ignore
from src.mcp.observability.metrics import Timer, increment  # type: ignore
from src.mcp.server.adapter_loader import load_adapter

from .schemas import CallToolParams, ListToolsParams, NegotiateParams  # type: ignore

logger = logging.getLogger(__name__)

_ADAPTER_CACHE: Optional[tuple[object, str]] = None
_ADAPTER_LOADER = load_adapter
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_clear_adapter_cache__mutmut_orig() -> None:
    global _ADAPTER_CACHE
    _ADAPTER_CACHE = None


def x_clear_adapter_cache__mutmut_1() -> None:
    global _ADAPTER_CACHE
    _ADAPTER_CACHE = ""

x_clear_adapter_cache__mutmut_mutants : ClassVar[MutantDict] = {
'x_clear_adapter_cache__mutmut_1': x_clear_adapter_cache__mutmut_1
}

def clear_adapter_cache(*args, **kwargs):
    result = _mutmut_trampoline(x_clear_adapter_cache__mutmut_orig, x_clear_adapter_cache__mutmut_mutants, args, kwargs)
    return result 

clear_adapter_cache.__signature__ = _mutmut_signature(x_clear_adapter_cache__mutmut_orig)
x_clear_adapter_cache__mutmut_orig.__name__ = 'x_clear_adapter_cache'


def x_register_jsonrpc_routes__mutmut_orig(app: FastAPI, adapter_loader_fn=load_adapter) -> None:
    global _ADAPTER_LOADER
    _ADAPTER_LOADER = adapter_loader_fn

    @app.post("/jsonrpc")
    async def jsonrpc_endpoint(payload: Any = Body(...)):
        adapter = _get_adapter()
        response = await handle_jsonrpc_request(payload, adapter)
        return response


def x_register_jsonrpc_routes__mutmut_1(app: FastAPI, adapter_loader_fn=load_adapter) -> None:
    global _ADAPTER_LOADER
    _ADAPTER_LOADER = None

    @app.post("/jsonrpc")
    async def jsonrpc_endpoint(payload: Any = Body(...)):
        adapter = _get_adapter()
        response = await handle_jsonrpc_request(payload, adapter)
        return response

x_register_jsonrpc_routes__mutmut_mutants : ClassVar[MutantDict] = {
'x_register_jsonrpc_routes__mutmut_1': x_register_jsonrpc_routes__mutmut_1
}

def register_jsonrpc_routes(*args, **kwargs):
    result = _mutmut_trampoline(x_register_jsonrpc_routes__mutmut_orig, x_register_jsonrpc_routes__mutmut_mutants, args, kwargs)
    return result 

register_jsonrpc_routes.__signature__ = _mutmut_signature(x_register_jsonrpc_routes__mutmut_orig)
x_register_jsonrpc_routes__mutmut_orig.__name__ = 'x_register_jsonrpc_routes'


def x__get_adapter__mutmut_orig() -> BackendAdapter:
    global _ADAPTER_CACHE
    if _ADAPTER_CACHE is None:
        _ADAPTER_CACHE = _ADAPTER_LOADER()
    adapter, _ = _ADAPTER_CACHE
    return adapter  # type: ignore[return-value]


def x__get_adapter__mutmut_1() -> BackendAdapter:
    global _ADAPTER_CACHE
    if _ADAPTER_CACHE is not None:
        _ADAPTER_CACHE = _ADAPTER_LOADER()
    adapter, _ = _ADAPTER_CACHE
    return adapter  # type: ignore[return-value]


def x__get_adapter__mutmut_2() -> BackendAdapter:
    global _ADAPTER_CACHE
    if _ADAPTER_CACHE is None:
        _ADAPTER_CACHE = None
    adapter, _ = _ADAPTER_CACHE
    return adapter  # type: ignore[return-value]


def x__get_adapter__mutmut_3() -> BackendAdapter:
    global _ADAPTER_CACHE
    if _ADAPTER_CACHE is None:
        _ADAPTER_CACHE = _ADAPTER_LOADER()
    adapter, _ = None
    return adapter  # type: ignore[return-value]

x__get_adapter__mutmut_mutants : ClassVar[MutantDict] = {
'x__get_adapter__mutmut_1': x__get_adapter__mutmut_1, 
    'x__get_adapter__mutmut_2': x__get_adapter__mutmut_2, 
    'x__get_adapter__mutmut_3': x__get_adapter__mutmut_3
}

def _get_adapter(*args, **kwargs):
    result = _mutmut_trampoline(x__get_adapter__mutmut_orig, x__get_adapter__mutmut_mutants, args, kwargs)
    return result 

_get_adapter.__signature__ = _mutmut_signature(x__get_adapter__mutmut_orig)
x__get_adapter__mutmut_orig.__name__ = 'x__get_adapter'


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_orig(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_1(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = None
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_2(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(None) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_3(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(None, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_4(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, None)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_5(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_6(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, )) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_7(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = None
        return results
    return await _dispatch_method(payload, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_8(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(None, adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_9(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, None)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_10(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(adapter)


# Minimal JSON-RPC helper. Supports batching and parameter validation; maps validation errors to JSON-RPC -32602.
async def x_handle_jsonrpc_request__mutmut_11(
    payload: Any, adapter: BackendAdapter
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    if isinstance(payload, list):
        tasks = [asyncio.create_task(_dispatch_method(p, adapter)) for p in payload]
        results = await asyncio.gather(*tasks)
        return results
    return await _dispatch_method(payload, )

x_handle_jsonrpc_request__mutmut_mutants : ClassVar[MutantDict] = {
'x_handle_jsonrpc_request__mutmut_1': x_handle_jsonrpc_request__mutmut_1, 
    'x_handle_jsonrpc_request__mutmut_2': x_handle_jsonrpc_request__mutmut_2, 
    'x_handle_jsonrpc_request__mutmut_3': x_handle_jsonrpc_request__mutmut_3, 
    'x_handle_jsonrpc_request__mutmut_4': x_handle_jsonrpc_request__mutmut_4, 
    'x_handle_jsonrpc_request__mutmut_5': x_handle_jsonrpc_request__mutmut_5, 
    'x_handle_jsonrpc_request__mutmut_6': x_handle_jsonrpc_request__mutmut_6, 
    'x_handle_jsonrpc_request__mutmut_7': x_handle_jsonrpc_request__mutmut_7, 
    'x_handle_jsonrpc_request__mutmut_8': x_handle_jsonrpc_request__mutmut_8, 
    'x_handle_jsonrpc_request__mutmut_9': x_handle_jsonrpc_request__mutmut_9, 
    'x_handle_jsonrpc_request__mutmut_10': x_handle_jsonrpc_request__mutmut_10, 
    'x_handle_jsonrpc_request__mutmut_11': x_handle_jsonrpc_request__mutmut_11
}

def handle_jsonrpc_request(*args, **kwargs):
    result = _mutmut_trampoline(x_handle_jsonrpc_request__mutmut_orig, x_handle_jsonrpc_request__mutmut_mutants, args, kwargs)
    return result 

handle_jsonrpc_request.__signature__ = _mutmut_signature(x_handle_jsonrpc_request__mutmut_orig)
x_handle_jsonrpc_request__mutmut_orig.__name__ = 'x_handle_jsonrpc_request'


async def x__dispatch_method__mutmut_orig(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_1(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = None
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_2(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get(None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_3(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("XXidXX")
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_4(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("ID")
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_5(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = None
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_6(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get(None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_7(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("XXmethodXX")
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_8(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("METHOD")
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_9(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = None

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_10(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get(None, {})

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_11(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", None)

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_12(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get({})

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_13(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", )

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_14(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("XXparamsXX", {})

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_15(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("PARAMS", {})

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_16(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method != "mcp.listTools":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_17(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "XXmcp.listToolsXX":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_18(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listtools":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_19(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "MCP.LISTTOOLS":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_20(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_21(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params and {})
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_22(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method != "mcp.negotiateVersion":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_23(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "XXmcp.negotiateVersionXX":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_24(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateversion":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_25(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "MCP.NEGOTIATEVERSION":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_26(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_27(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params and {})
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_28(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method != "mcp.callTool":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_29(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method == "XXmcp.callToolXX":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_30(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method == "mcp.calltool":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_31(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method == "MCP.CALLTOOL":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_32(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method == "mcp.callTool":
            validated = None
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_33(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method == "mcp.callTool":
            validated = CallToolParams.model_validate(None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_34(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
    req_id = p.get("id")
    method = p.get("method")
    params = p.get("params", {})

    try:
        if method == "mcp.listTools":
            ListToolsParams.model_validate(params or {})
        elif method == "mcp.negotiateVersion":
            NegotiateParams.model_validate(params or {})
        elif method == "mcp.callTool":
            validated = CallToolParams.model_validate(params and {})
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_35(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            params = None
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_36(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug(None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_37(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug(None, exc_info=True)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_38(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug("Exception caught, returning", exc_info=None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_39(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug(exc_info=True)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_40(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug("Exception caught, returning", )
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_41(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug("XXException caught, returningXX", exc_info=True)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_42(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug("exception caught, returning", exc_info=True)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_43(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug("EXCEPTION CAUGHT, RETURNING", exc_info=True)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_44(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        logger.debug("Exception caught, returning", exc_info=False)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_45(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "XXjsonrpcXX": "2.0",
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_46(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "JSONRPC": "2.0",
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_47(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "jsonrpc": "XX2.0XX",
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_48(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "XXerrorXX": {"code": -32602, "message": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_49(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "ERROR": {"code": -32602, "message": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_50(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"XXcodeXX": -32602, "message": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_51(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"CODE": -32602, "message": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_52(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": +32602, "message": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_53(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32603, "message": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_54(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32602, "XXmessageXX": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_55(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32602, "MESSAGE": "Invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_56(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32602, "message": "XXInvalid paramsXX", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_57(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32602, "message": "invalid params", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_58(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32602, "message": "INVALID PARAMS", "data": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_59(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32602, "message": "Invalid params", "XXdataXX": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_60(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "error": {"code": -32602, "message": "Invalid params", "DATA": ve.errors()},
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_61(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "XXidXX": req_id,
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_62(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            "ID": req_id,
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_63(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method != "mcp.listTools":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_64(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "XXmcp.listToolsXX":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_65(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "mcp.listtools":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_66(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "MCP.LISTTOOLS":
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_67(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        increment(None)
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_68(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        increment("XXmcp_list_tools_totalXX")
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_69(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        increment("MCP_LIST_TOOLS_TOTAL")
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_70(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = None
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_71(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"XXidXX": "mock.tool.echo", "name": "Echo Tool", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_72(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"ID": "mock.tool.echo", "name": "Echo Tool", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_73(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "XXmock.tool.echoXX", "name": "Echo Tool", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_74(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "MOCK.TOOL.ECHO", "name": "Echo Tool", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_75(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "XXnameXX": "Echo Tool", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_76(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "NAME": "Echo Tool", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_77(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "XXEcho ToolXX", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_78(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "echo tool", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_79(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "ECHO TOOL", "description": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_80(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "XXdescriptionXX": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_81(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "DESCRIPTION": "Echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_82(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "description": "XXEchoes inputXX"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_83(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "description": "echoes input"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_84(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tools = [{"id": "mock.tool.echo", "name": "Echo Tool", "description": "ECHOES INPUT"}]
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_85(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"XXjsonrpcXX": "2.0", "result": tools, "id": req_id}

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_86(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"JSONRPC": "2.0", "result": tools, "id": req_id}

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_87(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "XX2.0XX", "result": tools, "id": req_id}

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_88(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "XXresultXX": tools, "id": req_id}

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_89(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "RESULT": tools, "id": req_id}

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_90(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "result": tools, "XXidXX": req_id}

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_91(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "result": tools, "ID": req_id}

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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_92(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method != "mcp.negotiateVersion":
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_93(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "XXmcp.negotiateVersionXX":
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_94(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "mcp.negotiateversion":
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_95(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "MCP.NEGOTIATEVERSION":
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_96(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"XXjsonrpcXX": "2.0", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_97(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"JSONRPC": "2.0", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_98(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "XX2.0XX", "result": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_99(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "XXresultXX": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_100(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "RESULT": {"version": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_101(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "result": {"XXversionXX": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_102(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "result": {"VERSION": "1.0"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_103(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "result": {"version": "XX1.0XX"}, "id": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_104(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "XXidXX": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_105(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        return {"jsonrpc": "2.0", "result": {"version": "1.0"}, "ID": req_id}

    if method == "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_106(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method != "mcp.callTool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_107(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "XXmcp.callToolXX":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_108(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "mcp.calltool":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_109(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

    if method == "MCP.CALLTOOL":
        tool_id = params.get("tool_id")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_110(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tool_id = None
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_111(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tool_id = params.get(None)
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_112(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tool_id = params.get("XXtool_idXX")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_113(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tool_id = params.get("TOOL_ID")
        input_payload = params.get("input", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_114(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        input_payload = None
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_115(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        input_payload = params.get(None, {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_116(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        input_payload = params.get("input", None)
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_117(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        input_payload = params.get({})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_118(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        input_payload = params.get("input", )
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_119(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        input_payload = params.get("XXinputXX", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_120(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        input_payload = params.get("INPUT", {})
        tenant = params.get("tenant") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_121(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tenant = None
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_122(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tenant = params.get("tenant") and "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_123(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tenant = params.get(None) or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_124(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tenant = params.get("XXtenantXX") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_125(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tenant = params.get("TENANT") or "default"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_126(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tenant = params.get("tenant") or "XXdefaultXX"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_127(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        tenant = params.get("tenant") or "DEFAULT"
        top_k = params.get("top_k", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_128(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = None

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_129(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = params.get(None, 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_130(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = params.get("top_k", None)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_131(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = params.get(5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_132(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = params.get("top_k", )

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_133(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = params.get("XXtop_kXX", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_134(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = params.get("TOP_K", 5)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_135(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        top_k = params.get("top_k", 6)

        increment("mcp_call_tool_total")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_136(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

        increment(None)
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_137(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

        increment("XXmcp_call_tool_totalXX")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_138(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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

        increment("MCP_CALL_TOOL_TOTAL")
        with Timer("mcp_call_tool_latency"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_139(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        with Timer(None):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_140(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        with Timer("XXmcp_call_tool_latencyXX"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_141(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
        with Timer("MCP_CALL_TOOL_LATENCY"):
            if tool_id == "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_142(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            if tool_id != "mock.tool.echo":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_143(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            if tool_id == "XXmock.tool.echoXX":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_144(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
            if tool_id == "MOCK.TOOL.ECHO":
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_145(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"XXjsonrpcXX": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_146(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"JSONRPC": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_147(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "XX2.0XX", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_148(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "XXresultXX": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_149(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "RESULT": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_150(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"XXoutputXX": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_151(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"OUTPUT": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_152(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "XXidXX": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_153(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "ID": req_id}

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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_154(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id != "mcp.tool.query":
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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_155(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "XXmcp.tool.queryXX":
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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_156(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "MCP.TOOL.QUERY":
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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_157(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = None
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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_158(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get(None)
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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_159(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("XXembeddingXX")
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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_160(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("EMBEDDING")
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
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_161(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = None
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_162(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get(None)
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_163(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("XXfiltersXX")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_164(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("FILTERS")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_165(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = None
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_166(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=None,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_167(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=None,
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_168(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=None,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_169(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=None,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_170(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_171(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_172(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_173(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding or [],
                        top_k=top_k,
                        )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_174(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

            if tool_id == "mcp.tool.query":
                query_embedding = input_payload.get("embedding")
                filters = input_payload.get("filters")
                try:
                    results = adapter.query_top_k(
                        namespace=tenant,
                        query_embedding=query_embedding and [],
                        top_k=top_k,
                        filters=filters,
                    )
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_175(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"XXjsonrpcXX": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_176(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"JSONRPC": "2.0", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_177(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"jsonrpc": "XX2.0XX", "result": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_178(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"jsonrpc": "2.0", "XXresultXX": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_179(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"jsonrpc": "2.0", "RESULT": {"hits": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_180(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"jsonrpc": "2.0", "result": {"XXhitsXX": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_181(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"jsonrpc": "2.0", "result": {"HITS": results}, "id": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_182(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "XXidXX": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_183(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    return {"jsonrpc": "2.0", "result": {"hits": results}, "ID": req_id}
                except Exception as exc:
                    logger.debug(f"Exception: {exc}")
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


async def x__dispatch_method__mutmut_184(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(None)
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


async def x__dispatch_method__mutmut_185(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception(None, exc)
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


async def x__dispatch_method__mutmut_186(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", None)
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


async def x__dispatch_method__mutmut_187(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception(exc)
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


async def x__dispatch_method__mutmut_188(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", )
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


async def x__dispatch_method__mutmut_189(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("XXAdapter query failed: %sXX", exc)
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


async def x__dispatch_method__mutmut_190(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("adapter query failed: %s", exc)
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


async def x__dispatch_method__mutmut_191(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("ADAPTER QUERY FAILED: %S", exc)
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


async def x__dispatch_method__mutmut_192(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "XXjsonrpcXX": "2.0",
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


async def x__dispatch_method__mutmut_193(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "JSONRPC": "2.0",
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


async def x__dispatch_method__mutmut_194(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "XX2.0XX",
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


async def x__dispatch_method__mutmut_195(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "XXerrorXX": {"code": -32000, "message": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_196(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "ERROR": {"code": -32000, "message": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_197(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"XXcodeXX": -32000, "message": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_198(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"CODE": -32000, "message": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_199(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": +32000, "message": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_200(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32001, "message": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_201(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "XXmessageXX": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_202(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "MESSAGE": "Adapter query failed"},
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


async def x__dispatch_method__mutmut_203(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "XXAdapter query failedXX"},
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


async def x__dispatch_method__mutmut_204(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "adapter query failed"},
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


async def x__dispatch_method__mutmut_205(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "ADAPTER QUERY FAILED"},
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


async def x__dispatch_method__mutmut_206(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "XXidXX": req_id,
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


async def x__dispatch_method__mutmut_207(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "ID": req_id,
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


async def x__dispatch_method__mutmut_208(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "XXjsonrpcXX": "2.0",
                "error": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_209(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "JSONRPC": "2.0",
                "error": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_210(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "XX2.0XX",
                "error": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_211(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "XXerrorXX": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_212(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "ERROR": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_213(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"XXcodeXX": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_214(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"CODE": -32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_215(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"code": +32000, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_216(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"code": -32001, "message": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_217(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "XXmessageXX": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_218(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "MESSAGE": f"Unknown tool {tool_id}"},
                "id": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_219(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "XXidXX": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_220(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
                    logger.exception("Adapter query failed: %s", exc)
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32000, "message": "Adapter query failed"},
                        "id": req_id,
                    }

            return {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": f"Unknown tool {tool_id}"},
                "ID": req_id,
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_221(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "XXjsonrpcXX": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_222(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "JSONRPC": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_223(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "jsonrpc": "XX2.0XX",
        "error": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_224(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "XXerrorXX": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_225(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "ERROR": {"code": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_226(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"XXcodeXX": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_227(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"CODE": -32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_228(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"code": +32601, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_229(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"code": -32602, "message": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_230(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"code": -32601, "XXmessageXX": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_231(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"code": -32601, "MESSAGE": "Method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_232(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"code": -32601, "message": "XXMethod not foundXX"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_233(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"code": -32601, "message": "method not found"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_234(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "error": {"code": -32601, "message": "METHOD NOT FOUND"},
        "id": req_id,
    }


async def x__dispatch_method__mutmut_235(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "XXidXX": req_id,
    }


async def x__dispatch_method__mutmut_236(p: dict[str, Any], adapter: BackendAdapter) -> dict[str, Any]:
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
                return {"jsonrpc": "2.0", "result": {"output": input_payload}, "id": req_id}

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
                    logger.debug(f"Exception: {exc}")
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
        "ID": req_id,
    }

x__dispatch_method__mutmut_mutants : ClassVar[MutantDict] = {
'x__dispatch_method__mutmut_1': x__dispatch_method__mutmut_1, 
    'x__dispatch_method__mutmut_2': x__dispatch_method__mutmut_2, 
    'x__dispatch_method__mutmut_3': x__dispatch_method__mutmut_3, 
    'x__dispatch_method__mutmut_4': x__dispatch_method__mutmut_4, 
    'x__dispatch_method__mutmut_5': x__dispatch_method__mutmut_5, 
    'x__dispatch_method__mutmut_6': x__dispatch_method__mutmut_6, 
    'x__dispatch_method__mutmut_7': x__dispatch_method__mutmut_7, 
    'x__dispatch_method__mutmut_8': x__dispatch_method__mutmut_8, 
    'x__dispatch_method__mutmut_9': x__dispatch_method__mutmut_9, 
    'x__dispatch_method__mutmut_10': x__dispatch_method__mutmut_10, 
    'x__dispatch_method__mutmut_11': x__dispatch_method__mutmut_11, 
    'x__dispatch_method__mutmut_12': x__dispatch_method__mutmut_12, 
    'x__dispatch_method__mutmut_13': x__dispatch_method__mutmut_13, 
    'x__dispatch_method__mutmut_14': x__dispatch_method__mutmut_14, 
    'x__dispatch_method__mutmut_15': x__dispatch_method__mutmut_15, 
    'x__dispatch_method__mutmut_16': x__dispatch_method__mutmut_16, 
    'x__dispatch_method__mutmut_17': x__dispatch_method__mutmut_17, 
    'x__dispatch_method__mutmut_18': x__dispatch_method__mutmut_18, 
    'x__dispatch_method__mutmut_19': x__dispatch_method__mutmut_19, 
    'x__dispatch_method__mutmut_20': x__dispatch_method__mutmut_20, 
    'x__dispatch_method__mutmut_21': x__dispatch_method__mutmut_21, 
    'x__dispatch_method__mutmut_22': x__dispatch_method__mutmut_22, 
    'x__dispatch_method__mutmut_23': x__dispatch_method__mutmut_23, 
    'x__dispatch_method__mutmut_24': x__dispatch_method__mutmut_24, 
    'x__dispatch_method__mutmut_25': x__dispatch_method__mutmut_25, 
    'x__dispatch_method__mutmut_26': x__dispatch_method__mutmut_26, 
    'x__dispatch_method__mutmut_27': x__dispatch_method__mutmut_27, 
    'x__dispatch_method__mutmut_28': x__dispatch_method__mutmut_28, 
    'x__dispatch_method__mutmut_29': x__dispatch_method__mutmut_29, 
    'x__dispatch_method__mutmut_30': x__dispatch_method__mutmut_30, 
    'x__dispatch_method__mutmut_31': x__dispatch_method__mutmut_31, 
    'x__dispatch_method__mutmut_32': x__dispatch_method__mutmut_32, 
    'x__dispatch_method__mutmut_33': x__dispatch_method__mutmut_33, 
    'x__dispatch_method__mutmut_34': x__dispatch_method__mutmut_34, 
    'x__dispatch_method__mutmut_35': x__dispatch_method__mutmut_35, 
    'x__dispatch_method__mutmut_36': x__dispatch_method__mutmut_36, 
    'x__dispatch_method__mutmut_37': x__dispatch_method__mutmut_37, 
    'x__dispatch_method__mutmut_38': x__dispatch_method__mutmut_38, 
    'x__dispatch_method__mutmut_39': x__dispatch_method__mutmut_39, 
    'x__dispatch_method__mutmut_40': x__dispatch_method__mutmut_40, 
    'x__dispatch_method__mutmut_41': x__dispatch_method__mutmut_41, 
    'x__dispatch_method__mutmut_42': x__dispatch_method__mutmut_42, 
    'x__dispatch_method__mutmut_43': x__dispatch_method__mutmut_43, 
    'x__dispatch_method__mutmut_44': x__dispatch_method__mutmut_44, 
    'x__dispatch_method__mutmut_45': x__dispatch_method__mutmut_45, 
    'x__dispatch_method__mutmut_46': x__dispatch_method__mutmut_46, 
    'x__dispatch_method__mutmut_47': x__dispatch_method__mutmut_47, 
    'x__dispatch_method__mutmut_48': x__dispatch_method__mutmut_48, 
    'x__dispatch_method__mutmut_49': x__dispatch_method__mutmut_49, 
    'x__dispatch_method__mutmut_50': x__dispatch_method__mutmut_50, 
    'x__dispatch_method__mutmut_51': x__dispatch_method__mutmut_51, 
    'x__dispatch_method__mutmut_52': x__dispatch_method__mutmut_52, 
    'x__dispatch_method__mutmut_53': x__dispatch_method__mutmut_53, 
    'x__dispatch_method__mutmut_54': x__dispatch_method__mutmut_54, 
    'x__dispatch_method__mutmut_55': x__dispatch_method__mutmut_55, 
    'x__dispatch_method__mutmut_56': x__dispatch_method__mutmut_56, 
    'x__dispatch_method__mutmut_57': x__dispatch_method__mutmut_57, 
    'x__dispatch_method__mutmut_58': x__dispatch_method__mutmut_58, 
    'x__dispatch_method__mutmut_59': x__dispatch_method__mutmut_59, 
    'x__dispatch_method__mutmut_60': x__dispatch_method__mutmut_60, 
    'x__dispatch_method__mutmut_61': x__dispatch_method__mutmut_61, 
    'x__dispatch_method__mutmut_62': x__dispatch_method__mutmut_62, 
    'x__dispatch_method__mutmut_63': x__dispatch_method__mutmut_63, 
    'x__dispatch_method__mutmut_64': x__dispatch_method__mutmut_64, 
    'x__dispatch_method__mutmut_65': x__dispatch_method__mutmut_65, 
    'x__dispatch_method__mutmut_66': x__dispatch_method__mutmut_66, 
    'x__dispatch_method__mutmut_67': x__dispatch_method__mutmut_67, 
    'x__dispatch_method__mutmut_68': x__dispatch_method__mutmut_68, 
    'x__dispatch_method__mutmut_69': x__dispatch_method__mutmut_69, 
    'x__dispatch_method__mutmut_70': x__dispatch_method__mutmut_70, 
    'x__dispatch_method__mutmut_71': x__dispatch_method__mutmut_71, 
    'x__dispatch_method__mutmut_72': x__dispatch_method__mutmut_72, 
    'x__dispatch_method__mutmut_73': x__dispatch_method__mutmut_73, 
    'x__dispatch_method__mutmut_74': x__dispatch_method__mutmut_74, 
    'x__dispatch_method__mutmut_75': x__dispatch_method__mutmut_75, 
    'x__dispatch_method__mutmut_76': x__dispatch_method__mutmut_76, 
    'x__dispatch_method__mutmut_77': x__dispatch_method__mutmut_77, 
    'x__dispatch_method__mutmut_78': x__dispatch_method__mutmut_78, 
    'x__dispatch_method__mutmut_79': x__dispatch_method__mutmut_79, 
    'x__dispatch_method__mutmut_80': x__dispatch_method__mutmut_80, 
    'x__dispatch_method__mutmut_81': x__dispatch_method__mutmut_81, 
    'x__dispatch_method__mutmut_82': x__dispatch_method__mutmut_82, 
    'x__dispatch_method__mutmut_83': x__dispatch_method__mutmut_83, 
    'x__dispatch_method__mutmut_84': x__dispatch_method__mutmut_84, 
    'x__dispatch_method__mutmut_85': x__dispatch_method__mutmut_85, 
    'x__dispatch_method__mutmut_86': x__dispatch_method__mutmut_86, 
    'x__dispatch_method__mutmut_87': x__dispatch_method__mutmut_87, 
    'x__dispatch_method__mutmut_88': x__dispatch_method__mutmut_88, 
    'x__dispatch_method__mutmut_89': x__dispatch_method__mutmut_89, 
    'x__dispatch_method__mutmut_90': x__dispatch_method__mutmut_90, 
    'x__dispatch_method__mutmut_91': x__dispatch_method__mutmut_91, 
    'x__dispatch_method__mutmut_92': x__dispatch_method__mutmut_92, 
    'x__dispatch_method__mutmut_93': x__dispatch_method__mutmut_93, 
    'x__dispatch_method__mutmut_94': x__dispatch_method__mutmut_94, 
    'x__dispatch_method__mutmut_95': x__dispatch_method__mutmut_95, 
    'x__dispatch_method__mutmut_96': x__dispatch_method__mutmut_96, 
    'x__dispatch_method__mutmut_97': x__dispatch_method__mutmut_97, 
    'x__dispatch_method__mutmut_98': x__dispatch_method__mutmut_98, 
    'x__dispatch_method__mutmut_99': x__dispatch_method__mutmut_99, 
    'x__dispatch_method__mutmut_100': x__dispatch_method__mutmut_100, 
    'x__dispatch_method__mutmut_101': x__dispatch_method__mutmut_101, 
    'x__dispatch_method__mutmut_102': x__dispatch_method__mutmut_102, 
    'x__dispatch_method__mutmut_103': x__dispatch_method__mutmut_103, 
    'x__dispatch_method__mutmut_104': x__dispatch_method__mutmut_104, 
    'x__dispatch_method__mutmut_105': x__dispatch_method__mutmut_105, 
    'x__dispatch_method__mutmut_106': x__dispatch_method__mutmut_106, 
    'x__dispatch_method__mutmut_107': x__dispatch_method__mutmut_107, 
    'x__dispatch_method__mutmut_108': x__dispatch_method__mutmut_108, 
    'x__dispatch_method__mutmut_109': x__dispatch_method__mutmut_109, 
    'x__dispatch_method__mutmut_110': x__dispatch_method__mutmut_110, 
    'x__dispatch_method__mutmut_111': x__dispatch_method__mutmut_111, 
    'x__dispatch_method__mutmut_112': x__dispatch_method__mutmut_112, 
    'x__dispatch_method__mutmut_113': x__dispatch_method__mutmut_113, 
    'x__dispatch_method__mutmut_114': x__dispatch_method__mutmut_114, 
    'x__dispatch_method__mutmut_115': x__dispatch_method__mutmut_115, 
    'x__dispatch_method__mutmut_116': x__dispatch_method__mutmut_116, 
    'x__dispatch_method__mutmut_117': x__dispatch_method__mutmut_117, 
    'x__dispatch_method__mutmut_118': x__dispatch_method__mutmut_118, 
    'x__dispatch_method__mutmut_119': x__dispatch_method__mutmut_119, 
    'x__dispatch_method__mutmut_120': x__dispatch_method__mutmut_120, 
    'x__dispatch_method__mutmut_121': x__dispatch_method__mutmut_121, 
    'x__dispatch_method__mutmut_122': x__dispatch_method__mutmut_122, 
    'x__dispatch_method__mutmut_123': x__dispatch_method__mutmut_123, 
    'x__dispatch_method__mutmut_124': x__dispatch_method__mutmut_124, 
    'x__dispatch_method__mutmut_125': x__dispatch_method__mutmut_125, 
    'x__dispatch_method__mutmut_126': x__dispatch_method__mutmut_126, 
    'x__dispatch_method__mutmut_127': x__dispatch_method__mutmut_127, 
    'x__dispatch_method__mutmut_128': x__dispatch_method__mutmut_128, 
    'x__dispatch_method__mutmut_129': x__dispatch_method__mutmut_129, 
    'x__dispatch_method__mutmut_130': x__dispatch_method__mutmut_130, 
    'x__dispatch_method__mutmut_131': x__dispatch_method__mutmut_131, 
    'x__dispatch_method__mutmut_132': x__dispatch_method__mutmut_132, 
    'x__dispatch_method__mutmut_133': x__dispatch_method__mutmut_133, 
    'x__dispatch_method__mutmut_134': x__dispatch_method__mutmut_134, 
    'x__dispatch_method__mutmut_135': x__dispatch_method__mutmut_135, 
    'x__dispatch_method__mutmut_136': x__dispatch_method__mutmut_136, 
    'x__dispatch_method__mutmut_137': x__dispatch_method__mutmut_137, 
    'x__dispatch_method__mutmut_138': x__dispatch_method__mutmut_138, 
    'x__dispatch_method__mutmut_139': x__dispatch_method__mutmut_139, 
    'x__dispatch_method__mutmut_140': x__dispatch_method__mutmut_140, 
    'x__dispatch_method__mutmut_141': x__dispatch_method__mutmut_141, 
    'x__dispatch_method__mutmut_142': x__dispatch_method__mutmut_142, 
    'x__dispatch_method__mutmut_143': x__dispatch_method__mutmut_143, 
    'x__dispatch_method__mutmut_144': x__dispatch_method__mutmut_144, 
    'x__dispatch_method__mutmut_145': x__dispatch_method__mutmut_145, 
    'x__dispatch_method__mutmut_146': x__dispatch_method__mutmut_146, 
    'x__dispatch_method__mutmut_147': x__dispatch_method__mutmut_147, 
    'x__dispatch_method__mutmut_148': x__dispatch_method__mutmut_148, 
    'x__dispatch_method__mutmut_149': x__dispatch_method__mutmut_149, 
    'x__dispatch_method__mutmut_150': x__dispatch_method__mutmut_150, 
    'x__dispatch_method__mutmut_151': x__dispatch_method__mutmut_151, 
    'x__dispatch_method__mutmut_152': x__dispatch_method__mutmut_152, 
    'x__dispatch_method__mutmut_153': x__dispatch_method__mutmut_153, 
    'x__dispatch_method__mutmut_154': x__dispatch_method__mutmut_154, 
    'x__dispatch_method__mutmut_155': x__dispatch_method__mutmut_155, 
    'x__dispatch_method__mutmut_156': x__dispatch_method__mutmut_156, 
    'x__dispatch_method__mutmut_157': x__dispatch_method__mutmut_157, 
    'x__dispatch_method__mutmut_158': x__dispatch_method__mutmut_158, 
    'x__dispatch_method__mutmut_159': x__dispatch_method__mutmut_159, 
    'x__dispatch_method__mutmut_160': x__dispatch_method__mutmut_160, 
    'x__dispatch_method__mutmut_161': x__dispatch_method__mutmut_161, 
    'x__dispatch_method__mutmut_162': x__dispatch_method__mutmut_162, 
    'x__dispatch_method__mutmut_163': x__dispatch_method__mutmut_163, 
    'x__dispatch_method__mutmut_164': x__dispatch_method__mutmut_164, 
    'x__dispatch_method__mutmut_165': x__dispatch_method__mutmut_165, 
    'x__dispatch_method__mutmut_166': x__dispatch_method__mutmut_166, 
    'x__dispatch_method__mutmut_167': x__dispatch_method__mutmut_167, 
    'x__dispatch_method__mutmut_168': x__dispatch_method__mutmut_168, 
    'x__dispatch_method__mutmut_169': x__dispatch_method__mutmut_169, 
    'x__dispatch_method__mutmut_170': x__dispatch_method__mutmut_170, 
    'x__dispatch_method__mutmut_171': x__dispatch_method__mutmut_171, 
    'x__dispatch_method__mutmut_172': x__dispatch_method__mutmut_172, 
    'x__dispatch_method__mutmut_173': x__dispatch_method__mutmut_173, 
    'x__dispatch_method__mutmut_174': x__dispatch_method__mutmut_174, 
    'x__dispatch_method__mutmut_175': x__dispatch_method__mutmut_175, 
    'x__dispatch_method__mutmut_176': x__dispatch_method__mutmut_176, 
    'x__dispatch_method__mutmut_177': x__dispatch_method__mutmut_177, 
    'x__dispatch_method__mutmut_178': x__dispatch_method__mutmut_178, 
    'x__dispatch_method__mutmut_179': x__dispatch_method__mutmut_179, 
    'x__dispatch_method__mutmut_180': x__dispatch_method__mutmut_180, 
    'x__dispatch_method__mutmut_181': x__dispatch_method__mutmut_181, 
    'x__dispatch_method__mutmut_182': x__dispatch_method__mutmut_182, 
    'x__dispatch_method__mutmut_183': x__dispatch_method__mutmut_183, 
    'x__dispatch_method__mutmut_184': x__dispatch_method__mutmut_184, 
    'x__dispatch_method__mutmut_185': x__dispatch_method__mutmut_185, 
    'x__dispatch_method__mutmut_186': x__dispatch_method__mutmut_186, 
    'x__dispatch_method__mutmut_187': x__dispatch_method__mutmut_187, 
    'x__dispatch_method__mutmut_188': x__dispatch_method__mutmut_188, 
    'x__dispatch_method__mutmut_189': x__dispatch_method__mutmut_189, 
    'x__dispatch_method__mutmut_190': x__dispatch_method__mutmut_190, 
    'x__dispatch_method__mutmut_191': x__dispatch_method__mutmut_191, 
    'x__dispatch_method__mutmut_192': x__dispatch_method__mutmut_192, 
    'x__dispatch_method__mutmut_193': x__dispatch_method__mutmut_193, 
    'x__dispatch_method__mutmut_194': x__dispatch_method__mutmut_194, 
    'x__dispatch_method__mutmut_195': x__dispatch_method__mutmut_195, 
    'x__dispatch_method__mutmut_196': x__dispatch_method__mutmut_196, 
    'x__dispatch_method__mutmut_197': x__dispatch_method__mutmut_197, 
    'x__dispatch_method__mutmut_198': x__dispatch_method__mutmut_198, 
    'x__dispatch_method__mutmut_199': x__dispatch_method__mutmut_199, 
    'x__dispatch_method__mutmut_200': x__dispatch_method__mutmut_200, 
    'x__dispatch_method__mutmut_201': x__dispatch_method__mutmut_201, 
    'x__dispatch_method__mutmut_202': x__dispatch_method__mutmut_202, 
    'x__dispatch_method__mutmut_203': x__dispatch_method__mutmut_203, 
    'x__dispatch_method__mutmut_204': x__dispatch_method__mutmut_204, 
    'x__dispatch_method__mutmut_205': x__dispatch_method__mutmut_205, 
    'x__dispatch_method__mutmut_206': x__dispatch_method__mutmut_206, 
    'x__dispatch_method__mutmut_207': x__dispatch_method__mutmut_207, 
    'x__dispatch_method__mutmut_208': x__dispatch_method__mutmut_208, 
    'x__dispatch_method__mutmut_209': x__dispatch_method__mutmut_209, 
    'x__dispatch_method__mutmut_210': x__dispatch_method__mutmut_210, 
    'x__dispatch_method__mutmut_211': x__dispatch_method__mutmut_211, 
    'x__dispatch_method__mutmut_212': x__dispatch_method__mutmut_212, 
    'x__dispatch_method__mutmut_213': x__dispatch_method__mutmut_213, 
    'x__dispatch_method__mutmut_214': x__dispatch_method__mutmut_214, 
    'x__dispatch_method__mutmut_215': x__dispatch_method__mutmut_215, 
    'x__dispatch_method__mutmut_216': x__dispatch_method__mutmut_216, 
    'x__dispatch_method__mutmut_217': x__dispatch_method__mutmut_217, 
    'x__dispatch_method__mutmut_218': x__dispatch_method__mutmut_218, 
    'x__dispatch_method__mutmut_219': x__dispatch_method__mutmut_219, 
    'x__dispatch_method__mutmut_220': x__dispatch_method__mutmut_220, 
    'x__dispatch_method__mutmut_221': x__dispatch_method__mutmut_221, 
    'x__dispatch_method__mutmut_222': x__dispatch_method__mutmut_222, 
    'x__dispatch_method__mutmut_223': x__dispatch_method__mutmut_223, 
    'x__dispatch_method__mutmut_224': x__dispatch_method__mutmut_224, 
    'x__dispatch_method__mutmut_225': x__dispatch_method__mutmut_225, 
    'x__dispatch_method__mutmut_226': x__dispatch_method__mutmut_226, 
    'x__dispatch_method__mutmut_227': x__dispatch_method__mutmut_227, 
    'x__dispatch_method__mutmut_228': x__dispatch_method__mutmut_228, 
    'x__dispatch_method__mutmut_229': x__dispatch_method__mutmut_229, 
    'x__dispatch_method__mutmut_230': x__dispatch_method__mutmut_230, 
    'x__dispatch_method__mutmut_231': x__dispatch_method__mutmut_231, 
    'x__dispatch_method__mutmut_232': x__dispatch_method__mutmut_232, 
    'x__dispatch_method__mutmut_233': x__dispatch_method__mutmut_233, 
    'x__dispatch_method__mutmut_234': x__dispatch_method__mutmut_234, 
    'x__dispatch_method__mutmut_235': x__dispatch_method__mutmut_235, 
    'x__dispatch_method__mutmut_236': x__dispatch_method__mutmut_236
}

def _dispatch_method(*args, **kwargs):
    result = _mutmut_trampoline(x__dispatch_method__mutmut_orig, x__dispatch_method__mutmut_mutants, args, kwargs)
    return result 

_dispatch_method.__signature__ = _mutmut_signature(x__dispatch_method__mutmut_orig)
x__dispatch_method__mutmut_orig.__name__ = 'x__dispatch_method'
