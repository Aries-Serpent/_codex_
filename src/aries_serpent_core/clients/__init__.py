"""
Codex Clients Module

Centralized location for all client implementations (OpenAI, GitHub, etc.)
for proper namespace organization and P19 shadow import resolution.

This module provides:
- OpenAI client for autonomous agent execution
- GitHub client for repository operations

Author: Aries Serpent
Generated: 2025-12-17
"""

from __future__ import annotations

from .github_client import (
    CACHE_DIR,
    OWNER,
    REPO,
    TOKEN,
    cache_get,
    cache_set,
    code_search,
    get_text,
    gh_get,
    list_branches,
    most_recent_branch,
)
from .openai_client import (
    AVAILABLE_MODELS,
    AuditLogEntry,
    CodexOpenAIClient,
    CostTier,
    ExecutionResult,
    ModelConfig,
)

__all__ = [
    # OpenAI client exports
    "AVAILABLE_MODELS",
    "AuditLogEntry",
    "CodexOpenAIClient",
    "CostTier",
    "ExecutionResult",
    "ModelConfig",
    # GitHub client exports
    "CACHE_DIR",
    "OWNER",
    "REPO",
    "TOKEN",
    "cache_get",
    "cache_set",
    "code_search",
    "gh_get",
    "get_text",
    "list_branches",
    "most_recent_branch",
]
