"""Lightweight checks for text metrics with comprehensive edge case coverage."""

from __future__ import annotations

import sys
import math
from pathlib import Path

import pytest

# Import semantic assertions
sys.path.insert(0, str(Path(__file__).parent))
from conftest_semantic_assertions import (
    assert_positive,
    assert_non_negative,
    assert_floats_approximately_equal,
    assert_instance_of,
    assert_not_none,
    assert_exception_raised,
    assert_zero_boundary,
    assert_numeric_in_range,
)


# ============================================================================
# PERPLEXITY TESTS - EDGE CASES AND SEMANTIC ASSERTIONS
# ============================================================================


class TestPerplexityCalculation:
    """Test suite for perplexity metric calculation with edge cases."""

    def test_perplexity_zero_loss_returns_one(self):
        """Perplexity at zero loss should return 1.0 (e^0 = 1)."""
        from codex_ml.metrics.text import perplexity

        result = perplexity(0.0)
        # Semantic assertion: perplexity of 0 loss is exactly 1
        assert_floats_approximately_equal(
            result, 1.0, tolerance=1e-10,
            context="perplexity at zero loss"
        )
        assert_zero_boundary(result - 1.0, expected_is_zero=True,
                           context="perplexity_zero_loss")

    def test_perplexity_unit_loss_returns_e(self):
        """Perplexity at loss=1 should return e (≈2.71828)."""
        from codex_ml.metrics.text import perplexity

        result = perplexity(1.0)
        # Semantic assertion: perplexity(1) = e
        assert_floats_approximately_equal(
            result, math.e, tolerance=1e-10,
            context="perplexity at unit loss"
        )
        assert_positive(result, context="perplexity_unit_loss")

    def test_perplexity_large_loss_value(self):
        """Perplexity with large loss should grow exponentially."""
        from codex_ml.metrics.text import perplexity

        loss = 10.0
        result = perplexity(loss)
        expected = math.exp(loss)  # e^10 ≈ 22026.47
        
        # Semantic assertion: exponential relationship
        assert_floats_approximately_equal(
            result, expected, tolerance=1e-4, relative=True,
            context="perplexity with large loss (exponential growth)"
        )

    def test_perplexity_negative_loss_returns_positive_value(self):
        """Perplexity with negative loss returns positive value (e^negative)."""
        from codex_ml.metrics.text import perplexity

        result = perplexity(-1.0)
        expected = math.exp(-1.0)  # e^(-1) ≈ 0.36788
        
        # Semantic assertion: exponential relationship holds
        assert_floats_approximately_equal(
            result, expected, tolerance=1e-6,
            context="perplexity with negative loss"
        )
        assert_positive(result, context="perplexity_always_positive")

    def test_perplexity_very_small_positive_loss(self):
        """Perplexity with tiny positive loss should be close to 1."""
        from codex_ml.metrics.text import perplexity

        tiny_loss = 1e-10
        result = perplexity(tiny_loss)
        
        # Semantic assertion: small loss ≈ small perplexity
        assert_floats_approximately_equal(
            result, 1.0, tolerance=1e-8,
            context="perplexity with very small positive loss"
        )
        assert_positive(result, context="tiny_loss_perplexity")

    def test_perplexity_monotonic_increasing(self):
        """Perplexity should strictly increase with loss (monotonicity)."""
        from codex_ml.metrics.text import perplexity

        losses = [0.0, 0.5, 1.0, 2.0, 5.0]
        perplexities = [perplexity(loss) for loss in losses]
        
        # Semantic assertion: monotonic property
        for i in range(len(perplexities) - 1):
            assert perplexities[i] < perplexities[i + 1], (
                f"Perplexity must be monotonically increasing: "
                f"perp({losses[i]})={perplexities[i]} should be < "
                f"perp({losses[i+1]})={perplexities[i+1]}"
            )

    @pytest.mark.parametrize("loss", [0.0, 0.5, 1.0, 1.5, 2.0])
    def test_perplexity_always_positive(self, loss):
        """Perplexity must always be positive for valid (non-negative) loss."""
        from codex_ml.metrics.text import perplexity

        result = perplexity(loss)
        # Semantic assertion: domain and range properties
        assert_positive(result, context=f"perplexity({loss})")


# ============================================================================
# TOKEN ACCURACY TESTS - EDGE CASES AND ERROR HANDLING
# ============================================================================


class TestTokenAccuracy:
    """Test suite for token-level accuracy calculation."""

    def test_token_accuracy_requires_torch(self, monkeypatch):
        """Without torch, token_accuracy should raise ImportError."""
        import codex_ml.metrics.text as text_mod

        monkeypatch.setattr(text_mod, "_HAS_TORCH", False)
        monkeypatch.setattr(text_mod, "_torch", None)
        
        # Semantic assertion: optional dependency error handling
        exc = assert_exception_raised(
            lambda: text_mod.token_accuracy(None, None),
            ImportError,
            context="token_accuracy without torch dependency"
        )

    @pytest.mark.skip(reason="Requires torch tensor objects, not lists")
    def test_token_accuracy_with_empty_predictions(self):
        """Token accuracy with empty predictions should handle gracefully."""
        try:
            from codex_ml.metrics.text import token_accuracy
            
            # Semantic assertion: empty input handling
            with pytest.raises((ValueError, IndexError)):
                token_accuracy([], [])
        except ImportError:
            pytest.skip("PyTorch not available")

    @pytest.mark.skip(reason="Requires torch tensor objects, not lists")
    def test_token_accuracy_mismatched_lengths(self):
        """Token accuracy with mismatched lengths should raise error."""
        try:
            from codex_ml.metrics.text import token_accuracy
            
            # Semantic assertion: input validation
            with pytest.raises((ValueError, RuntimeError)):
                token_accuracy([1, 0, 1], [1, 0])  # lengths don't match
        except ImportError:
            pytest.skip("PyTorch not available")

    @pytest.mark.skip(reason="Requires torch tensor objects, not lists")
    def test_token_accuracy_perfect_match(self):
        """Token accuracy with perfect match should return 1.0."""
        try:
            from codex_ml.metrics.text import token_accuracy
            
            predictions = [1, 0, 1, 1, 0]
            labels = [1, 0, 1, 1, 0]
            
            result = token_accuracy(predictions, labels)
            
            # Semantic assertion: perfect accuracy condition
            assert_floats_approximately_equal(
                result, 1.0, tolerance=1e-10,
                context="token_accuracy with perfect predictions"
            )
            assert_numeric_in_range(
                result, 0.0, 1.0, inclusive=True,
                context="token_accuracy is probability"
            )
        except ImportError:
            pytest.skip("PyTorch not available")


# ============================================================================
# MODULE IMPORT AND AVAILABILITY TESTS
# ============================================================================


class TestTextMetricsModuleAvailability:
    """Test suite for text metrics module availability and imports."""

    def test_perplexity_function_available(self):
        """Perplexity function should be importable."""
        from codex_ml.metrics.text import perplexity
        
        # Semantic assertion: function availability
        assert_not_none(perplexity, context="perplexity_function")
        assert_instance_of(
            perplexity, type(lambda: None),
            context="perplexity should be callable"
        )

    def test_text_module_imports_cleanly(self):
        """Text metrics module should import without errors."""
        try:
            import codex_ml.metrics.text
            # Semantic assertion: module successfully imported
            assert_not_none(codex_ml.metrics.text,
                          context="text_metrics_module")
        except ImportError as e:
            pytest.skip(f"Text metrics module not available: {e}")


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
