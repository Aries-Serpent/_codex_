from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class CallToolParams(BaseModel):
    tool_id: str = Field(..., description="Identifier of the tool to call")
    input: Dict[str, Any] = Field(..., description="Tool input payload")
    top_k: Optional[int] = Field(default=5, ge=1)
    tenant: Optional[str] = None


class NegotiateParams(BaseModel):
    client_versions: Optional[Dict[str, Any]] = None


class ListToolsParams(BaseModel):
    # Placeholder in case listTools supports filters in future
    include_internal: Optional[bool] = False
