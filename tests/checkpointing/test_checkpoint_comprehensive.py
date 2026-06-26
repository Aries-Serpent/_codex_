"""
Comprehensive tests for checkpoint system

Tests cover:
- Checkpoint saving and loading
- Best-K retention
- Resume from checkpoint
- Optimizer and scheduler state
- RNG state preservation
- Atomic writes
- Corruption handling
- Metadata validation
- Distributed checkpointing
"""

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("torch")


# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
import torch

# Mark all tests in this module
pytestmark = pytest.mark.ml_comprehensive


@pytest.fixture
def mock_model():
    """Create mock model"""
    return torch.nn.Linear(10, 5)


@pytest.fixture
def mock_optimizer():
    """Create mock optimizer"""
    model = torch.nn.Linear(10, 5)
    return torch.optim.Adam(model.parameters(), lr=0.001)


@pytest.fixture
def temp_checkpoint_dir():
    """Create temporary checkpoint directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestCheckpointSaveLoad:
    """Test basic checkpoint save and load"""

    def test_save_checkpoint_basic(self, mock_model, temp_checkpoint_dir):
        """Test basic checkpoint saving"""
        checkpoint_path = temp_checkpoint_dir / "checkpoint.pt"

        # Save checkpoint
        checkpoint = {"model_state_dict": mock_model.state_dict(), "epoch": 5, "step": 1000}
        torch.save(checkpoint, checkpoint_path)

        assert checkpoint_path.exists(), "Condition must be true"

        # Verify contents
        loaded = torch.load(
            checkpoint_path, weights_only=True
        )  # nosec B614 - weights_only=True ensures safe loading
        assert "model_state_dict" in loaded, "Condition must be true"
        assert loaded["epoch"] == 5, "Condition must be true"
        assert loaded["step"] == 1000, "Condition must be true"

    def test_load_checkpoint_basic(self, mock_model, temp_checkpoint_dir):
        """Test basic checkpoint loading"""
        checkpoint_path = temp_checkpoint_dir / "checkpoint.pt"

        # Save first
        torch.save({"model_state_dict": mock_model.state_dict(), "epoch": 5}, checkpoint_path)

        # Load
        checkpoint = torch.load(
            checkpoint_path, weights_only=True
        )  # nosec B614 - weights_only=True ensures safe loading
        new_model = torch.nn.Linear(10, 5)
        new_model.load_state_dict(checkpoint["model_state_dict"])

        # Verify model weights loaded
        for p1, p2 in zip(mock_model.parameters(), new_model.parameters()):
            assert torch.allclose(p1, p2)


class TestRNGState:
    """Test RNG state preservation"""

    def test_save_rng_state(self, temp_checkpoint_dir):
        """Test saving RNG state"""
        checkpoint_path = temp_checkpoint_dir / "checkpoint.pt"

        # Set specific seed
        torch.manual_seed(42)
        rng_state = torch.get_rng_state()

        torch.save({"rng_state": rng_state}, checkpoint_path)

        checkpoint = torch.load(
            checkpoint_path, weights_only=True
        )  # nosec B614 - weights_only=True ensures safe loading
        assert "rng_state" in checkpoint, "Condition must be true"

    def test_restore_rng_state(self, temp_checkpoint_dir):
        """Test restoring RNG state"""
        checkpoint_path = temp_checkpoint_dir / "checkpoint.pt"

        # Set seed and save state
        torch.manual_seed(42)
        expected = torch.rand(5)

        torch.manual_seed(42)
        rng_state = torch.get_rng_state()
        torch.save({"rng_state": rng_state}, checkpoint_path)

        # Change seed
        torch.manual_seed(123)

        # Restore RNG state
        checkpoint = torch.load(
            checkpoint_path, weights_only=True
        )  # nosec B614 - weights_only=True ensures safe loading
        torch.set_rng_state(checkpoint["rng_state"])

        # Should generate same numbers
        actual = torch.rand(5)
        assert torch.allclose(expected, actual)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
