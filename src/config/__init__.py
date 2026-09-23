"""
Init Module

This module provides functionality for config package.

Usage:
    from config import CodexOpenAIClient, ExecutionResult

    # For backward compatibility, imports are re-exported from:
    # codex.clients.openai_client

Classes:
    CodexOpenAIClient - OpenAI client for autonomous agents
    ExecutionResult - Result of agent execution
    ModelConfig - Configuration for an OpenAI model
    AuditLogEntry - Audit log entry for API usage tracking

Author: Codex Team
"""

from __future__ import annotations

# Keep the public config namespace lightweight and import-safe.
# Importing the legacy codex.clients package pulls in networked client modules
# and their optional dependencies at import time, which violates the repo's
# no-network-on-import guard.  Re-export the local, in-tree implementation
# directly instead.
from .openai_client import (
    AVAILABLE_MODELS,
    AuditLogEntry,
    CodexOpenAIClient,
    CostTier,
    ExecutionResult,
    ModelConfig,
)

__all__ = [
    "AVAILABLE_MODELS",
    "AuditLogEntry",
    "CodexOpenAIClient",
    "CostTier",
    "ExecutionResult",
    "ModelConfig",
]
