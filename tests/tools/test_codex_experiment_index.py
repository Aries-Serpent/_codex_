"""
Test Codex Experiment Index

Test module for codex experiment index.
"""

from pathlib import Path
import json

import yaml

import tools.codex_experiment_index as idx


def test_experiment_index_builds_summary(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    train_run = runs_dir / "train" / "runA"
    eval_run = runs_dir / "eval" / "runB"
    train_run.mkdir(parents=True, exist_ok=True)
    eval_run.mkdir(parents=True, exist_ok=True)

    (train_run / "run_manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "context": {
                    "run_id": "runA",
                    "seed": 1,
                    "created_at": "2025-01-01T00-00-00Z",
                    "config_path": "conf/minimal_train.yaml",
                },
                "config": {},
            }
        ),
        encoding="utf-8",
    )

    (eval_run / "run_manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "context": {
                    "run_id": "runB",
                    "seed": 2,
                    "created_at": "2025-01-01T01-00-00Z",
                    "config_path": "conf/minimal_eval.yaml",
                },
                "config": {},
            }
        ),
        encoding="utf-8",
    )

    (train_run / "metrics.ndjson").write_text(
        '{"step": 0, "timestamp": 1.0, "metrics": {"loss": 1.0}}\n'
        '{"step": 1, "timestamp": 2.0, "metrics": {"loss": 0.9, "accuracy": 0.5}}\n',
        encoding="utf-8",
    )

    rc = idx.main(
        [
            "--runs-dir",
            str(runs_dir),
            "--json-out",
            "index.json",
            "--md-out",
            "index.md",
        ]
    )
    assert rc == 0

    json_out = tmp_path / "index.json"
    md_out = tmp_path / "index.md"
    assert json_out.exists()
    assert md_out.exists()

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["total_runs"] == 2
    modes = {r["mode"] for r in data["runs"]}
    assert modes == {"train", "eval"}
