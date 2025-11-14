"""Tests for generative metrics (BLEU, ROUGE) with optional dependency gating.

These tests validate that:
1. Metrics work correctly when optional dependencies are installed
2. Metrics gracefully return None when dependencies are missing
3. Deterministic behavior on trivial examples
"""
import sys
from pathlib import Path

import pytest

# Add src to path
_REPO_ROOT = Path(__file__).parent.parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


# Check if optional dependencies are available
try:
    import nltk  # noqa: F401
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import rouge_score  # noqa: F401
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False


class TestBLEUMetric:
    """Tests for BLEU metric."""

    @pytest.mark.skipif(not NLTK_AVAILABLE, reason="nltk not installed")
    def test_bleu_perfect_match(self):
        """Test BLEU with perfect match (trivial case)."""
        from codex_ml.metrics.registry import get_metric
        
        bleu = get_metric("bleu")
        
        # Perfect match should give high score
        preds = ["the cat sat on the mat"]
        targets = ["the cat sat on the mat"]
        
        score = bleu(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert score > 0.9  # Should be close to 1.0 for perfect match

    @pytest.mark.skipif(not NLTK_AVAILABLE, reason="nltk not installed")
    def test_bleu_no_match(self):
        """Test BLEU with no matching words."""
        from codex_ml.metrics.registry import get_metric
        
        bleu = get_metric("bleu")
        
        # No overlapping words
        preds = ["foo bar baz"]
        targets = ["qux quux corge"]
        
        score = bleu(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert score == 0.0  # No matching n-grams

    @pytest.mark.skipif(not NLTK_AVAILABLE, reason="nltk not installed")
    def test_bleu_partial_match(self):
        """Test BLEU with partial match."""
        from codex_ml.metrics.registry import get_metric
        
        bleu = get_metric("bleu")
        
        # Some overlapping words
        preds = ["the cat sat"]
        targets = ["the dog sat"]
        
        score = bleu(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert 0.0 < score < 1.0  # Partial match

    @pytest.mark.skipif(not NLTK_AVAILABLE, reason="nltk not installed")
    def test_bleu_multiple_samples(self):
        """Test BLEU with multiple prediction-target pairs."""
        from codex_ml.metrics.registry import get_metric
        
        bleu = get_metric("bleu")
        
        preds = [
            "the cat sat on the mat",
            "hello world",
        ]
        targets = [
            "the cat sat on the mat",
            "hello world",
        ]
        
        score = bleu(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert score > 0.9  # Perfect matches

    def test_bleu_works_offline(self):
        """Test that BLEU works without nltk (using offline implementation)."""
        from codex_ml.metrics.registry import get_metric
        
        bleu = get_metric("bleu")
        
        # Offline implementation always returns a score
        result = bleu(["test"], ["test"])
        assert result is not None
        assert isinstance(result, float)
        assert result > 0.0  # Perfect match should score well


class TestROUGEMetric:
    """Tests for ROUGE-L metric."""

    @pytest.mark.skipif(not ROUGE_AVAILABLE, reason="rouge-score not installed")
    def test_rouge_perfect_match(self):
        """Test ROUGE-L with perfect match (trivial case)."""
        from codex_ml.metrics.registry import get_metric
        
        rouge = get_metric("rougeL")
        
        # Perfect match should give high score
        preds = ["the quick brown fox"]
        targets = ["the quick brown fox"]
        
        score = rouge(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert score > 0.9  # Should be close to 1.0 for perfect match

    @pytest.mark.skipif(not ROUGE_AVAILABLE, reason="rouge-score not installed")
    def test_rouge_no_match(self):
        """Test ROUGE-L with no matching words."""
        from codex_ml.metrics.registry import get_metric
        
        rouge = get_metric("rougeL")
        
        # No overlapping words
        preds = ["foo bar baz"]
        targets = ["qux quux corge"]
        
        score = rouge(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert score == 0.0  # No matching subsequences

    @pytest.mark.skipif(not ROUGE_AVAILABLE, reason="rouge-score not installed")
    def test_rouge_partial_match(self):
        """Test ROUGE-L with partial match."""
        from codex_ml.metrics.registry import get_metric
        
        rouge = get_metric("rougeL")
        
        # Some overlapping words in sequence
        preds = ["the cat sat"]
        targets = ["the dog sat"]
        
        score = rouge(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert 0.0 < score < 1.0  # Partial match

    @pytest.mark.skipif(not ROUGE_AVAILABLE, reason="rouge-score not installed")
    def test_rouge_multiple_samples(self):
        """Test ROUGE-L with multiple prediction-target pairs."""
        from codex_ml.metrics.registry import get_metric
        
        rouge = get_metric("rougeL")
        
        preds = [
            "the quick brown fox",
            "hello world",
        ]
        targets = [
            "the quick brown fox",
            "hello world",
        ]
        
        score = rouge(preds, targets)
        assert score is not None
        assert isinstance(score, float)
        assert score > 0.9  # Perfect matches

    def test_rouge_works_offline(self):
        """Test that ROUGE works without rouge-score (using offline implementation)."""
        from codex_ml.metrics.registry import get_metric
        
        rouge = get_metric("rougeL")
        
        # Offline implementation always returns a score
        result = rouge(["test"], ["test"])
        assert result is not None
        assert isinstance(result, float)
        assert result > 0.0  # Perfect match should score well


class TestMetricRegistryIntegration:
    """Integration tests for metric registry with optional dependencies."""

    def test_metrics_registered(self):
        """Test that BLEU and ROUGE are registered in the metric registry."""
        from codex_ml.metrics.registry import list_metrics
        
        # Both should be registered regardless of dependency availability
        # Note: registry normalizes names to lowercase
        registered = list_metrics()
        assert "bleu" in registered
        assert "rougel" in registered  # Normalized to lowercase

    def test_get_metric_returns_callable(self):
        """Test that get_metric returns callable for BLEU and ROUGE."""
        from codex_ml.metrics.registry import get_metric
        
        bleu = get_metric("bleu")
        rouge = get_metric("rougeL")
        
        assert callable(bleu)
        assert callable(rouge)

    def test_metrics_handle_empty_inputs(self):
        """Test that metrics handle empty inputs gracefully."""
        from codex_ml.metrics.registry import get_metric
        
        bleu = get_metric("bleu")
        rouge = get_metric("rougeL")
        
        # Empty inputs - may return None or 0.0 depending on implementation
        bleu_result = bleu([], [])
        rouge_result = rouge([], [])
        
        # Should not raise, may return None or numeric value
        assert bleu_result is None or isinstance(bleu_result, (int, float))
        assert rouge_result is None or isinstance(rouge_result, (int, float))
