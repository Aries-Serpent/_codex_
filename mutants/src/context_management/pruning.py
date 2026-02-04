"""
Priority Pruner

Implements priority-based context pruning with configurable strategies
for different content types.
"""

from typing import Optional, Callable
import logging
logger = logging.getLogger(__name__)
from dataclasses import dataclass, field
from enum import IntEnum
import re
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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

    def xǁPriorityPrunerǁ__init____mutmut_orig(
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

    def xǁPriorityPrunerǁ__init____mutmut_1(
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
        self.rules = None
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_2(
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
        self.rules = rules if rules is None else self.DEFAULT_RULES.copy()
        self._summarizer = summarizer
        self._token_counter = token_counter or (lambda t: len(t) // 4)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_3(
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
        self._summarizer = None
        self._token_counter = token_counter or (lambda t: len(t) // 4)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_4(
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
        self._token_counter = None

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_5(
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
        self._token_counter = token_counter and (lambda t: len(t) // 4)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_6(
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
        self._token_counter = token_counter or (lambda t: None)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_7(
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
        self._token_counter = token_counter or (lambda t: len(t) / 4)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_8(
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
        self._token_counter = token_counter or (lambda t: len(t) // 5)

        # Metrics
        self._total_pruned = 0
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_9(
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
        self._total_pruned = None
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_10(
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
        self._total_pruned = 1
        self._blocks_processed = 0

    def xǁPriorityPrunerǁ__init____mutmut_11(
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
        self._blocks_processed = None

    def xǁPriorityPrunerǁ__init____mutmut_12(
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
        self._blocks_processed = 1
    
    xǁPriorityPrunerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPriorityPrunerǁ__init____mutmut_1': xǁPriorityPrunerǁ__init____mutmut_1, 
        'xǁPriorityPrunerǁ__init____mutmut_2': xǁPriorityPrunerǁ__init____mutmut_2, 
        'xǁPriorityPrunerǁ__init____mutmut_3': xǁPriorityPrunerǁ__init____mutmut_3, 
        'xǁPriorityPrunerǁ__init____mutmut_4': xǁPriorityPrunerǁ__init____mutmut_4, 
        'xǁPriorityPrunerǁ__init____mutmut_5': xǁPriorityPrunerǁ__init____mutmut_5, 
        'xǁPriorityPrunerǁ__init____mutmut_6': xǁPriorityPrunerǁ__init____mutmut_6, 
        'xǁPriorityPrunerǁ__init____mutmut_7': xǁPriorityPrunerǁ__init____mutmut_7, 
        'xǁPriorityPrunerǁ__init____mutmut_8': xǁPriorityPrunerǁ__init____mutmut_8, 
        'xǁPriorityPrunerǁ__init____mutmut_9': xǁPriorityPrunerǁ__init____mutmut_9, 
        'xǁPriorityPrunerǁ__init____mutmut_10': xǁPriorityPrunerǁ__init____mutmut_10, 
        'xǁPriorityPrunerǁ__init____mutmut_11': xǁPriorityPrunerǁ__init____mutmut_11, 
        'xǁPriorityPrunerǁ__init____mutmut_12': xǁPriorityPrunerǁ__init____mutmut_12
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPriorityPrunerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁPriorityPrunerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁPriorityPrunerǁ__init____mutmut_orig)
    xǁPriorityPrunerǁ__init____mutmut_orig.__name__ = 'xǁPriorityPrunerǁ__init__'

    def xǁPriorityPrunerǁadd_rule__mutmut_orig(self, rule: PruneRule):
        """Add a pruning rule."""
        self.rules.append(rule)

    def xǁPriorityPrunerǁadd_rule__mutmut_1(self, rule: PruneRule):
        """Add a pruning rule."""
        self.rules.append(None)
    
    xǁPriorityPrunerǁadd_rule__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPriorityPrunerǁadd_rule__mutmut_1': xǁPriorityPrunerǁadd_rule__mutmut_1
    }
    
    def add_rule(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPriorityPrunerǁadd_rule__mutmut_orig"), object.__getattribute__(self, "xǁPriorityPrunerǁadd_rule__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_rule.__signature__ = _mutmut_signature(xǁPriorityPrunerǁadd_rule__mutmut_orig)
    xǁPriorityPrunerǁadd_rule__mutmut_orig.__name__ = 'xǁPriorityPrunerǁadd_rule'

    def xǁPriorityPrunerǁprune__mutmut_orig(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_1(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
        """
        Prune a text block according to rules.

        Args:
            text: Text to prune
            force_strategy: Override matched rule strategy

        Returns:
            PrunedBlock with results
        """
        self._blocks_processed = 1
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_2(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
        """
        Prune a text block according to rules.

        Args:
            text: Text to prune
            force_strategy: Override matched rule strategy

        Returns:
            PrunedBlock with results
        """
        self._blocks_processed -= 1
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_3(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
        """
        Prune a text block according to rules.

        Args:
            text: Text to prune
            force_strategy: Override matched rule strategy

        Returns:
            PrunedBlock with results
        """
        self._blocks_processed += 2
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_4(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
        """
        Prune a text block according to rules.

        Args:
            text: Text to prune
            force_strategy: Override matched rule strategy

        Returns:
            PrunedBlock with results
        """
        self._blocks_processed += 1
        original_tokens = None

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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_5(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
        """
        Prune a text block according to rules.

        Args:
            text: Text to prune
            force_strategy: Override matched rule strategy

        Returns:
            PrunedBlock with results
        """
        self._blocks_processed += 1
        original_tokens = self._token_counter(None)

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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_6(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
        matched_rule = ""
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_7(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
            if rule.matches(None):
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_8(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                matched_rule = None
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_9(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                return

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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_10(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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

        strategy = None
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_11(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
        if strategy is not None:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_12(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
            strategy = None

        # Apply strategy
        pruned_text = text
        key_info_preserved = True

        if strategy == PruneStrategy.KEEP:
            pruned_text = text

        elif strategy == PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_13(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
        pruned_text = None
        key_info_preserved = True

        if strategy == PruneStrategy.KEEP:
            pruned_text = text

        elif strategy == PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_14(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
        key_info_preserved = None

        if strategy == PruneStrategy.KEEP:
            pruned_text = text

        elif strategy == PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_15(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
        key_info_preserved = False

        if strategy == PruneStrategy.KEEP:
            pruned_text = text

        elif strategy == PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_16(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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

        if strategy != PruneStrategy.KEEP:
            pruned_text = text

        elif strategy == PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_17(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
            pruned_text = None

        elif strategy == PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_18(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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

        elif strategy != PruneStrategy.SUMMARIZE:
            if self._summarizer:
                try:
                    pruned_text = self._summarizer(text)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_19(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                    pruned_text = None
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_20(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                    pruned_text = self._summarizer(None)
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_21(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning(None, exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_22(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=None)
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

    def xǁPriorityPrunerǁprune__mutmut_23(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning(exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_24(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", )
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

    def xǁPriorityPrunerǁprune__mutmut_25(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("XXException occurredXX", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_26(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_27(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("EXCEPTION OCCURRED", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_28(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=False)
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

    def xǁPriorityPrunerǁprune__mutmut_29(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning(None, exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_30(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=None)
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

    def xǁPriorityPrunerǁprune__mutmut_31(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning(exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_32(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", )
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

    def xǁPriorityPrunerǁprune__mutmut_33(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("XXException occurredXX", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_34(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("exception occurred", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_35(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("EXCEPTION OCCURRED", exc_info=True)
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

    def xǁPriorityPrunerǁprune__mutmut_36(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=False)
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

    def xǁPriorityPrunerǁprune__mutmut_37(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = None
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

    def xǁPriorityPrunerǁprune__mutmut_38(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(None, matched_rule)
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

    def xǁPriorityPrunerǁprune__mutmut_39(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, None)
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

    def xǁPriorityPrunerǁprune__mutmut_40(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(matched_rule)
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

    def xǁPriorityPrunerǁprune__mutmut_41(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, )
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

    def xǁPriorityPrunerǁprune__mutmut_42(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = None

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

    def xǁPriorityPrunerǁprune__mutmut_43(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(None, matched_rule)

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

    def xǁPriorityPrunerǁprune__mutmut_44(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, None)

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

    def xǁPriorityPrunerǁprune__mutmut_45(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(matched_rule)

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

    def xǁPriorityPrunerǁprune__mutmut_46(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, )

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

    def xǁPriorityPrunerǁprune__mutmut_47(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy != PruneStrategy.TRUNCATE:
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

    def xǁPriorityPrunerǁprune__mutmut_48(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = None
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

    def xǁPriorityPrunerǁprune__mutmut_49(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(None, matched_rule)
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

    def xǁPriorityPrunerǁprune__mutmut_50(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(text, None)
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

    def xǁPriorityPrunerǁprune__mutmut_51(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(matched_rule)
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

    def xǁPriorityPrunerǁprune__mutmut_52(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(text, )
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

    def xǁPriorityPrunerǁprune__mutmut_53(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(text, matched_rule)
            key_info_preserved = None

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

    def xǁPriorityPrunerǁprune__mutmut_54(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(text, matched_rule)
            key_info_preserved = (
                matched_rule is not None or matched_rule.extract_pattern is not None
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

    def xǁPriorityPrunerǁprune__mutmut_55(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(text, matched_rule)
            key_info_preserved = (
                matched_rule is None and matched_rule.extract_pattern is not None
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

    def xǁPriorityPrunerǁprune__mutmut_56(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    # Fall back to truncation
                    pruned_text = self._truncate(text, matched_rule)
            else:
                pruned_text = self._truncate(text, matched_rule)

        elif strategy == PruneStrategy.TRUNCATE:
            pruned_text = self._truncate(text, matched_rule)
            key_info_preserved = (
                matched_rule is not None and matched_rule.extract_pattern is None
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

    def xǁPriorityPrunerǁprune__mutmut_57(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

        elif strategy != PruneStrategy.REMOVE:
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

    def xǁPriorityPrunerǁprune__mutmut_58(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            pruned_text = None
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

    def xǁPriorityPrunerǁprune__mutmut_59(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            pruned_text = "XXXX"
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

    def xǁPriorityPrunerǁprune__mutmut_60(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            key_info_preserved = None

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

    def xǁPriorityPrunerǁprune__mutmut_61(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            key_info_preserved = True

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

    def xǁPriorityPrunerǁprune__mutmut_62(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

        pruned_tokens = None
        tokens_saved = original_tokens - pruned_tokens
        self._total_pruned += tokens_saved

        return PrunedBlock(
            original_text=text,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_63(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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

        pruned_tokens = self._token_counter(None)
        tokens_saved = original_tokens - pruned_tokens
        self._total_pruned += tokens_saved

        return PrunedBlock(
            original_text=text,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_64(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
        tokens_saved = None
        self._total_pruned += tokens_saved

        return PrunedBlock(
            original_text=text,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_65(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
        tokens_saved = original_tokens + pruned_tokens
        self._total_pruned += tokens_saved

        return PrunedBlock(
            original_text=text,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_66(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
        self._total_pruned = tokens_saved

        return PrunedBlock(
            original_text=text,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_67(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
        self._total_pruned -= tokens_saved

        return PrunedBlock(
            original_text=text,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_68(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            original_text=None,
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_69(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            pruned_text=None,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_70(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            strategy_used=None,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_71(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            tokens_saved=None,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_72(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            key_info_preserved=None,
        )

    def xǁPriorityPrunerǁprune__mutmut_73(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            pruned_text=pruned_text,
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_74(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            strategy_used=strategy,
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_75(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            tokens_saved=tokens_saved,
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_76(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            key_info_preserved=key_info_preserved,
        )

    def xǁPriorityPrunerǁprune__mutmut_77(self, text: str, force_strategy: Optional[PruneStrategy] = None) -> PrunedBlock:
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
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
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
            )
    
    xǁPriorityPrunerǁprune__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPriorityPrunerǁprune__mutmut_1': xǁPriorityPrunerǁprune__mutmut_1, 
        'xǁPriorityPrunerǁprune__mutmut_2': xǁPriorityPrunerǁprune__mutmut_2, 
        'xǁPriorityPrunerǁprune__mutmut_3': xǁPriorityPrunerǁprune__mutmut_3, 
        'xǁPriorityPrunerǁprune__mutmut_4': xǁPriorityPrunerǁprune__mutmut_4, 
        'xǁPriorityPrunerǁprune__mutmut_5': xǁPriorityPrunerǁprune__mutmut_5, 
        'xǁPriorityPrunerǁprune__mutmut_6': xǁPriorityPrunerǁprune__mutmut_6, 
        'xǁPriorityPrunerǁprune__mutmut_7': xǁPriorityPrunerǁprune__mutmut_7, 
        'xǁPriorityPrunerǁprune__mutmut_8': xǁPriorityPrunerǁprune__mutmut_8, 
        'xǁPriorityPrunerǁprune__mutmut_9': xǁPriorityPrunerǁprune__mutmut_9, 
        'xǁPriorityPrunerǁprune__mutmut_10': xǁPriorityPrunerǁprune__mutmut_10, 
        'xǁPriorityPrunerǁprune__mutmut_11': xǁPriorityPrunerǁprune__mutmut_11, 
        'xǁPriorityPrunerǁprune__mutmut_12': xǁPriorityPrunerǁprune__mutmut_12, 
        'xǁPriorityPrunerǁprune__mutmut_13': xǁPriorityPrunerǁprune__mutmut_13, 
        'xǁPriorityPrunerǁprune__mutmut_14': xǁPriorityPrunerǁprune__mutmut_14, 
        'xǁPriorityPrunerǁprune__mutmut_15': xǁPriorityPrunerǁprune__mutmut_15, 
        'xǁPriorityPrunerǁprune__mutmut_16': xǁPriorityPrunerǁprune__mutmut_16, 
        'xǁPriorityPrunerǁprune__mutmut_17': xǁPriorityPrunerǁprune__mutmut_17, 
        'xǁPriorityPrunerǁprune__mutmut_18': xǁPriorityPrunerǁprune__mutmut_18, 
        'xǁPriorityPrunerǁprune__mutmut_19': xǁPriorityPrunerǁprune__mutmut_19, 
        'xǁPriorityPrunerǁprune__mutmut_20': xǁPriorityPrunerǁprune__mutmut_20, 
        'xǁPriorityPrunerǁprune__mutmut_21': xǁPriorityPrunerǁprune__mutmut_21, 
        'xǁPriorityPrunerǁprune__mutmut_22': xǁPriorityPrunerǁprune__mutmut_22, 
        'xǁPriorityPrunerǁprune__mutmut_23': xǁPriorityPrunerǁprune__mutmut_23, 
        'xǁPriorityPrunerǁprune__mutmut_24': xǁPriorityPrunerǁprune__mutmut_24, 
        'xǁPriorityPrunerǁprune__mutmut_25': xǁPriorityPrunerǁprune__mutmut_25, 
        'xǁPriorityPrunerǁprune__mutmut_26': xǁPriorityPrunerǁprune__mutmut_26, 
        'xǁPriorityPrunerǁprune__mutmut_27': xǁPriorityPrunerǁprune__mutmut_27, 
        'xǁPriorityPrunerǁprune__mutmut_28': xǁPriorityPrunerǁprune__mutmut_28, 
        'xǁPriorityPrunerǁprune__mutmut_29': xǁPriorityPrunerǁprune__mutmut_29, 
        'xǁPriorityPrunerǁprune__mutmut_30': xǁPriorityPrunerǁprune__mutmut_30, 
        'xǁPriorityPrunerǁprune__mutmut_31': xǁPriorityPrunerǁprune__mutmut_31, 
        'xǁPriorityPrunerǁprune__mutmut_32': xǁPriorityPrunerǁprune__mutmut_32, 
        'xǁPriorityPrunerǁprune__mutmut_33': xǁPriorityPrunerǁprune__mutmut_33, 
        'xǁPriorityPrunerǁprune__mutmut_34': xǁPriorityPrunerǁprune__mutmut_34, 
        'xǁPriorityPrunerǁprune__mutmut_35': xǁPriorityPrunerǁprune__mutmut_35, 
        'xǁPriorityPrunerǁprune__mutmut_36': xǁPriorityPrunerǁprune__mutmut_36, 
        'xǁPriorityPrunerǁprune__mutmut_37': xǁPriorityPrunerǁprune__mutmut_37, 
        'xǁPriorityPrunerǁprune__mutmut_38': xǁPriorityPrunerǁprune__mutmut_38, 
        'xǁPriorityPrunerǁprune__mutmut_39': xǁPriorityPrunerǁprune__mutmut_39, 
        'xǁPriorityPrunerǁprune__mutmut_40': xǁPriorityPrunerǁprune__mutmut_40, 
        'xǁPriorityPrunerǁprune__mutmut_41': xǁPriorityPrunerǁprune__mutmut_41, 
        'xǁPriorityPrunerǁprune__mutmut_42': xǁPriorityPrunerǁprune__mutmut_42, 
        'xǁPriorityPrunerǁprune__mutmut_43': xǁPriorityPrunerǁprune__mutmut_43, 
        'xǁPriorityPrunerǁprune__mutmut_44': xǁPriorityPrunerǁprune__mutmut_44, 
        'xǁPriorityPrunerǁprune__mutmut_45': xǁPriorityPrunerǁprune__mutmut_45, 
        'xǁPriorityPrunerǁprune__mutmut_46': xǁPriorityPrunerǁprune__mutmut_46, 
        'xǁPriorityPrunerǁprune__mutmut_47': xǁPriorityPrunerǁprune__mutmut_47, 
        'xǁPriorityPrunerǁprune__mutmut_48': xǁPriorityPrunerǁprune__mutmut_48, 
        'xǁPriorityPrunerǁprune__mutmut_49': xǁPriorityPrunerǁprune__mutmut_49, 
        'xǁPriorityPrunerǁprune__mutmut_50': xǁPriorityPrunerǁprune__mutmut_50, 
        'xǁPriorityPrunerǁprune__mutmut_51': xǁPriorityPrunerǁprune__mutmut_51, 
        'xǁPriorityPrunerǁprune__mutmut_52': xǁPriorityPrunerǁprune__mutmut_52, 
        'xǁPriorityPrunerǁprune__mutmut_53': xǁPriorityPrunerǁprune__mutmut_53, 
        'xǁPriorityPrunerǁprune__mutmut_54': xǁPriorityPrunerǁprune__mutmut_54, 
        'xǁPriorityPrunerǁprune__mutmut_55': xǁPriorityPrunerǁprune__mutmut_55, 
        'xǁPriorityPrunerǁprune__mutmut_56': xǁPriorityPrunerǁprune__mutmut_56, 
        'xǁPriorityPrunerǁprune__mutmut_57': xǁPriorityPrunerǁprune__mutmut_57, 
        'xǁPriorityPrunerǁprune__mutmut_58': xǁPriorityPrunerǁprune__mutmut_58, 
        'xǁPriorityPrunerǁprune__mutmut_59': xǁPriorityPrunerǁprune__mutmut_59, 
        'xǁPriorityPrunerǁprune__mutmut_60': xǁPriorityPrunerǁprune__mutmut_60, 
        'xǁPriorityPrunerǁprune__mutmut_61': xǁPriorityPrunerǁprune__mutmut_61, 
        'xǁPriorityPrunerǁprune__mutmut_62': xǁPriorityPrunerǁprune__mutmut_62, 
        'xǁPriorityPrunerǁprune__mutmut_63': xǁPriorityPrunerǁprune__mutmut_63, 
        'xǁPriorityPrunerǁprune__mutmut_64': xǁPriorityPrunerǁprune__mutmut_64, 
        'xǁPriorityPrunerǁprune__mutmut_65': xǁPriorityPrunerǁprune__mutmut_65, 
        'xǁPriorityPrunerǁprune__mutmut_66': xǁPriorityPrunerǁprune__mutmut_66, 
        'xǁPriorityPrunerǁprune__mutmut_67': xǁPriorityPrunerǁprune__mutmut_67, 
        'xǁPriorityPrunerǁprune__mutmut_68': xǁPriorityPrunerǁprune__mutmut_68, 
        'xǁPriorityPrunerǁprune__mutmut_69': xǁPriorityPrunerǁprune__mutmut_69, 
        'xǁPriorityPrunerǁprune__mutmut_70': xǁPriorityPrunerǁprune__mutmut_70, 
        'xǁPriorityPrunerǁprune__mutmut_71': xǁPriorityPrunerǁprune__mutmut_71, 
        'xǁPriorityPrunerǁprune__mutmut_72': xǁPriorityPrunerǁprune__mutmut_72, 
        'xǁPriorityPrunerǁprune__mutmut_73': xǁPriorityPrunerǁprune__mutmut_73, 
        'xǁPriorityPrunerǁprune__mutmut_74': xǁPriorityPrunerǁprune__mutmut_74, 
        'xǁPriorityPrunerǁprune__mutmut_75': xǁPriorityPrunerǁprune__mutmut_75, 
        'xǁPriorityPrunerǁprune__mutmut_76': xǁPriorityPrunerǁprune__mutmut_76, 
        'xǁPriorityPrunerǁprune__mutmut_77': xǁPriorityPrunerǁprune__mutmut_77
    }
    
    def prune(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPriorityPrunerǁprune__mutmut_orig"), object.__getattribute__(self, "xǁPriorityPrunerǁprune__mutmut_mutants"), args, kwargs, self)
        return result 
    
    prune.__signature__ = _mutmut_signature(xǁPriorityPrunerǁprune__mutmut_orig)
    xǁPriorityPrunerǁprune__mutmut_orig.__name__ = 'xǁPriorityPrunerǁprune'

    def xǁPriorityPrunerǁprune_batch__mutmut_orig(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_1(
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
        if target_tokens:
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_2(
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
            results = None
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_3(
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
            results = [self.prune(None) for t in texts]
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_4(
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
            return [r.pruned_text for r in results], sum(None)

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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_5(
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
        current_tokens = None
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_6(
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
        current_tokens = sum(None)
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_7(
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
        current_tokens = sum(self._token_counter(None) for t in texts)
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_8(
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
        if current_tokens < target_tokens:
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_9(
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
            return texts, 1

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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_10(
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
        scored = None
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_11(
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
        for i, text in enumerate(None):
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_12(
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
            priority = None  # Default
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_13(
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
            priority = 51  # Default
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_14(
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
                if rule.matches(None):
                    if rule.strategy == PruneStrategy.KEEP:
                        priority = 100
                    elif rule.priority_override:
                        priority = rule.priority_override
                    break
            scored.append((i, text, priority))

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_15(
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
                    if rule.strategy != PruneStrategy.KEEP:
                        priority = 100
                    elif rule.priority_override:
                        priority = rule.priority_override
                    break
            scored.append((i, text, priority))

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_16(
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
                        priority = None
                    elif rule.priority_override:
                        priority = rule.priority_override
                    break
            scored.append((i, text, priority))

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_17(
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
                        priority = 101
                    elif rule.priority_override:
                        priority = rule.priority_override
                    break
            scored.append((i, text, priority))

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_18(
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
                        priority = None
                    break
            scored.append((i, text, priority))

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_19(
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
                    return
            scored.append((i, text, priority))

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_20(
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
            scored.append(None)

        # Sort by priority (ascending - lowest priority first)
        scored.sort(key=lambda x: x[2])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_21(
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
        scored.sort(key=None)

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_22(
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
        scored.sort(key=lambda x: None)

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_23(
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
        scored.sort(key=lambda x: x[3])

        # Prune until under target
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_24(
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
        results = None
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_25(
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
        results = list(None)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_26(
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
        results = list(texts)
        tokens_saved = None

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_27(
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
        results = list(texts)
        tokens_saved = 1

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_28(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens + tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_29(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved < target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_30(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                return

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_31(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = None
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_32(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(None)
            results[idx] = result.pruned_text
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_33(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = None
            tokens_saved += result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_34(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved = result.tokens_saved

        return results, tokens_saved

    def xǁPriorityPrunerǁprune_batch__mutmut_35(
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
        results = list(texts)
        tokens_saved = 0

        for idx, text, priority in scored:
            if current_tokens - tokens_saved <= target_tokens:
                break

            result = self.prune(text)
            results[idx] = result.pruned_text
            tokens_saved -= result.tokens_saved

        return results, tokens_saved
    
    xǁPriorityPrunerǁprune_batch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPriorityPrunerǁprune_batch__mutmut_1': xǁPriorityPrunerǁprune_batch__mutmut_1, 
        'xǁPriorityPrunerǁprune_batch__mutmut_2': xǁPriorityPrunerǁprune_batch__mutmut_2, 
        'xǁPriorityPrunerǁprune_batch__mutmut_3': xǁPriorityPrunerǁprune_batch__mutmut_3, 
        'xǁPriorityPrunerǁprune_batch__mutmut_4': xǁPriorityPrunerǁprune_batch__mutmut_4, 
        'xǁPriorityPrunerǁprune_batch__mutmut_5': xǁPriorityPrunerǁprune_batch__mutmut_5, 
        'xǁPriorityPrunerǁprune_batch__mutmut_6': xǁPriorityPrunerǁprune_batch__mutmut_6, 
        'xǁPriorityPrunerǁprune_batch__mutmut_7': xǁPriorityPrunerǁprune_batch__mutmut_7, 
        'xǁPriorityPrunerǁprune_batch__mutmut_8': xǁPriorityPrunerǁprune_batch__mutmut_8, 
        'xǁPriorityPrunerǁprune_batch__mutmut_9': xǁPriorityPrunerǁprune_batch__mutmut_9, 
        'xǁPriorityPrunerǁprune_batch__mutmut_10': xǁPriorityPrunerǁprune_batch__mutmut_10, 
        'xǁPriorityPrunerǁprune_batch__mutmut_11': xǁPriorityPrunerǁprune_batch__mutmut_11, 
        'xǁPriorityPrunerǁprune_batch__mutmut_12': xǁPriorityPrunerǁprune_batch__mutmut_12, 
        'xǁPriorityPrunerǁprune_batch__mutmut_13': xǁPriorityPrunerǁprune_batch__mutmut_13, 
        'xǁPriorityPrunerǁprune_batch__mutmut_14': xǁPriorityPrunerǁprune_batch__mutmut_14, 
        'xǁPriorityPrunerǁprune_batch__mutmut_15': xǁPriorityPrunerǁprune_batch__mutmut_15, 
        'xǁPriorityPrunerǁprune_batch__mutmut_16': xǁPriorityPrunerǁprune_batch__mutmut_16, 
        'xǁPriorityPrunerǁprune_batch__mutmut_17': xǁPriorityPrunerǁprune_batch__mutmut_17, 
        'xǁPriorityPrunerǁprune_batch__mutmut_18': xǁPriorityPrunerǁprune_batch__mutmut_18, 
        'xǁPriorityPrunerǁprune_batch__mutmut_19': xǁPriorityPrunerǁprune_batch__mutmut_19, 
        'xǁPriorityPrunerǁprune_batch__mutmut_20': xǁPriorityPrunerǁprune_batch__mutmut_20, 
        'xǁPriorityPrunerǁprune_batch__mutmut_21': xǁPriorityPrunerǁprune_batch__mutmut_21, 
        'xǁPriorityPrunerǁprune_batch__mutmut_22': xǁPriorityPrunerǁprune_batch__mutmut_22, 
        'xǁPriorityPrunerǁprune_batch__mutmut_23': xǁPriorityPrunerǁprune_batch__mutmut_23, 
        'xǁPriorityPrunerǁprune_batch__mutmut_24': xǁPriorityPrunerǁprune_batch__mutmut_24, 
        'xǁPriorityPrunerǁprune_batch__mutmut_25': xǁPriorityPrunerǁprune_batch__mutmut_25, 
        'xǁPriorityPrunerǁprune_batch__mutmut_26': xǁPriorityPrunerǁprune_batch__mutmut_26, 
        'xǁPriorityPrunerǁprune_batch__mutmut_27': xǁPriorityPrunerǁprune_batch__mutmut_27, 
        'xǁPriorityPrunerǁprune_batch__mutmut_28': xǁPriorityPrunerǁprune_batch__mutmut_28, 
        'xǁPriorityPrunerǁprune_batch__mutmut_29': xǁPriorityPrunerǁprune_batch__mutmut_29, 
        'xǁPriorityPrunerǁprune_batch__mutmut_30': xǁPriorityPrunerǁprune_batch__mutmut_30, 
        'xǁPriorityPrunerǁprune_batch__mutmut_31': xǁPriorityPrunerǁprune_batch__mutmut_31, 
        'xǁPriorityPrunerǁprune_batch__mutmut_32': xǁPriorityPrunerǁprune_batch__mutmut_32, 
        'xǁPriorityPrunerǁprune_batch__mutmut_33': xǁPriorityPrunerǁprune_batch__mutmut_33, 
        'xǁPriorityPrunerǁprune_batch__mutmut_34': xǁPriorityPrunerǁprune_batch__mutmut_34, 
        'xǁPriorityPrunerǁprune_batch__mutmut_35': xǁPriorityPrunerǁprune_batch__mutmut_35
    }
    
    def prune_batch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPriorityPrunerǁprune_batch__mutmut_orig"), object.__getattribute__(self, "xǁPriorityPrunerǁprune_batch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    prune_batch.__signature__ = _mutmut_signature(xǁPriorityPrunerǁprune_batch__mutmut_orig)
    xǁPriorityPrunerǁprune_batch__mutmut_orig.__name__ = 'xǁPriorityPrunerǁprune_batch'

    def xǁPriorityPrunerǁget_metrics__mutmut_orig(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_1(self) -> dict:
        """Get pruning metrics."""
        return {
            "XXtotal_tokens_prunedXX": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_2(self) -> dict:
        """Get pruning metrics."""
        return {
            "TOTAL_TOKENS_PRUNED": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_3(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "XXblocks_processedXX": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_4(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "BLOCKS_PROCESSED": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_5(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "XXavg_tokens_per_blockXX": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_6(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "AVG_TOKENS_PER_BLOCK": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_7(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned * self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_8(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed >= 0 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_9(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 1 else 0
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_10(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 1
            ),
            "rule_count": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_11(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "XXrule_countXX": len(self.rules),
        }

    def xǁPriorityPrunerǁget_metrics__mutmut_12(self) -> dict:
        """Get pruning metrics."""
        return {
            "total_tokens_pruned": self._total_pruned,
            "blocks_processed": self._blocks_processed,
            "avg_tokens_per_block": (
                self._total_pruned / self._blocks_processed if self._blocks_processed > 0 else 0
            ),
            "RULE_COUNT": len(self.rules),
        }
    
    xǁPriorityPrunerǁget_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPriorityPrunerǁget_metrics__mutmut_1': xǁPriorityPrunerǁget_metrics__mutmut_1, 
        'xǁPriorityPrunerǁget_metrics__mutmut_2': xǁPriorityPrunerǁget_metrics__mutmut_2, 
        'xǁPriorityPrunerǁget_metrics__mutmut_3': xǁPriorityPrunerǁget_metrics__mutmut_3, 
        'xǁPriorityPrunerǁget_metrics__mutmut_4': xǁPriorityPrunerǁget_metrics__mutmut_4, 
        'xǁPriorityPrunerǁget_metrics__mutmut_5': xǁPriorityPrunerǁget_metrics__mutmut_5, 
        'xǁPriorityPrunerǁget_metrics__mutmut_6': xǁPriorityPrunerǁget_metrics__mutmut_6, 
        'xǁPriorityPrunerǁget_metrics__mutmut_7': xǁPriorityPrunerǁget_metrics__mutmut_7, 
        'xǁPriorityPrunerǁget_metrics__mutmut_8': xǁPriorityPrunerǁget_metrics__mutmut_8, 
        'xǁPriorityPrunerǁget_metrics__mutmut_9': xǁPriorityPrunerǁget_metrics__mutmut_9, 
        'xǁPriorityPrunerǁget_metrics__mutmut_10': xǁPriorityPrunerǁget_metrics__mutmut_10, 
        'xǁPriorityPrunerǁget_metrics__mutmut_11': xǁPriorityPrunerǁget_metrics__mutmut_11, 
        'xǁPriorityPrunerǁget_metrics__mutmut_12': xǁPriorityPrunerǁget_metrics__mutmut_12
    }
    
    def get_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPriorityPrunerǁget_metrics__mutmut_orig"), object.__getattribute__(self, "xǁPriorityPrunerǁget_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_metrics.__signature__ = _mutmut_signature(xǁPriorityPrunerǁget_metrics__mutmut_orig)
    xǁPriorityPrunerǁget_metrics__mutmut_orig.__name__ = 'xǁPriorityPrunerǁget_metrics'

    def xǁPriorityPrunerǁ_truncate__mutmut_orig(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_1(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule or rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_2(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(None)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_3(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = None
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_4(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 501 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_5(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is not None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_6(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length and 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_7(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 501)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_8(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) < max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_9(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = None
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_10(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len / 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_11(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 3
        return f"{text[:keep]}\n... [truncated] ...\n{text[-keep:]}"

    def xǁPriorityPrunerǁ_truncate__mutmut_12(self, text: str, rule: Optional[PruneRule]) -> str:
        """Truncate text according to rule."""
        if rule and rule.extract_pattern:
            return rule.extract_key_info(text)

        max_len = 500 if rule is None else (rule.max_length or 500)
        if len(text) <= max_len:
            return text

        # Keep beginning and end
        keep = max_len // 2
        return f"{text[:keep]}\n... [truncated] ...\n{text[+keep:]}"
    
    xǁPriorityPrunerǁ_truncate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPriorityPrunerǁ_truncate__mutmut_1': xǁPriorityPrunerǁ_truncate__mutmut_1, 
        'xǁPriorityPrunerǁ_truncate__mutmut_2': xǁPriorityPrunerǁ_truncate__mutmut_2, 
        'xǁPriorityPrunerǁ_truncate__mutmut_3': xǁPriorityPrunerǁ_truncate__mutmut_3, 
        'xǁPriorityPrunerǁ_truncate__mutmut_4': xǁPriorityPrunerǁ_truncate__mutmut_4, 
        'xǁPriorityPrunerǁ_truncate__mutmut_5': xǁPriorityPrunerǁ_truncate__mutmut_5, 
        'xǁPriorityPrunerǁ_truncate__mutmut_6': xǁPriorityPrunerǁ_truncate__mutmut_6, 
        'xǁPriorityPrunerǁ_truncate__mutmut_7': xǁPriorityPrunerǁ_truncate__mutmut_7, 
        'xǁPriorityPrunerǁ_truncate__mutmut_8': xǁPriorityPrunerǁ_truncate__mutmut_8, 
        'xǁPriorityPrunerǁ_truncate__mutmut_9': xǁPriorityPrunerǁ_truncate__mutmut_9, 
        'xǁPriorityPrunerǁ_truncate__mutmut_10': xǁPriorityPrunerǁ_truncate__mutmut_10, 
        'xǁPriorityPrunerǁ_truncate__mutmut_11': xǁPriorityPrunerǁ_truncate__mutmut_11, 
        'xǁPriorityPrunerǁ_truncate__mutmut_12': xǁPriorityPrunerǁ_truncate__mutmut_12
    }
    
    def _truncate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPriorityPrunerǁ_truncate__mutmut_orig"), object.__getattribute__(self, "xǁPriorityPrunerǁ_truncate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _truncate.__signature__ = _mutmut_signature(xǁPriorityPrunerǁ_truncate__mutmut_orig)
    xǁPriorityPrunerǁ_truncate__mutmut_orig.__name__ = 'xǁPriorityPrunerǁ_truncate'
