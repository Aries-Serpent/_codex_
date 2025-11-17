"""Response schemas for MSP Gateway API"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AuditRef(BaseModel):
    """Audit reference for tracking requests"""

    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    tenant_id: str = Field(..., description="Tenant identifier")
    endpoint: str = Field(..., description="API endpoint called")


class EvidenceTag(BaseModel):
    """Evidence tag for source attribution"""

    source_id: str = Field(..., description="Source document identifier")
    chunk_id: Optional[str] = Field(default=None, description="Chunk identifier within source")
    score: float = Field(..., description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class InferResponse(BaseModel):
    """Response model for inference endpoint"""

    request_id: str = Field(..., description="Request identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    generated_text: str = Field(..., description="Generated output text")
    tokens_used: int = Field(..., description="Total tokens consumed")
    model: str = Field(..., description="Model used for inference")
    audit: AuditRef = Field(..., description="Audit reference")
    evidence: Optional[List[EvidenceTag]] = Field(
        default_factory=list, description="Source evidence tags"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class KBSearchResult(BaseModel):
    """Single search result from knowledge base"""

    document_id: str = Field(..., description="Document identifier")
    content: str = Field(..., description="Document content or excerpt")
    score: float = Field(..., description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Document metadata"
    )


class KBQueryResponse(BaseModel):
    """Response model for knowledge base query endpoint"""

    request_id: str = Field(..., description="Request identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    query: str = Field(..., description="Original query")
    results: List[KBSearchResult] = Field(default_factory=list, description="Search results")
    total_results: int = Field(..., description="Total number of results found")
    audit: AuditRef = Field(..., description="Audit reference")


class TenantResponse(BaseModel):
    """Response model for tenant operations"""

    tenant_id: str = Field(..., description="Tenant identifier")
    name: str = Field(..., description="Tenant display name")
    quota: Dict[str, int] = Field(..., description="Resource quotas")
    policies: List[str] = Field(default_factory=list, description="Applied policy names")
    active: bool = Field(default=True, description="Tenant active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    offline_mode: bool = Field(..., description="Offline mode enabled")
    uptime_seconds: float = Field(..., description="Uptime in seconds")
    checks: Optional[Dict[str, bool]] = Field(
        default_factory=dict, description="Component health checks"
    )


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    request_id: Optional[str] = Field(default=None, description="Request identifier if available")
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional error details"
    )
