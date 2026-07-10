"""Comprehensive experiment tracking validation for full profile.

Tests for Phase 3 Lane 3.2 - Full Experiment Tracking Validation.
Covers advanced MLflow and wandb features at production scale.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add fixtures path
full_test_dir = Path(__file__).parent
sys.path.insert(0, str(full_test_dir))

try:
    from experiment_fixtures import (
        mlflow_client_full,
        mlflow_tracking_uri_full,
        parent_experiment,
        child_experiment,
        parent_run,
        child_run,
        multi_metric_run,
        artifact_run,
        sweep_run_set,
        distributed_run_set,
        model_registry_run,
        export_import_run,
    )
except ImportError:
    # Fixtures will be loaded by pytest discovery
    pass


class TestExperimentNesting:
    """Test parent-child experiment hierarchies."""

    def test_parent_experiment_creation(self, parent_experiment):
        """Test that parent experiment is created successfully."""
        assert parent_experiment is not None
        assert "id" in parent_experiment
        assert "name" in parent_experiment
        assert parent_experiment["name"] == "parent_experiment_full"

    def test_child_experiment_creation(self, child_experiment, parent_experiment):
        """Test that child experiment is created and linked to parent."""
        assert child_experiment is not None
        assert "id" in child_experiment
        assert "parent_id" in child_experiment
        assert child_experiment["parent_id"] == parent_experiment["id"]

    def test_experiment_hierarchy_query(self, mlflow_client_full, parent_experiment):
        """Test querying experiment hierarchy."""
        try:
            import mlflow

            # Get parent experiment
            exp = mlflow_client_full.get_experiment(parent_experiment["id"])
            assert exp is not None
            assert exp.experiment_id == parent_experiment["id"]

            # Verify experiment properties
            assert exp.name == parent_experiment["name"]
            assert exp.lifecycle_stage == "active"

        except ImportError:
            pytest.skip("MLflow not installed")


class TestMultiMetricTracking:
    """Test tracking 100+ metrics per run."""

    def test_multi_metric_logging(self, mlflow_client_full, multi_metric_run):
        """Test logging multiple metrics to a single run."""
        assert multi_metric_run["metric_count"] == 150

        # Query metrics from run
        try:
            import mlflow

            metrics = mlflow_client_full.get_run(multi_metric_run["id"]).data.metrics
            assert len(metrics) == 150

            # Verify metric values
            for i in range(150):
                metric_key = f"metric_{i:03d}"
                assert metric_key in metrics
                expected_value = float(i) * 1.5
                assert abs(metrics[metric_key] - expected_value) < 0.01

        except ImportError:
            pytest.skip("MLflow not installed")

    def test_metric_step_tracking(self, mlflow_client_full, parent_experiment):
        """Test tracking metrics across multiple steps."""
        try:
            import mlflow

            exp_id = parent_experiment["id"]
            run = mlflow_client_full.create_run(experiment_id=exp_id)

            # Log metric across 50 steps
            for step in range(50):
                loss = 1.0 / (step + 1)
                mlflow_client_full.log_metric(run.info.run_id, "loss", loss, step=step)

            # Query run data
            run_data = mlflow_client_full.get_run(run.info.run_id).data
            metrics = run_data.metrics

            assert "loss" in metrics
            # Latest metric (step 49) should be smallest
            assert metrics["loss"] < 0.1

            mlflow_client_full.set_terminated(run.info.run_id)

        except ImportError:
            pytest.skip("MLflow not installed")


class TestArtifactManagement:
    """Test large artifact storage and retrieval."""

    def test_artifact_logging(self, mlflow_client_full, artifact_run):
        """Test logging artifacts to MLflow."""
        try:
            import mlflow

            # Log artifacts
            artifacts_dir = Path(artifact_run["artifacts_dir"])
            for artifact_path in artifacts_dir.glob("artifact_*.txt"):
                mlflow_client_full.log_artifact(
                    artifact_run["id"], str(artifact_path)
                )

            # Query artifacts
            artifacts = mlflow_client_full.list_artifacts(artifact_run["id"])
            assert artifacts is not None
            assert len(artifacts) > 0

        except ImportError:
            pytest.skip("MLflow not installed")

    def test_large_artifact_handling(self, mlflow_client_full, parent_experiment):
        """Test handling of large artifacts."""
        try:
            import mlflow

            exp_id = parent_experiment["id"]
            run = mlflow_client_full.create_run(experiment_id=exp_id)

            # Create a large artifact
            with tempfile.TemporaryDirectory() as tmpdir:
                large_file = Path(tmpdir) / "large_artifact.bin"
                # Create 1MB file
                large_file.write_bytes(b"x" * (1024 * 1024))

                # Log large artifact
                mlflow_client_full.log_artifact(run.info.run_id, str(large_file))

                # Verify artifact was logged
                artifacts = mlflow_client_full.list_artifacts(run.info.run_id)
                assert artifacts is not None

            mlflow_client_full.set_terminated(run.info.run_id)

        except ImportError:
            pytest.skip("MLflow not installed")


class TestModelRegistry:
    """Test model registry functionality."""

    def test_model_registration(self, mlflow_client_full, model_registry_run):
        """Test registering a model in the model registry."""
        try:
            import mlflow
            from mlflow.entities.model_registry import ModelVersion

            # Create a simple mock model and log it
            exp_id = model_registry_run["experiment_id"]
            run_id = model_registry_run["id"]

            # Note: Full model registry testing requires more setup
            # This test validates the basic run structure
            run_data = mlflow_client_full.get_run(run_id).data
            assert run_data.tags.get("test_type") == "model_registry"

        except ImportError:
            pytest.skip("MLflow not installed")

    def test_model_versioning(self, mlflow_client_full, parent_experiment):
        """Test model versioning and staging."""
        try:
            import mlflow

            exp_id = parent_experiment["id"]
            run = mlflow_client_full.create_run(experiment_id=exp_id)

            # Log model metadata
            mlflow_client_full.log_param(run.info.run_id, "model_version", "1.0.0")
            mlflow_client_full.log_param(
                run.info.run_id, "model_stage", "production"
            )

            run_data = mlflow_client_full.get_run(run.info.run_id).data
            assert run_data.params.get("model_version") == "1.0.0"
            assert run_data.params.get("model_stage") == "production"

            mlflow_client_full.set_terminated(run.info.run_id)

        except ImportError:
            pytest.skip("MLflow not installed")


class TestHyperparameterSweeps:
    """Test logging grid search and hyperparameter sweep results."""

    def test_sweep_run_creation(self, sweep_run_set):
        """Test that sweep runs are created with hyperparameters."""
        assert sweep_run_set is not None
        assert len(sweep_run_set) == 10

        # Verify each run has hyperparameters
        for run_info in sweep_run_set:
            assert "id" in run_info
            assert "hyperparams" in run_info
            assert "lr" in run_info["hyperparams"]
            assert "batch_size" in run_info["hyperparams"]
            assert "epochs" in run_info["hyperparams"]

    def test_sweep_parameter_logging(self, mlflow_client_full, sweep_run_set):
        """Test querying sweep runs and comparing hyperparameters."""
        try:
            import mlflow

            # Collect all sweep parameters
            sweep_params = []
            for run_info in sweep_run_set:
                run_data = mlflow_client_full.get_run(run_info["id"]).data
                sweep_params.append(run_data.params)

            # Verify parameter diversity
            assert len(sweep_params) == 10
            unique_lrs = set(p.get("lr") for p in sweep_params if "lr" in p)
            unique_batch_sizes = set(
                p.get("batch_size") for p in sweep_params if "batch_size" in p
            )

            # Should have multiple learning rates and batch sizes
            assert len(unique_lrs) > 1
            assert len(unique_batch_sizes) > 1

        except ImportError:
            pytest.skip("MLflow not installed")


class TestCrossRunComparison:
    """Test querying and analyzing multiple runs."""

    def test_search_runs(self, mlflow_client_full, sweep_run_set, parent_experiment):
        """Test searching and comparing runs."""
        try:
            import mlflow

            exp_id = parent_experiment["id"]

            # Search runs by tag
            runs = mlflow_client_full.search_runs(
                experiment_ids=[exp_id],
                filter_string="tags.test_type = 'hyperparameter_sweep'",
            )

            assert len(runs) == 10

            # Extract metrics for comparison
            accuracies = [run.data.metrics.get("accuracy", 0) for run in runs]
            assert len(accuracies) == 10
            assert all(0 < acc < 1 for acc in accuracies)

        except ImportError:
            pytest.skip("MLflow not installed")

    def test_run_comparison_metrics(self, mlflow_client_full, sweep_run_set):
        """Test comparing metrics across multiple runs."""
        try:
            import mlflow

            # Collect metrics from all runs
            all_metrics = {}
            for run_info in sweep_run_set:
                run_data = mlflow_client_full.get_run(run_info["id"]).data
                accuracy = run_data.metrics.get("accuracy", 0)
                all_metrics[run_info["id"]] = accuracy

            # Verify metrics collection
            assert len(all_metrics) == 10
            accuracies = list(all_metrics.values())

            # Find best and worst runs
            best_accuracy = max(accuracies)
            worst_accuracy = min(accuracies)

            assert best_accuracy > worst_accuracy
            assert best_accuracy > 0.8

        except ImportError:
            pytest.skip("MLflow not installed")


class TestNestedRuns:
    """Test complex run hierarchies."""

    def test_nested_run_creation(self, parent_run, child_run):
        """Test creating nested run structure."""
        assert parent_run is not None
        assert child_run is not None
        assert child_run["parent_run_id"] == parent_run["id"]

    def test_nested_run_tags(self, mlflow_client_full, parent_run, child_run):
        """Test that nested runs have proper tags."""
        try:
            import mlflow

            parent_data = mlflow_client_full.get_run(parent_run["id"]).data
            child_data = mlflow_client_full.get_run(child_run["id"]).data

            assert parent_data.tags.get("run_type") == "parent"
            assert child_data.tags.get("run_type") == "child"
            assert child_data.tags.get("parent") == parent_run["id"]

        except ImportError:
            pytest.skip("MLflow not installed")


class TestDistributedLogging:
    """Test parallel run logging without conflicts."""

    def test_distributed_run_logging(self, distributed_run_set):
        """Test logging from multiple distributed ranks."""
        assert distributed_run_set is not None
        assert len(distributed_run_set) == 5

        # Verify each rank has its own run
        for i, run_info in enumerate(distributed_run_set):
            assert run_info["rank"] == i
            assert "id" in run_info

    def test_distributed_metrics_isolation(self, mlflow_client_full, distributed_run_set):
        """Test that distributed metrics are properly isolated."""
        try:
            import mlflow

            # Collect metrics from all ranks
            for i, run_info in enumerate(distributed_run_set):
                run_data = mlflow_client_full.get_run(run_info["id"]).data
                metrics = run_data.metrics

                # Should have metrics from this rank
                rank_metric_key = f"rank_{i}_loss"
                assert rank_metric_key in metrics

                # Should not have metrics from other ranks
                for j in range(5):
                    if j != i:
                        other_metric_key = f"rank_{j}_loss"
                        assert other_metric_key not in metrics

        except ImportError:
            pytest.skip("MLflow not installed")


class TestExportImport:
    """Test experiment data serialization and portability."""

    def test_run_data_export(self, mlflow_client_full, export_import_run):
        """Test exporting run data."""
        try:
            import mlflow

            run_data = mlflow_client_full.get_run(export_import_run["id"]).data

            # Serialize run data
            exported_data = {
                "run_id": export_import_run["id"],
                "params": dict(run_data.params),
                "metrics": dict(run_data.metrics),
                "tags": dict(run_data.tags),
            }

            # Verify exported data structure
            assert "run_id" in exported_data
            assert "params" in exported_data
            assert "metrics" in exported_data
            assert exported_data["params"].get("param1") == "value1"
            assert exported_data["metrics"].get("metric1") == 0.97

        except ImportError:
            pytest.skip("MLflow not installed")

    def test_experiment_data_serialization(
        self, mlflow_client_full, parent_experiment
    ):
        """Test serializing complete experiment data."""
        try:
            import mlflow

            exp_id = parent_experiment["id"]
            runs = mlflow_client_full.search_runs(experiment_ids=[exp_id])

            # Serialize experiment
            serialized_exp = {
                "experiment_id": exp_id,
                "experiment_name": parent_experiment["name"],
                "run_count": len(runs),
                "runs": [],
            }

            for run in runs:
                run_data = {
                    "run_id": run.info.run_id,
                    "params": dict(run.data.params),
                    "metrics": dict(run.data.metrics),
                    "tags": dict(run.data.tags),
                }
                serialized_exp["runs"].append(run_data)

            # Verify serialized data
            assert serialized_exp["experiment_id"] == exp_id
            assert serialized_exp["run_count"] >= 0

        except ImportError:
            pytest.skip("MLflow not installed")


class TestPerformanceTracking:
    """Test latency and resource monitoring."""

    def test_metric_logging_performance(self, mlflow_client_full, parent_experiment):
        """Test performance of logging many metrics."""
        try:
            import mlflow
            import time

            exp_id = parent_experiment["id"]
            run = mlflow_client_full.create_run(experiment_id=exp_id)

            # Measure time to log 1000 metrics
            start_time = time.time()
            for i in range(1000):
                mlflow_client_full.log_metric(
                    run.info.run_id, f"perf_metric_{i}", float(i) * 0.001, step=0
                )
            duration = time.time() - start_time

            # Should complete in reasonable time (< 30 seconds)
            assert duration < 30.0

            mlflow_client_full.set_terminated(run.info.run_id)

        except ImportError:
            pytest.skip("MLflow not installed")

    def test_run_query_performance(self, mlflow_client_full, parent_experiment):
        """Test performance of querying runs."""
        try:
            import mlflow
            import time

            exp_id = parent_experiment["id"]

            # Create multiple runs
            run_ids = []
            for i in range(50):
                run = mlflow_client_full.create_run(experiment_id=exp_id)
                run_ids.append(run.info.run_id)
                mlflow_client_full.set_terminated(run.info.run_id)

            # Measure query performance
            start_time = time.time()
            runs = mlflow_client_full.search_runs(experiment_ids=[exp_id])
            query_duration = time.time() - start_time

            # Query should be fast (< 5 seconds)
            assert query_duration < 5.0
            assert len(runs) >= 50

        except ImportError:
            pytest.skip("MLflow not installed")
