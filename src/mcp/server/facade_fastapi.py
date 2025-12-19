from __future__ import annotations
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from .adapter_loader import load_adapter
from .jsonrpc_adapter import handle_jsonrpc_request
from .routes_health import router as health_router
from .middleware.auth import APIKeyAuthMiddleware  # type: ignore
from src.mcp.middleware.rate_limit_middleware import RateLimitMiddleware  # type: ignore
from src.mcp.server.tracing import init_tracing, ensure_request_id  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore

APP = FastAPI(title="MCP Façade (FastAPI)")

# Initialize tracing (no-op if OTel not installed)
init_tracing(service_name="mcp-facade")

# Mount health routes
APP.include_router(health_router, prefix="")

# Install middleware: auth then rate-limit (order matters)
APP.add_middleware(APIKeyAuthMiddleware)
APP.add_middleware(RateLimitMiddleware)

# Lazy adapter instance (loaded at startup or first request)
ADAPTER = None


@APP.on_event("startup")
async def startup_event():
    global ADAPTER
    adapter, adapter_name = load_adapter()
    ADAPTER = adapter


@APP.middleware("http")
async def request_id_middleware(request: Request, call_next):
    # Ensure X-Request-Id present and instrument request metrics
    request_id = ensure_request_id(request)
    increment("requests_total")
    with Timer("request_latency"):
        response = await call_next(request)
    response.headers.setdefault("X-Request-Id", request_id)
    return response


@APP.post("/jsonrpc")
async def jsonrpc_endpoint(request: Request):
    """
    Accept JSON-RPC 2.0 requests and route to MCP handlers.
    Expects request body to be JSON-RPC 2.0 object or batch (list).
    """
    body = await request.json()
    try:
        adapter = ADAPTER
        if adapter is None:
            adapter, _ = load_adapter()
        response = await handle_jsonrpc_request(body, adapter)
        return JSONResponse(content=response)
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"jsonrpc": "2.0", "error": {"code": -32000, "message": str(he.detail)}, "id": None},
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"jsonrpc": "2.0", "error": {"code": -32603, "message": str(exc)}, "id": None},
        )
