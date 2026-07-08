"""
Test Randomness

Test module for randomness.
"""

#!/usr/bin/env python3
"""Tests for common.randomness module."""
import os
import random
from unittest.mock import Mock, patch

from src.common.randomness import set_seed


def test_set_seed_with_explicit_value():
    """Test that set_seed sets the seed to explicit value."""
    result = set_seed(42)
    assert result == 42, "Result must not be empty"
    # Verify Python random is seeded
    val1 = random.random()
    set_seed(42)
    val2 = random.random()
    assert val1 == val2, "Same seed should produce same random values"


def test_set_seed_with_none_uses_default():
    """Test that set_seed with None uses default seed 1337."""
    result = set_seed(None)
    assert result == 1337, "Result must not be empty"


def test_set_seed_with_none_uses_env_variable(monkeypatch):
    """Test that set_seed with None uses SEED environment variable."""
    monkeypatch.setenv("SEED", "9999")
    result = set_seed(None)
    assert result == 9999, "Result must not be empty"


def test_set_seed_sets_numpy_seed_when_available():
    """Test that numpy seed is set when numpy is available."""
    try:
        import numpy as np

        set_seed(42)
        val1 = np.random.random()
        set_seed(42)
        val2 = np.random.random()
        assert val1 == val2, "Same seed should produce same numpy random values"
    except ImportError:
        # Skip if numpy not available
        _ = None  # suppressed: no action needed


def test_set_seed_handles_missing_numpy_gracefully():
    """Test that set_seed works even if numpy is not available."""
    with patch("src.common.randomness.np", None):
        result = set_seed(42)
        assert result == 42, "Result must not be empty"


def test_set_seed_handles_missing_torch_gracefully():
    """Test that set_seed works even if torch is not available."""
    with patch("src.common.randomness.torch", None):
        result = set_seed(42)
        assert result == 42, "Result must not be empty"


def test_set_seed_sets_torch_seed_when_available():
    """Test that torch seed is set when torch is available."""
    mock_torch = Mock()
    mock_torch.manual_seed = Mock()
    mock_torch.cuda = Mock()
    mock_torch.cuda.is_available = Mock(return_value=False)
    mock_torch.backends = Mock()
    mock_torch.backends.cudnn = Mock()

    with patch("src.common.randomness.torch", mock_torch):
        result = set_seed(42)
        assert result == 42, "Result must not be empty"
        mock_torch.manual_seed.assert_called_once_with(42)


def test_set_seed_handles_torch_manual_seed_exception():
    """Test that exceptions in torch.manual_seed are handled gracefully."""
    mock_torch = Mock()
    mock_torch.manual_seed = Mock(side_effect=RuntimeError("test error"))

    with patch("src.common.randomness.torch", mock_torch):
        result = set_seed(42)
        assert result == 42, "Result must not be empty"


def test_set_seed_sets_cuda_seeds_when_available():
    """Test that CUDA seeds are set when CUDA is available."""
    mock_torch = Mock()
    mock_torch.manual_seed = Mock()
    mock_torch.cuda = Mock()
    mock_torch.cuda.is_available = Mock(return_value=True)
    mock_torch.cuda.manual_seed_all = Mock()
    mock_torch.backends = Mock()
    mock_torch.backends.cudnn = Mock()

    with patch("src.common.randomness.torch", mock_torch):
        result = set_seed(42)
        assert result == 42, "Result must not be empty"
        mock_torch.cuda.manual_seed_all.assert_called_once_with(42)


def test_set_seed_sets_cudnn_deterministic_flags():
    """Test that CuDNN deterministic flags are set."""
    mock_torch = Mock()
    mock_torch.manual_seed = Mock()
    mock_torch.cuda = Mock()
    mock_torch.cuda.is_available = Mock(return_value=False)
    mock_backends = Mock()
    mock_cudnn = Mock()
    # Configure mock to allow attribute assignment and retrieval
    mock_cudnn.deterministic = False
    mock_cudnn.benchmark = True
    mock_backends.cudnn = mock_cudnn
    mock_torch.backends = mock_backends

    with patch("src.common.randomness.torch", mock_torch):
        set_seed(42)
        # Check that the attributes were set correctly
        assert mock_cudnn.deterministic is True, "deterministic is not valid"
        assert mock_cudnn.benchmark is False, "benchmark is not valid"


def test_set_seed_handles_cudnn_exception_gracefully():
    """Test that exceptions when setting CuDNN flags are handled gracefully."""
    mock_torch = Mock()
    mock_torch.manual_seed = Mock()
    mock_torch.cuda = Mock()
    mock_torch.cuda.is_available = Mock(return_value=False)
    mock_backends = Mock()
    mock_cudnn = Mock()
    # Make setting deterministic raise an exception
    type(mock_cudnn).deterministic = property(
        fget=lambda self: False,
        fset=lambda self, value: (_ for _ in ()).throw(RuntimeError("test")),
    )
    mock_backends.cudnn = mock_cudnn
    mock_torch.backends = mock_backends

    with patch("src.common.randomness.torch", mock_torch):
        result = set_seed(42)
        assert result == 42, "Result must not be empty"


def test_set_seed_returns_used_seed():
    """Test that set_seed returns the seed that was actually used."""
    result = set_seed(12345)
    assert result == 12345, "Result must not be empty"

    result = set_seed(None)
    assert result == 1337 or result == int(os.environ.get("SEED", "1337"))
