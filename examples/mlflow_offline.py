"""Inspect local Codex runs and launch MLflow in offline mode.

Usage
-----

1. Enable MLflow when invoking ``codex codex train``::

       CODEX_MLFLOW_ENABLE=1 codex codex train --config configs/training/base.yaml \
           --mlflow-uri file:./runs/mlflow

2. After the run completes, point this helper at the run directory::

       python examples/mlflow_offline.py runs/20240101-120000-default

The script prints a quick summary of the run and shows how to launch the
``mlflow ui`` against the local store.  All interactions remain on disk, making
it safe for air-gapped or cost-conscious environments.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def _load_ndjson(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def summarize_run(run_dir: Path) -> None:
    metrics = _load_ndjson(run_dir / "metrics.ndjson")
    params = _load_ndjson(run_dir / "params.ndjson")
    config = _load_ndjson(run_dir / "config.ndjson")

    print(f"Run directory: {run_dir}")
    if params:
        print("Parameters:")
        for entry in params:
            print(f"  {entry['name']}: {entry['value']}")
    if metrics:
        last = metrics[-1]
        print("Last metric:")
        print(
            f"  step={last['step']} split={last['split']} metric={last['metric']} value={last['value']}"
        )
    if config:
        print("Config snapshot recorded.")
    mlflow_uri = os.getenv("CODEX_MLFLOW_URI", "file:./runs/mlflow")
    print("\nTo inspect in MLflow UI (offline):")
    print(f"  mlflow ui --backend-store-uri {mlflow_uri}")
    if (run_dir / "tb").exists():
        print(f"TensorBoard logs detected. Launch with: tensorboard --logdir {run_dir / 'tb'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a Codex run directory")
    parser.add_argument("run_dir", type=Path, help="Path to the run directory under ./runs")
    args = parser.parse_args()
    summarize_run(args.run_dir)


if __name__ == "__main__":
    main()
