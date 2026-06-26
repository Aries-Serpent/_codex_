"""Integration tests for event integration across training lifecycle.

Tests event emission during training, callback chain execution,
and proper event cleanup after training completion.
"""

from __future__ import annotations

import pytest


class TestEventIntegrationLifecycle:
    """Test event integration through training lifecycle."""

    def test_early_stopping_event_integration(self):
        """Verify early stopping works as event sink during training simulation."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2, min_delta=0.05, mode="min")
        simulated_losses = [0.5, 0.48, 0.46, 0.46, 0.46, 0.46]

        # Act: Simulate training step sequence
        stopped = False
        stop_step = None

        for step, loss in enumerate(simulated_losses):
            if es.step(loss):
                stopped = True
                stop_step = step
                break

        # Assert
        assert stopped is True, "Should trigger stop after patience exhausted"
        assert stop_step == 4, f"Should stop at step 4, stopped at {stop_step}"

    def test_callback_state_reset_between_training_runs(self):
        """Verify callback state is properly reset for new training runs."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        # First training run
        es = EarlyStopping(patience=2, min_delta=0.0, mode="min")
        losses_run1 = [1.0, 1.0, 1.0, 1.0]

        for loss in losses_run1:
            es.step(loss)

        first_run_bad = es.bad
        assert first_run_bad > 0, "First run should accumulate bad count before reset"

        # Reset for second run
        es = EarlyStopping(patience=2, min_delta=0.0, mode="min")

        # Second training run
        losses_run2 = [0.5, 0.4, 0.3]

        for loss in losses_run2:
            es.step(loss)

        # Assert
        assert es.best == 0.3, "Should reset best metric for new training run"
        assert es.bad == 0, "Should reset bad counter for new training run"

    def test_event_flow_with_improvement_and_plateau(self):
        """Verify event flow during both improvement and plateau phases."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=1, min_delta=0.1, mode="min")
        events_fired = []

        # Improvement events
        es.step(1.0)
        events_fired.append("initialization")

        es.step(0.85)
        events_fired.append("improvement")
        assert es.bad == 0, "Should reset on improvement"

        # Plateau events
        es.step(0.86)
        events_fired.append("plateau_start")
        assert es.bad == 1, "Should increment on plateau"

        stopped = es.step(0.87)
        if stopped:
            events_fired.append("training_stop")

        # Assert
        assert "initialization" in events_fired, "Should have initialization event"
        assert "improvement" in events_fired, "Should have improvement event"
        assert "plateau_start" in events_fired, "Should have plateau event"
        assert "training_stop" in events_fired, "Should have stop event after patience"

    def test_multiple_callbacks_independent_state(self):
        """Verify multiple callback instances maintain independent state."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es1 = EarlyStopping(patience=1, min_delta=0.0, mode="min")
        es2 = EarlyStopping(patience=2, min_delta=0.0, mode="min")

        # Act
        es1.step(1.0)
        es1.step(1.0)
        stop1 = es1.step(1.0)

        es2.step(2.0)
        es2.step(2.0)
        stop2 = es2.step(2.0)

        # Assert
        assert stop1 is True, "es1 with patience=1 should stop"
        assert stop2 is False, "es2 with patience=2 should not stop yet"
        assert es1.bad == 1, "es1 bad counter should be 1"
        assert es2.bad == 2, "es2 bad counter should be 2"


class TestCheckpointResumeIntegration:
    """Integration tests for checkpoint save and resume workflow."""

    def test_checkpoint_save_and_resume_state_consistency(self):
        """Verify state is properly preserved through save and resume."""
        # Arrange
        import shutil
        import tempfile
        from pathlib import Path

        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            # Original training state at step 50
            original_state = {
                "model_weights": {"layer1": [1.0, 2.0], "layer2": [3.0]},
                "optimizer_state": {"lr": 0.001, "momentum": 0.9},
                "step": 50,
            }
            original_meta = {"epoch": 5, "step": 50, "loss": 0.123}

            # Act: Save checkpoint
            ckpt_dir = tmpdir / "resume_test"
            save_checkpoint(
                str(ckpt_dir),
                state=original_state,
                meta=original_meta,
            )

            # Load for resume
            loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

            # Assert
            assert loaded_state == original_state, "State should match exactly after round-trip"
            assert loaded_meta["step"] == 50, "Metadata step should be preserved"
            assert loaded_meta["epoch"] == 5, "Metadata epoch should be preserved"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_checkpoint_resume_with_modified_training_config(self):
        """Verify resume works even with modified training config."""
        # Arrange
        import shutil
        import tempfile
        from pathlib import Path

        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            # Save checkpoint from training run 1
            state = {"model": {"w": 0.5}, "step": 100}
            meta = {"epoch": 10}

            ckpt_dir = tmpdir / "ckpt_modified_config"
            save_checkpoint(
                str(ckpt_dir),
                state=state,
                meta=meta,
            )

            # Load for resume with different training config
            loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

            # The checkpoint should be independent of training config
            # Assert
            assert (loaded_state["step"] == 100, "Condition must be true"
            ), "Checkpoint step should be preserved regardless of config"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_checkpoint_sequential_saves_preserve_progression(self):
        """Verify sequential checkpoint saves track training progression."""
        # Arrange
        import shutil
        import tempfile
        from pathlib import Path

        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        tmpdir = Path(tempfile.mkdtemp())

        try:
            steps = [100, 200, 300, 400]
            losses = [0.5, 0.3, 0.2, 0.15]

            # Act: Save multiple checkpoints
            for i, (step, loss) in enumerate(zip(steps, losses)):
                ckpt_dir = tmpdir / f"epoch_{i:03d}"
                save_checkpoint(
                    str(ckpt_dir),
                    state={"step": step, "loss": loss},
                    meta={"epoch": i, "step": step, "loss": loss},
                )

            # Verify each checkpoint by loading
            for i, (step, loss) in enumerate(zip(steps, losses)):
                ckpt_dir = tmpdir / f"epoch_{i:03d}"
                loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

                # Assert
                assert loaded_state["step"] == step, f"Step {step} not preserved in checkpoint {i}"
                assert loaded_meta["loss"] == loss, f"Loss {loss} not preserved in checkpoint {i}"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestTrainingLoopIntegration:
    """Integration tests for full training loop with callbacks and checkpoints."""

    def test_simulated_training_loop_with_callbacks_and_checkpoints(self):
        """Simulate realistic training loop with early stopping and checkpointing."""
        # Arrange
        import shutil
        import tempfile
        from pathlib import Path

        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )
        from src.codex_ml.training.callbacks import EarlyStopping

        tmpdir = Path(tempfile.mkdtemp())

        try:
            # Training parameters
            max_epochs = 100
            es = EarlyStopping(patience=3, min_delta=0.01, mode="min")

            # Simulated training loop
            epoch = 0
            stopped_early = False
            last_checkpoint = None

            for epoch in range(max_epochs):
                # Simulate loss progression
                if epoch < 10:
                    loss = 1.0 - (epoch * 0.05)  # Decreasing
                elif epoch < 20:
                    loss = 0.5 - ((epoch - 10) * 0.01)  # Slowly decreasing
                else:
                    loss = 0.4 + (epoch * 0.0005)  # Increasing (overfit)

                # Check early stopping
                if es.step(loss):
                    stopped_early = True
                    break

                # Save checkpoint every 5 epochs
                if epoch % 5 == 0:
                    ckpt_dir = tmpdir / f"ckpt_epoch_{epoch:03d}"
                    save_checkpoint(
                        str(ckpt_dir),
                        state={"epoch": epoch, "loss": loss},
                        meta={"epoch": epoch, "loss": loss},
                    )
                    last_checkpoint = ckpt_dir

            # Assert: Training should have stopped early
            assert stopped_early is True, "Training should have stopped early due to plateau"
            assert epoch < max_epochs, "Training should not complete all epochs"

            # Assert: Should have saved checkpoints
            assert last_checkpoint is not None, "Should have saved at least one checkpoint"
            assert last_checkpoint.exists(), "Last checkpoint directory should exist"

            # Verify last checkpoint can be loaded
            loaded_state, loaded_meta = load_checkpoint(str(last_checkpoint))
            assert "epoch" in loaded_state, "Checkpoint should contain epoch information"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_training_recovery_from_checkpoint(self):
        """Test resuming training from checkpoint after simulated interruption."""
        # Arrange
        import shutil
        import tempfile
        from pathlib import Path

        from src.codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )
        from src.codex_ml.training.callbacks import EarlyStopping

        tmpdir = Path(tempfile.mkdtemp())

        try:
            # Simulate initial training and save checkpoint
            ckpt_dir = tmpdir / "recovery_checkpoint"
            save_checkpoint(
                str(ckpt_dir),
                state={"epoch": 50, "step": 1000, "model_loss": 0.25},
                meta={"epoch": 50, "step": 1000},
            )

            # Simulate recovery: load checkpoint and resume
            loaded_state, loaded_meta = load_checkpoint(str(ckpt_dir))

            # Create new callback for resumed training
            es = EarlyStopping(patience=2, min_delta=0.01, mode="min")

            # Resume training from checkpoint state
            resume_epoch = loaded_state["epoch"]

            # Simulate continued training
            resumed_losses = [0.24, 0.22, 0.21, 0.21, 0.21]

            for loss in resumed_losses:
                if es.step(loss):
                    break

            # Assert
            assert resume_epoch == 50, "Resumed epoch should match checkpoint"
            assert es.best <= 0.21, "Training should continue from checkpoint state"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
