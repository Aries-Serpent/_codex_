"""
Test Experiment

Test module for experiment.
"""

from pathlib import Path

from codex_ml.logging.experiment import ExperimentTracker


def test_experiment_tracker_writes_metadata(tmp_path: Path):
    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    tracker = ExperimentTracker(run_dir, mode="train", run_id="r1")

    tracker.log_experiment("demo", labels={"stage": "unit"})

    out_file = run_dir / "experiment_meta.json"
    content = out_file.read_text(encoding="utf-8")
    assert '"experiment_name": ' in content, "Content must not be empty"
    assert "demo" in content, "Content must not be empty"
    assert '"stage": ' in content, "Content must not be empty"
