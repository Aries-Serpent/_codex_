"""
Test Rng Checkpoint

Test module for rng checkpoint.
"""

#!/usr/bin/env python3
"""Tests for RNG checkpoint functionality."""
import json
import random
import sys
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import pytest

from codex_ml.training.rng_checkpoint import RNGState, set_seed


def test_rng_state_capture():
    """Test that RNG state can be captured."""
    rng_state = RNGState()
    rng_state.capture()

    assert rng_state.state is not None, "state must be initialized"
    assert isinstance(rng_state.state, dict)
    assert len(rng_state.state) > 0, "Collection must not be empty"


def test_rng_state_restore_determinism():
    """Test that restoring RNG state produces deterministic results."""
    # Set a specific seed
    set_seed(42)

    # Capture state
    rng_state = RNGState()
    rng_state.capture()

    # Generate some random numbers
    val1 = random.random()

    try:
        import numpy as np

        np_val1 = np.random.rand()
    except ImportError:
        np_val1 = None

    # Restore state
    rng_state.restore()

    # Generate again - should be same
    val2 = random.random()
    assert val1 == val2, "Python random should be deterministic after restore"

    if np_val1 is not None:
        np_val2 = np.random.rand()
        assert np_val1 == np_val2, "NumPy random should be deterministic after restore"


def test_rng_state_save_and_load(tmp_path):
    """Test saving and loading RNG state from file."""
    # Capture state
    set_seed(123)
    rng_state = RNGState()
    rng_state.capture()

    # Save to file
    save_path = tmp_path / "test_rng.json"
    rng_state.save_to_file(save_path)

    assert save_path.exists(), "Condition must be true"
    assert save_path.stat().st_size > 0, "st_size must be greater than zero"

    # Verify JSON is valid
    with open(save_path) as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_rng_state_load_from_file(tmp_path):
    """Test loading RNG state from file."""
    # Save state
    set_seed(456)
    rng_state1 = RNGState()
    rng_state1.capture()

    save_path = tmp_path / "test_rng.json"
    rng_state1.save_to_file(save_path)

    # Generate random number
    val1 = random.random()

    # Load state from file
    rng_state2 = RNGState.load_from_file(save_path)
    rng_state2.restore()

    # Generate again - should match
    val2 = random.random()
    assert val1 == val2, "val1 is not valid"


def test_rng_state_path_for_checkpoint():
    """Test that checkpoint path generation works correctly."""
    checkpoint_path = Path("/path/to/checkpoint.pt")
    rng_path = RNGState.path_for_checkpoint(checkpoint_path)

    assert rng_path == Path("/path/to/checkpoint.pt.rng.json"), "rng_path is not valid"
    assert rng_path.suffix == ".json", "suffix is not valid"
    assert ".rng.json" in str(rng_path), "Condition must be true"


def test_set_seed_sets_python_random():
    """Test that set_seed sets Python random."""
    set_seed(789)
    val1 = random.random()

    set_seed(789)
    val2 = random.random()

    assert val1 == val2, "val1 is not valid"


def test_set_seed_sets_numpy_random():
    """Test that set_seed sets NumPy random if available."""
    try:
        import numpy as np

        set_seed(101112)
        val1 = np.random.rand()

        set_seed(101112)
        val2 = np.random.rand()

        assert val1 == val2, "val1 is not valid"
    except ImportError:
        # Skip if NumPy not available
        pytest.skip("NumPy not available")


def test_rng_state_handles_missing_file():
    """Test that loading from non-existent file raises appropriate error."""
    with pytest.raises(FileNotFoundError):
        RNGState.load_from_file(Path("/nonexistent/path/rng.json"))


def test_rng_state_save_creates_parent_dirs(tmp_path):
    """Test that save creates parent directories if needed."""
    nested_path = tmp_path / "nested" / "dir" / "rng.json"

    rng_state = RNGState()
    rng_state.capture()
    rng_state.save_to_file(nested_path)

    assert nested_path.exists(), "Condition must be true"
    assert nested_path.parent.exists(), "Condition must be true"


def test_rng_state_round_trip_preserves_state(tmp_path):
    """Test that save/load round trip preserves exact state."""
    set_seed(131415)

    # Capture initial state
    rng_state1 = RNGState()
    rng_state1.capture()

    # Save and load
    save_path = tmp_path / "roundtrip_rng.json"
    rng_state1.save_to_file(save_path)
    rng_state2 = RNGState.load_from_file(save_path)

    # States should be equal
    assert rng_state1.state == rng_state2.state, "state is not valid"


def test_rng_state_different_seeds_produce_different_values():
    """Test that different seeds produce different random values."""
    set_seed(111)
    val1 = random.random()

    set_seed(222)
    val2 = random.random()

    assert val1 != val2, "val1 is not valid"


def test_rng_state_empty_state_restore_is_noop():
    """Test that restoring empty state doesn't crash."""
    rng_state = RNGState()
    # Don't capture, leave state empty
    rng_state.restore()  # Should not raise
