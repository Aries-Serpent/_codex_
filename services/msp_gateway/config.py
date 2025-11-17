"""
MSP Gateway Configuration (Local-first, Offline-capable)

Purpose:
- Provide a single source of truth for gateway settings with sane local defaults.
- Avoid hard dependencies on paid/managed services; prefer in-process or file-backed state.
- Power cascading components (routers, middleware, providers, RAG) via explicit, validated settings.

Conventions:
- Environment variables prefixed with MSP_ (fallback to generic OFFLINE for offline guard).
- Optional .env support if python-dotenv is installed; otherwise environment-only.
- All paths are relative to repo root or working directory unless absolute.

Key Features:
- OFFLINE guard (blocks network assumptions, enables file-based behavior).
- Local SQLite persistence option for simple tenant registry, if desired.
- FAISS-first retrieval (no external vector DB required), pgvector/weaviate configurable but off by default.
- Model adapters default to CPU-only local usage; mock adapter available for tests.

Usage:
    from services.msp_gateway.config import settings

    # Access configuration
    print(f"Gateway running on {settings.host}:{settings.port}")
    print(f"Offline mode: {settings.offline}")

Environment Variables (selected):
    MSP_HOST=127.0.0.1
    MSP_PORT=8080
    MSP_OFFLINE=1
    MSP_API_KEY_REQUIRED=1
    MSP_BASE_DIR=.codex
    MSP_DB_PATH=.codex/msp_gateway.db
    MSP_MODEL_BACKEND=mock|local|transformers
    MSP_MODEL_PATH=/path/to/local/model
    MSP_MODEL_DEVICE=cpu
    MSP_VECTOR_BACKEND=faiss
    MSP_FAISS_INDEX_DIR=.codex/tenants
    MSP_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
    MSP_EMBEDDING_CACHE_DIR=artifacts/emb
    MSP_RATE_LIMIT_ENABLED=1
    MSP_RATE_LIMIT_REQUESTS_PER_MINUTE=60
    MSP_RATE_LIMIT_TOKENS_PER_MINUTE=10000
    MSP_POLICY_DIR=policies
    MSP_REDACTION_ENABLED=1
    MSP_ADMIN_API_ENABLED=1
    MSP_KB_QUERY_ENABLED=1
    MSP_TENANT_REGISTRY_BACKEND=sqlite|memory
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MSPGatewaySettings(BaseSettings):
    """
    Settings for MSP Gateway - Local Mode

    All settings can be overridden via environment variables with MSP_ prefix.
    Supports .env file loading if available.

    Examples:
        >>> settings = MSPGatewaySettings()
        >>> settings.host
        '127.0.0.1'
        >>> settings.offline
        True
    """

    model_config = SettingsConfigDict(
        env_prefix="MSP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server settings
    host: str = Field(
        default="127.0.0.1", description="Bind address (localhost only for security in local mode)"
    )
    port: int = Field(default=8080, description="Server port for HTTP API")

    # Offline mode enforcement
    offline: bool = Field(
        default=True,
        description="Enforce offline-only operation (blocks network calls, uses local resources only)",
    )

    # Base directory for MSP data
    base_dir: str = Field(
        default=".codex", description="Base directory for all MSP data and artifacts"
    )

    # Database settings (SQLite for local mode)
    db_path: str = Field(
        default=".codex/msp_gateway.db",
        description="SQLite database path for tenant registry and metadata",
    )

    # Logging settings
    log_dir: str = Field(default=".codex/logs", description="Directory for application logs")
    log_format: str = Field(
        default="json",
        description="Log format: 'json' for structured logs or 'text' for human-readable",
    )
    log_level: str = Field(
        default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    # Model settings
    model_backend: str = Field(
        default="mock",
        description="Model backend type: 'mock' for testing, 'local'/'transformers' for HF models, 'llama.cpp' for GGUF",
    )
    model_path: Optional[str] = Field(
        default=None, description="Path to local model weights (required for non-mock backends)"
    )
    model_device: str = Field(
        default="cpu",
        description="Device for model inference: 'cpu' or 'cuda' (offline mode uses CPU only)",
    )
    model_name_or_path: Optional[str] = Field(
        default=None, description="Alternative to model_path for Hugging Face model identifier"
    )

    # Retrieval settings
    vector_backend: str = Field(
        default="faiss",
        description="Vector store backend: 'faiss' (local CPU), 'pgvector' (disabled), 'weaviate' (disabled)",
    )
    faiss_index_dir: str = Field(
        default=".codex/tenants", description="Base directory for per-tenant FAISS indexes"
    )
    index_dir: Optional[str] = Field(
        default=None, description="Alternative to faiss_index_dir for generic vector store path"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence-transformers model for generating embeddings (384-dim, fast on CPU)",
    )
    embedding_cache_dir: str = Field(
        default="artifacts/emb",
        description="Cache directory for downloaded embedding model weights",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Default number of top results to return from vector search",
    )

    # Rate limiting (in-memory token bucket)
    rate_limit_enabled: bool = Field(default=True, description="Enable per-tenant rate limiting")
    rate_limit_requests_per_minute: int = Field(
        default=60,
        ge=1,
        description="Maximum requests per minute per tenant (token bucket capacity)",
    )
    rate_limit_tokens_per_minute: int = Field(
        default=10000, ge=1, description="Maximum inference tokens per minute per tenant"
    )

    # Security and policies
    policy_dir: str = Field(
        default="policies",
        description="Directory containing safelist.yaml, denylist.yaml, and policy schemas",
    )
    redaction_enabled: bool = Field(
        default=True,
        description="Enable automatic PII redaction (email, phone, SSN, credit cards, etc.)",
    )
    api_key_required: bool = Field(
        default=True, description="Require API key authentication for all non-public endpoints"
    )

    # Feature flags
    admin_api_enabled: bool = Field(
        default=True, description="Enable admin API endpoints (/admin/tenants/*)"
    )
    kb_query_enabled: bool = Field(
        default=True, description="Enable knowledge base query endpoint (/v1/query_kb)"
    )

    # Tenant registry
    tenant_registry_backend: str = Field(
        default="sqlite",
        description="Tenant registry storage: 'sqlite' for persistence, 'memory' for ephemeral",
    )


# Global settings instance (singleton pattern)
# This is lazily initialized on first import and cached
settings = MSPGatewaySettings()


def get_settings() -> MSPGatewaySettings:
    """
    Get the global MSP Gateway settings instance.

    This function returns a cached singleton instance of MSPGatewaySettings.
    Settings are loaded from environment variables with MSP_ prefix and
    optionally from a .env file.

    Returns:
        MSPGatewaySettings: The global settings instance

    Examples:
        >>> from services.msp_gateway.config import get_settings
        >>> cfg = get_settings()
        >>> print(f"Server: {cfg.host}:{cfg.port}")
        Server: 127.0.0.1:8080
    """
    return settings


__all__ = ["MSPGatewaySettings", "settings", "get_settings"]
