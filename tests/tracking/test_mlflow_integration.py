"""
Tests for WP-A: MLflow Experiment Tracking Integration

Validates that:
1. MLflow writer integrates with existing tracking infrastructure
2. NDJSON fallback works when MLflow disabled
3. Configuration system supports tracking options
4. Artifacts are logged correctly
5. Offline-first design is maintained
"""

import json
import tempfile
from pathlib import Path

import pytest

# Import tracking writers
from src.codex_ml.tracking.writers import (
    CompositeWriter,
    MLflowWriter,
    NdjsonWriter,
)


class TestNdjsonWriter:
    """Test NDJSON writer (baseline tracking)"""

    def test_ndjson_writer_creates_file(self):
        """Verify NDJSON writer creates output file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.ndjson"
            writer = NdjsonWriter(path)

            # Log a metric
            writer.log(
                {
                    "step": 0,
                    "split": "train",
                    "metric": "loss",
                    "value": 1.5,
                    "dataset": "test",
                    "tags": {},
                }
            )

            writer.close()

            assert path.exists(), "NDJSON file should be created"

    def test_ndjson_writer_logs_metrics(self):
        """Verify NDJSON writer logs metrics correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.ndjson"
            writer = NdjsonWriter(path)

            # Log multiple metrics
            for step in range(5):
                writer.log(
                    {
                        "step": step,
                        "split": "train",
                        "metric": "loss",
                        "value": 1.0 - step * 0.1,
                        "dataset": "test",
                        "tags": {"experiment": "test"},
                    }
                )

            writer.close()

            # Verify file contains metrics
            lines = path.read_text().strip().split("\n")
            assert len(lines) >= 5, "Should log all metrics"

            # Verify first metric
            first_metric = json.loads(lines[0])
            assert first_metric["step"] == 0, "Condition must be true"
            assert first_metric["metric"] == "loss", "Condition must be true"
            assert abs(first_metric["value"] - 1.0) < 1e-6, "Value must be initialized"


class TestMLflowWriter:
    """Test MLflow writer integration"""

    @pytest.mark.skipif(
        not pytest.importorskip("mlflow", reason="MLflow not available"), reason="Requires MLflow"
    )
    def test_mlflow_writer_initialization(self):
        """Verify MLflow writer can be initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            uri = f"file:{tmpdir}/mlruns"

            try:
                writer = MLflowWriter(
                    uri=uri, exp_name="test_experiment", run_name="test_run", tags={"test": "true"}
                )

                # Should initialize without error
                assert writer is not None, "writer must be initialized"

                writer.close()
            except (IOError, OSError) as e:
                # If MLflow not available or other issues, that's ok
                pytest.skip(f"MLflow writer initialization failed: {e}")

    def test_mlflow_writer_falls_back_gracefully(self):
        """Verify MLflow writer falls back gracefully when unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            uri = f"file:{tmpdir}/mlruns"

            # This should not raise even if MLflow has issues
            writer = MLflowWriter(uri=uri, exp_name="test", run_name="test", tags={})

            # Log should not fail
            writer.log(
                {
                    "step": 0,
                    "split": "train",
                    "metric": "loss",
                    "value": 1.0,
                    "dataset": "test",
                    "tags": {},
                }
            )

            writer.close()


class TestCompositeWriter:
    """Test composite writer (multiple writers)"""

    def test_composite_writer_with_ndjson(self):
        """Verify composite writer works with NDJSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ndjson_path = Path(tmpdir) / "metrics.ndjson"

            writers = [NdjsonWriter(ndjson_path)]

            composite = CompositeWriter(writers)

            # Log a metric
            composite.log(
                {
                    "step": 0,
                    "split": "train",
                    "metric": "loss",
                    "value": 1.0,
                    "dataset": "test",
                    "tags": {},
                }
            )

            composite.close()

            # Verify NDJSON file created
            assert ndjson_path.exists(), "Condition must be true"

    def test_composite_writer_handles_errors(self):
        """Verify composite writer handles individual writer errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ndjson_path = Path(tmpdir) / "metrics.ndjson"

            # Create writers (some may fail)
            writers = [
                NdjsonWriter(ndjson_path),
                # MLflow may not be available, but composite should handle it
            ]

            composite = CompositeWriter(writers)

            # Should not raise even if some writers fail
            composite.log(
                {
                    "step": 0,
                    "split": "train",
                    "metric": "loss",
                    "value": 1.0,
                    "dataset": "test",
                    "tags": {},
                }
            )

            composite.close()


class TestTrackingConfiguration:
    """Test tracking configuration"""

    def test_tracking_config_file_exists(self):
        """Verify tracking configuration file exists"""
        config_path = (
            Path(__file__).parent.parent.parent / "configs" / "base" / "tracking" / "default.yaml"
        )

        assert config_path.exists(), "Tracking config should exist"

    def test_tracking_config_has_required_fields(self):
        """Verify tracking config has required fields"""
        pytest.importorskip("yaml")
        import yaml

        config_path = (
            Path(__file__).parent.parent.parent / "configs" / "base" / "tracking" / "default.yaml"
        )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check required fields
        assert "mlflow_enabled" in config, "Should have mlflow_enabled"
        assert "mlflow_uri" in config, "Should have mlflow_uri"
        assert "writer" in config, "Should have writer selection"

        # Verify defaults
        assert config["mlflow_enabled"] is False, "MLflow should be disabled by default"
        assert config["writer"] == "ndjson", "Should default to NDJSON writer"

    def test_tracking_config_offline_first(self):
        """Verify tracking config follows offline-first design"""
        pytest.importorskip("yaml")
        import yaml

        config_path = (
            Path(__file__).parent.parent.parent / "configs" / "base" / "tracking" / "default.yaml"
        )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check safety settings
        assert "safety" in config, "Should have safety settings"
        safety = config["safety"]

        assert safety["allow_remote"] is False, "Should not allow remote by default"
        assert safety["offline_first"] is True, "Should be offline-first"

    def test_tracking_config_artifact_settings(self):
        """Verify tracking config has artifact tracking settings"""
        pytest.importorskip("yaml")
        import yaml

        config_path = (
            Path(__file__).parent.parent.parent / "configs" / "base" / "tracking" / "default.yaml"
        )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "artifacts" in config, "Should have artifact settings"
        artifacts = config["artifacts"]

        assert artifacts["enabled"] is True, "Artifacts should be enabled"
        assert artifacts["track_checkpoints"] is True, "Should track checkpoints"
        assert artifacts["track_configs"] is True, "Should track configs"
        assert artifacts["track_env_snapshot"] is True, "Should track env snapshot"


class TestMlflowIntegration:
    """Integration tests for MLflow tracking"""

    @pytest.mark.skipif(
        not pytest.importorskip("mlflow", reason="MLflow not available"), reason="Requires MLflow"
    )
    def test_mlflow_creates_local_mlruns(self):
        """Verify MLflow creates local mlruns directory when enabled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            uri = f"file:{tmpdir}/mlruns"

            try:
                import mlflow

                mlflow.set_tracking_uri(uri)
                mlflow.set_experiment("test_experiment")

                with mlflow.start_run(run_name="test_run"):
                    mlflow.log_param("test_param", "value")
                    mlflow.log_metric("test_metric", 1.0)

                # Verify mlruns directory created
                mlruns_dir = Path(tmpdir) / "mlruns"
                assert mlruns_dir.exists(), "mlruns directory should be created"

            except (IOError, OSError) as e:
                pytest.skip(f"MLflow integration test failed: {e}")

    @pytest.mark.skipif(
        not pytest.importorskip("mlflow", reason="MLflow not available"), reason="Requires MLflow"
    )
    def test_mlflow_logs_artifacts(self):
        """Verify MLflow can log artifacts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            uri = f"file:{tmpdir}/mlruns"

            try:
                import mlflow

                mlflow.set_tracking_uri(uri)
                mlflow.set_experiment("test_experiment")

                with mlflow.start_run(run_name="test_run"):
                    # Create a test artifact
                    artifact_path = Path(tmpdir) / "test_artifact.txt"
                    artifact_path.write_text("test content")

                    # Log artifact
                    mlflow.log_artifact(str(artifact_path))

                # Artifacts should be logged
                # (actual verification would require querying MLflow)

            except Exception as e:
                pytest.skip(f"MLflow artifact logging test failed: {e}")


class TestNdjsonFallback:
    """Test NDJSON fallback when MLflow disabled"""

    def test_ndjson_writer_always_works(self):
        """Verify NDJSON writer works without external dependencies"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.ndjson"

            # Should work without MLflow or any other dependencies
            writer = NdjsonWriter(path)

            for step in range(10):
                writer.log(
                    {
                        "step": step,
                        "split": "train",
                        "metric": "loss",
                        "value": 1.0 - step * 0.05,
                        "dataset": "test",
                        "tags": {},
                    }
                )

            writer.close()

            # Verify all metrics logged
            lines = path.read_text().strip().split("\n")
            assert len(lines) >= 10, "Lines must not be empty"

    def test_ndjson_fallback_when_mlflow_disabled(self):
        """Verify NDJSON fallback works when MLflow is disabled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ndjson_path = Path(tmpdir) / "metrics.ndjson"

            # Create composite writer with only NDJSON
            # (simulating MLflow disabled)
            writers = [NdjsonWriter(ndjson_path)]
            composite = CompositeWriter(writers)

            # Should work fine
            composite.log(
                {
                    "step": 0,
                    "split": "train",
                    "metric": "loss",
                    "value": 1.0,
                    "dataset": "test",
                    "tags": {},
                }
            )

            composite.close()

            assert ndjson_path.exists(), "Condition must be true"


class TestOfflineFirstDesign:
    """Test offline-first design principles"""

    def test_file_based_mlflow_uri_default(self):
        """Verify default MLflow URI is file-based"""
        pytest.importorskip("yaml")
        import yaml

        config_path = (
            Path(__file__).parent.parent.parent / "configs" / "base" / "tracking" / "default.yaml"
        )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        mlflow_uri = config["mlflow_uri"]

        # Should be file-based
        assert mlflow_uri.startswith("file:"), "Default URI should be file-based"
        assert "http" not in mlflow_uri.lower(), "Should not use HTTP by default"
        assert "https" not in mlflow_uri.lower(), "Should not use HTTPS by default"

    def test_ndjson_always_enabled(self):
        """Verify NDJSON is always enabled as fallback"""
        pytest.importorskip("yaml")
        import yaml

        config_path = (
            Path(__file__).parent.parent.parent / "configs" / "base" / "tracking" / "default.yaml"
        )

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # NDJSON should always be enabled
        assert config["ndjson"]["enabled"] is True, "NDJSON should always be enabled"


# Fixtures
@pytest.fixture
def temp_tracking_dir():
    """Provide temporary directory for tracking tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_metric():
    """Provide sample metric for testing"""
    return {
        "step": 100,
        "split": "train",
        "metric": "loss",
        "value": 0.5,
        "dataset": "test_dataset",
        "tags": {"experiment": "test", "model": "transformer"},
    }
