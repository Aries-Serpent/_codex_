"""Tests ensuring importing train_loop does not mutate the workspace."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def test_import_has_no_artifact_side_effects(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parent.parent
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(repo_root))

    sys.modules.pop("codex_ml.train_loop", None)

    module = importlib.import_module("codex_ml.train_loop")
    module = importlib.reload(module)

    assert not (tmp_path / "artifacts").exists()
    assert not (tmp_path / "artifacts" / "metrics").exists()


def test_run_training_creates_artifacts_on_demand(tmp_path):
    module = importlib.import_module("codex_ml.train_loop")
    module = importlib.reload(module)

    art_dir = tmp_path / "artifacts" / "metrics"
    assert not art_dir.exists()

    module.run_training(epochs=0, grad_accum=1, seed=1234, art_dir=art_dir)

    assert art_dir.exists()
    assert (art_dir / "metrics.json").exists()
    assert (art_dir / "metrics.ndjson").exists()
