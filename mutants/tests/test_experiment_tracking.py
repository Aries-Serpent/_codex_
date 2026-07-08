"""
Test Experiment Tracking

Test module for experiment tracking.
"""

from pathlib import Path

from codex_ml.tracking.experiments import (
    finish_run,
    load_events,
    log_metric,
    new_run_info,
    start_run,
)
from scripts.analyze_experiments import analyze


def test_experiment_tracking_roundtrip(tmp_path: Path) -> None:
    base_dir = tmp_path / "artifacts" / "experiments"
    run_info = new_run_info("unit-test", git_hash="abc123", run_id="run-test")

    run_dir = start_run(run_info, base_dir)
    log_metric(run_info, "loss", 0.5, step=1, base_dir=base_dir)
    finish_run(run_info, base_dir=base_dir)

    events = load_events(run_dir)
    assert any(event.get("type") == "metric" for event in events), "Condition must be true"

    summary = analyze(base_dir=base_dir, output_dir=tmp_path / "artifacts")
    md_path = summary["markdown_path"]
    json_path = summary["json_path"]

    assert md_path.exists(), "Condition must be true"
    assert json_path.exists(), "Condition must be true"
    assert "run-test" in md_path.read_text(encoding="utf-8"), "Condition must be true"
