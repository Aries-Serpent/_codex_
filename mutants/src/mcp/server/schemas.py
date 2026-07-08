"""
Schemas Module

This module provides functionality for schemas.

Usage:
    from server.schemas import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class CallToolParams(BaseModel):
    tool_id: str = Field(..., description="Identifier of the tool to call")
    input: dict[str, Any] = Field(..., description="Tool input payload")
    top_k: Optional[int] = Field(default=5, ge=1)
    tenant: Optional[str] = None


class NegotiateParams(BaseModel):
    client_versions: Optional[dict[str, Any]] = None


class ListToolsParams(BaseModel):
    # Placeholder in case listTools supports filters in future
    include_internal: Optional[bool] = False
