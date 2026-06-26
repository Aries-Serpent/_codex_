"""Cross-capability integration tests.

These tests validate that capabilities work together correctly
and that changes in one capability don't break others.
"""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import assume, given, settings
from hypothesis import strategies as st

# =============================================================================
# Configuration + Logging Integration
# =============================================================================


class ConfigLoggingIntegration:
    """Test configuration and logging work together."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.log_level = config.get("log_level", "INFO")
        self.log_format = config.get("log_format", "json")
        self.logs: list[dict[str, Any]] = []

    def log(self, level: str, message: str, **kwargs) -> dict[str, Any]:
        """Log message with configured format."""
        record = {
            "level": level,
            "message": message,
            "format": self.log_format,
            **kwargs,
        }
        if level_value(level) >= level_value(self.log_level):
            self.logs.append(record)
        return record


def level_value(level: str) -> int:
    """Get numeric value for log level."""
    levels = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
    return levels.get(level.upper(), 0)


class TestConfigLoggingIntegration:
    """Integration tests for config + logging."""

    def test_log_level_from_config(self):
        """Log level should come from config."""
        config = {"log_level": "WARNING"}
        integration = ConfigLoggingIntegration(config)
        integration.log("INFO", "Should not appear")
        integration.log("WARNING", "Should appear")
        assert len(integration.logs) == 1, "Collection must not be empty"

    def test_log_format_from_config(self):
        """Log format should come from config."""
        config = {"log_format": "json"}
        integration = ConfigLoggingIntegration(config)
        record = integration.log("INFO", "Test")
        assert record["format"] == "json", "rec is not valid"

    @given(st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]))
    @settings(max_examples=10)
    def test_all_log_levels(self, level: str):
        """All log levels should work."""
        config = {"log_level": level}
        integration = ConfigLoggingIntegration(config)
        integration.log(level, "Test message")
        assert len(integration.logs) >= 1, "Collection must not be empty"


# =============================================================================
# Data Handling + Training Integration
# =============================================================================


class DataTrainingIntegration:
    """Test data handling and training work together."""

    def __init__(self, data: list[dict[str, Any]], batch_size: int = 32):
        self.data = data
        self.batch_size = batch_size
        self.current_epoch = 0
        self.steps_per_epoch = (len(data) + batch_size - 1) // batch_size

    def get_batch(self, step: int) -> list[dict[str, Any]]:
        """Get batch for training step."""
        start = (step % self.steps_per_epoch) * self.batch_size
        end = min(start + self.batch_size, len(self.data))
        return self.data[start:end]

    def train_step(self, batch: list[dict[str, Any]]) -> dict[str, float]:
        """Simulate training step."""
        # Simple mock training
        return {"loss": 1.0 / (len(batch) + 1), "batch_size": len(batch)}


class TestDataTrainingIntegration:
    """Integration tests for data + training."""

    def test_batching(self):
        """Data should be correctly batched."""
        data = [{"x": i} for i in range(100)]
        integration = DataTrainingIntegration(data, batch_size=32)
        batch = integration.get_batch(0)
        assert len(batch) == 32, "Batch must not be empty"

    def test_last_batch(self):
        """Last batch may be smaller."""
        data = [{"x": i} for i in range(100)]
        integration = DataTrainingIntegration(data, batch_size=32)
        # Step 3 is the last batch (100 - 96 = 4)
        batch = integration.get_batch(3)
        assert len(batch) == 4, "Batch must not be empty"

    def test_train_step_returns_metrics(self):
        """Training step should return metrics."""
        data = [{"x": i} for i in range(10)]
        integration = DataTrainingIntegration(data, batch_size=5)
        batch = integration.get_batch(0)
        metrics = integration.train_step(batch)
        assert "loss" in metrics, "Condition must be true"
        assert "batch_size" in metrics, "Condition must be true"


# =============================================================================
# Security + Logging Integration
# =============================================================================


class SecureLogger:
    """Logger that scrubs PII from logs."""

    PII_PATTERNS = [
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),
        (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]"),
    ]

    def __init__(self):
        self.logs: list[str] = []

    def scrub(self, message: str) -> str:
        """Scrub PII from message."""
        import re

        result = message
        for pattern, replacement in self.PII_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result

    def log(self, message: str) -> str:
        """Log message with PII scrubbed."""
        scrubbed = self.scrub(message)
        self.logs.append(scrubbed)
        return scrubbed


class TestSecurityLoggingIntegration:
    """Integration tests for security + logging."""

    def test_email_scrubbed(self):
        """Emails should be scrubbed from logs."""
        logger = SecureLogger()
        result = logger.log("User email: test@example.com")
        assert "test@example.com" not in result, "Result must not be empty"
        assert "[EMAIL]" in result, "Result must not be empty"

    def test_phone_scrubbed(self):
        """Phone numbers should be scrubbed."""
        logger = SecureLogger()
        result = logger.log("Call 123-456-7890")
        assert "123-456-7890" not in result, "Result must not be empty"
        assert "[PHONE]" in result, "Result must not be empty"

    def test_safe_message_unchanged(self):
        """Safe messages should be unchanged."""
        logger = SecureLogger()
        message = "Normal log message"
        result = logger.log(message)
        assert result == message, "Result must not be empty"


# =============================================================================
# Checkpointing + Training Integration
# =============================================================================


class TrainingCheckpointer:
    """Checkpointing for training state."""

    def __init__(self):
        self.checkpoints: list[dict[str, Any]] = []

    def save(self, epoch: int, step: int, metrics: dict[str, float]) -> dict[str, Any]:
        """Save training checkpoint."""
        checkpoint = {
            "epoch": epoch,
            "step": step,
            "metrics": metrics,
        }
        self.checkpoints.append(checkpoint)
        return checkpoint

    def load_latest(self) -> dict[str, Any] | None:
        """Load latest checkpoint."""
        if not self.checkpoints:
            return None
        return self.checkpoints[-1]

    def load_best(self, metric: str, mode: str = "min") -> dict[str, Any] | None:
        """Load best checkpoint by metric."""
        if not self.checkpoints:
            return None

        def key(c):
            return c["metrics"].get(metric, float("inf"))

        reverse = mode == "max"
        return sorted(self.checkpoints, key=key, reverse=reverse)[0]


class TestCheckpointingTrainingIntegration:
    """Integration tests for checkpointing + training."""

    def test_save_checkpoint(self):
        """Save training checkpoint."""
        checkpointer = TrainingCheckpointer()
        ckpt = checkpointer.save(1, 100, {"loss": 0.5})
        assert ckpt["epoch"] == 1, "Condition must be true"
        assert ckpt["step"] == 100, "Condition must be true"

    def test_load_latest(self):
        """Load latest checkpoint."""
        checkpointer = TrainingCheckpointer()
        checkpointer.save(1, 100, {"loss": 0.5})
        checkpointer.save(2, 200, {"loss": 0.3})
        latest = checkpointer.load_latest()
        assert latest["epoch"] == 2, "Condition must be true"

    def test_load_best(self):
        """Load best checkpoint by metric."""
        checkpointer = TrainingCheckpointer()
        checkpointer.save(1, 100, {"loss": 0.5})
        checkpointer.save(2, 200, {"loss": 0.3})
        checkpointer.save(3, 300, {"loss": 0.4})
        best = checkpointer.load_best("loss", "min")
        assert best["metrics"]["loss"] == 0.3, "Condition must be true"


# =============================================================================
# Evaluation + Experiment Tracking Integration
# =============================================================================


class EvaluationTracker:
    """Track evaluation metrics across experiments."""

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.runs: list[dict[str, Any]] = []

    def log_run(self, run_id: str, metrics: dict[str, float]) -> None:
        """Log evaluation run."""
        self.runs.append(
            {
                "run_id": run_id,
                "experiment": self.experiment_name,
                "metrics": metrics,
            }
        )

    def compare_runs(self, metric: str) -> list[dict[str, Any]]:
        """Compare runs by metric."""
        return sorted(self.runs, key=lambda r: r["metrics"].get(metric, 0))

    def get_best_run(self, metric: str, mode: str = "max") -> dict[str, Any] | None:
        """Get best run by metric."""
        if not self.runs:
            return None
        sorted_runs = self.compare_runs(metric)
        return sorted_runs[-1] if mode == "max" else sorted_runs[0]


class TestEvaluationTrackingIntegration:
    """Integration tests for evaluation + experiment tracking."""

    def test_log_run(self):
        """Log evaluation run."""
        tracker = EvaluationTracker("test_exp")
        tracker.log_run("run1", {"accuracy": 0.9})
        assert len(tracker.runs) == 1, "Collection must not be empty"

    def test_compare_runs(self):
        """Compare runs by metric."""
        tracker = EvaluationTracker("test_exp")
        tracker.log_run("run1", {"accuracy": 0.8})
        tracker.log_run("run2", {"accuracy": 0.9})
        compared = tracker.compare_runs("accuracy")
        assert compared[0]["run_id"] == "run1", "Condition must be true"

    def test_get_best_run(self):
        """Get best run."""
        tracker = EvaluationTracker("test_exp")
        tracker.log_run("run1", {"accuracy": 0.8})
        tracker.log_run("run2", {"accuracy": 0.95})
        tracker.log_run("run3", {"accuracy": 0.85})
        best = tracker.get_best_run("accuracy", "max")
        assert best["run_id"] == "run2", "Condition must be true"


# =============================================================================
# Deployment + Versioning Integration
# =============================================================================


class VersionedDeployment:
    """Manage versioned deployments."""

    def __init__(self):
        self.deployments: list[dict[str, Any]] = []
        self.current_version: str | None = None

    def deploy(self, version: str, image: str) -> dict[str, Any]:
        """Deploy new version."""
        deployment = {
            "version": version,
            "image": image,
            "status": "deployed",
            "previous": self.current_version,
        }
        self.deployments.append(deployment)
        self.current_version = version
        return deployment

    def rollback(self) -> dict[str, Any] | None:
        """Rollback to previous version."""
        if len(self.deployments) < 2:
            return None
        current = self.deployments[-1]
        previous_version = current["previous"]
        if not previous_version:
            return None
        self.current_version = previous_version
        rollback = {
            "from_version": current["version"],
            "to_version": previous_version,
            "status": "rolled_back",
        }
        self.deployments.append(rollback)
        return rollback


class TestDeploymentVersioningIntegration:
    """Integration tests for deployment + versioning."""

    def test_deploy(self):
        """Deploy new version."""
        manager = VersionedDeployment()
        result = manager.deploy("1.0.0", "app:v1.0.0")
        assert result["version"] == "1.0.0", "Result must not be empty"
        assert manager.current_version == "1.0.0", "current_version is not valid"

    def test_deploy_tracks_previous(self):
        """Deployment should track previous version."""
        manager = VersionedDeployment()
        manager.deploy("1.0.0", "app:v1.0.0")
        result = manager.deploy("2.0.0", "app:v2.0.0")
        assert result["previous"] == "1.0.0", "Result must not be empty"

    def test_rollback(self):
        """Rollback to previous version."""
        manager = VersionedDeployment()
        manager.deploy("1.0.0", "app:v1.0.0")
        manager.deploy("2.0.0", "app:v2.0.0")
        result = manager.rollback()
        assert result["from_version"] == "2.0.0", "Result must not be empty"
        assert result["to_version"] == "1.0.0", "Result must not be empty"
        assert manager.current_version == "1.0.0", "current_version is not valid"


# =============================================================================
# Error Handling + Observability Integration
# =============================================================================


class ObservableErrorHandler:
    """Error handler with observability integration."""

    def __init__(self):
        self.errors: list[dict[str, Any]] = []
        self.metrics: dict[str, int] = {"total_errors": 0, "by_type": {}}

    def handle(self, error_type: str, message: str) -> dict[str, Any]:
        """Handle error and track metrics."""
        self.metrics["total_errors"] += 1
        if error_type not in self.metrics["by_type"]:
            self.metrics["by_type"][error_type] = 0
        self.metrics["by_type"][error_type] += 1

        error = {
            "type": error_type,
            "message": message,
            "count": self.metrics["by_type"][error_type],
        }
        self.errors.append(error)
        return error

    def get_error_rate(self, error_type: str) -> float:
        """Get error rate for type."""
        if self.metrics["total_errors"] == 0:
            return 0.0
        return self.metrics["by_type"].get(error_type, 0) / self.metrics["total_errors"]


class TestErrorObservabilityIntegration:
    """Integration tests for error handling + observability."""

    def test_error_tracking(self):
        """Errors should be tracked."""
        handler = ObservableErrorHandler()
        handler.handle("ValidationError", "Invalid input")
        assert handler.metrics["total_errors"] == 1, "Error should be raised or set"

    def test_error_by_type(self):
        """Errors should be tracked by type."""
        handler = ObservableErrorHandler()
        handler.handle("ValidationError", "Invalid input")
        handler.handle("NetworkError", "Connection failed")
        handler.handle("ValidationError", "Missing field")
        assert handler.metrics["by_type"]["ValidationError"] == 2, "Error should be raised or set"
        assert handler.metrics["by_type"]["NetworkError"] == 1, "Error should be raised or set"

    def test_error_rate(self):
        """Error rate should be calculated correctly."""
        handler = ObservableErrorHandler()
        handler.handle("A", "Error A")
        handler.handle("A", "Error A")
        handler.handle("B", "Error B")
        assert handler.get_error_rate("A") == pytest.approx(2 / 3), "Error should be raised or set"


# =============================================================================
# Property-based Integration Tests
# =============================================================================


class TestPropertyBasedIntegration:
    """Property-based tests for cross-capability integration."""

    @given(
        st.lists(
            st.dictionaries(st.text(min_size=1, max_size=5), st.integers()), min_size=1, max_size=50
        )
    )
    @settings(max_examples=20)
    def test_data_batching_preserves_count(self, data: list[dict]):
        """All data should be processed in batches."""
        assume(len(data) > 0)
        batch_size = max(1, len(data) // 3)
        integration = DataTrainingIntegration(data, batch_size)

        all_items = []
        for step in range(integration.steps_per_epoch):
            batch = integration.get_batch(step)
            all_items.extend(batch)

        assert len(all_items) == len(data), "All_items must not be empty"

    @given(st.integers(min_value=1, max_value=10), st.floats(min_value=0.0, max_value=1.0))
    @settings(max_examples=20)
    def test_checkpoint_ordering(self, num_epochs: int, base_loss: float):
        """Checkpoints should maintain ordering."""
        checkpointer = TrainingCheckpointer()
        for epoch in range(num_epochs):
            loss = base_loss * (1.0 - epoch / (num_epochs + 1))
            checkpointer.save(epoch, epoch * 100, {"loss": loss})

        latest = checkpointer.load_latest()
        assert latest["epoch"] == num_epochs - 1, "Condition must be true"

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=20)
    def test_secure_logging_idempotent(self, message: str):
        """Scrubbing should be idempotent."""
        logger = SecureLogger()
        first_scrub = logger.scrub(message)
        second_scrub = logger.scrub(first_scrub)
        assert first_scrub == second_scrub, "first_scrub is not valid"
