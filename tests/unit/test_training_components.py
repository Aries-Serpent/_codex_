"""
Unit tests for codex_ml.training module components.

Tests training loop functionality, loss computation, and metric logging.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


class TestTrainOneStep:
    """Test train_one_step function."""

    def test_train_one_step_import(self):
        """Test train_one_step can be imported."""
        from codex_ml.training.loop import train_one_step

        assert train_one_step is not None, "train_one_step must be initialized"
        assert callable(train_one_step), "Condition must be true"

    def test_train_one_step_reduces_loss(self):
        """Test train_one_step reduces loss value."""
        from codex_ml.training.loop import train_one_step

        loss = 10.0
        new_loss = train_one_step(loss)

        assert new_loss < loss, "new_loss is not valid"
        assert new_loss == pytest.approx(9.0, rel=0.01)

    def test_train_one_step_decay_factor(self):
        """Test train_one_step applies 0.9 decay factor."""
        from codex_ml.training.loop import train_one_step

        loss = 100.0
        new_loss = train_one_step(loss)

        assert new_loss == pytest.approx(90.0, rel=0.01)

    def test_train_one_step_multiple_iterations(self):
        """Test train_one_step over multiple iterations."""
        from codex_ml.training.loop import train_one_step

        loss = 10.0
        for _ in range(5):
            loss = train_one_step(loss)

        # After 5 iterations: 10 * 0.9^5 ≈ 5.9
        assert loss < 6.0, "loss is not valid"
        assert loss > 5.5, "loss must be greater than zero"


class TestTrainEpoch:
    """Test train_epoch function."""

    def test_train_epoch_import(self):
        """Test train_epoch can be imported."""
        from codex_ml.training.loop import train_epoch

        assert train_epoch is not None, "train_epoch must be initialized"
        assert callable(train_epoch), "Condition must be true"

    def test_train_epoch_empty_dataloader_raises(self):
        """Test train_epoch raises on empty dataloader."""
        from codex_ml.interfaces.contracts import TrainingContractError
        from codex_ml.training.loop import train_epoch

        model = MagicMock()
        dataloader = []
        state = {}

        with pytest.raises(TrainingContractError, match="Dataloader must not be empty"):
            train_epoch(model, dataloader, state)

    def test_train_epoch_missing_input_ids_raises(self):
        """Test train_epoch raises when input_ids missing."""
        from codex_ml.interfaces.contracts import TrainingContractError
        from codex_ml.training.loop import train_epoch

        model = MagicMock()
        dataloader = [{"other_key": "value"}]
        state = {}

        with pytest.raises(TrainingContractError, match="input_ids missing"):
            train_epoch(model, dataloader, state)

    def test_train_epoch_missing_loss_raises(self):
        """Test train_epoch raises when loss not returned."""
        from codex_ml.interfaces.contracts import TrainingContractError
        from codex_ml.training.loop import train_epoch

        model = MagicMock()
        model.step.return_value = {"other": "result"}  # No loss
        dataloader = [{"input_ids": [1, 2, 3]}]
        state = {}

        with pytest.raises(TrainingContractError, match="did not return loss"):
            train_epoch(model, dataloader, state)

    def test_train_epoch_success(self):
        """Test train_epoch with successful batch processing."""
        from codex_ml.training.loop import train_epoch

        model = MagicMock()
        model.step.return_value = {"loss": 0.5}
        dataloader = [
            {"input_ids": [1, 2, 3]},
            {"input_ids": [4, 5, 6]},
            {"input_ids": [7, 8, 9]},
        ]
        state = {}

        result = train_epoch(model, dataloader, state)

        assert "loss_mean" in result, "Result must not be empty"
        assert "loss_last" in result, "Result must not be empty"
        assert "num_batches" in result, "Result must not be empty"
        assert result["loss_mean"] == 0.5, "Result must not be empty"
        assert result["loss_last"] == 0.5, "Result must not be empty"
        assert result["num_batches"] == 3, "Result must not be empty"


class TestRunMinimalTraining:
    """Test run_minimal_training function."""

    def test_run_minimal_training_import(self):
        """Test run_minimal_training can be imported."""
        from codex_ml.training.loop import run_minimal_training

        assert run_minimal_training is not None, "run_minimal_training must be initialized"
        assert callable(run_minimal_training), "Condition must be true"

    def test_run_minimal_training_creates_directory(self):
        """Test run_minimal_training creates output directory."""
        from codex_ml.training.loop import run_minimal_training

        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "new_run"
            config = {}

            run_minimal_training(config, max_steps=1, run_dir=str(run_dir))

            assert run_dir.exists(), "Condition must be true"
            assert run_dir.is_dir(), "Condition must be true"

    def test_run_minimal_training_creates_metrics_file(self):
        """Test run_minimal_training creates metrics.ndjson."""
        from codex_ml.training.loop import run_minimal_training

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {}

            run_minimal_training(config, max_steps=2, run_dir=tmpdir)

            metrics_file = Path(tmpdir) / "metrics.ndjson"
            assert metrics_file.exists(), "Condition must be true"

    def test_run_minimal_training_returns_loss_final(self):
        """Test run_minimal_training returns loss_final."""
        from codex_ml.training.loop import run_minimal_training

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"training": {"base_loss": 10.0, "decay": 0.9}}

            result = run_minimal_training(config, max_steps=5, run_dir=tmpdir)

            assert "loss_final" in result, "Result must not be empty"
            assert isinstance(result["loss_final"], float)

    def test_run_minimal_training_default_config(self):
        """Test run_minimal_training with default config."""
        from codex_ml.training.loop import run_minimal_training

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {}  # Empty config, should use defaults

            result = run_minimal_training(config, max_steps=1, run_dir=tmpdir)

            assert "loss_final" in result, "Result must not be empty"
            # Default base_loss=10.0, after 1 step with decay: ~9.0
            assert result["loss_final"] < 10.0, "Result must not be empty"

    def test_run_minimal_training_min_steps(self):
        """Test run_minimal_training with minimum steps."""
        from codex_ml.training.loop import run_minimal_training

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {}

            # Should handle max_steps < 1 gracefully
            result = run_minimal_training(config, max_steps=0, run_dir=tmpdir)

            assert "loss_final" in result, "Result must not be empty"


class TestRunMinimalEvaluation:
    """Test run_minimal_evaluation function."""

    def test_run_minimal_evaluation_import(self):
        """Test run_minimal_evaluation can be imported."""
        from codex_ml.training.loop import run_minimal_evaluation

        assert run_minimal_evaluation is not None, "run_minimal_evaluation must be initialized"
        assert callable(run_minimal_evaluation), "Condition must be true"

    def test_run_minimal_evaluation_creates_directory(self):
        """Test run_minimal_evaluation creates output directory."""
        from codex_ml.training.loop import run_minimal_evaluation

        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "eval_run"
            config = {}

            run_minimal_evaluation(config, checkpoint="", run_dir=str(run_dir))

            assert run_dir.exists(), "Condition must be true"

    def test_run_minimal_evaluation_returns_score(self):
        """Test run_minimal_evaluation returns score."""
        from codex_ml.training.loop import run_minimal_evaluation

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"eval": {"base_score": 0.7}}

            result = run_minimal_evaluation(config, checkpoint="", run_dir=tmpdir)

            assert "score" in result, "Result must not be empty"
            assert 0.0 <= result["score"] <= 1.0, "Result must not be empty"

    def test_run_minimal_evaluation_with_checkpoint(self):
        """Test run_minimal_evaluation with checkpoint provided."""
        from codex_ml.training.loop import run_minimal_evaluation

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"eval": {"base_score": 0.5}}

            result = run_minimal_evaluation(config, checkpoint="model.pt", run_dir=tmpdir)

            # With checkpoint, should add 0.1 to base_score
            assert result["score"] == pytest.approx(0.6, rel=0.01)

    def test_run_minimal_evaluation_score_capped(self):
        """Test run_minimal_evaluation caps score at 1.0."""
        from codex_ml.training.loop import run_minimal_evaluation

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"eval": {"base_score": 0.95}}

            result = run_minimal_evaluation(config, checkpoint="model.pt", run_dir=tmpdir)

            # Even with +0.1, should not exceed 1.0
            assert result["score"] <= 1.0, "Result must not be empty"
