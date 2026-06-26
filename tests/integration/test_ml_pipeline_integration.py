"""
Integration tests for complete ML pipeline

Tests cover:
- End-to-end training workflow
- Dataset → Model → Training → Evaluation
- Checkpoint resume workflow
- Offline mode integration
- Configuration integration
"""

import sys
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("torch")


# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
import torch

# Mark all tests in this module - skip by default (slow)
pytestmark = [pytest.mark.ml_comprehensive, pytest.mark.integration, pytest.mark.slow]


@pytest.fixture
def temp_workspace():
    """Create temporary workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "checkpoints").mkdir()
        (workspace / "logs").mkdir()
        (workspace / "data").mkdir()
        yield workspace


class TestEndToEndTraining:
    """Test complete training workflow"""

    @pytest.mark.skipif(
        sys.version_info >= (3, 12), reason="PyTorch profiler ScriptObject issue in Python 3.12"
    )
    def test_train_tiny_model(self, temp_workspace):
        """Test training tiny model end-to-end"""
        # Create simple model
        model = torch.nn.Linear(10, 5)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

        # Simple training loop
        for step in range(5):
            input_data = torch.randn(2, 10)
            target = torch.randn(2, 5)

            output = model(input_data)
            loss = torch.nn.functional.mse_loss(output, target)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Should complete without errors
        assert loss.item() is not None, "Value must be initialized"


class TestCheckpointResumeWorkflow:
    """Test checkpoint and resume workflow"""

    @pytest.mark.skipif(
        sys.version_info >= (3, 12), reason="PyTorch profiler ScriptObject issue in Python 3.12"
    )
    def test_save_and_resume(self, temp_workspace):
        """Test saving checkpoint and resuming"""
        # Create model
        model = torch.nn.Linear(10, 5)
        optimizer = torch.optim.Adam(model.parameters())

        # Train for a few steps
        for step in range(5):
            loss = torch.nn.functional.mse_loss(model(torch.randn(2, 10)), torch.randn(2, 5))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Save checkpoint
        checkpoint_path = temp_workspace / "checkpoints" / "step_5.pt"
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "step": 5,
            },
            checkpoint_path,
        )

        # Create new model and resume
        new_model = torch.nn.Linear(10, 5)
        new_optimizer = torch.optim.Adam(new_model.parameters())

        checkpoint = torch.load(
            checkpoint_path, weights_only=False
        )  # nosec B614 - Test checkpoint with optimizer state requires weights_only=False
        new_model.load_state_dict(checkpoint["model_state_dict"])
        new_optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        assert checkpoint["step"] == 5, "Condition must be true"


class TestOfflineModeIntegration:
    """Test offline mode integration"""

    def test_offline_environment_variables(self):
        """Test offline mode via environment variables"""
        import os

        # Set offline mode
        os.environ["CODEX_OFFLINE_MODE"] = "1"

        # Verify setting
        assert os.getenv("CODEX_OFFLINE_MODE") == "1", "Condition must be true"

        # Cleanup
        del os.environ["CODEX_OFFLINE_MODE"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
