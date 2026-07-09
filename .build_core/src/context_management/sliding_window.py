"""
Sliding Window Manager

Manages token windows for context management, implementing
sliding window strategy with summarization triggers.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional


class WindowStrategy(Enum):
    """Strategy for handling window overflow."""

    DROP_OLDEST = "drop_oldest"  # Remove oldest entries first
    SUMMARIZE = "summarize"  # Summarize and compress
    CHUNK = "chunk"  # Split into chunks
    PRIORITY_PRUNE = "priority"  # Remove by priority


@dataclass
class WindowEntry:
    """An entry in the sliding window."""

    content: str
    token_count: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    priority: int = 0
    entry_type: str = "content"
    metadata: dict = field(default_factory=dict)

    @property
    def age_seconds(self) -> float:
        """Age of entry in seconds."""
        return (datetime.now(UTC) - self.timestamp).total_seconds()


@dataclass
class WindowState:
    """Current state of the sliding window."""

    total_tokens: int
    entry_count: int
    oldest_age_seconds: float
    newest_age_seconds: float
    utilization_percent: float
    needs_pruning: bool
    summary_available: bool


class SlidingWindowManager:
    """
    Manages a sliding window of context with token budget.

    Implements:
    - Token-based windowing with configurable limits
    - Multiple overflow strategies (drop, summarize, chunk)
    - Priority-aware pruning
    - Automatic summarization triggers
    """

    # Global token limits per policy
    HARD_CEILING = 64_000
    SOFT_CAP = 56_000
    SUMMARIZATION_THRESHOLD = 0.90  # 90% of soft cap

    def __init__(
        self,
        max_tokens: int = SOFT_CAP,
        strategy: WindowStrategy = WindowStrategy.DROP_OLDEST,
        summarizer: Optional[Callable[[list[str]], str]] = None,
        reserve_tokens: int = 8000,
    ):
        """
        Initialize sliding window.

        Args:
            max_tokens: Maximum tokens in window
            strategy: Strategy for handling overflow
            summarizer: Optional function to summarize content
            reserve_tokens: Tokens to reserve for new content
        """
        self.max_tokens = min(max_tokens, self.HARD_CEILING)
        self.strategy = strategy
        self.summarizer = summarizer
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def add(
        self,
        content: str,
        priority: int = 0,
        entry_type: str = "content",
        metadata: Optional[dict] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Add content to window.

        Args:
            content: Content text
            priority: Priority level (higher = more important)
            entry_type: Type of entry for categorization
            metadata: Optional metadata

        Returns:
            tuple of (success, warning_message)
        """
        token_count = self._estimate_tokens(content)

        # Check if we need to make room
        warning = None
        if self._total_tokens + token_count > self.max_tokens:
            warning = self._make_room(token_count)

        # Check again after making room
        if self._total_tokens + token_count > self.max_tokens:
            return False, "Unable to add content: window at capacity"

        entry = WindowEntry(
            content=content,
            token_count=token_count,
            priority=priority,
            entry_type=entry_type,
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def get_window(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result: list[Any] = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def get_window_with_summary(self) -> tuple[Optional[str], list[str]]:
        """
        Get window with summary of pruned content.

        Returns:
            tuple of (summary, current_entries)
        """
        return self._summary, [e.content for e in self._entries]

    def get_state(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def prune_to_tokens(self, target_tokens: int) -> list[WindowEntry]:
        """
        Prune window to target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned entries
        """
        pruned = []

        while self._total_tokens > target_tokens and self._entries:
            if self.strategy == WindowStrategy.DROP_OLDEST:
                entry = self._entries.pop(0)
            elif self.strategy == WindowStrategy.PRIORITY_PRUNE:
                # Find lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def slide(self, keep_tokens: int) -> list[WindowEntry]:
        """
        Slide window to keep only most recent tokens.

        Args:
            keep_tokens: Number of tokens to keep

        Returns:
            list of removed entries
        """
        removed = []

        while self._total_tokens > keep_tokens and self._entries:
            entry = self._entries.pop(0)
            self._total_tokens -= entry.token_count
            removed.append(entry)

        # Update summary with removed content
        if removed and self.summarizer:
            removed_text = [e.content for e in removed]
            if self._summary:
                removed_text.insert(0, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def clear(self):
        """Clear window contents."""
        self._entries.clear()
        self._total_tokens = 0
        self._summary = None
        self._summary_tokens = 0

    def get_entries_by_type(self, entry_type: str) -> list[WindowEntry]:
        """Get all entries of a specific type."""
        return [e for e in self._entries if e.entry_type == entry_type]

    def get_entries_by_priority(self, min_priority: int) -> list[WindowEntry]:
        """Get all entries at or above minimum priority."""
        return [e for e in self._entries if e.priority >= min_priority]

    @property
    def total_tokens(self) -> int:
        """Total tokens in window."""
        return self._total_tokens

    @property
    def available_tokens(self) -> int:
        """Available tokens before hitting limit."""
        return max(0, self.max_tokens - self._total_tokens)

    @property
    def entry_count(self) -> int:
        """Number of entries in window."""
        return len(self._entries)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough: 4 chars per token)."""
        return len(text) // 4 + 1

    def _should_summarize(self) -> bool:
        """Check if summarization should be triggered."""
        threshold = self.max_tokens * self.SUMMARIZATION_THRESHOLD
        return self._total_tokens >= threshold

    def _trigger_summarization(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, len(self._entries) // 3)
        to_summarize = self._entries[:summarize_count]

        if not to_summarize:
            return

        # Generate summary
        texts = [e.content for e in to_summarize]
        if self._summary:
            texts.insert(0, self._summary)

        new_summary = self.summarizer(texts)

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def _make_room(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = self._entries.pop(0)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Dropped {len(removed)} oldest entries to make room"

        elif self.strategy == WindowStrategy.SUMMARIZE:
            if self.summarizer:
                self._trigger_summarization()
                return "Triggered summarization to make room"

        elif self.strategy == WindowStrategy.PRIORITY_PRUNE:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                # Remove lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None
