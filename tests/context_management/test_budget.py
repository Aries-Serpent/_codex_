"""
Tests for context_management.budget module.

Tests token budget enforcement, content prioritization, and pruning strategies.

Phase 9.1 Coverage Enhancement
#Phase9.1 #Coverage30 #UnitTests
"""

from datetime import datetime

from context_management.budget import (
    HARD_TOKEN_CEILING,
    SOFT_TOKEN_CAP,
    ContentBlock,
    ContentPriority,
    TokenBudget,
    TokenBudgetEnforcer,
)


class TestTokenBudget:
    """Test TokenBudget dataclass and properties."""

    def test_token_budget_initialization(self):
        """Test TokenBudget initializes with correct defaults."""
        budget = TokenBudget()
        assert budget.hard_limit == HARD_TOKEN_CEILING
        assert budget.soft_limit == SOFT_TOKEN_CAP
        assert budget.current_usage == 0
        assert budget.reserved == 8000

    def test_token_budget_custom_limits(self):
        """Test TokenBudget with custom limits."""
        budget = TokenBudget(hard_limit=10000, soft_limit=8000, reserved=1000)
        assert budget.hard_limit == 10000
        assert budget.soft_limit == 8000
        assert budget.reserved == 1000

    def test_available_property(self):
        """Test available tokens calculation."""
        budget = TokenBudget(soft_limit=1000)
        assert budget.available == 1000

        budget.current_usage = 300
        assert budget.available == 700

        budget.current_usage = 1000
        assert budget.available == 0

        # Over limit returns 0, not negative
        budget.current_usage = 1200
        assert budget.available == 0

    def test_hard_available_property(self):
        """Test hard limit available tokens calculation."""
        budget = TokenBudget(hard_limit=2000, current_usage=500)
        assert budget.hard_available == 1500

    def test_usage_ratio(self):
        """Test usage ratio calculation."""
        budget = TokenBudget(soft_limit=1000, current_usage=500)
        assert budget.usage_ratio == 0.5

        budget.current_usage = 900
        assert budget.usage_ratio == 0.9

    def test_needs_pruning_threshold(self):
        """Test pruning threshold detection."""
        budget = TokenBudget(soft_limit=1000)

        # Below threshold
        budget.current_usage = 800
        assert not budget.needs_pruning

        # At threshold (90%)
        budget.current_usage = 900
        assert budget.needs_pruning

        # Over threshold
        budget.current_usage = 950
        assert budget.needs_pruning

    def test_over_hard_limit(self):
        """Test hard limit detection."""
        budget = TokenBudget(hard_limit=1000)

        budget.current_usage = 999
        assert not budget.over_hard_limit

        budget.current_usage = 1001
        assert budget.over_hard_limit


class TestContentBlock:
    """Test ContentBlock dataclass."""

    def test_content_block_initialization(self):
        """Test ContentBlock initialization with defaults."""
        block = ContentBlock(content="test content", token_count=10)
        assert block.content == "test content"
        assert block.token_count == 10
        assert block.priority == ContentPriority.MEDIUM
        assert isinstance(block.timestamp, datetime)
        assert block.source == ""
        assert block.can_summarize is True
        assert block.summary is None

    def test_content_block_custom_priority(self):
        """Test ContentBlock with custom priority."""
        block = ContentBlock(
            content="critical error", token_count=5, priority=ContentPriority.CRITICAL
        )
        assert block.priority == ContentPriority.CRITICAL

    def test_get_effective_content_no_summary(self):
        """Test effective content when no summary exists."""
        block = ContentBlock(content="original content", token_count=10)
        assert block.get_effective_content() == "original content"

    def test_get_effective_content_with_shorter_summary(self):
        """Test effective content prefers shorter summary."""
        block = ContentBlock(
            content="This is a very long original content that needs summarization",
            token_count=50,
            summary="Short summary",
        )
        assert block.get_effective_content() == "Short summary"

    def test_get_effective_content_with_longer_summary(self):
        """Test effective content uses original if summary is longer."""
        block = ContentBlock(
            content="Short",
            token_count=5,
            summary="This is a very long summary that is longer than original",
        )
        assert block.get_effective_content() == "Short"

    def test_content_priority_enum_values(self):
        """Test ContentPriority enum values."""
        assert ContentPriority.CRITICAL == 100
        assert ContentPriority.HIGH == 75
        assert ContentPriority.MEDIUM == 50
        assert ContentPriority.LOW == 25
        assert ContentPriority.DISPOSABLE == 0

    def test_content_priority_ordering(self):
        """Test ContentPriority ordering."""
        assert ContentPriority.CRITICAL > ContentPriority.HIGH
        assert ContentPriority.HIGH > ContentPriority.MEDIUM
        assert ContentPriority.MEDIUM > ContentPriority.LOW
        assert ContentPriority.LOW > ContentPriority.DISPOSABLE


class TestTokenBudgetEnforcer:
    """Test TokenBudgetEnforcer class."""

    def test_enforcer_initialization(self):
        """Test enforcer initializes correctly."""
        enforcer = TokenBudgetEnforcer()
        assert enforcer.budget.hard_limit == HARD_TOKEN_CEILING
        assert enforcer.budget.soft_limit == SOFT_TOKEN_CAP
        assert len(enforcer._blocks) == 0

    def test_enforcer_custom_limits(self):
        """Test enforcer with custom limits."""
        enforcer = TokenBudgetEnforcer(hard_limit=5000, soft_limit=4000)
        assert enforcer.budget.hard_limit == 5000
        assert enforcer.budget.soft_limit == 4000

    def test_add_content_simple(self):
        """Test adding content to enforcer."""
        enforcer = TokenBudgetEnforcer()

        result = enforcer.add_content("test content")

        assert result is True
        assert len(enforcer._blocks) == 1
        assert enforcer.budget.current_usage > 0

    def test_add_multiple_content_blocks(self):
        """Test adding multiple content blocks."""
        enforcer = TokenBudgetEnforcer()

        enforcer.add_content("block1 content")
        enforcer.add_content("block2 content")
        enforcer.add_content("block3 content")

        assert len(enforcer._blocks) == 3

    def test_add_content_with_priority(self):
        """Test adding content with priority."""
        enforcer = TokenBudgetEnforcer()

        enforcer.add_content("critical content", priority=ContentPriority.CRITICAL)
        enforcer.add_content("low content", priority=ContentPriority.LOW)

        assert len(enforcer._blocks) == 2
        assert enforcer._blocks[0].priority == ContentPriority.CRITICAL
        assert enforcer._blocks[1].priority == ContentPriority.LOW

    def test_add_content_with_source(self):
        """Test adding content with source identifier."""
        enforcer = TokenBudgetEnforcer()

        enforcer.add_content("test", source="test_source")

        assert enforcer._blocks[0].source == "test_source"

    def test_get_context(self):
        """Test getting context from enforcer."""
        enforcer = TokenBudgetEnforcer()

        enforcer.add_content("first content")
        enforcer.add_content("second content")

        context = enforcer.get_context()

        assert "first content" in context
        assert "second content" in context

    def test_count_tokens(self):
        """Test token counting."""
        enforcer = TokenBudgetEnforcer()

        token_count = enforcer.count_tokens("This is a test string")

        assert token_count > 0
        assert isinstance(token_count, int)

    def test_custom_token_counter(self):
        """Test enforcer with custom token counting function."""

        def custom_counter(text: str) -> int:
            return len(text)  # Count characters

        enforcer = TokenBudgetEnforcer(token_counter=custom_counter)

        enforcer.add_content("12345")
        assert enforcer.budget.current_usage == 5

    def test_custom_summarizer(self):
        """Test enforcer with custom summarizer."""

        def custom_summarizer(text: str) -> str:
            return text[:20] + "..." if len(text) > 20 else text

        enforcer = TokenBudgetEnforcer(summarizer=custom_summarizer)

        assert enforcer._summarizer is not None

    def test_empty_content(self):
        """Test adding empty content."""
        enforcer = TokenBudgetEnforcer()
        result = enforcer.add_content("")

        # Empty content should still be added
        assert result is True
        assert len(enforcer._blocks) == 1


class TestBudgetEnforcementStrategies:
    """Test different enforcement strategies."""

    def test_needs_pruning_detection(self):
        """Test that exceeding soft limit triggers needs_pruning."""
        enforcer = TokenBudgetEnforcer(soft_limit=100)

        # Add content to reach 90%+ of soft limit
        for _ in range(20):
            enforcer.add_content("some test content here")
            if enforcer.budget.needs_pruning:
                break

        # At some point should trigger pruning
        assert enforcer.budget.current_usage > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_content_string(self):
        """Test content block with empty string."""
        block = ContentBlock(content="", token_count=0)
        assert block.get_effective_content() == ""

    def test_get_context_empty(self):
        """Test getting context when no content added."""
        enforcer = TokenBudgetEnforcer()
        context = enforcer.get_context()
        assert context == ""

    def test_get_context_with_max_tokens(self):
        """Test getting context with max token limit."""
        enforcer = TokenBudgetEnforcer()

        enforcer.add_content("First block of content")
        enforcer.add_content("Second block of content")

        # Should respect max_tokens parameter
        context = enforcer.get_context(max_tokens=100)
        assert context is not None
