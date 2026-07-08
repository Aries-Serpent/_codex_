"""
Test Experiment Logging

Test module for experiment logging.
"""

import json
from pathlib import Path

import yaml

from codex_ml.cli import eval_minimal, train_minimal
from codex_ml.logging.experiment import ExperimentTracker


def test_experiment_tracker_writes_meta(tmp_path: Path):
    run_dir = tmp_path / "runs" / "train" / "train-run"
    run_dir.mkdir(parents=True, exist_ok=True)

    tracker = ExperimentTracker(run_dir=run_dir, mode="train", run_id="train-run")
    tracker.log_experiment(
        experiment_name="exp-test",
        labels={"k": "v"},
    )

    meta_path = run_dir / "experiment_meta.json"
    assert meta_path.exists(), "Condition must be true"
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    assert data["experiment_name"] == "exp-test", "Data must not be empty"
    assert data["mode"] == "train", "Data must not be empty"
    assert data["run_id"] == "train-run", "Data must not be empty"
    assert data["labels"]["k"] == "v", "Data must not be empty"


def _write_dummy_config(path: Path) -> None:
    cfg = {
        "model": {"hidden_size": 64},
        "training": {"max_steps": 2, "batch_size": 1},
        "data": {"dataset_name": "dummy"},
        "eval": {"batch_size": 1},
    }
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")


def test_train_minimal_integration_with_experiment_tracker(tmp_path: Path):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    cfg_path = conf_dir / "train.yaml"
    _write_dummy_config(cfg_path)

    runs_dir = tmp_path / "runs"

    rc = train_minimal.main(
        [
            "--config",
            str(cfg_path),
            "--runs-dir",
            str(runs_dir),
            "--seed",
            "13",
            "--max-steps",
            "2",
            "--experiment-name",
            "exp-train",
        ]
    )
    assert rc == 0, "rc is not valid"

    train_root = runs_dir / "train"
    run_dirs = [p for p in train_root.iterdir() if p.is_dir()]
    assert run_dirs, "run_dirs is not valid"
    meta = (run_dirs[0] / "experiment_meta.json").read_text(encoding="utf-8")
    data = json.loads(meta)
    assert data["experiment_name"] == "exp-train", "Data must not be empty"


def test_eval_minimal_integration_with_experiment_tracker(tmp_path: Path):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    cfg_path = conf_dir / "eval.yaml"
    _write_dummy_config(cfg_path)

    runs_dir = tmp_path / "runs"
    ckpt_dir = runs_dir / "train"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    rc = eval_minimal.main(
        [
            "--config",
            str(cfg_path),
            "--runs-dir",
            str(runs_dir),
            "--seed",
            "17",
            "--checkpoint",
            str(ckpt_dir),
            "--experiment-name",
            "exp-eval",
        ]
    )
    assert rc == 0, "rc is not valid"

    eval_root = runs_dir / "eval"
    run_dirs = [p for p in eval_root.iterdir() if p.is_dir()]
    assert run_dirs, "run_dirs is not valid"
    meta = (run_dirs[0] / "experiment_meta.json").read_text(encoding="utf-8")
    data = json.loads(meta)
    assert data["experiment_name"] == "exp-eval", "Data must not be empty"
    assert data["labels"]["checkpoint"].endswith("train"), "Data must not be empty"
