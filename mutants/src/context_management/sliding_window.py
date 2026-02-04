"""
Sliding Window Manager

Manages token windows for context management, implementing
sliding window strategy with summarization triggers.
"""

from typing import Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0
    entry_type: str = "content"
    metadata: dict = field(default_factory=dict)

    @property
    def age_seconds(self) -> float:
        """Age of entry in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()


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

    def xǁSlidingWindowManagerǁ__init____mutmut_orig(
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

    def xǁSlidingWindowManagerǁ__init____mutmut_1(
        self,
        max_tokens: int = SOFT_CAP,
        strategy: WindowStrategy = WindowStrategy.DROP_OLDEST,
        summarizer: Optional[Callable[[list[str]], str]] = None,
        reserve_tokens: int = 8001,
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

    def xǁSlidingWindowManagerǁ__init____mutmut_2(
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
        self.max_tokens = None
        self.strategy = strategy
        self.summarizer = summarizer
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_3(
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
        self.max_tokens = min(None, self.HARD_CEILING)
        self.strategy = strategy
        self.summarizer = summarizer
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_4(
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
        self.max_tokens = min(max_tokens, None)
        self.strategy = strategy
        self.summarizer = summarizer
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_5(
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
        self.max_tokens = min(self.HARD_CEILING)
        self.strategy = strategy
        self.summarizer = summarizer
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_6(
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
        self.max_tokens = min(max_tokens, )
        self.strategy = strategy
        self.summarizer = summarizer
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_7(
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
        self.strategy = None
        self.summarizer = summarizer
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_8(
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
        self.summarizer = None
        self.reserve_tokens = reserve_tokens

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_9(
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
        self.reserve_tokens = None

        self._entries: list[WindowEntry] = []
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_10(
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

        self._entries: list[WindowEntry] = None
        self._total_tokens = 0
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_11(
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
        self._total_tokens = None
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_12(
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
        self._total_tokens = 1
        self._summary: Optional[str] = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_13(
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
        self._summary: Optional[str] = ""
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁ__init____mutmut_14(
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
        self._summary_tokens = None

    def xǁSlidingWindowManagerǁ__init____mutmut_15(
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
        self._summary_tokens = 1
    
    xǁSlidingWindowManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁ__init____mutmut_1': xǁSlidingWindowManagerǁ__init____mutmut_1, 
        'xǁSlidingWindowManagerǁ__init____mutmut_2': xǁSlidingWindowManagerǁ__init____mutmut_2, 
        'xǁSlidingWindowManagerǁ__init____mutmut_3': xǁSlidingWindowManagerǁ__init____mutmut_3, 
        'xǁSlidingWindowManagerǁ__init____mutmut_4': xǁSlidingWindowManagerǁ__init____mutmut_4, 
        'xǁSlidingWindowManagerǁ__init____mutmut_5': xǁSlidingWindowManagerǁ__init____mutmut_5, 
        'xǁSlidingWindowManagerǁ__init____mutmut_6': xǁSlidingWindowManagerǁ__init____mutmut_6, 
        'xǁSlidingWindowManagerǁ__init____mutmut_7': xǁSlidingWindowManagerǁ__init____mutmut_7, 
        'xǁSlidingWindowManagerǁ__init____mutmut_8': xǁSlidingWindowManagerǁ__init____mutmut_8, 
        'xǁSlidingWindowManagerǁ__init____mutmut_9': xǁSlidingWindowManagerǁ__init____mutmut_9, 
        'xǁSlidingWindowManagerǁ__init____mutmut_10': xǁSlidingWindowManagerǁ__init____mutmut_10, 
        'xǁSlidingWindowManagerǁ__init____mutmut_11': xǁSlidingWindowManagerǁ__init____mutmut_11, 
        'xǁSlidingWindowManagerǁ__init____mutmut_12': xǁSlidingWindowManagerǁ__init____mutmut_12, 
        'xǁSlidingWindowManagerǁ__init____mutmut_13': xǁSlidingWindowManagerǁ__init____mutmut_13, 
        'xǁSlidingWindowManagerǁ__init____mutmut_14': xǁSlidingWindowManagerǁ__init____mutmut_14, 
        'xǁSlidingWindowManagerǁ__init____mutmut_15': xǁSlidingWindowManagerǁ__init____mutmut_15
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁ__init____mutmut_orig)
    xǁSlidingWindowManagerǁ__init____mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁ__init__'

    def xǁSlidingWindowManagerǁadd__mutmut_orig(
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

    def xǁSlidingWindowManagerǁadd__mutmut_1(
        self,
        content: str,
        priority: int = 1,
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

    def xǁSlidingWindowManagerǁadd__mutmut_2(
        self,
        content: str,
        priority: int = 0,
        entry_type: str = "XXcontentXX",
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

    def xǁSlidingWindowManagerǁadd__mutmut_3(
        self,
        content: str,
        priority: int = 0,
        entry_type: str = "CONTENT",
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

    def xǁSlidingWindowManagerǁadd__mutmut_4(
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
        token_count = None

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

    def xǁSlidingWindowManagerǁadd__mutmut_5(
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
        token_count = self._estimate_tokens(None)

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

    def xǁSlidingWindowManagerǁadd__mutmut_6(
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
        warning = ""
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

    def xǁSlidingWindowManagerǁadd__mutmut_7(
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
        if self._total_tokens - token_count > self.max_tokens:
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

    def xǁSlidingWindowManagerǁadd__mutmut_8(
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
        if self._total_tokens + token_count >= self.max_tokens:
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

    def xǁSlidingWindowManagerǁadd__mutmut_9(
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
            warning = None

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

    def xǁSlidingWindowManagerǁadd__mutmut_10(
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
            warning = self._make_room(None)

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

    def xǁSlidingWindowManagerǁadd__mutmut_11(
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
        if self._total_tokens - token_count > self.max_tokens:
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

    def xǁSlidingWindowManagerǁadd__mutmut_12(
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
        if self._total_tokens + token_count >= self.max_tokens:
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

    def xǁSlidingWindowManagerǁadd__mutmut_13(
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
            return True, "Unable to add content: window at capacity"

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

    def xǁSlidingWindowManagerǁadd__mutmut_14(
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
            return False, "XXUnable to add content: window at capacityXX"

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

    def xǁSlidingWindowManagerǁadd__mutmut_15(
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
            return False, "unable to add content: window at capacity"

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

    def xǁSlidingWindowManagerǁadd__mutmut_16(
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
            return False, "UNABLE TO ADD CONTENT: WINDOW AT CAPACITY"

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

    def xǁSlidingWindowManagerǁadd__mutmut_17(
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

        entry = None

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_18(
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
            content=None,
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

    def xǁSlidingWindowManagerǁadd__mutmut_19(
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
            token_count=None,
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

    def xǁSlidingWindowManagerǁadd__mutmut_20(
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
            priority=None,
            entry_type=entry_type,
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_21(
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
            entry_type=None,
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_22(
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
            metadata=None,
        )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_23(
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

    def xǁSlidingWindowManagerǁadd__mutmut_24(
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

    def xǁSlidingWindowManagerǁadd__mutmut_25(
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
            entry_type=entry_type,
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_26(
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
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_27(
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
            )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_28(
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
            metadata=metadata and {},
        )

        self._entries.append(entry)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_29(
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

        self._entries.append(None)
        self._total_tokens += token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_30(
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
        self._total_tokens = token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_31(
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
        self._total_tokens -= token_count

        # Check if summarization needed
        if self._should_summarize():
            self._trigger_summarization()

        return True, warning

    def xǁSlidingWindowManagerǁadd__mutmut_32(
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

        return False, warning
    
    xǁSlidingWindowManagerǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁadd__mutmut_1': xǁSlidingWindowManagerǁadd__mutmut_1, 
        'xǁSlidingWindowManagerǁadd__mutmut_2': xǁSlidingWindowManagerǁadd__mutmut_2, 
        'xǁSlidingWindowManagerǁadd__mutmut_3': xǁSlidingWindowManagerǁadd__mutmut_3, 
        'xǁSlidingWindowManagerǁadd__mutmut_4': xǁSlidingWindowManagerǁadd__mutmut_4, 
        'xǁSlidingWindowManagerǁadd__mutmut_5': xǁSlidingWindowManagerǁadd__mutmut_5, 
        'xǁSlidingWindowManagerǁadd__mutmut_6': xǁSlidingWindowManagerǁadd__mutmut_6, 
        'xǁSlidingWindowManagerǁadd__mutmut_7': xǁSlidingWindowManagerǁadd__mutmut_7, 
        'xǁSlidingWindowManagerǁadd__mutmut_8': xǁSlidingWindowManagerǁadd__mutmut_8, 
        'xǁSlidingWindowManagerǁadd__mutmut_9': xǁSlidingWindowManagerǁadd__mutmut_9, 
        'xǁSlidingWindowManagerǁadd__mutmut_10': xǁSlidingWindowManagerǁadd__mutmut_10, 
        'xǁSlidingWindowManagerǁadd__mutmut_11': xǁSlidingWindowManagerǁadd__mutmut_11, 
        'xǁSlidingWindowManagerǁadd__mutmut_12': xǁSlidingWindowManagerǁadd__mutmut_12, 
        'xǁSlidingWindowManagerǁadd__mutmut_13': xǁSlidingWindowManagerǁadd__mutmut_13, 
        'xǁSlidingWindowManagerǁadd__mutmut_14': xǁSlidingWindowManagerǁadd__mutmut_14, 
        'xǁSlidingWindowManagerǁadd__mutmut_15': xǁSlidingWindowManagerǁadd__mutmut_15, 
        'xǁSlidingWindowManagerǁadd__mutmut_16': xǁSlidingWindowManagerǁadd__mutmut_16, 
        'xǁSlidingWindowManagerǁadd__mutmut_17': xǁSlidingWindowManagerǁadd__mutmut_17, 
        'xǁSlidingWindowManagerǁadd__mutmut_18': xǁSlidingWindowManagerǁadd__mutmut_18, 
        'xǁSlidingWindowManagerǁadd__mutmut_19': xǁSlidingWindowManagerǁadd__mutmut_19, 
        'xǁSlidingWindowManagerǁadd__mutmut_20': xǁSlidingWindowManagerǁadd__mutmut_20, 
        'xǁSlidingWindowManagerǁadd__mutmut_21': xǁSlidingWindowManagerǁadd__mutmut_21, 
        'xǁSlidingWindowManagerǁadd__mutmut_22': xǁSlidingWindowManagerǁadd__mutmut_22, 
        'xǁSlidingWindowManagerǁadd__mutmut_23': xǁSlidingWindowManagerǁadd__mutmut_23, 
        'xǁSlidingWindowManagerǁadd__mutmut_24': xǁSlidingWindowManagerǁadd__mutmut_24, 
        'xǁSlidingWindowManagerǁadd__mutmut_25': xǁSlidingWindowManagerǁadd__mutmut_25, 
        'xǁSlidingWindowManagerǁadd__mutmut_26': xǁSlidingWindowManagerǁadd__mutmut_26, 
        'xǁSlidingWindowManagerǁadd__mutmut_27': xǁSlidingWindowManagerǁadd__mutmut_27, 
        'xǁSlidingWindowManagerǁadd__mutmut_28': xǁSlidingWindowManagerǁadd__mutmut_28, 
        'xǁSlidingWindowManagerǁadd__mutmut_29': xǁSlidingWindowManagerǁadd__mutmut_29, 
        'xǁSlidingWindowManagerǁadd__mutmut_30': xǁSlidingWindowManagerǁadd__mutmut_30, 
        'xǁSlidingWindowManagerǁadd__mutmut_31': xǁSlidingWindowManagerǁadd__mutmut_31, 
        'xǁSlidingWindowManagerǁadd__mutmut_32': xǁSlidingWindowManagerǁadd__mutmut_32
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁadd__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁadd__mutmut_orig)
    xǁSlidingWindowManagerǁadd__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁadd'

    def xǁSlidingWindowManagerǁget_window__mutmut_orig(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_1(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is not None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_2(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = None
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_3(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = None
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_4(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 1
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_5(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(None):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_6(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens - entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_7(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count < max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_8(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(None, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_9(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, None)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_10(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_11(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, )
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_12(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(1, entry.content)
                tokens += entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_13(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens = entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_14(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens -= entry.token_count
            else:
                break
        return result

    def xǁSlidingWindowManagerǁget_window__mutmut_15(self, max_tokens: Optional[int] = None) -> list[str]:
        """
        Get current window contents.

        Args:
            max_tokens: Optional limit on returned tokens

        Returns:
            list of content strings
        """
        if max_tokens is None:
            return [e.content for e in self._entries]

        result = []
        tokens = 0
        for entry in reversed(self._entries):  # Newest first
            if tokens + entry.token_count <= max_tokens:
                result.insert(0, entry.content)
                tokens += entry.token_count
            else:
                return
        return result
    
    xǁSlidingWindowManagerǁget_window__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁget_window__mutmut_1': xǁSlidingWindowManagerǁget_window__mutmut_1, 
        'xǁSlidingWindowManagerǁget_window__mutmut_2': xǁSlidingWindowManagerǁget_window__mutmut_2, 
        'xǁSlidingWindowManagerǁget_window__mutmut_3': xǁSlidingWindowManagerǁget_window__mutmut_3, 
        'xǁSlidingWindowManagerǁget_window__mutmut_4': xǁSlidingWindowManagerǁget_window__mutmut_4, 
        'xǁSlidingWindowManagerǁget_window__mutmut_5': xǁSlidingWindowManagerǁget_window__mutmut_5, 
        'xǁSlidingWindowManagerǁget_window__mutmut_6': xǁSlidingWindowManagerǁget_window__mutmut_6, 
        'xǁSlidingWindowManagerǁget_window__mutmut_7': xǁSlidingWindowManagerǁget_window__mutmut_7, 
        'xǁSlidingWindowManagerǁget_window__mutmut_8': xǁSlidingWindowManagerǁget_window__mutmut_8, 
        'xǁSlidingWindowManagerǁget_window__mutmut_9': xǁSlidingWindowManagerǁget_window__mutmut_9, 
        'xǁSlidingWindowManagerǁget_window__mutmut_10': xǁSlidingWindowManagerǁget_window__mutmut_10, 
        'xǁSlidingWindowManagerǁget_window__mutmut_11': xǁSlidingWindowManagerǁget_window__mutmut_11, 
        'xǁSlidingWindowManagerǁget_window__mutmut_12': xǁSlidingWindowManagerǁget_window__mutmut_12, 
        'xǁSlidingWindowManagerǁget_window__mutmut_13': xǁSlidingWindowManagerǁget_window__mutmut_13, 
        'xǁSlidingWindowManagerǁget_window__mutmut_14': xǁSlidingWindowManagerǁget_window__mutmut_14, 
        'xǁSlidingWindowManagerǁget_window__mutmut_15': xǁSlidingWindowManagerǁget_window__mutmut_15
    }
    
    def get_window(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁget_window__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁget_window__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_window.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁget_window__mutmut_orig)
    xǁSlidingWindowManagerǁget_window__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁget_window'

    def get_window_with_summary(self) -> tuple[Optional[str], list[str]]:
        """
        Get window with summary of pruned content.

        Returns:
            tuple of (summary, current_entries)
        """
        return self._summary, [e.content for e in self._entries]

    def xǁSlidingWindowManagerǁget_state__mutmut_orig(self) -> WindowState:
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

    def xǁSlidingWindowManagerǁget_state__mutmut_1(self) -> WindowState:
        """Get current window state."""
        oldest_age = None
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

    def xǁSlidingWindowManagerǁget_state__mutmut_2(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[1].age_seconds if self._entries else 0
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

    def xǁSlidingWindowManagerǁget_state__mutmut_3(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 1
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

    def xǁSlidingWindowManagerǁget_state__mutmut_4(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = None
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

    def xǁSlidingWindowManagerǁget_state__mutmut_5(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[+1].age_seconds if self._entries else 0
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

    def xǁSlidingWindowManagerǁget_state__mutmut_6(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-2].age_seconds if self._entries else 0
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

    def xǁSlidingWindowManagerǁget_state__mutmut_7(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 1
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

    def xǁSlidingWindowManagerǁget_state__mutmut_8(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = None

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_9(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens / 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_10(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens * self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_11(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 101) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_12(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens >= 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_13(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 1 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_14(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 1

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_15(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=None,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_16(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=None,
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_17(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=None,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_18(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=None,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_19(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=None,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_20(self) -> WindowState:
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
            needs_pruning=None,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_21(self) -> WindowState:
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
            summary_available=None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_22(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_23(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_24(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            newest_age_seconds=newest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_25(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            utilization_percent=utilization,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_26(self) -> WindowState:
        """Get current window state."""
        oldest_age = self._entries[0].age_seconds if self._entries else 0
        newest_age = self._entries[-1].age_seconds if self._entries else 0
        utilization = (self._total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0

        return WindowState(
            total_tokens=self._total_tokens,
            entry_count=len(self._entries),
            oldest_age_seconds=oldest_age,
            newest_age_seconds=newest_age,
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_27(self) -> WindowState:
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
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_28(self) -> WindowState:
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
            )

    def xǁSlidingWindowManagerǁget_state__mutmut_29(self) -> WindowState:
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
            needs_pruning=utilization > self.SUMMARIZATION_THRESHOLD * 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_30(self) -> WindowState:
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
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD / 100,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_31(self) -> WindowState:
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
            needs_pruning=utilization >= self.SUMMARIZATION_THRESHOLD * 101,
            summary_available=self._summary is not None,
        )

    def xǁSlidingWindowManagerǁget_state__mutmut_32(self) -> WindowState:
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
            summary_available=self._summary is None,
        )
    
    xǁSlidingWindowManagerǁget_state__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁget_state__mutmut_1': xǁSlidingWindowManagerǁget_state__mutmut_1, 
        'xǁSlidingWindowManagerǁget_state__mutmut_2': xǁSlidingWindowManagerǁget_state__mutmut_2, 
        'xǁSlidingWindowManagerǁget_state__mutmut_3': xǁSlidingWindowManagerǁget_state__mutmut_3, 
        'xǁSlidingWindowManagerǁget_state__mutmut_4': xǁSlidingWindowManagerǁget_state__mutmut_4, 
        'xǁSlidingWindowManagerǁget_state__mutmut_5': xǁSlidingWindowManagerǁget_state__mutmut_5, 
        'xǁSlidingWindowManagerǁget_state__mutmut_6': xǁSlidingWindowManagerǁget_state__mutmut_6, 
        'xǁSlidingWindowManagerǁget_state__mutmut_7': xǁSlidingWindowManagerǁget_state__mutmut_7, 
        'xǁSlidingWindowManagerǁget_state__mutmut_8': xǁSlidingWindowManagerǁget_state__mutmut_8, 
        'xǁSlidingWindowManagerǁget_state__mutmut_9': xǁSlidingWindowManagerǁget_state__mutmut_9, 
        'xǁSlidingWindowManagerǁget_state__mutmut_10': xǁSlidingWindowManagerǁget_state__mutmut_10, 
        'xǁSlidingWindowManagerǁget_state__mutmut_11': xǁSlidingWindowManagerǁget_state__mutmut_11, 
        'xǁSlidingWindowManagerǁget_state__mutmut_12': xǁSlidingWindowManagerǁget_state__mutmut_12, 
        'xǁSlidingWindowManagerǁget_state__mutmut_13': xǁSlidingWindowManagerǁget_state__mutmut_13, 
        'xǁSlidingWindowManagerǁget_state__mutmut_14': xǁSlidingWindowManagerǁget_state__mutmut_14, 
        'xǁSlidingWindowManagerǁget_state__mutmut_15': xǁSlidingWindowManagerǁget_state__mutmut_15, 
        'xǁSlidingWindowManagerǁget_state__mutmut_16': xǁSlidingWindowManagerǁget_state__mutmut_16, 
        'xǁSlidingWindowManagerǁget_state__mutmut_17': xǁSlidingWindowManagerǁget_state__mutmut_17, 
        'xǁSlidingWindowManagerǁget_state__mutmut_18': xǁSlidingWindowManagerǁget_state__mutmut_18, 
        'xǁSlidingWindowManagerǁget_state__mutmut_19': xǁSlidingWindowManagerǁget_state__mutmut_19, 
        'xǁSlidingWindowManagerǁget_state__mutmut_20': xǁSlidingWindowManagerǁget_state__mutmut_20, 
        'xǁSlidingWindowManagerǁget_state__mutmut_21': xǁSlidingWindowManagerǁget_state__mutmut_21, 
        'xǁSlidingWindowManagerǁget_state__mutmut_22': xǁSlidingWindowManagerǁget_state__mutmut_22, 
        'xǁSlidingWindowManagerǁget_state__mutmut_23': xǁSlidingWindowManagerǁget_state__mutmut_23, 
        'xǁSlidingWindowManagerǁget_state__mutmut_24': xǁSlidingWindowManagerǁget_state__mutmut_24, 
        'xǁSlidingWindowManagerǁget_state__mutmut_25': xǁSlidingWindowManagerǁget_state__mutmut_25, 
        'xǁSlidingWindowManagerǁget_state__mutmut_26': xǁSlidingWindowManagerǁget_state__mutmut_26, 
        'xǁSlidingWindowManagerǁget_state__mutmut_27': xǁSlidingWindowManagerǁget_state__mutmut_27, 
        'xǁSlidingWindowManagerǁget_state__mutmut_28': xǁSlidingWindowManagerǁget_state__mutmut_28, 
        'xǁSlidingWindowManagerǁget_state__mutmut_29': xǁSlidingWindowManagerǁget_state__mutmut_29, 
        'xǁSlidingWindowManagerǁget_state__mutmut_30': xǁSlidingWindowManagerǁget_state__mutmut_30, 
        'xǁSlidingWindowManagerǁget_state__mutmut_31': xǁSlidingWindowManagerǁget_state__mutmut_31, 
        'xǁSlidingWindowManagerǁget_state__mutmut_32': xǁSlidingWindowManagerǁget_state__mutmut_32
    }
    
    def get_state(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁget_state__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁget_state__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_state.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁget_state__mutmut_orig)
    xǁSlidingWindowManagerǁget_state__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁget_state'

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_orig(self, target_tokens: int) -> list[WindowEntry]:
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

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_1(self, target_tokens: int) -> list[WindowEntry]:
        """
        Prune window to target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned entries
        """
        pruned = None

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

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_2(self, target_tokens: int) -> list[WindowEntry]:
        """
        Prune window to target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned entries
        """
        pruned = []

        while self._total_tokens > target_tokens or self._entries:
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

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_3(self, target_tokens: int) -> list[WindowEntry]:
        """
        Prune window to target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned entries
        """
        pruned = []

        while self._total_tokens >= target_tokens and self._entries:
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

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_4(self, target_tokens: int) -> list[WindowEntry]:
        """
        Prune window to target token count.

        Args:
            target_tokens: Target maximum tokens

        Returns:
            list of pruned entries
        """
        pruned = []

        while self._total_tokens > target_tokens and self._entries:
            if self.strategy != WindowStrategy.DROP_OLDEST:
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

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_5(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = None
            elif self.strategy == WindowStrategy.PRIORITY_PRUNE:
                # Find lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_6(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = self._entries.pop(None)
            elif self.strategy == WindowStrategy.PRIORITY_PRUNE:
                # Find lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_7(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = self._entries.pop(1)
            elif self.strategy == WindowStrategy.PRIORITY_PRUNE:
                # Find lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_8(self, target_tokens: int) -> list[WindowEntry]:
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
            elif self.strategy != WindowStrategy.PRIORITY_PRUNE:
                # Find lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_9(self, target_tokens: int) -> list[WindowEntry]:
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
                min_idx = None
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_10(self, target_tokens: int) -> list[WindowEntry]:
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
                min_idx = min(None, key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_11(self, target_tokens: int) -> list[WindowEntry]:
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
                min_idx = min(range(len(self._entries)), key=None)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_12(self, target_tokens: int) -> list[WindowEntry]:
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
                min_idx = min(key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_13(self, target_tokens: int) -> list[WindowEntry]:
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
                min_idx = min(range(len(self._entries)), )
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_14(self, target_tokens: int) -> list[WindowEntry]:
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
                min_idx = min(range(None), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_15(self, target_tokens: int) -> list[WindowEntry]:
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
                min_idx = min(range(len(self._entries)), key=lambda i: None)
                entry = self._entries.pop(min_idx)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_16(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = None
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_17(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = self._entries.pop(None)
            else:
                entry = self._entries.pop(0)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_18(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = None

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_19(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = self._entries.pop(None)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_20(self, target_tokens: int) -> list[WindowEntry]:
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
                entry = self._entries.pop(1)

            self._total_tokens -= entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_21(self, target_tokens: int) -> list[WindowEntry]:
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

            self._total_tokens = entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_22(self, target_tokens: int) -> list[WindowEntry]:
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

            self._total_tokens += entry.token_count
            pruned.append(entry)

        return pruned

    def xǁSlidingWindowManagerǁprune_to_tokens__mutmut_23(self, target_tokens: int) -> list[WindowEntry]:
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
            pruned.append(None)

        return pruned
    
    xǁSlidingWindowManagerǁprune_to_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_1': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_1, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_2': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_2, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_3': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_3, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_4': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_4, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_5': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_5, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_6': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_6, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_7': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_7, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_8': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_8, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_9': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_9, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_10': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_10, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_11': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_11, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_12': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_12, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_13': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_13, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_14': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_14, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_15': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_15, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_16': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_16, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_17': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_17, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_18': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_18, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_19': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_19, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_20': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_20, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_21': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_21, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_22': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_22, 
        'xǁSlidingWindowManagerǁprune_to_tokens__mutmut_23': xǁSlidingWindowManagerǁprune_to_tokens__mutmut_23
    }
    
    def prune_to_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁprune_to_tokens__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁprune_to_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    prune_to_tokens.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁprune_to_tokens__mutmut_orig)
    xǁSlidingWindowManagerǁprune_to_tokens__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁprune_to_tokens'

    def xǁSlidingWindowManagerǁslide__mutmut_orig(self, keep_tokens: int) -> list[WindowEntry]:
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

    def xǁSlidingWindowManagerǁslide__mutmut_1(self, keep_tokens: int) -> list[WindowEntry]:
        """
        Slide window to keep only most recent tokens.

        Args:
            keep_tokens: Number of tokens to keep

        Returns:
            list of removed entries
        """
        removed = None

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

    def xǁSlidingWindowManagerǁslide__mutmut_2(self, keep_tokens: int) -> list[WindowEntry]:
        """
        Slide window to keep only most recent tokens.

        Args:
            keep_tokens: Number of tokens to keep

        Returns:
            list of removed entries
        """
        removed = []

        while self._total_tokens > keep_tokens or self._entries:
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

    def xǁSlidingWindowManagerǁslide__mutmut_3(self, keep_tokens: int) -> list[WindowEntry]:
        """
        Slide window to keep only most recent tokens.

        Args:
            keep_tokens: Number of tokens to keep

        Returns:
            list of removed entries
        """
        removed = []

        while self._total_tokens >= keep_tokens and self._entries:
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

    def xǁSlidingWindowManagerǁslide__mutmut_4(self, keep_tokens: int) -> list[WindowEntry]:
        """
        Slide window to keep only most recent tokens.

        Args:
            keep_tokens: Number of tokens to keep

        Returns:
            list of removed entries
        """
        removed = []

        while self._total_tokens > keep_tokens and self._entries:
            entry = None
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

    def xǁSlidingWindowManagerǁslide__mutmut_5(self, keep_tokens: int) -> list[WindowEntry]:
        """
        Slide window to keep only most recent tokens.

        Args:
            keep_tokens: Number of tokens to keep

        Returns:
            list of removed entries
        """
        removed = []

        while self._total_tokens > keep_tokens and self._entries:
            entry = self._entries.pop(None)
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

    def xǁSlidingWindowManagerǁslide__mutmut_6(self, keep_tokens: int) -> list[WindowEntry]:
        """
        Slide window to keep only most recent tokens.

        Args:
            keep_tokens: Number of tokens to keep

        Returns:
            list of removed entries
        """
        removed = []

        while self._total_tokens > keep_tokens and self._entries:
            entry = self._entries.pop(1)
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

    def xǁSlidingWindowManagerǁslide__mutmut_7(self, keep_tokens: int) -> list[WindowEntry]:
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
            self._total_tokens = entry.token_count
            removed.append(entry)

        # Update summary with removed content
        if removed and self.summarizer:
            removed_text = [e.content for e in removed]
            if self._summary:
                removed_text.insert(0, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_8(self, keep_tokens: int) -> list[WindowEntry]:
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
            self._total_tokens += entry.token_count
            removed.append(entry)

        # Update summary with removed content
        if removed and self.summarizer:
            removed_text = [e.content for e in removed]
            if self._summary:
                removed_text.insert(0, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_9(self, keep_tokens: int) -> list[WindowEntry]:
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
            removed.append(None)

        # Update summary with removed content
        if removed and self.summarizer:
            removed_text = [e.content for e in removed]
            if self._summary:
                removed_text.insert(0, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_10(self, keep_tokens: int) -> list[WindowEntry]:
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
        if removed or self.summarizer:
            removed_text = [e.content for e in removed]
            if self._summary:
                removed_text.insert(0, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_11(self, keep_tokens: int) -> list[WindowEntry]:
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
            removed_text = None
            if self._summary:
                removed_text.insert(0, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_12(self, keep_tokens: int) -> list[WindowEntry]:
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
                removed_text.insert(None, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_13(self, keep_tokens: int) -> list[WindowEntry]:
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
                removed_text.insert(0, None)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_14(self, keep_tokens: int) -> list[WindowEntry]:
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
                removed_text.insert(self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_15(self, keep_tokens: int) -> list[WindowEntry]:
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
                removed_text.insert(0, )
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_16(self, keep_tokens: int) -> list[WindowEntry]:
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
                removed_text.insert(1, self._summary)
            self._summary = self.summarizer(removed_text)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_17(self, keep_tokens: int) -> list[WindowEntry]:
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
            self._summary = None
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_18(self, keep_tokens: int) -> list[WindowEntry]:
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
            self._summary = self.summarizer(None)
            self._summary_tokens = self._estimate_tokens(self._summary)

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_19(self, keep_tokens: int) -> list[WindowEntry]:
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
            self._summary_tokens = None

        return removed

    def xǁSlidingWindowManagerǁslide__mutmut_20(self, keep_tokens: int) -> list[WindowEntry]:
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
            self._summary_tokens = self._estimate_tokens(None)

        return removed
    
    xǁSlidingWindowManagerǁslide__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁslide__mutmut_1': xǁSlidingWindowManagerǁslide__mutmut_1, 
        'xǁSlidingWindowManagerǁslide__mutmut_2': xǁSlidingWindowManagerǁslide__mutmut_2, 
        'xǁSlidingWindowManagerǁslide__mutmut_3': xǁSlidingWindowManagerǁslide__mutmut_3, 
        'xǁSlidingWindowManagerǁslide__mutmut_4': xǁSlidingWindowManagerǁslide__mutmut_4, 
        'xǁSlidingWindowManagerǁslide__mutmut_5': xǁSlidingWindowManagerǁslide__mutmut_5, 
        'xǁSlidingWindowManagerǁslide__mutmut_6': xǁSlidingWindowManagerǁslide__mutmut_6, 
        'xǁSlidingWindowManagerǁslide__mutmut_7': xǁSlidingWindowManagerǁslide__mutmut_7, 
        'xǁSlidingWindowManagerǁslide__mutmut_8': xǁSlidingWindowManagerǁslide__mutmut_8, 
        'xǁSlidingWindowManagerǁslide__mutmut_9': xǁSlidingWindowManagerǁslide__mutmut_9, 
        'xǁSlidingWindowManagerǁslide__mutmut_10': xǁSlidingWindowManagerǁslide__mutmut_10, 
        'xǁSlidingWindowManagerǁslide__mutmut_11': xǁSlidingWindowManagerǁslide__mutmut_11, 
        'xǁSlidingWindowManagerǁslide__mutmut_12': xǁSlidingWindowManagerǁslide__mutmut_12, 
        'xǁSlidingWindowManagerǁslide__mutmut_13': xǁSlidingWindowManagerǁslide__mutmut_13, 
        'xǁSlidingWindowManagerǁslide__mutmut_14': xǁSlidingWindowManagerǁslide__mutmut_14, 
        'xǁSlidingWindowManagerǁslide__mutmut_15': xǁSlidingWindowManagerǁslide__mutmut_15, 
        'xǁSlidingWindowManagerǁslide__mutmut_16': xǁSlidingWindowManagerǁslide__mutmut_16, 
        'xǁSlidingWindowManagerǁslide__mutmut_17': xǁSlidingWindowManagerǁslide__mutmut_17, 
        'xǁSlidingWindowManagerǁslide__mutmut_18': xǁSlidingWindowManagerǁslide__mutmut_18, 
        'xǁSlidingWindowManagerǁslide__mutmut_19': xǁSlidingWindowManagerǁslide__mutmut_19, 
        'xǁSlidingWindowManagerǁslide__mutmut_20': xǁSlidingWindowManagerǁslide__mutmut_20
    }
    
    def slide(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁslide__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁslide__mutmut_mutants"), args, kwargs, self)
        return result 
    
    slide.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁslide__mutmut_orig)
    xǁSlidingWindowManagerǁslide__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁslide'

    def xǁSlidingWindowManagerǁclear__mutmut_orig(self):
        """Clear window contents."""
        self._entries.clear()
        self._total_tokens = 0
        self._summary = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁclear__mutmut_1(self):
        """Clear window contents."""
        self._entries.clear()
        self._total_tokens = None
        self._summary = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁclear__mutmut_2(self):
        """Clear window contents."""
        self._entries.clear()
        self._total_tokens = 1
        self._summary = None
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁclear__mutmut_3(self):
        """Clear window contents."""
        self._entries.clear()
        self._total_tokens = 0
        self._summary = ""
        self._summary_tokens = 0

    def xǁSlidingWindowManagerǁclear__mutmut_4(self):
        """Clear window contents."""
        self._entries.clear()
        self._total_tokens = 0
        self._summary = None
        self._summary_tokens = None

    def xǁSlidingWindowManagerǁclear__mutmut_5(self):
        """Clear window contents."""
        self._entries.clear()
        self._total_tokens = 0
        self._summary = None
        self._summary_tokens = 1
    
    xǁSlidingWindowManagerǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁclear__mutmut_1': xǁSlidingWindowManagerǁclear__mutmut_1, 
        'xǁSlidingWindowManagerǁclear__mutmut_2': xǁSlidingWindowManagerǁclear__mutmut_2, 
        'xǁSlidingWindowManagerǁclear__mutmut_3': xǁSlidingWindowManagerǁclear__mutmut_3, 
        'xǁSlidingWindowManagerǁclear__mutmut_4': xǁSlidingWindowManagerǁclear__mutmut_4, 
        'xǁSlidingWindowManagerǁclear__mutmut_5': xǁSlidingWindowManagerǁclear__mutmut_5
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁclear__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁclear__mutmut_orig)
    xǁSlidingWindowManagerǁclear__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁclear'

    def xǁSlidingWindowManagerǁget_entries_by_type__mutmut_orig(self, entry_type: str) -> list[WindowEntry]:
        """Get all entries of a specific type."""
        return [e for e in self._entries if e.entry_type == entry_type]

    def xǁSlidingWindowManagerǁget_entries_by_type__mutmut_1(self, entry_type: str) -> list[WindowEntry]:
        """Get all entries of a specific type."""
        return [e for e in self._entries if e.entry_type != entry_type]
    
    xǁSlidingWindowManagerǁget_entries_by_type__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁget_entries_by_type__mutmut_1': xǁSlidingWindowManagerǁget_entries_by_type__mutmut_1
    }
    
    def get_entries_by_type(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁget_entries_by_type__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁget_entries_by_type__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entries_by_type.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁget_entries_by_type__mutmut_orig)
    xǁSlidingWindowManagerǁget_entries_by_type__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁget_entries_by_type'

    def xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_orig(self, min_priority: int) -> list[WindowEntry]:
        """Get all entries at or above minimum priority."""
        return [e for e in self._entries if e.priority >= min_priority]

    def xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_1(self, min_priority: int) -> list[WindowEntry]:
        """Get all entries at or above minimum priority."""
        return [e for e in self._entries if e.priority > min_priority]
    
    xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_1': xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_1
    }
    
    def get_entries_by_priority(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_entries_by_priority.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_orig)
    xǁSlidingWindowManagerǁget_entries_by_priority__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁget_entries_by_priority'

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

    def xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_orig(self, text: str) -> int:
        """Estimate token count for text (rough: 4 chars per token)."""
        return len(text) // 4 + 1

    def xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_1(self, text: str) -> int:
        """Estimate token count for text (rough: 4 chars per token)."""
        return len(text) // 4 - 1

    def xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_2(self, text: str) -> int:
        """Estimate token count for text (rough: 4 chars per token)."""
        return len(text) / 4 + 1

    def xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_3(self, text: str) -> int:
        """Estimate token count for text (rough: 4 chars per token)."""
        return len(text) // 5 + 1

    def xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_4(self, text: str) -> int:
        """Estimate token count for text (rough: 4 chars per token)."""
        return len(text) // 4 + 2
    
    xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_1': xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_1, 
        'xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_2': xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_2, 
        'xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_3': xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_3, 
        'xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_4': xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_4
    }
    
    def _estimate_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _estimate_tokens.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_orig)
    xǁSlidingWindowManagerǁ_estimate_tokens__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁ_estimate_tokens'

    def xǁSlidingWindowManagerǁ_should_summarize__mutmut_orig(self) -> bool:
        """Check if summarization should be triggered."""
        threshold = self.max_tokens * self.SUMMARIZATION_THRESHOLD
        return self._total_tokens >= threshold

    def xǁSlidingWindowManagerǁ_should_summarize__mutmut_1(self) -> bool:
        """Check if summarization should be triggered."""
        threshold = None
        return self._total_tokens >= threshold

    def xǁSlidingWindowManagerǁ_should_summarize__mutmut_2(self) -> bool:
        """Check if summarization should be triggered."""
        threshold = self.max_tokens / self.SUMMARIZATION_THRESHOLD
        return self._total_tokens >= threshold

    def xǁSlidingWindowManagerǁ_should_summarize__mutmut_3(self) -> bool:
        """Check if summarization should be triggered."""
        threshold = self.max_tokens * self.SUMMARIZATION_THRESHOLD
        return self._total_tokens > threshold
    
    xǁSlidingWindowManagerǁ_should_summarize__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁ_should_summarize__mutmut_1': xǁSlidingWindowManagerǁ_should_summarize__mutmut_1, 
        'xǁSlidingWindowManagerǁ_should_summarize__mutmut_2': xǁSlidingWindowManagerǁ_should_summarize__mutmut_2, 
        'xǁSlidingWindowManagerǁ_should_summarize__mutmut_3': xǁSlidingWindowManagerǁ_should_summarize__mutmut_3
    }
    
    def _should_summarize(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁ_should_summarize__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁ_should_summarize__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _should_summarize.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁ_should_summarize__mutmut_orig)
    xǁSlidingWindowManagerǁ_should_summarize__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁ_should_summarize'

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_orig(self):
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_1(self):
        """Trigger summarization of oldest content."""
        if self.summarizer:
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_2(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = None
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_3(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(None, len(self._entries) // 3)
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_4(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, None)
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_5(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(len(self._entries) // 3)
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_6(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, )
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_7(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(2, len(self._entries) // 3)
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_8(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, len(self._entries) / 3)
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_9(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, len(self._entries) // 4)
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_10(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, len(self._entries) // 3)
        to_summarize = None

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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_11(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, len(self._entries) // 3)
        to_summarize = self._entries[:summarize_count]

        if to_summarize:
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_12(self):
        """Trigger summarization of oldest content."""
        if not self.summarizer:
            return

        # Summarize oldest 30% of entries
        summarize_count = max(1, len(self._entries) // 3)
        to_summarize = self._entries[:summarize_count]

        if not to_summarize:
            return

        # Generate summary
        texts = None
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

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_13(self):
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
            texts.insert(None, self._summary)

        new_summary = self.summarizer(texts)

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_14(self):
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
            texts.insert(0, None)

        new_summary = self.summarizer(texts)

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_15(self):
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
            texts.insert(self._summary)

        new_summary = self.summarizer(texts)

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_16(self):
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
            texts.insert(0, )

        new_summary = self.summarizer(texts)

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_17(self):
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
            texts.insert(1, self._summary)

        new_summary = self.summarizer(texts)

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_18(self):
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

        new_summary = None

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_19(self):
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

        new_summary = self.summarizer(None)

        # Remove summarized entries
        for entry in to_summarize:
            self._entries.remove(entry)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_20(self):
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
            self._entries.remove(None)
            self._total_tokens -= entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_21(self):
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
            self._total_tokens = entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_22(self):
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
            self._total_tokens += entry.token_count

        # Update summary
        self._summary = new_summary
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_23(self):
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
        self._summary = None
        self._summary_tokens = self._estimate_tokens(new_summary)

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_24(self):
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
        self._summary_tokens = None

    def xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_25(self):
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
        self._summary_tokens = self._estimate_tokens(None)
    
    xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_1': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_1, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_2': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_2, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_3': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_3, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_4': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_4, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_5': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_5, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_6': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_6, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_7': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_7, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_8': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_8, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_9': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_9, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_10': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_10, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_11': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_11, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_12': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_12, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_13': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_13, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_14': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_14, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_15': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_15, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_16': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_16, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_17': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_17, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_18': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_18, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_19': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_19, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_20': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_20, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_21': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_21, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_22': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_22, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_23': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_23, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_24': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_24, 
        'xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_25': xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_25
    }
    
    def _trigger_summarization(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _trigger_summarization.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_orig)
    xǁSlidingWindowManagerǁ_trigger_summarization__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁ_trigger_summarization'

    def xǁSlidingWindowManagerǁ_make_room__mutmut_orig(self, needed_tokens: int) -> Optional[str]:
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_1(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy != WindowStrategy.DROP_OLDEST:
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_2(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = None
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_3(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens or self._entries:
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_4(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens - needed_tokens > self.max_tokens and self._entries:
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_5(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens >= self.max_tokens and self._entries:
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_6(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = None
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_7(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = self._entries.pop(None)
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_8(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = self._entries.pop(1)
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_9(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = self._entries.pop(0)
                self._total_tokens = entry.token_count
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_10(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = self._entries.pop(0)
                self._total_tokens += entry.token_count
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_11(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = self._entries.pop(0)
                self._total_tokens -= entry.token_count
                removed.append(None)

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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_12(self, needed_tokens: int) -> Optional[str]:
        """Make room for new content based on strategy."""
        if self.strategy == WindowStrategy.DROP_OLDEST:
            removed = []
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                entry = self._entries.pop(0)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Dropped {len(removed)} oldest entries to make room"

        elif self.strategy != WindowStrategy.SUMMARIZE:
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_13(self, needed_tokens: int) -> Optional[str]:
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
                return "XXTriggered summarization to make roomXX"

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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_14(self, needed_tokens: int) -> Optional[str]:
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
                return "triggered summarization to make room"

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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_15(self, needed_tokens: int) -> Optional[str]:
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
                return "TRIGGERED SUMMARIZATION TO MAKE ROOM"

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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_16(self, needed_tokens: int) -> Optional[str]:
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

        elif self.strategy != WindowStrategy.PRIORITY_PRUNE:
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

    def xǁSlidingWindowManagerǁ_make_room__mutmut_17(self, needed_tokens: int) -> Optional[str]:
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
            removed = None
            while self._total_tokens + needed_tokens > self.max_tokens and self._entries:
                # Remove lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_18(self, needed_tokens: int) -> Optional[str]:
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
            while self._total_tokens + needed_tokens > self.max_tokens or self._entries:
                # Remove lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_19(self, needed_tokens: int) -> Optional[str]:
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
            while self._total_tokens - needed_tokens > self.max_tokens and self._entries:
                # Remove lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_20(self, needed_tokens: int) -> Optional[str]:
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
            while self._total_tokens + needed_tokens >= self.max_tokens and self._entries:
                # Remove lowest priority
                min_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_21(self, needed_tokens: int) -> Optional[str]:
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
                min_idx = None
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_22(self, needed_tokens: int) -> Optional[str]:
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
                min_idx = min(None, key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_23(self, needed_tokens: int) -> Optional[str]:
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
                min_idx = min(range(len(self._entries)), key=None)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_24(self, needed_tokens: int) -> Optional[str]:
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
                min_idx = min(key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_25(self, needed_tokens: int) -> Optional[str]:
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
                min_idx = min(range(len(self._entries)), )
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_26(self, needed_tokens: int) -> Optional[str]:
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
                min_idx = min(range(None), key=lambda i: self._entries[i].priority)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_27(self, needed_tokens: int) -> Optional[str]:
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
                min_idx = min(range(len(self._entries)), key=lambda i: None)
                entry = self._entries.pop(min_idx)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_28(self, needed_tokens: int) -> Optional[str]:
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
                entry = None
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_29(self, needed_tokens: int) -> Optional[str]:
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
                entry = self._entries.pop(None)
                self._total_tokens -= entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_30(self, needed_tokens: int) -> Optional[str]:
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
                self._total_tokens = entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_31(self, needed_tokens: int) -> Optional[str]:
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
                self._total_tokens += entry.token_count
                removed.append(entry)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None

    def xǁSlidingWindowManagerǁ_make_room__mutmut_32(self, needed_tokens: int) -> Optional[str]:
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
                removed.append(None)

            if removed:
                return f"Pruned {len(removed)} low-priority entries"

        return None
    
    xǁSlidingWindowManagerǁ_make_room__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSlidingWindowManagerǁ_make_room__mutmut_1': xǁSlidingWindowManagerǁ_make_room__mutmut_1, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_2': xǁSlidingWindowManagerǁ_make_room__mutmut_2, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_3': xǁSlidingWindowManagerǁ_make_room__mutmut_3, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_4': xǁSlidingWindowManagerǁ_make_room__mutmut_4, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_5': xǁSlidingWindowManagerǁ_make_room__mutmut_5, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_6': xǁSlidingWindowManagerǁ_make_room__mutmut_6, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_7': xǁSlidingWindowManagerǁ_make_room__mutmut_7, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_8': xǁSlidingWindowManagerǁ_make_room__mutmut_8, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_9': xǁSlidingWindowManagerǁ_make_room__mutmut_9, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_10': xǁSlidingWindowManagerǁ_make_room__mutmut_10, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_11': xǁSlidingWindowManagerǁ_make_room__mutmut_11, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_12': xǁSlidingWindowManagerǁ_make_room__mutmut_12, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_13': xǁSlidingWindowManagerǁ_make_room__mutmut_13, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_14': xǁSlidingWindowManagerǁ_make_room__mutmut_14, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_15': xǁSlidingWindowManagerǁ_make_room__mutmut_15, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_16': xǁSlidingWindowManagerǁ_make_room__mutmut_16, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_17': xǁSlidingWindowManagerǁ_make_room__mutmut_17, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_18': xǁSlidingWindowManagerǁ_make_room__mutmut_18, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_19': xǁSlidingWindowManagerǁ_make_room__mutmut_19, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_20': xǁSlidingWindowManagerǁ_make_room__mutmut_20, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_21': xǁSlidingWindowManagerǁ_make_room__mutmut_21, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_22': xǁSlidingWindowManagerǁ_make_room__mutmut_22, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_23': xǁSlidingWindowManagerǁ_make_room__mutmut_23, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_24': xǁSlidingWindowManagerǁ_make_room__mutmut_24, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_25': xǁSlidingWindowManagerǁ_make_room__mutmut_25, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_26': xǁSlidingWindowManagerǁ_make_room__mutmut_26, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_27': xǁSlidingWindowManagerǁ_make_room__mutmut_27, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_28': xǁSlidingWindowManagerǁ_make_room__mutmut_28, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_29': xǁSlidingWindowManagerǁ_make_room__mutmut_29, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_30': xǁSlidingWindowManagerǁ_make_room__mutmut_30, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_31': xǁSlidingWindowManagerǁ_make_room__mutmut_31, 
        'xǁSlidingWindowManagerǁ_make_room__mutmut_32': xǁSlidingWindowManagerǁ_make_room__mutmut_32
    }
    
    def _make_room(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSlidingWindowManagerǁ_make_room__mutmut_orig"), object.__getattribute__(self, "xǁSlidingWindowManagerǁ_make_room__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _make_room.__signature__ = _mutmut_signature(xǁSlidingWindowManagerǁ_make_room__mutmut_orig)
    xǁSlidingWindowManagerǁ_make_room__mutmut_orig.__name__ = 'xǁSlidingWindowManagerǁ_make_room'
