"""
Priority Pruner

Implements priority-based context pruning with configurable strategies
for different content types.
"""

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

logger = logging.getLogger(__name__)


class PruneStrategy(IntEnum):
    """Pruning strategy for content blocks."""

    KEEP = 0  # Never prune
    SUMMARIZE = 1  # Try summarization first
    TRUNCATE = 2  # Truncate to key parts
    REMOVE = 3  # Remove entirely


@dataclass
class PruneRule:
    """Rule for pruning specific content types."""

    pattern: str  # Regex pattern to match
    strategy: PruneStrategy
    priority_override: Optional[int] = None
    max_length: Optional[int] = None
    extract_pattern: Optional[str] = None  # Pattern to extract key info

    _compiled: Optional[re.Pattern] = field(default=None, repr=False)

    def matches(self, text: str) -> bool:
        """Check if text matches this rule."""
        if self._compiled is None:
            self._compiled = re.compile(self.pattern, re.IGNORECASE | re.DOTALL)
        return bool(self._compiled.search(text))

    def extract_key_info(self, text: str) -> str:
        """Extract key information from text."""
        if not self.extract_pattern:
            return text[: self.max_length] if self.max_length else text

        pattern = re.compile(self.extract_pattern, re.IGNORECASE | re.DOTALL)
        matches = pattern.findall(text)
        if matches:
            return "\n".join(str(m) for m in matches[:10])
        return text[: self.max_length] if self.max_length else text


@dataclass
class PrunedBlock:
    """Result of pruning a content block."""

    original_text: str
    pruned_text: str
    strategy_used: PruneStrategy
    tokens_saved: int
    key_info_preserved: bool


class PriorityPruner:
    """
    Priority-based content pruning with configurable strategies.

    Features:
    - Content-type specific rules
    - Key information extraction
    - Summarization integration
    - Metrics tracking
    """

    # Default rules for common content types
    DEFAULT_RULES = [
        # Never prune errors
        PruneRule(
            pattern=r"error|exception|failed|failure",
            strategy=PruneStrategy.KEEP,
            priority_override=100,
        ),
        # Summarize stack traces
        PruneRule(
            pattern=r"traceback|stack trace",
            strategy=PruneStrategy.TRUNCATE,
            max_length=500,
            extract_pattern=r'(?:File "([^"]+)", line \d+|^\s+\w+Error:.+$)',
        ),
        # Truncate verbose logs
        PruneRule(pattern=r"^\d{4}-\d{2}-\d{2}.*(?:INFO|DEBUG)", strategy=PruneStrategy.REMOVE),
        # Keep test results
        PruneRule(
            pattern=r"(?:PASSED|FAILED|SKIPPED)\s+test_",
            strategy=PruneStrategy.KEEP,
            priority_override=90,
        ),
        # Truncate large diffs
        PruneRule(
            pattern=r"^(?:diff --git|@@\s)",
            strategy=PruneStrategy.TRUNCATE,
            max_length=1000,
            extract_pattern=r"^(?:diff --git|[\+\-]{3}\s|@@\s).*$",
        ),
        # Summarize repetitive output
        PruneRule(pattern=r"(?:\.{10,}|={10,}|-{10,})", strategy=PruneStrategy.SUMMARIZE),
    ]

    def __init__(
        self,
        rules: Optional[list[PruneRule]] = None,
        summarizer: Optional[Callable[[str], str]] = None,
        token_counter: Optional[Callable[[str], int]] = None,
    ):
        """
        Initialize pruner.

        Args:
            rules: Custom pruning rules (defaults used if None)
            summarizer: Function to summarize content
            token_counter: Function to count tokens
        """
        self.rules = rules if rules is not None else self.DEFAULT_RULES.copy()
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def add_rule(self, rule: PruneRule):
        """Add a pruning rule."""
        self.rules.append(rule)

    def prune(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
        """
        Prune a text block according to rules.

        Args:
            text: Text to prune
            force_strategy: Override matched rule strategy

        Returns:
            PrunedBlock with results
        """
        self._blocks_processed += 1
        original_tokens = self._token_counter(text)

        # Find matching rule
        matched_rule = None
        for rule in self.rules:
            if rule.matches(text):
                matched_rule = rule
                break

        strategy = force_strategy
        if strategy is None:
            strategy = matched_rule.strategy if matched_rule else PruneStrategy.SUMMARIZE

        # Apply strategy
        pruned_text = text
        key_info_preserved = True

        if strategy == PruneStrategy.KEEP:
            pruned_text = text

        elif strategy == PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except (ValueError, TypeError, RuntimeError):
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(text, matched_rule)
            key_info_preserved = (
                matched_rule is not None and matched_rule.extract_pattern is not None
            )

        elif strategy == PruneStrategy.REMOVE:
            pruned_text = ""
            key_info_preserved = False

        pruned_tokens = self._token_counter(pruned_text)
        tokens_saved = original_tokens - pruned_tokens
        self._total_pruned += tokens_saved

        return PrunedBlock(
            original_text=text,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def prune_batch(
        self, texts: list[str], target_tokens: Optional[int] = None
    ) -> tuple[list[str], int]:
        """
        Prune a batch of texts to fit target token count.

        Args:
            texts: list of texts to prune
            target_tokens: Target total token count

        Returns:
            tuple of (pruned texts, total tokens saved)
        """
        if not target_tokens:
            # Just apply rules without target
            results = [self.prune(t) for t in texts]
            return [r.pruned_text for r in results], sum(r.tokens_saved for r in results)

        # Calculate current total
        current_tokens = sum(self._token_counter(t) for t in texts)
        if current_tokens <= target_tokens:
            return texts, 0

        # Score texts by priority (lower = prune first)
        scored = []
        for i, text in enumerate(texts):
            priority = 50  # Default
            for rule in self.rules:
                if rule.matches(text):
                    if rule.strategy == PruneStrategy.KEEP:
                        priority = 100
                    elif rule.priority_override:
                        priority = rule.priority_override
                    break
            scored.append((i, text, priority))

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)  # type: ignore[arg-type]
        tokens_saved = 0

        for idx, text, _ in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text  # type: ignore[call-overload]
            tokens_saved += result.tokens_saved

        return results, tokens_saved  # type: ignore[return-value]

    def get_metrics(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def _truncate(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"
