"""MCP API - FastAPI façade for MCP operations."""

from __future__ import annotations

from .schemas import (
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

# create_app not yet implemented - will be added when FastAPI integration is complete
__all__ = [
    "ErrorCodes",
    "HealthResponse",
    "JSONRPCError",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "QueryRequest",
    "QueryResponse",
    "UpsertRequest",
    "UpsertResponse",
]
