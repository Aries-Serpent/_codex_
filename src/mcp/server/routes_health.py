from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .adapter_loader import load_adapter

router = APIRouter()


@router.get("/health")
async def health_root():
    adapter, adapter_path = load_adapter()
    try:
        adapter_health = adapter.health_check()
    except Exception:
        adapter_health = {"status": "error"}
    payload = {"service": "mcp-facade", "adapter": adapter_path, "adapter_health": adapter_health}
    return JSONResponse(content=payload)


@router.get("/mcp/v1/health")
async def mcp_health():
    adapter, adapter_path = load_adapter()
    try:
        adapter_health = adapter.health_check()
    except Exception:
        adapter_health = {"status": "error"}
    return JSONResponse(content={"status": "ok", "adapter": adapter_path, "adapter_health": adapter_health})
