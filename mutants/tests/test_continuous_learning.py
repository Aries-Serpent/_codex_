"""Behavioral checks for :mod:`codex_ml.training.continuous_learning`."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _train_fn(data: Any):
    return {"weights": 1}, {"accuracy": data.get("acc", 0.8)}


def test_registry_persistence(tmp_path):
    from codex_ml.training.continuous_learning import ContinuousLearningPipeline

    registry_path = tmp_path / "registry.json"
    pipeline = ContinuousLearningPipeline(
        "demo", registry_path=registry_path, drift_threshold=0.1, min_samples_retrain=1
    )

    should = pipeline.should_retrain(drift_score=0.05, samples_count=10)
    assert should is False

    version = pipeline.retrain(_train_fn, {"acc": 0.9}, dataset_hash="abc", drift_score=0.2)
    assert version.version.startswith("v1")
    assert pipeline.registry.get_latest() == version
    assert registry_path.exists()


def test_model_comparison_and_rollback(tmp_path):
    from codex_ml.training.continuous_learning import ContinuousLearningPipeline, ModelVersion

    registry_path = tmp_path / "registry.json"
    pipeline = ContinuousLearningPipeline(
        "demo", registry_path=registry_path, drift_threshold=0.0, min_samples_retrain=1
    )

    v1 = ModelVersion(
        version="v1", model_path=Path("/tmp/model1"), metrics={"accuracy": 0.8}, trained_at="now"
    )
    pipeline.registry.register(v1)
    v2 = pipeline.retrain(_train_fn, {"acc": 0.82}, dataset_hash=None, drift_score=0.3)

    comparison = pipeline.compare_models(v2, baseline_version=v1)
    assert comparison["is_better"] is True

    pipeline.rollback(to_version=v1.version)
