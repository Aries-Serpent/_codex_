# BEGIN: CODEX_TEST_MLFLOW_UTILS
from __future__ import annotations

import json
from argparse import ArgumentParser
from pathlib import Path

from codex_ml.tracking import (
    MlflowConfig,
    add_mlflow_flags,
    mlflow_from_args,
    seed_snapshot,
    start_run,
)


def test_seed_snapshot(tmp_path: Path) -> None:
    seeds = {"python": 123}
    seed_snapshot(seeds, tmp_path)
    data = json.loads((tmp_path / "seeds.json").read_text())
    assert data == seeds


def test_start_run_no_mlflow(tmp_path: Path) -> None:
    cfg = MlflowConfig(enable=True, tracking_uri=str(tmp_path), experiment="demo")
    with start_run(cfg) as run:
        assert run is False


def test_cli_flag_parsing() -> None:
    parser = ArgumentParser()
    add_mlflow_flags(parser)
    args = parser.parse_args(
        [
            "--mlflow-enable",
            "--mlflow-tracking-uri",
            "file:mlruns",
            "--mlflow-experiment",
            "exp",
        ]
    )
    cfg = mlflow_from_args(args)
    assert cfg.enable is True
    assert cfg.tracking_uri == "file:mlruns"
    assert cfg.experiment == "exp"


# END: CODEX_TEST_MLFLOW_UTILS
