"""Tests for reproducibility seed manager."""

import json
import tempfile
from pathlib import Path

import pytest


class TestSeedManager:
    """Test seed management."""

    def test_set_seeds(self):
        """Test setting all seeds."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        manager = SeedManager(seed=42)
        state = manager.set_all_seeds()

        assert state.seed == 42, "seed is not valid"
        assert state.python_hash_seed is not None, "python_hash_seed must be initialized"

    def test_save_load_state(self):
        """Test saving and loading seed state."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seed_state.json"

            # Save
            manager = SeedManager(seed=123)
            manager.set_all_seeds()
            manager.save_state(str(path))

            # Verify file exists and has content
            assert path.exists(), "Condition must be true"
            with open(path) as f:
                data = json.load(f)
            assert data["seed"] == 123, "Data must not be empty"

            # Load
            loaded = SeedManager.load_state(str(path))
            assert loaded.seed == 123, "seed is not valid"

    def test_convenience_function(self):
        """Test set_seed convenience function."""
        from codex_ml.reproducibility.seed_manager import set_seed

        state = set_seed(42)
        assert state.seed == 42, "seed is not valid"

    def test_deterministic_mode(self):
        """Test deterministic mode setting."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        manager = SeedManager(seed=42, deterministic=True)
        state = manager.set_all_seeds()

        assert state.seed == 42, "seed is not valid"
        # Deterministic flags are set based on torch availability
        if state.torch_seed is not None:
            assert state.cudnn_deterministic is True, "cudnn_deterministic is not valid"
            assert state.cudnn_benchmark is False, "cudnn_benchmark is not valid"

    def test_non_deterministic_mode(self):
        """Test non-deterministic mode (default)."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        manager = SeedManager(seed=42, deterministic=False)
        state = manager.set_all_seeds()

        assert state.seed == 42, "seed is not valid"
        # Non-deterministic flags
        assert state.cudnn_deterministic is False, "cudnn_deterministic is not valid"
        assert state.cudnn_benchmark is True, "cudnn_benchmark is not valid"

    def test_save_without_set_raises_error(self):
        """Saving without setting seeds should raise error."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seed_state.json"

            manager = SeedManager(seed=42)
            # Don't call set_all_seeds()

            with pytest.raises(RuntimeError, match="No seed state"):
                manager.save_state(str(path))

    def test_environment_hash(self):
        """Test environment hash generation."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        manager = SeedManager(seed=42)
        manager.set_all_seeds()

        hash1 = manager.get_environment_hash()

        # Hash should be a string
        assert isinstance(hash1, str)
        # Should be 16 characters (truncated SHA256)
        assert len(hash1) == 16, "Hash1 must not be empty"

        # Same manager should give same hash
        hash2 = manager.get_environment_hash()
        assert hash1 == hash2, "hash1 is not valid"

    def test_different_seeds_different_states(self):
        """Different seeds should produce different states."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        manager1 = SeedManager(seed=42)
        state1 = manager1.set_all_seeds()

        manager2 = SeedManager(seed=123)
        state2 = manager2.set_all_seeds()

        assert state1.seed != state2.seed, "seed is not valid"

    def test_warn_on_missing_libraries(self):
        """Test warning behavior for missing libraries."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        # Should not crash even if libraries are missing
        manager = SeedManager(seed=42, warn_on_missing=True)
        state = manager.set_all_seeds()

        # Should at least have Python seed
        assert state.seed == 42, "seed is not valid"
        assert state.python_hash_seed is not None, "python_hash_seed must be initialized"

    def test_no_warnings_when_disabled(self):
        """Test disabling warnings for missing libraries."""
        from codex_ml.reproducibility.seed_manager import SeedManager

        manager = SeedManager(seed=42, warn_on_missing=False)
        state = manager.set_all_seeds()

        # Should still work
        assert state.seed == 42, "seed is not valid"


class TestSeedState:
    """Test SeedState dataclass."""

    def test_seed_state_creation(self):
        """Test creating SeedState."""
        from codex_ml.reproducibility.seed_manager import SeedState

        state = SeedState(
            seed=42,
            python_hash_seed="42",
            numpy_seed=42,
        )

        assert state.seed == 42, "seed is not valid"
        assert state.python_hash_seed == "42", "python_hash_seed is not valid"
        assert state.numpy_seed == 42, "numpy_seed is not valid"

    def test_seed_state_defaults(self):
        """Test SeedState default values."""
        from codex_ml.reproducibility.seed_manager import SeedState

        state = SeedState(seed=42, python_hash_seed="42")

        # Check defaults
        assert state.numpy_seed is None, "numpy_seed is not valid"
        assert state.torch_seed is None, "torch_seed is not valid"
        assert state.cuda_seed is None, "cuda_seed is not valid"
        assert state.cudnn_deterministic is False, "cudnn_deterministic is not valid"
        assert state.cudnn_benchmark is True, "cudnn_benchmark is not valid"
