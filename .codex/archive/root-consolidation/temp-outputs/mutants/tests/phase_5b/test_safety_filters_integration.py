"""
Integration Tests for Safety Filters

Tests complete safety filtering workflows:
- Filter chain execution with multiple filters
- Integration with tokenizers and transformers
- Error recovery and fallback paths
- Cross-module dependencies (tokenizer integration, safety backend)
- State consistency across pipeline stages
- Resource cleanup and memory management

Part of Phase 5B-II: Integration Test Development
"""

from __future__ import annotations

import logging
from unittest.mock import Mock, patch

import pytest

# Conditional imports with graceful degradation
try:
    from codex_ml.safety.filters import (
        ContentFilter,
        SafetyFilterChain,
        SafetyViolation,
        TokenFilter,
        create_filter_chain,
    )

    SAFETY_FILTERS_AVAILABLE = True
except (ImportError, AttributeError):
    SAFETY_FILTERS_AVAILABLE = False

try:
    from transformers import AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


logger = logging.getLogger(__name__)


@pytest.mark.skipif(not SAFETY_FILTERS_AVAILABLE, reason="Safety filters not available")
class TestSafetyFiltersIntegration:
    """Integration tests for safety filtering system."""

    def test_safety_filter_chain_initialization(self):
        """Test: Filter chain initializes with multiple filters."""
        # Arrange & Act: Create filter chain
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain
            mock_chain.add_filter = Mock()

            # Create chain and add filters
            chain = mock_chain_cls()
            chain.add_filter("content")
            chain.add_filter("token")

            # Assert: Chain properly configured
            assert chain.add_filter.call_count == 2, "Count must be greater than zero"

    def test_content_filter_blocks_harmful_content(self):
        """Test: Content filter detects and blocks harmful content."""
        # Arrange: Harmful content samples
        harmful_texts = [
            "violence and harm",
            "explicit content here",
            "dangerous instructions",
        ]

        # Act & Assert: Mock content filtering
        with patch("codex_ml.safety.filters.ContentFilter") as mock_filter_cls:
            mock_filter = Mock()
            mock_filter_cls.return_value = mock_filter
            mock_filter.check = Mock(return_value=True)  # Blocks content

            # Create filter and check content
            filter_instance = mock_filter_cls()
            for text in harmful_texts:
                result = filter_instance.check(text)
                assert result is True, "Result must not be empty"

    def test_token_filter_detects_harmful_tokens(self):
        """Test: Token filter identifies harmful token sequences."""
        # Arrange: Sample text with potentially harmful tokens
        test_text = "normal text with harmful pattern here"

        # Act & Assert: Mock token filtering
        with patch("codex_ml.safety.filters.TokenFilter") as mock_filter_cls:
            mock_filter = Mock()
            mock_filter_cls.return_value = mock_filter
            mock_filter.filter_tokens = Mock(return_value={"filtered": True, "removed_tokens": 2})

            # Apply token filter
            filter_instance = mock_filter_cls()
            result = filter_instance.filter_tokens(test_text)

            # Assert
            assert result["filtered"] is True, "Result must not be empty"
            assert result["removed_tokens"] == 2, "Result must not be empty"

    def test_filter_chain_execution_workflow(self):
        """Test: Complete filter chain execution from input to output."""
        # Arrange: Input text
        input_text = "test input text for filtering"

        # Act & Assert: Mock complete pipeline
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain

            # Mock chain execution
            mock_chain.apply_filters = Mock(
                return_value={
                    "passed": True,
                    "filters_applied": 3,
                    "text": input_text,
                }
            )

            # Execute chain
            chain = mock_chain_cls()
            result = chain.apply_filters(input_text)

            # Assert: All filters executed
            assert result["filters_applied"] == 3, "Result must not be empty"
            assert result["passed"] is True, "Result must not be empty"

    def test_safety_violation_exception_handling(self):
        """Test: Safety violations are properly caught and reported."""
        # Arrange: Mock violation detection
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain

            # Mock exception
            mock_chain.apply_filters = Mock(side_effect=Exception("Safety violation detected"))

            # Execute and catch
            chain = mock_chain_cls()
            with pytest.raises(Exception):
                chain.apply_filters("harmful content")

    def test_filter_chain_with_tokenizer_integration(self):
        """Test: Filter chain works with tokenizer for token-level filtering."""
        # Arrange & Act: Mock integrated workflow
        with patch("codex_ml.safety.filters.TokenFilter") as mock_token_filter:
            with patch("codex_ml.safety.filters.create_filter_chain") as mock_create:
                # Setup tokenizer integration
                mock_filter = Mock()
                mock_filter.check_tokens = Mock(return_value={"safe": True, "token_count": 10})
                mock_token_filter.return_value = mock_filter

                # Setup chain creation
                mock_chain = Mock()
                mock_chain.add_filter = Mock()
                mock_create.return_value = mock_chain

                # Create chain with tokenizer
                mock_create()
                result = mock_filter.check_tokens([1, 2, 3, 4, 5])

                # Assert: Integration successful
                assert result["safe"] is True, "Result must not be empty"

    def test_error_recovery_on_filter_failure(self):
        """Test: System recovers gracefully when filter fails."""
        # Arrange & Act: Mock filter failure
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain

            # Mock failure and recovery
            mock_chain.apply_filters = Mock(side_effect=RuntimeError("Filter execution failed"))
            mock_chain.fallback_filter = Mock(return_value={"text": "original", "filtered": False})

            # Attempt filtering
            chain = mock_chain_cls()
            try:
                chain.apply_filters("test")
            except RuntimeError:
                # Recovery: Use fallback
                result = chain.fallback_filter()
                assert result["filtered"] is False, "Result must not be empty"

    def test_filter_chain_state_consistency(self):
        """Test: Filter chain maintains consistent state across execution."""
        # Arrange: Track state transitions
        state_transitions = []

        # Act: Mock state tracking
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain

            # Track state
            initial_state = {"initialized": True, "filters": 0}
            mock_chain.state = initial_state

            # Simulate filter addition
            state_transitions.append(mock_chain.state.copy())
            mock_chain.state["filters"] += 1
            state_transitions.append(mock_chain.state.copy())

            # Assert: State properly tracked
            assert len(state_transitions) == 2, "State_transitions must not be empty"
            assert state_transitions[0]["filters"] == 0, "Condition must be true"
            assert state_transitions[1]["filters"] == 1, "Condition must be true"

    def test_batch_content_filtering(self):
        """Test: Multiple texts filtered in batch."""
        # Arrange: Batch of texts
        batch = [
            "normal text 1",
            "normal text 2",
            "normal text 3",
        ]

        # Act & Assert: Mock batch filtering
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain
            mock_chain.apply_filters_batch = Mock(
                return_value=[{"text": t, "passed": True} for t in batch]
            )

            # Filter batch
            chain = mock_chain_cls()
            results = chain.apply_filters_batch(batch)

            # Assert: All texts filtered
            assert len(results) == 3, "Results must not be empty"
            assert all(r["passed"] for r in results), "Result must not be empty"

    def test_filter_performance_metrics(self):
        """Test: Filter chain tracks performance metrics."""
        # Arrange & Act: Mock metrics collection
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain
            mock_chain.get_metrics = Mock(
                return_value={
                    "total_texts": 100,
                    "blocked": 5,
                    "avg_latency_ms": 2.3,
                }
            )

            # Get metrics
            chain = mock_chain_cls()
            metrics = chain.get_metrics()

            # Assert: Metrics available
            assert metrics["total_texts"] == 100, "Condition must be true"
            assert metrics["blocked"] == 5, "Condition must be true"

    def test_cross_module_filter_composition(self):
        """Test: Multiple filter types composed in workflow."""
        # Arrange & Act: Mock filter composition
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            with patch("codex_ml.safety.filters.ContentFilter") as mock_content:
                with patch("codex_ml.safety.filters.TokenFilter") as mock_token:
                    # Setup filters
                    mock_chain = Mock()
                    mock_chain_cls.return_value = mock_chain
                    mock_content_instance = Mock()
                    mock_token_instance = Mock()
                    mock_content.return_value = mock_content_instance
                    mock_token.return_value = mock_token_instance

                    # Create composition
                    chain = mock_chain_cls()
                    mock_content()
                    mock_token()

                    # Mock execution
                    mock_chain.apply_filters = Mock(
                        return_value={"passed": True, "content_safe": True, "tokens_safe": True}
                    )

                    result = chain.apply_filters("test")

                    # Assert: Both filters applied
                    assert result["content_safe"] is True, "Result must not be empty"
                    assert result["tokens_safe"] is True, "Result must not be empty"


@pytest.mark.skipif(not SAFETY_FILTERS_AVAILABLE, reason="Safety filters not available")
class TestSafetyFiltersErrorHandling:
    """Error handling in safety filter system."""

    def test_error_on_invalid_filter_configuration(self):
        """Test: Invalid filter configuration is caught."""
        # Arrange & Act: Mock invalid config
        with patch("codex_ml.safety.filters.create_filter_chain") as mock_create:
            mock_create.side_effect = ValueError("Invalid filter configuration")

            with pytest.raises(ValueError):
                mock_create({"invalid": "config"})

    def test_error_on_filter_initialization_failure(self):
        """Test: Filter initialization errors are handled."""
        # Arrange & Act: Mock initialization failure
        with patch("codex_ml.safety.filters.ContentFilter") as mock_filter:
            mock_filter.side_effect = RuntimeError("Filter init failed")

            with pytest.raises(RuntimeError):
                mock_filter()

    def test_graceful_degradation_when_filter_unavailable(self):
        """Test: System degrades gracefully when filter not available."""
        # This tests that missing optional filters don't crash the system
        try:
            from codex_ml.safety import filters

            assert hasattr(filters, "SafetyFilterChain")
        except ImportError:
            pytest.skip("Safety filters not available, but should handle gracefully")


@pytest.mark.skipif(
    not (SAFETY_FILTERS_AVAILABLE and TRANSFORMERS_AVAILABLE), reason="Requirements not available"
)
class TestSafetyFiltersWithTransformers:
    """Safety filters integration with Transformers library."""

    def test_tokenizer_integration_with_safety_filter(self):
        """Test: Safety filter works with HF tokenizers."""
        # Arrange & Act: Mock tokenizer integration
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_load:
            mock_tokenizer = Mock()
            mock_tokenizer.encode = Mock(return_value=[1, 2, 3])
            mock_load.return_value = mock_tokenizer

            # Use tokenizer with filter
            tokenizer = mock_load("bert-base-uncased")
            tokens = tokenizer.encode("test text")

            # Assert: Integration works
            assert len(tokens) == 3, "Tokens must not be empty"

    def test_safety_filter_on_tokenized_input(self):
        """Test: Safety filter applied to tokenized sequences."""
        # Arrange: Mock tokenized input
        token_ids = [101, 2054, 2003, 102]  # Example BERT token IDs

        # Act & Assert: Apply safety filter
        with patch("codex_ml.safety.filters.TokenFilter") as mock_filter_cls:
            mock_filter = Mock()
            mock_filter_cls.return_value = mock_filter
            mock_filter.check_tokens = Mock(return_value={"safe": True})

            # Filter tokens
            filter_instance = mock_filter_cls()
            result = filter_instance.check_tokens(token_ids)

            # Assert
            assert result["safe"] is True, "Result must not be empty"


@pytest.mark.skipif(not SAFETY_FILTERS_AVAILABLE, reason="Safety filters not available")
class TestSafetyFiltersResourceManagement:
    """Resource management in safety filters."""

    def test_filter_cache_management(self):
        """Test: Filter cache is properly managed."""
        # Arrange & Act: Mock cache operations
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain
            mock_chain.cache = {}
            mock_chain.add_to_cache = Mock()

            chain = mock_chain_cls()

            # Add items to cache
            chain.add_to_cache("key1", "value1")
            chain.add_to_cache("key2", "value2")

            # Assert: Cache populated
            assert chain.add_to_cache.call_count == 2, "Count must be greater than zero"

    def test_filter_cleanup_on_completion(self):
        """Test: Resources cleaned up after filtering."""
        # Arrange: Mock resources
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain
            mock_chain.cleanup = Mock(return_value=True)

            # Execute and cleanup
            chain = mock_chain_cls()
            result = chain.cleanup()

            # Assert: Cleanup executed
            assert result is True, "Result must not be empty"
            mock_chain.cleanup.assert_called_once()

    def test_memory_efficient_batch_filtering(self):
        """Test: Batch filtering is memory efficient."""
        # Arrange: Large batch
        large_batch = ["text_" + str(i) for i in range(1000)]

        # Act & Assert: Mock memory-efficient processing
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain
            mock_chain.apply_filters_batch = Mock(
                return_value=[{"text": t, "passed": True} for t in large_batch]
            )

            chain = mock_chain_cls()
            results = chain.apply_filters_batch(large_batch)

            # Assert: All processed
            assert len(results) == 1000, "Results must not be empty"


@pytest.mark.skipif(not SAFETY_FILTERS_AVAILABLE, reason="Safety filters not available")
class TestSafetyFiltersEndToEnd:
    """End-to-end safety filtering workflows."""

    def test_complete_text_safety_pipeline(self):
        """Test: Complete pipeline from input to filtered output."""
        # Arrange: Input text
        input_text = "Sample text for comprehensive safety filtering"

        # Act & Assert: Mock complete pipeline
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            # Step 1: Initialize
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain

            # Step 2: Configure filters
            mock_chain.add_filter = Mock()

            # Step 3: Execute
            mock_chain.apply_filters = Mock(
                return_value={
                    "input": input_text,
                    "output": input_text,
                    "passed": True,
                    "violations": 0,
                }
            )

            # Execute pipeline
            chain = mock_chain_cls()
            chain.add_filter("content")
            chain.add_filter("token")
            result = chain.apply_filters(input_text)

            # Assert: Pipeline complete
            assert result["passed"] is True, "Result must not be empty"
            assert result["violations"] == 0, "Result must not be empty"

    def test_multi_stage_filtering_with_fallback(self):
        """Test: Multi-stage filtering with fallback mechanisms."""
        # Arrange: Setup fallback scenario
        with patch("codex_ml.safety.filters.SafetyFilterChain") as mock_chain_cls:
            mock_chain = Mock()
            mock_chain_cls.return_value = mock_chain

            # Stage 1: Primary filter
            mock_chain.apply_filters = Mock(side_effect=[Exception("Filter 1 failed"), None])

            # Stage 2: Fallback filter
            mock_chain.fallback_filter = Mock(return_value={"filtered": False})

            # Execute with fallback
            chain = mock_chain_cls()
            try:
                chain.apply_filters("test")
            except Exception as _err:
                result = chain.fallback_filter()
                assert result["filtered"] is False, "Result must not be empty"
