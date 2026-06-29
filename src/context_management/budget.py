"""
Token Budget Enforcer

Enforces token limits with sliding windows and priority-based pruning.
Implements hard ceiling (64k), soft cap (56k), and auto-summarization triggers.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from typing import Optional

# Token limits per Global Policies

logger = logging.getLogger(__name__)
HARD_TOKEN_CEILING = 64_000
SOFT_TOKEN_CAP = 56_000
SOFT_CAP_THRESHOLD = 0.90  # 90% of soft cap triggers summarization


class ContentPriority(IntEnum):
    """Priority levels for content during pruning."""

    CRITICAL = 100  # Errors, failures - never prune
    HIGH = 75  # Test results, file paths
    MEDIUM = 50  # Context, explanations
    LOW = 25  # Verbose output, logs
    DISPOSABLE = 0  # Can be pruned first


@dataclass
class TokenBudget:
    """Current token budget state."""

    hard_limit: int = HARD_TOKEN_CEILING
    soft_limit: int = SOFT_TOKEN_CAP
    current_usage: int = 0
    reserved: int = 8000  # Reserved buffer

    @property
    def available(self) -> int:
        """Available tokens before soft limit."""
        return max(0, self.soft_limit - self.current_usage)

    @property
    def hard_available(self) -> int:
        """Available tokens before hard limit."""
        return max(0, self.hard_limit - self.current_usage)

    @property
    def usage_ratio(self) -> float:
        """Current usage as ratio of soft limit."""
        return self.current_usage / self.soft_limit if self.soft_limit > 0 else 0.0

    @property
    def needs_pruning(self) -> bool:
        """Whether pruning is needed (≥90% of soft cap)."""
        return self.usage_ratio >= SOFT_CAP_THRESHOLD

    @property
    def over_hard_limit(self) -> bool:
        """Whether we're over hard limit."""
        return self.current_usage > self.hard_limit


@dataclass
class ContentBlock:
    """A block of content with metadata for budget management."""

    content: str
    token_count: int
    priority: ContentPriority = ContentPriority.MEDIUM
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = ""
    can_summarize: bool = True
    summary: Optional[str] = None

    def get_effective_content(self) -> str:
        """Get content, preferring summary if available and shorter."""
        if self.summary and len(self.summary) < len(self.content):
            return self.summary
        return self.content


class TokenBudgetEnforcer:
    """
    Enforce token budgets with sliding windows and priority pruning.

    Features:
    - Hard ceiling enforcement (64k tokens)
    - Soft cap with auto-summarization trigger (56k tokens)
    - Priority-based content pruning
    - Sliding window for context management
    """

    def __init__(
        self,
        hard_limit: int = HARD_TOKEN_CEILING,
        soft_limit: int = SOFT_TOKEN_CAP,
        token_counter: Optional[Callable[[str], int]] = None,
        summarizer: Optional[Callable[[str], str]] = None,
    ):
        """
        Initialize budget enforcer.

        Args:
            hard_limit: Absolute maximum tokens
            soft_limit: Soft cap triggering summarization
            token_counter: Function to count tokens (default: word-based estimate)
            summarizer: Function to summarize content
        """
        self.budget = TokenBudget(hard_limit=hard_limit, soft_limit=soft_limit)
        self._token_counter = token_counter or self._estimate_tokens
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return self._token_counter(text)

    def add_content(
        self,
        content: str,
        priority: ContentPriority = ContentPriority.MEDIUM,
        source: str = "",
        can_summarize: bool = True,
    ) -> bool:
        """
        Add content to budget, pruning if necessary.

        Args:
            content: Text content to add
            priority: Content priority level
            source: Source identifier
            can_summarize: Whether content can be summarized

        Returns:
            True if content was added, False if rejected
        """
        token_count = self.count_tokens(content)

        # Check if adding would exceed hard limit
        if self.budget.current_usage + token_count > self.budget.hard_limit:
            # Try to make room
            freed = self._prune_to_fit(token_count)
            if freed < token_count:
                return False

        # Check if we need to trigger summarization
        if self.budget.needs_pruning:
            self._summarize_low_priority()

        # Create and add block
        block = ContentBlock(
            content=content,
            token_count=token_count,
            priority=priority,
            source=source,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def get_context(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(self._blocks, key=lambda b: (b.priority, b.timestamp), reverse=True)

        selected = []
        total_tokens = 0

        for block in sorted_blocks:
            content = block.get_effective_content()
            tokens = self.count_tokens(content)

            if total_tokens + tokens <= limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def enforce_budget(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = int(self.budget.soft_limit * 0.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def get_budget_status(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def clear(self):
        """Clear all content and reset budget."""
        self._blocks.clear()
        self.budget.current_usage = 0

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (approximately 1 token per 4 characters)."""
        return len(text) // 4 + 1

    def _prune_to_fit(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=lambda x: (x[1].priority, x[1].timestamp))

        freed = 0
        to_remove = []

        for idx, block in prunable:
            if freed >= tokens_needed:
                break

            # Try summarization first if available
            if block.can_summarize and self._summarizer and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    summary_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def _summarize_low_priority(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
