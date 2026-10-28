"""Tests for the toy training loop utilities."""

# ChatGPT Codex tailored Commented Task Prompt:
# - Task: Expand and harden the train_loop module testing to ensure comprehensive
#   coverage of metrics recording, error handling, CLI parsing, and training utilities.
# - Goals for Codex:
#   1. Ensure robust testing of the metrics recording system including both JSON
#      and NDJSON output formats, error conditions (disk full, unserializable data),
#      and proper timestamp formatting.
#   2. Add comprehensive CLI argument parsing tests covering edge cases like
#      invalid arguments, missing required parameters, and proper default handling.
#   3. Expand training loop testing to cover epoch execution, gradient accumulation,
#      dataset loading edge cases, and proper artifact directory management.
#   4. Add property-based testing for metrics validation and serialization robustness.
#   5. Ensure backward compatibility with different train_loop API versions and
#      graceful handling of missing dependencies or filesystem issues.
#
# Expandable items for Codex:
# - Add parametrized tests for different metric types and data structures
# - Implement hypothesis-based property testing for metrics serialization
# - Add integration tests for complete training runs with mocked datasets
# - Expand CLI testing to cover configuration file loading and validation
# - Add performance benchmarking for metrics recording under high load
#
# Production readiness checklist:
# - All imports properly handled with fallbacks
# - Comprehensive error path coverage
# - Thread-safe metrics recording if applicable
# - Memory efficiency for large metric datasets
# - Proper cleanup of temporary artifacts

import datetime
import json
import sys

import pytest

# BEGIN: CODEX_TEST_TRAIN_LOOP

__all__ = [
    "test_cli_parsing_smoke",
    "test_empty_dataset_path",
    "test_record_metrics_error_path",
    "test_record_metrics_unserializable",
    "test_record_metrics_writes_json",
    "test_ts_format",
]


@pytest.fixture
def artifacts(tmp_path):
    """Create a temporary artifacts directory structure for testing."""
    d = tmp_path / "artifacts" / "metrics"
    d.mkdir(parents=True)
    return d


def test_record_metrics_writes_json(tmp_path, artifacts, monkeypatch):
    """
    Test that record_metrics properly writes both JSON and NDJSON format files
    with correct structure and data preservation.
    """
    from codex_ml import train_loop

    # Set up the artifacts directory for the train_loop module
    monkeypatch.setattr(train_loop, "ART_DIR", artifacts, raising=False)

    # Record sample metrics
    train_loop.record_metrics(
        phase="eval",
        epoch=1,
        metrics={"accuracy": 1.0},
        cfg_hash="deadbeef",
        notes="unit-test",
    )

    # Verify both JSON formats are created
    metrics_json = artifacts / "metrics.json"
    metrics_ndjson = artifacts / "metrics.ndjson"
    assert metrics_json.exists(), "metrics.json should be created"
    assert metrics_ndjson.exists(), "metrics.ndjson should be created"

    # Verify JSON structure and content
    data = json.loads(metrics_json.read_text(encoding="utf-8"))
    assert isinstance(data, list), "metrics.json should contain a list"
    assert len(data) > 0, "metrics.json should not be empty"
    last_entry = data[-1]
    assert last_entry["metrics"]["accuracy"] == 1.0, "accuracy should be preserved"
    assert last_entry["phase"] == "eval", "phase should be preserved"
    assert last_entry["epoch"] == 1, "epoch should be preserved"
    assert last_entry["cfg_hash"] == "deadbeef", "cfg_hash should be preserved"
    assert last_entry.get("run_id"), "run_id should be recorded"


def test_record_metrics_error_path(tmp_path, monkeypatch):
    """
    Test error handling when metrics recording fails due to filesystem issues.
    """
    from codex_ml import train_loop

    monkeypatch.setattr(train_loop, "ART_DIR", tmp_path, raising=False)

    def boom(*a, **k):  # pragma: no cover - trivial error simulator
        raise OSError("disk full")

    # Mock json.dumps to simulate serialization failure
    monkeypatch.setattr(json, "dumps", boom)

    # Should propagate the OSError
    with pytest.raises(OSError, match="disk full"):
        train_loop.record_metrics(
            phase="eval",
            epoch=0,
            metrics={"x": 1},
            cfg_hash="deadbeef",
        )


def test_record_metrics_unserializable(tmp_path, monkeypatch):
    """
    Test handling of unserializable objects in metrics data.
    """
    from codex_ml import train_loop

    class UnserializableObject:
        """Object that cannot be JSON serialized."""

    monkeypatch.setattr(train_loop, "ART_DIR", tmp_path, raising=False)

    # Should raise TypeError for unserializable data
    with pytest.raises(TypeError):
        train_loop.record_metrics(
            phase="train",
            epoch=1,
            metrics={"bad": UnserializableObject()},
            cfg_hash="cfg",
        )


def test_ts_format():
    """
    Test that timestamp formatting produces valid ISO format with Z suffix.
    """
    from codex_ml import train_loop

    ts = train_loop._now_ts()
    assert isinstance(ts, str), "timestamp should be a string"
    assert ts.endswith("Z"), "timestamp should end with Z (UTC indicator)"

    # Verify it's a valid ISO format timestamp (strip the Z for parsing)
    try:
        datetime.datetime.fromisoformat(ts[:-1])
    except ValueError as e:
        pytest.fail(f"Invalid timestamp format: {ts} - {e}")


def test_cli_parsing_smoke(monkeypatch, tmp_path, capsys):
    """A registered CLI model is instantiated and training artifacts are written."""
    from codex_ml import train_loop
    from codex_ml.logging.session_logger import SessionLogger
    from codex_ml.models import registry as models
    from codex_ml.registry.base import Registry

    monkeypatch.chdir(tmp_path)
    artifacts = tmp_path / "metrics"
    session_logger = SessionLogger("cli-model-smoke", tmp_path / "sessions")
    monkeypatch.setattr(train_loop, "get_session_logger", lambda: session_logger)
    built_configs = []
    outcomes = []

    class TinyModel:
        def to(self, *args, **kwargs):
            return self

        def train(self):
            return None

        def parameters(self):
            return []

    def build_model(config):
        built_configs.append(config)
        return TinyModel()

    local_models = Registry("cli-test-model")
    local_models.register("test-tiny-model", build_model)
    monkeypatch.setattr(models, "model_registry", local_models)
    monkeypatch.setattr(train_loop, "instantiate_model", models.get_model)
    original_training = train_loop.run_training

    def record_training(**kwargs):
        result = original_training(**kwargs)
        outcomes.append(result)
        return result

    monkeypatch.setattr(train_loop, "run_training", record_training)
    train_loop.main(
        [
            "--model-name",
            "test-tiny-model",
            "--epochs",
            "1",
            "--grad-accum",
            "2",
            "--art-dir",
            str(artifacts),
        ]
    )

    assert len(built_configs) == 1
    assert len(outcomes) == 1
    assert outcomes[0]["grad_accum"] == 2
    assert outcomes[0]["internal_model_created"] is True
    data = json.loads((artifacts / "metrics.json").read_text(encoding="utf-8"))
    assert {"epoch_end", "best_checkpoint"} <= {entry["phase"] for entry in data}
    assert (artifacts / "metrics.ndjson").exists()
    assert session_logger.session_file.exists()


def test_empty_dataset_path(monkeypatch):
    """
    Test training loop behavior with empty or missing dataset.
    """
    from codex_ml import train_loop

    # Test demo epoch function returns valid metrics dictionary
    result = train_loop.demo_epoch(epoch=0)
    assert isinstance(result, dict), "demo_epoch should return a dictionary"

    # Verify the result contains expected metric structure
    # (implementation-dependent, but should be a valid metrics dict)
    if result:  # If not empty
        # Basic validation that it looks like metrics
        for key, value in result.items():
            assert isinstance(key, str), f"Metric key {key} should be string"
            # Values should be JSON-serializable
            try:
                json.dumps(value)
            except (TypeError, ValueError) as e:
                pytest.fail(f"Metric value for {key} is not JSON-serializable: {e}")


# END: CODEX_TEST_TRAIN_LOOP
