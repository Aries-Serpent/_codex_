"""
MSP Gateway Configuration
Centralized settings for the tenant-aware inference gateway.
Supports local-first, offline operation.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MSPGatewaySettings(BaseSettings):
    """Settings for MSP Gateway - Local Mode"""
    
    model_config = SettingsConfigDict(
        env_prefix="MSP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Server settings
    host: str = Field(default="127.0.0.1", description="Bind address (localhost only)")
    port: int = Field(default=8080, description="Server port")
    
    # Offline mode enforcement
    offline: bool = Field(default=True, description="Enforce offline-only operation")
    
    # Database settings (SQLite for local mode)
    db_path: str = Field(default=".codex/msp_gateway.db", description="SQLite database path")
    
    # Logging settings
    log_dir: str = Field(default=".codex/logs", description="Log directory")
    log_format: str = Field(default="json", description="Log format: json or text")
    log_level: str = Field(default="INFO", description="Log level")
    
    # Model settings
    model_backend: str = Field(default="local", description="Model backend: local, hf")
    model_path: Optional[str] = Field(default=None, description="Path to local model weights")
    model_device: str = Field(default="cpu", description="Device for model inference")
    
    # Retrieval settings
    vector_backend: str = Field(default="faiss", description="Vector store backend")
    faiss_index_dir: str = Field(default=".codex/tenants", description="Directory for FAISS indexes")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model")
    embedding_cache_dir: str = Field(default="artifacts/emb", description="Embedding cache directory")
    
    # Rate limiting (in-memory)
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, description="Requests per minute per tenant")
    rate_limit_tokens_per_minute: int = Field(default=10000, description="Tokens per minute per tenant")
    
    # Security and policies
    policy_dir: str = Field(default="policies", description="Policy files directory")
    redaction_enabled: bool = Field(default=True, description="Enable content redaction")
    
    # Feature flags
    admin_api_enabled: bool = Field(default=True, description="Enable admin API")
    kb_query_enabled: bool = Field(default=True, description="Enable knowledge base queries")
    
    # Tenant registry
    tenant_registry_backend: str = Field(default="sqlite", description="Tenant registry: sqlite, memory")


# Global settings instance
settings = MSPGatewaySettings()
