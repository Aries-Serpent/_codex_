"""Request schemas for MSP Gateway API"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class InferRequest(BaseModel):
    """Request model for inference endpoint"""

    tenant_id: str = Field(..., description="Tenant identifier")
    prompt: str = Field(..., description="Input prompt for inference")
    options: Optional[dict[str, Any]] = Field(default_factory=dict, description="Inference options")
    max_tokens: Optional[int] = Field(default=512, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )
    top_p: Optional[float] = Field(
        default=0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter"
    )
    stream: Optional[bool] = Field(default=False, description="Enable streaming response")


class KBQueryRequest(BaseModel):
    """Request model for knowledge base query endpoint"""

    tenant_id: str = Field(..., description="Tenant identifier")
    query: str = Field(..., description="Search query")
    top_k: Optional[int] = Field(default=5, ge=1, le=50, description="Number of results to return")
    filters: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Additional filters"
    )
    include_metadata: Optional[bool] = Field(default=True, description="Include document metadata")


class TenantCreateRequest(BaseModel):
    """Request model for creating a tenant"""

    tenant_id: str = Field(..., description="Unique tenant identifier")
    name: str = Field(..., description="Tenant display name")
    api_key: str = Field(..., description="API key for authentication")
    quota: Optional[dict[str, int]] = Field(
        default_factory=lambda: {"requests_per_minute": 60, "tokens_per_minute": 10000},
        description="Resource quotas",
    )
    policies: Optional[list[str]] = Field(default_factory=list, description="Applied policy names")
    metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class TenantUpdateRequest(BaseModel):
    """Request model for updating a tenant"""

    name: Optional[str] = Field(default=None, description="Updated tenant display name")
    quota: Optional[dict[str, int]] = Field(default=None, description="Updated resource quotas")
    policies: Optional[list[str]] = Field(default=None, description="Updated policy names")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Updated metadata")
    active: Optional[bool] = Field(default=None, description="Tenant active status")
