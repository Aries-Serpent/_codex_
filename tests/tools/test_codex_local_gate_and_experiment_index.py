"""
Test Codex Local Gate And Experiment Index

Test module for codex local gate and experiment index.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools import codex_dataset_index, codex_experiment_index, codex_local_gate_runner


def test_local_gate_runner_uses_default_gate_when_config_missing(
    tmp_path: Path,
) -> None:
    json_out = tmp_path / "report.json"
    rc = codex_local_gate_runner.main(
        [
            "--repo-root",
            str(tmp_path),
            "--config",
            str(tmp_path / "missing.yaml"),
            "--json-out",
            str(json_out),
            "--md-out",
            str(tmp_path / "report.md"),
        ]
    )
    assert rc == 0, "rc is not valid"
    summary = json.loads(json_out.read_text(encoding="utf-8"))
    assert summary["results"], "Result must not be empty"


def test_local_gate_runner_with_custom_config(tmp_path: Path) -> None:
    config = tmp_path / "codex_local_gate.yaml"
    config.write_text(
        """
gates:
  - name: echo-one
    cmd: [python, -c, "logger.info('one')"]
  - name: echo-two
    cmd: [python, -c, "logger.info('two')"]
""",
        encoding="utf-8",
    )
    json_out = tmp_path / "custom_report.json"
    rc = codex_local_gate_runner.main(
        [
            "--repo-root",
            str(tmp_path),
            "--config",
            str(config),
            "--json-out",
            str(json_out),
            "--md-out",
            str(tmp_path / "custom_report.md"),
        ]
    )
    assert rc == 0, "rc is not valid"
    data = json.loads(json_out.read_text(encoding="utf-8"))
    names = [entry["name"] for entry in data["results"]]
    assert names == ["echo-one", "echo-two"]


def test_experiment_index_handles_empty_runs_dir(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    json_out = tmp_path / "index.json"
    rc = codex_experiment_index.main(
        [
            "--runs-dir",
            str(runs_dir),
            "--json-out",
            str(json_out),
            "--md-out",
            str(tmp_path / "index.md"),
        ]
    )
    assert rc == 0, "rc is not valid"
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["runs"] == [], "Data must not be empty"


def test_experiment_index_collects_meta(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    run_path = runs_dir / "run-123"
    run_path.mkdir(parents=True)
    meta = {"id": "run-123", "metric": 0.5}
    (run_path / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    json_out = tmp_path / "index.json"
    rc = codex_experiment_index.main(
        [
            "--runs-dir",
            str(runs_dir),
            "--json-out",
            str(json_out),
            "--md-out",
            str(tmp_path / "index.md"),
        ]
    )
    assert rc == 0, "rc is not valid"
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["runs"][0]["run_id"] == "run-123", "Data must not be empty"
    assert data["runs"][0]["meta"]["metric"] == 0.5, "Data must not be empty"


def test_dataset_index_builds_outputs(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir()
    (data_root / "sample.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    json_out = tmp_path / "dataset.json"
    md_out = tmp_path / "dataset.md"
    rc = codex_dataset_index.main(
        [
            "--data-root",
            str(data_root),
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ]
    )
    assert rc == 0, "rc is not valid"
    index = json.loads(json_out.read_text(encoding="utf-8"))
    assert index["files"], "Condition must be true"
    assert md_out.exists(), "Condition must be true"
