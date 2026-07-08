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

# Backward compatibility imports (P19 shadow import fix)
# These modules have been moved to src/codex/clients/
from codex.clients.openai_client import (
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
