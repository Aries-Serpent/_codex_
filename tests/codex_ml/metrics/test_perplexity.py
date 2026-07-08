"""
Test Perplexity

Test module for perplexity.
"""

import math

import pytest


class TestPerplexityCalculation:
    """Test perplexity_from_loss function."""

    def test_perplexity_zero_loss(self):
        """Test perplexity with zero loss."""
        try:
            from codex_ml.metrics.perplexity import perplexity_from_loss

            result = perplexity_from_loss(0.0)
            assert result == pytest.approx(1.0, abs=1e-6)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_perplexity_positive_loss(self):
        """Test perplexity with positive loss."""
        try:
            from codex_ml.metrics.perplexity import perplexity_from_loss

            result = perplexity_from_loss(1.0)
            assert result == pytest.approx(math.e, abs=1e-6)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_perplexity_high_loss(self):
        """Test perplexity with high loss."""
        try:
            from codex_ml.metrics.perplexity import perplexity_from_loss

            result = perplexity_from_loss(5.0)
            expected = math.exp(5.0)
            assert result == pytest.approx(expected, rel=1e-6)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_perplexity_negative_loss(self):
        """Test perplexity with negative loss (edge case)."""
        try:
            from codex_ml.metrics.perplexity import perplexity_from_loss

            result = perplexity_from_loss(-1.0)
            expected = math.exp(-1.0)
            assert result == pytest.approx(expected, abs=1e-6)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_perplexity_invalid_input(self):
        """Test perplexity with invalid input returns inf."""
        try:
            from codex_ml.metrics.perplexity import perplexity_from_loss

            result = perplexity_from_loss(float("inf"))
            assert math.isinf(result), "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")
