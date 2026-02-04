"""
Token Budget Enforcer

Enforces token limits with sliding windows and priority-based pruning.
Implements hard ceiling (64k), soft cap (56k), and auto-summarization triggers.
"""

import logging
logger = logging.getLogger(__name__)
from typing import Optional, Callable
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime


# Token limits per Global Policies
HARD_TOKEN_CEILING = 64_000
SOFT_TOKEN_CAP = 56_000
SOFT_CAP_THRESHOLD = 0.90  # 90% of soft cap triggers summarization
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
    timestamp: datetime = field(default_factory=datetime.now)
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

    def xǁTokenBudgetEnforcerǁ__init____mutmut_orig(
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

    def xǁTokenBudgetEnforcerǁ__init____mutmut_1(
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
        self.budget = None
        self._token_counter = token_counter or self._estimate_tokens
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_2(
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
        self.budget = TokenBudget(hard_limit=None, soft_limit=soft_limit)
        self._token_counter = token_counter or self._estimate_tokens
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_3(
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
        self.budget = TokenBudget(hard_limit=hard_limit, soft_limit=None)
        self._token_counter = token_counter or self._estimate_tokens
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_4(
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
        self.budget = TokenBudget(soft_limit=soft_limit)
        self._token_counter = token_counter or self._estimate_tokens
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_5(
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
        self.budget = TokenBudget(hard_limit=hard_limit, )
        self._token_counter = token_counter or self._estimate_tokens
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_6(
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
        self._token_counter = None
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_7(
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
        self._token_counter = token_counter and self._estimate_tokens
        self._summarizer = summarizer

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_8(
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
        self._summarizer = None

        # Content blocks in order
        self._blocks: list[ContentBlock] = []

    def xǁTokenBudgetEnforcerǁ__init____mutmut_9(
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
        self._blocks: list[ContentBlock] = None
    
    xǁTokenBudgetEnforcerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁ__init____mutmut_1': xǁTokenBudgetEnforcerǁ__init____mutmut_1, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_2': xǁTokenBudgetEnforcerǁ__init____mutmut_2, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_3': xǁTokenBudgetEnforcerǁ__init____mutmut_3, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_4': xǁTokenBudgetEnforcerǁ__init____mutmut_4, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_5': xǁTokenBudgetEnforcerǁ__init____mutmut_5, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_6': xǁTokenBudgetEnforcerǁ__init____mutmut_6, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_7': xǁTokenBudgetEnforcerǁ__init____mutmut_7, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_8': xǁTokenBudgetEnforcerǁ__init____mutmut_8, 
        'xǁTokenBudgetEnforcerǁ__init____mutmut_9': xǁTokenBudgetEnforcerǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁ__init____mutmut_orig)
    xǁTokenBudgetEnforcerǁ__init____mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁ__init__'

    def xǁTokenBudgetEnforcerǁcount_tokens__mutmut_orig(self, text: str) -> int:
        """Count tokens in text."""
        return self._token_counter(text)

    def xǁTokenBudgetEnforcerǁcount_tokens__mutmut_1(self, text: str) -> int:
        """Count tokens in text."""
        return self._token_counter(None)
    
    xǁTokenBudgetEnforcerǁcount_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁcount_tokens__mutmut_1': xǁTokenBudgetEnforcerǁcount_tokens__mutmut_1
    }
    
    def count_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁcount_tokens__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁcount_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    count_tokens.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁcount_tokens__mutmut_orig)
    xǁTokenBudgetEnforcerǁcount_tokens__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁcount_tokens'

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_orig(
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_1(
        self,
        content: str,
        priority: ContentPriority = ContentPriority.MEDIUM,
        source: str = "XXXX",
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_2(
        self,
        content: str,
        priority: ContentPriority = ContentPriority.MEDIUM,
        source: str = "",
        can_summarize: bool = False,
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_3(
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
        token_count = None

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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_4(
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
        token_count = self.count_tokens(None)

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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_5(
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
        if self.budget.current_usage - token_count > self.budget.hard_limit:
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_6(
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
        if self.budget.current_usage + token_count >= self.budget.hard_limit:
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_7(
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
            freed = None
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_8(
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
            freed = self._prune_to_fit(None)
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_9(
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
            if freed <= token_count:
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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_10(
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
                return True

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

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_11(
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
        block = None

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_12(
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
            content=None,
            token_count=token_count,
            priority=priority,
            source=source,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_13(
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
            token_count=None,
            priority=priority,
            source=source,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_14(
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
            priority=None,
            source=source,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_15(
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
            source=None,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_16(
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
            can_summarize=None,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_17(
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
            token_count=token_count,
            priority=priority,
            source=source,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_18(
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
            priority=priority,
            source=source,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_19(
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
            source=source,
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_20(
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
            can_summarize=can_summarize,
        )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_21(
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
            )

        self._blocks.append(block)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_22(
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

        self._blocks.append(None)
        self.budget.current_usage += token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_23(
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
        self.budget.current_usage = token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_24(
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
        self.budget.current_usage -= token_count

        return True

    def xǁTokenBudgetEnforcerǁadd_content__mutmut_25(
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

        return False
    
    xǁTokenBudgetEnforcerǁadd_content__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁadd_content__mutmut_1': xǁTokenBudgetEnforcerǁadd_content__mutmut_1, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_2': xǁTokenBudgetEnforcerǁadd_content__mutmut_2, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_3': xǁTokenBudgetEnforcerǁadd_content__mutmut_3, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_4': xǁTokenBudgetEnforcerǁadd_content__mutmut_4, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_5': xǁTokenBudgetEnforcerǁadd_content__mutmut_5, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_6': xǁTokenBudgetEnforcerǁadd_content__mutmut_6, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_7': xǁTokenBudgetEnforcerǁadd_content__mutmut_7, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_8': xǁTokenBudgetEnforcerǁadd_content__mutmut_8, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_9': xǁTokenBudgetEnforcerǁadd_content__mutmut_9, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_10': xǁTokenBudgetEnforcerǁadd_content__mutmut_10, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_11': xǁTokenBudgetEnforcerǁadd_content__mutmut_11, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_12': xǁTokenBudgetEnforcerǁadd_content__mutmut_12, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_13': xǁTokenBudgetEnforcerǁadd_content__mutmut_13, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_14': xǁTokenBudgetEnforcerǁadd_content__mutmut_14, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_15': xǁTokenBudgetEnforcerǁadd_content__mutmut_15, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_16': xǁTokenBudgetEnforcerǁadd_content__mutmut_16, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_17': xǁTokenBudgetEnforcerǁadd_content__mutmut_17, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_18': xǁTokenBudgetEnforcerǁadd_content__mutmut_18, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_19': xǁTokenBudgetEnforcerǁadd_content__mutmut_19, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_20': xǁTokenBudgetEnforcerǁadd_content__mutmut_20, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_21': xǁTokenBudgetEnforcerǁadd_content__mutmut_21, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_22': xǁTokenBudgetEnforcerǁadd_content__mutmut_22, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_23': xǁTokenBudgetEnforcerǁadd_content__mutmut_23, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_24': xǁTokenBudgetEnforcerǁadd_content__mutmut_24, 
        'xǁTokenBudgetEnforcerǁadd_content__mutmut_25': xǁTokenBudgetEnforcerǁadd_content__mutmut_25
    }
    
    def add_content(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁadd_content__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁadd_content__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_content.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁadd_content__mutmut_orig)
    xǁTokenBudgetEnforcerǁadd_content__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁadd_content'

    def xǁTokenBudgetEnforcerǁget_context__mutmut_orig(self, max_tokens: Optional[int] = None) -> str:
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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_1(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = None

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_2(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens and self.budget.soft_limit

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_3(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = None

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_4(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(None, key=lambda b: (b.priority, b.timestamp), reverse=True)

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_5(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(self._blocks, key=None, reverse=True)

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_6(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(self._blocks, key=lambda b: (b.priority, b.timestamp), reverse=None)

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_7(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(key=lambda b: (b.priority, b.timestamp), reverse=True)

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_8(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(self._blocks, reverse=True)

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_9(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(self._blocks, key=lambda b: (b.priority, b.timestamp), )

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_10(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(self._blocks, key=lambda b: None, reverse=True)

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_11(self, max_tokens: Optional[int] = None) -> str:
        """
        Get current context within token budget.

        Args:
            max_tokens: Maximum tokens to return (default: soft limit)

        Returns:
            Combined context string
        """
        limit = max_tokens or self.budget.soft_limit

        # Sort blocks by priority (highest first) for selection
        sorted_blocks = sorted(self._blocks, key=lambda b: (b.priority, b.timestamp), reverse=False)

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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_12(self, max_tokens: Optional[int] = None) -> str:
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

        selected = None
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

    def xǁTokenBudgetEnforcerǁget_context__mutmut_13(self, max_tokens: Optional[int] = None) -> str:
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
        total_tokens = None

        for block in sorted_blocks:
            content = block.get_effective_content()
            tokens = self.count_tokens(content)

            if total_tokens + tokens <= limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_14(self, max_tokens: Optional[int] = None) -> str:
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
        total_tokens = 1

        for block in sorted_blocks:
            content = block.get_effective_content()
            tokens = self.count_tokens(content)

            if total_tokens + tokens <= limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_15(self, max_tokens: Optional[int] = None) -> str:
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
            content = None
            tokens = self.count_tokens(content)

            if total_tokens + tokens <= limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_16(self, max_tokens: Optional[int] = None) -> str:
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
            tokens = None

            if total_tokens + tokens <= limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_17(self, max_tokens: Optional[int] = None) -> str:
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
            tokens = self.count_tokens(None)

            if total_tokens + tokens <= limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_18(self, max_tokens: Optional[int] = None) -> str:
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

            if total_tokens - tokens <= limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_19(self, max_tokens: Optional[int] = None) -> str:
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

            if total_tokens + tokens < limit:
                selected.append((block.timestamp, content))
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_20(self, max_tokens: Optional[int] = None) -> str:
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
                selected.append(None)
                total_tokens += tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_21(self, max_tokens: Optional[int] = None) -> str:
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
                total_tokens = tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_22(self, max_tokens: Optional[int] = None) -> str:
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
                total_tokens -= tokens

        # Sort by timestamp for chronological order
        selected.sort(key=lambda x: x[0])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_23(self, max_tokens: Optional[int] = None) -> str:
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
        selected.sort(key=None)

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_24(self, max_tokens: Optional[int] = None) -> str:
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
        selected.sort(key=lambda x: None)

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_25(self, max_tokens: Optional[int] = None) -> str:
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
        selected.sort(key=lambda x: x[1])

        return "\n".join(content for _, content in selected)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_26(self, max_tokens: Optional[int] = None) -> str:
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

        return "\n".join(None)

    def xǁTokenBudgetEnforcerǁget_context__mutmut_27(self, max_tokens: Optional[int] = None) -> str:
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

        return "XX\nXX".join(content for _, content in selected)
    
    xǁTokenBudgetEnforcerǁget_context__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁget_context__mutmut_1': xǁTokenBudgetEnforcerǁget_context__mutmut_1, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_2': xǁTokenBudgetEnforcerǁget_context__mutmut_2, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_3': xǁTokenBudgetEnforcerǁget_context__mutmut_3, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_4': xǁTokenBudgetEnforcerǁget_context__mutmut_4, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_5': xǁTokenBudgetEnforcerǁget_context__mutmut_5, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_6': xǁTokenBudgetEnforcerǁget_context__mutmut_6, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_7': xǁTokenBudgetEnforcerǁget_context__mutmut_7, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_8': xǁTokenBudgetEnforcerǁget_context__mutmut_8, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_9': xǁTokenBudgetEnforcerǁget_context__mutmut_9, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_10': xǁTokenBudgetEnforcerǁget_context__mutmut_10, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_11': xǁTokenBudgetEnforcerǁget_context__mutmut_11, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_12': xǁTokenBudgetEnforcerǁget_context__mutmut_12, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_13': xǁTokenBudgetEnforcerǁget_context__mutmut_13, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_14': xǁTokenBudgetEnforcerǁget_context__mutmut_14, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_15': xǁTokenBudgetEnforcerǁget_context__mutmut_15, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_16': xǁTokenBudgetEnforcerǁget_context__mutmut_16, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_17': xǁTokenBudgetEnforcerǁget_context__mutmut_17, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_18': xǁTokenBudgetEnforcerǁget_context__mutmut_18, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_19': xǁTokenBudgetEnforcerǁget_context__mutmut_19, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_20': xǁTokenBudgetEnforcerǁget_context__mutmut_20, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_21': xǁTokenBudgetEnforcerǁget_context__mutmut_21, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_22': xǁTokenBudgetEnforcerǁget_context__mutmut_22, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_23': xǁTokenBudgetEnforcerǁget_context__mutmut_23, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_24': xǁTokenBudgetEnforcerǁget_context__mutmut_24, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_25': xǁTokenBudgetEnforcerǁget_context__mutmut_25, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_26': xǁTokenBudgetEnforcerǁget_context__mutmut_26, 
        'xǁTokenBudgetEnforcerǁget_context__mutmut_27': xǁTokenBudgetEnforcerǁget_context__mutmut_27
    }
    
    def get_context(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁget_context__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁget_context__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_context.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁget_context__mutmut_orig)
    xǁTokenBudgetEnforcerǁget_context__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁget_context'

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_orig(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = int(self.budget.soft_limit * 0.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_1(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if self.budget.needs_pruning:
            return 0

        target = int(self.budget.soft_limit * 0.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_2(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 1

        target = int(self.budget.soft_limit * 0.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_3(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = None  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_4(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = int(None)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_5(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = int(self.budget.soft_limit / 0.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_6(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = int(self.budget.soft_limit * 1.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage - target)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_7(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = int(self.budget.soft_limit * 0.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(None)

    def xǁTokenBudgetEnforcerǁenforce_budget__mutmut_8(self) -> int:
        """
        Enforce budget by pruning excess content.

        Returns:
            Number of tokens pruned
        """
        if not self.budget.needs_pruning:
            return 0

        target = int(self.budget.soft_limit * 0.75)  # Prune to 75% of soft cap
        return self._prune_to_fit(self.budget.current_usage + target)
    
    xǁTokenBudgetEnforcerǁenforce_budget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_1': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_1, 
        'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_2': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_2, 
        'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_3': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_3, 
        'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_4': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_4, 
        'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_5': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_5, 
        'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_6': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_6, 
        'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_7': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_7, 
        'xǁTokenBudgetEnforcerǁenforce_budget__mutmut_8': xǁTokenBudgetEnforcerǁenforce_budget__mutmut_8
    }
    
    def enforce_budget(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁenforce_budget__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁenforce_budget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    enforce_budget.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁenforce_budget__mutmut_orig)
    xǁTokenBudgetEnforcerǁenforce_budget__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁenforce_budget'

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_orig(self) -> dict:
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

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_1(self) -> dict:
        """Get current budget status."""
        return {
            "XXcurrent_usageXX": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_2(self) -> dict:
        """Get current budget status."""
        return {
            "CURRENT_USAGE": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_3(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "XXsoft_limitXX": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_4(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "SOFT_LIMIT": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_5(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "XXhard_limitXX": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_6(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "HARD_LIMIT": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_7(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "XXavailableXX": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_8(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "AVAILABLE": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_9(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "XXusage_ratioXX": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_10(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "USAGE_RATIO": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_11(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "XXneeds_pruningXX": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_12(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "NEEDS_PRUNING": self.budget.needs_pruning,
            "block_count": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_13(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "XXblock_countXX": len(self._blocks),
        }

    def xǁTokenBudgetEnforcerǁget_budget_status__mutmut_14(self) -> dict:
        """Get current budget status."""
        return {
            "current_usage": self.budget.current_usage,
            "soft_limit": self.budget.soft_limit,
            "hard_limit": self.budget.hard_limit,
            "available": self.budget.available,
            "usage_ratio": self.budget.usage_ratio,
            "needs_pruning": self.budget.needs_pruning,
            "BLOCK_COUNT": len(self._blocks),
        }
    
    xǁTokenBudgetEnforcerǁget_budget_status__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_1': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_1, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_2': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_2, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_3': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_3, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_4': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_4, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_5': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_5, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_6': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_6, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_7': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_7, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_8': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_8, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_9': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_9, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_10': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_10, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_11': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_11, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_12': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_12, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_13': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_13, 
        'xǁTokenBudgetEnforcerǁget_budget_status__mutmut_14': xǁTokenBudgetEnforcerǁget_budget_status__mutmut_14
    }
    
    def get_budget_status(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁget_budget_status__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁget_budget_status__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_budget_status.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁget_budget_status__mutmut_orig)
    xǁTokenBudgetEnforcerǁget_budget_status__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁget_budget_status'

    def xǁTokenBudgetEnforcerǁclear__mutmut_orig(self):
        """Clear all content and reset budget."""
        self._blocks.clear()
        self.budget.current_usage = 0

    def xǁTokenBudgetEnforcerǁclear__mutmut_1(self):
        """Clear all content and reset budget."""
        self._blocks.clear()
        self.budget.current_usage = None

    def xǁTokenBudgetEnforcerǁclear__mutmut_2(self):
        """Clear all content and reset budget."""
        self._blocks.clear()
        self.budget.current_usage = 1
    
    xǁTokenBudgetEnforcerǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁclear__mutmut_1': xǁTokenBudgetEnforcerǁclear__mutmut_1, 
        'xǁTokenBudgetEnforcerǁclear__mutmut_2': xǁTokenBudgetEnforcerǁclear__mutmut_2
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁclear__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁclear__mutmut_orig)
    xǁTokenBudgetEnforcerǁclear__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁclear'

    def xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_orig(self, text: str) -> int:
        """Estimate token count (approximately 1 token per 4 characters)."""
        return len(text) // 4 + 1

    def xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_1(self, text: str) -> int:
        """Estimate token count (approximately 1 token per 4 characters)."""
        return len(text) // 4 - 1

    def xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_2(self, text: str) -> int:
        """Estimate token count (approximately 1 token per 4 characters)."""
        return len(text) / 4 + 1

    def xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_3(self, text: str) -> int:
        """Estimate token count (approximately 1 token per 4 characters)."""
        return len(text) // 5 + 1

    def xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_4(self, text: str) -> int:
        """Estimate token count (approximately 1 token per 4 characters)."""
        return len(text) // 4 + 2
    
    xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_1': xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_1, 
        'xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_2': xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_2, 
        'xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_3': xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_3, 
        'xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_4': xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_4
    }
    
    def _estimate_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _estimate_tokens.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_orig)
    xǁTokenBudgetEnforcerǁ_estimate_tokens__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁ_estimate_tokens'

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_orig(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_1(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed < 0:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_2(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 1:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_3(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 1

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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_4(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = None
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_5(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(None) if b.priority < ContentPriority.CRITICAL
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_6(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority <= ContentPriority.CRITICAL
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_7(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=None)

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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_8(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=lambda x: None)

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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_9(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=lambda x: (x[2].priority, x[1].timestamp))

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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_10(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=lambda x: (x[1].priority, x[2].timestamp))

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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_11(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=lambda x: (x[1].priority, x[1].timestamp))

        freed = None
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_12(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=lambda x: (x[1].priority, x[1].timestamp))

        freed = 1
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_13(self, tokens_needed: int) -> int:
        """Prune low-priority content to free tokens."""
        if tokens_needed <= 0:
            return 0

        # Sort by priority (lowest first) for pruning
        prunable = [
            (i, b) for i, b in enumerate(self._blocks) if b.priority < ContentPriority.CRITICAL
        ]
        prunable.sort(key=lambda x: (x[1].priority, x[1].timestamp))

        freed = 0
        to_remove = None

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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_14(self, tokens_needed: int) -> int:
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
            if freed > tokens_needed:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_15(self, tokens_needed: int) -> int:
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
                return

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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_16(self, tokens_needed: int) -> int:
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
            if block.can_summarize and self._summarizer or not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    summary_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_17(self, tokens_needed: int) -> int:
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
            if block.can_summarize or self._summarizer and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    summary_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_18(self, tokens_needed: int) -> int:
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
            if block.can_summarize and self._summarizer and block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    summary_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_19(self, tokens_needed: int) -> int:
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
                    block.summary = None
                    summary_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_20(self, tokens_needed: int) -> int:
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
                    block.summary = self._summarizer(None)
                    summary_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_21(self, tokens_needed: int) -> int:
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
                    summary_tokens = None
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_22(self, tokens_needed: int) -> int:
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
                    summary_tokens = self.count_tokens(None)
                    saved = block.token_count - summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_23(self, tokens_needed: int) -> int:
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
                    saved = None
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_24(self, tokens_needed: int) -> int:
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
                    saved = block.token_count + summary_tokens
                    if saved > 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_25(self, tokens_needed: int) -> int:
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
                    if saved >= 0:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_26(self, tokens_needed: int) -> int:
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
                    if saved > 1:
                        freed += saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_27(self, tokens_needed: int) -> int:
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
                        freed = saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_28(self, tokens_needed: int) -> int:
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
                        freed -= saved
                        self.budget.current_usage -= saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_29(self, tokens_needed: int) -> int:
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
                        self.budget.current_usage = saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_30(self, tokens_needed: int) -> int:
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
                        self.budget.current_usage += saved
                        block.token_count = summary_tokens
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_31(self, tokens_needed: int) -> int:
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
                        block.token_count = None
                        continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_32(self, tokens_needed: int) -> int:
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
                        break
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_33(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(None)
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_34(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(None, exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_35(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=None)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_36(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_37(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", )

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_38(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=False)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_39(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(None)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_40(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed = block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_41(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed -= block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_42(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(None):
            block = self._blocks.pop(idx)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_43(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = None
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_44(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(None)
            self.budget.current_usage -= block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_45(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage = block.token_count

        return freed

    def xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_46(self, tokens_needed: int) -> int:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

            # Remove block
            to_remove.append(idx)
            freed += block.token_count

        # Remove blocks in reverse order to maintain indices
        for idx in reversed(to_remove):
            block = self._blocks.pop(idx)
            self.budget.current_usage += block.token_count

        return freed
    
    xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_1': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_1, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_2': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_2, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_3': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_3, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_4': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_4, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_5': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_5, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_6': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_6, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_7': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_7, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_8': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_8, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_9': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_9, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_10': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_10, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_11': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_11, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_12': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_12, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_13': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_13, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_14': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_14, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_15': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_15, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_16': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_16, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_17': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_17, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_18': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_18, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_19': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_19, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_20': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_20, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_21': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_21, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_22': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_22, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_23': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_23, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_24': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_24, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_25': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_25, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_26': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_26, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_27': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_27, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_28': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_28, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_29': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_29, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_30': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_30, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_31': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_31, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_32': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_32, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_33': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_33, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_34': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_34, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_35': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_35, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_36': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_36, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_37': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_37, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_38': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_38, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_39': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_39, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_40': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_40, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_41': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_41, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_42': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_42, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_43': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_43, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_44': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_44, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_45': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_45, 
        'xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_46': xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_46
    }
    
    def _prune_to_fit(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _prune_to_fit.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_orig)
    xǁTokenBudgetEnforcerǁ_prune_to_fit__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁ_prune_to_fit'

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_orig(self):
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_1(self):
        """Summarize low-priority blocks to save space."""
        if self._summarizer:
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_2(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize or not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_3(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW or block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_4(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority < ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_5(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_6(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = None
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_7(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(None)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_8(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = None
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_9(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(None)
                    saved = block.token_count - new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_10(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = None
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_11(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count + new_tokens
                    if saved > 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_12(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved >= 0:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_13(self):
        """Summarize low-priority blocks to save space."""
        if not self._summarizer:
            return

        for block in self._blocks:
            if block.priority <= ContentPriority.LOW and block.can_summarize and not block.summary:
                try:
                    block.summary = self._summarizer(block.content)
                    new_tokens = self.count_tokens(block.summary)
                    saved = block.token_count - new_tokens
                    if saved > 1:
                        self.budget.current_usage -= saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_14(self):
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
                        self.budget.current_usage = saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_15(self):
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
                        self.budget.current_usage += saved
                        block.token_count = new_tokens
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_16(self):
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
                        block.token_count = None
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_17(self):
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
                except Exception as e:
                    logger.debug(None)
                    logger.warning(f"Exception: {e}", exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_18(self):
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(None, exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_19(self):
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=None)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_20(self):
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(exc_info=True)

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_21(self):
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", )

    def xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_22(self):
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
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Exception: {e}", exc_info=False)
    
    xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_1': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_1, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_2': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_2, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_3': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_3, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_4': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_4, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_5': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_5, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_6': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_6, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_7': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_7, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_8': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_8, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_9': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_9, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_10': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_10, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_11': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_11, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_12': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_12, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_13': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_13, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_14': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_14, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_15': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_15, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_16': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_16, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_17': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_17, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_18': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_18, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_19': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_19, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_20': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_20, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_21': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_21, 
        'xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_22': xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_22
    }
    
    def _summarize_low_priority(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_orig"), object.__getattribute__(self, "xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _summarize_low_priority.__signature__ = _mutmut_signature(xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_orig)
    xǁTokenBudgetEnforcerǁ_summarize_low_priority__mutmut_orig.__name__ = 'xǁTokenBudgetEnforcerǁ_summarize_low_priority'
