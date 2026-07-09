"""
MCP API Schemas - JSON-RPC and REST schemas for MCP operations.

Author: Copilot Agent
Generated: 2025-12-24
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryRequest:
    """Request schema for vector queries."""

    query: str
    top_k: int = 10
    filters: dict[str, Any] | None = None
    include_metadata: bool = True


@dataclass
class QueryResponse:
    """Response schema for vector queries."""

    matches: list[dict[str, Any]]
    query_time_ms: float
    total_matches: int


@dataclass
class UpsertRequest:
    """Request schema for vector upserts."""

    vectors: list[dict[str, Any]]
    namespace: str = "default"


@dataclass
class UpsertResponse:
    """Response schema for vector upserts."""

    upserted_count: int
    success: bool
    error: str | None = None


@dataclass
class HealthResponse:
    """Response schema for health checks."""

    status: str  # "healthy" or "unhealthy"
    adapters: dict[str, bool] = field(default_factory=dict)
    version: str = "1.0.0"


@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 request schema."""

    jsonrpc: str = "2.0"
    method: str = ""
    params: dict[str, Any] | None = None
    id: str | int | None = None


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 response schema."""

    jsonrpc: str = "2.0"
    result: Any = None
    error: dict[str, Any] | None = None
    id: str | int | None = None


@dataclass
class JSONRPCError:
    """JSON-RPC 2.0 error object."""

    code: int
    message: str
    data: Any = None


# Standard JSON-RPC error codes
class ErrorCodes:
    """Standard JSON-RPC error codes."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Custom error codes
    ADAPTER_ERROR = -32001
    NOT_CONNECTED = -32002
    RATE_LIMITED = -32003
