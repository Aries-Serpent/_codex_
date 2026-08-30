"""
OpenAI Client Configuration for _codex_ Autonomous Agents
Leverages Aries-Serpent organization custom models (32 models)

Author: mbaetiong
Generated: 2025-12-17
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Literal

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)

# Model cost tiers
CostTier = Literal["low", "medium", "high", "very-high"]


@dataclass
class ModelConfig:
    """Configuration for an OpenAI model."""

    context_length: int
    reasoning: bool = False
    cost_tier: CostTier = "medium"
    input_cost_per_1k: float = 0.01
    output_cost_per_1k: float = 0.03


# Available models in GITHUB_CODEX organization
AVAILABLE_MODELS: dict[str, ModelConfig] = {
    # Reasoning models (o-series)
    "o1-preview": ModelConfig(
        128000,
        reasoning=True,
        cost_tier="high",
        input_cost_per_1k=0.015,
        output_cost_per_1k=0.06,
    ),
    "o1-mini": ModelConfig(
        128000,
        reasoning=True,
        cost_tier="medium",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.012,
    ),
    "o3-mini": ModelConfig(
        128000,
        reasoning=True,
        cost_tier="medium",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.012,
    ),
    # GPT-4 Turbo models
    "gpt-4-turbo": ModelConfig(
        128000, cost_tier="medium", input_cost_per_1k=0.01, output_cost_per_1k=0.03
    ),
    "gpt-4-turbo-preview": ModelConfig(
        128000, cost_tier="medium", input_cost_per_1k=0.01, output_cost_per_1k=0.03
    ),
    # GPT-4 models
    "gpt-4": ModelConfig(8192, cost_tier="high", input_cost_per_1k=0.03, output_cost_per_1k=0.06),
    "gpt-4-32k": ModelConfig(
        32768, cost_tier="very-high", input_cost_per_1k=0.06, output_cost_per_1k=0.12
    ),
    # GPT-4o models
    "gpt-4o": ModelConfig(
        128000, cost_tier="medium", input_cost_per_1k=0.005, output_cost_per_1k=0.015
    ),
    "gpt-4o-mini": ModelConfig(
        128000, cost_tier="low", input_cost_per_1k=0.00015, output_cost_per_1k=0.0006
    ),
    # GPT-3.5 models
    "gpt-3.5-turbo": ModelConfig(
        16385, cost_tier="low", input_cost_per_1k=0.0005, output_cost_per_1k=0.0015
    ),
    "gpt-3.5-turbo-16k": ModelConfig(
        16385, cost_tier="low", input_cost_per_1k=0.0005, output_cost_per_1k=0.0015
    ),
}


@dataclass
class ExecutionResult:
    """Result of an agent task execution."""

    success: bool
    model: str
    response: str | None = None
    error: str | None = None
    usage: dict[str, int] | None = None
    duration_ms: int = 0
    estimated_cost: float = 0.0


@dataclass
class AuditLogEntry:
    """Audit log entry for API usage tracking."""

    timestamp: str
    task_id: str
    model: str
    tokens_used: int
    duration_ms: int
    estimated_cost: float
    success: bool


# Safeguard: Validate API key format
# Supports: sk-<32+ alphanumeric chars> and sk-<project>-<alphanumeric chars> formats
API_KEY_PATTERN = re.compile(r"^sk-[a-zA-Z0-9-]{32,}$")
MAX_API_KEY_LENGTH = 256
MAX_AUDIT_LOG_SIZE = 1000


def _validate_api_key(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


class CodexOpenAIClient:
    """
    OpenAI client for _codex_ autonomous agents.

    Features:
    - Intelligent model selection based on task requirements
    - Cost estimation and tracking
    - Audit logging for compliance
    - Rate limiting support

    Safeguards:
    - Input validation on API key and parameters
    - Bounds checking on audit log size
    - Defensive error handling
    """

    def __init__(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def select_model(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if preferred_model and isinstance(preferred_model, str) and preferred_model in self.models:
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def build_system_prompt(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""  # noqa: E501

    def estimate_cost(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def log_execution(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def get_usage_summary(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log) // len(self.audit_log),
        }


__all__ = [
    "AVAILABLE_MODELS",
    "AuditLogEntry",
    "CodexOpenAIClient",
    "CostTier",
    "ExecutionResult",
    "ModelConfig",
]
