"""Complete MLflow integration tests."""

import pytest

from codex_ml.tracking.mlflow_wrapper import MLflowTracker, init_tracking


class TestMLflowTracker:
    """Test complete MLflow tracker implementation."""

    def test_tracker_disabled_noop(self):
        """Tracker should no-op when disabled."""
        tracker = MLflowTracker(enabled=False)

        with tracker.start_run():
            tracker.log_params({"lr": 0.001})
            tracker.log_metrics({"loss": 0.5})
            tracker.log_param("model", "test")
            tracker.log_metric("accuracy", 0.95)

        # Should complete without error
        assert True, "True is not valid"

    def test_tracker_enabled_offline(self, tmp_path):
        """Tracker should work in offline mode."""
        pytest.importorskip("mlflow")

        tracker = MLflowTracker(
            enabled=True,
            tracking_uri=f"file:{tmp_path}/mlruns",
            experiment_name="test_experiment",
        )

        with tracker.start_run(run_name="test_run"):
            tracker.log_params({"lr": 0.001, "batch_size": 32})
            tracker.log_metrics({"loss": 0.5, "accuracy": 0.9}, step=0)
            tracker.log_metric("val_loss", 0.4, step=1)

        # Verify run was created
        assert (tmp_path / "mlruns").exists(), "Condition must be true"

    def test_log_artifact(self, tmp_path):
        """Should log artifact files."""
        pytest.importorskip("mlflow")

        artifact_file = tmp_path / "model.txt"
        artifact_file.write_text("dummy model")

        tracker = MLflowTracker(
            enabled=True,
            tracking_uri=f"file:{tmp_path}/mlruns",
        )

        with tracker.start_run():
            tracker.log_artifact(str(artifact_file))

    def test_context_manager(self, tmp_path):
        """Test context manager functionality."""
        pytest.importorskip("mlflow")

        tracker = MLflowTracker(
            enabled=True,
            tracking_uri=f"file:{tmp_path}/mlruns",
        )

        with tracker.start_run("run1"):
            tracker.log_metric("loss", 1.0)
            assert tracker._active, "Condition must be true"

        # Should be inactive after context
        assert not tracker._active, "Condition must be true"

    def test_nested_runs(self, tmp_path):
        """Test nested run support."""
        pytest.importorskip("mlflow")

        tracker = MLflowTracker(
            enabled=True,
            tracking_uri=f"file:{tmp_path}/mlruns",
        )

        with tracker.start_run("parent"):
            tracker.log_metric("parent_metric", 1.0)

            with tracker.start_run("child", nested=True):
                tracker.log_metric("child_metric", 2.0)

    def test_tags(self, tmp_path):
        """Test tag logging."""
        pytest.importorskip("mlflow")

        tracker = MLflowTracker(
            enabled=True,
            tracking_uri=f"file:{tmp_path}/mlruns",
        )

        with tracker.start_run():
            tracker.set_tag("model_type", "transformer")
            tracker.set_tags({"env": "test", "version": "1.0"})

    def test_init_tracking(self, tmp_path):
        """Test global tracker initialization."""
        pytest.importorskip("mlflow")

        tracker = init_tracking(
            enabled=True,
            tracking_uri=f"file:{tmp_path}/mlruns",
            experiment_name="global_test",
        )

        assert tracker.enabled, "Condition must be true"
        assert tracker.experiment_name == "global_test", "experiment_name is not valid"


class TestMLflowIntegration:
    """Test integration with training loops."""

    def test_training_loop_integration(self, tmp_path):
        """Test integration with training loop."""
        pytest.importorskip("mlflow")

        tracker = MLflowTracker(
            enabled=True,
            tracking_uri=f"file:{tmp_path}/mlruns",
        )

        # Simulate training loop
        with tracker.start_run("training"):
            # Log hyperparameters
            tracker.log_params(
                {
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 10,
                }
            )

            # Simulate training epochs
            for epoch in range(3):
                train_loss = 1.0 / (epoch + 1)
                val_loss = 0.9 / (epoch + 1)

                tracker.log_metrics(
                    {
                        "train_loss": train_loss,
                        "val_loss": val_loss,
                    },
                    step=epoch,
                )

            # Log final metrics
            tracker.log_metric("final_accuracy", 0.95)

    def test_graceful_degradation(self):
        """Test graceful degradation when MLflow unavailable."""
        tracker = MLflowTracker(enabled=True)  # May fail to init

        # Should not raise errors
        with tracker.start_run():
            tracker.log_params({"test": "value"})
            tracker.log_metrics({"loss": 0.5})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
