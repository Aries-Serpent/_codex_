"""Simple Hydra sweep runner.

Expands a parameter grid defined in a YAML file and sequentially launches
`codex_ml.cli.main` for each combination. Metrics are aggregated into CSV and
NDJSON summaries. Intended for local experimentation; all runs execute
sequentially.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import yaml

CODEX_HY_OUT = Path(".codex") / "hydra_last"


def _expand(grid: Dict[str, List[object]]) -> List[Dict[str, object]]:
    keys = list(grid.keys())
    values = [v if isinstance(v, list) else [v] for v in grid.values()]
    combos = [dict(zip(keys, combo)) for combo in itertools.product(*values)]
    return combos


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sweep-file", required=True, help="YAML defining sweep axes")
    parser.add_argument("--max-runs", type=int, default=0, help="Cap number of runs")
    parser.add_argument("--seed-grid", type=str, default="", help="Comma-separated seeds")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    grid = yaml.safe_load(Path(args.sweep_file).read_text()) or {}
    if args.seed_grid:
        grid["train.seed"] = [int(s) for s in args.seed_grid.split(",") if s]
    combos = _expand(grid)
    if args.max_runs and len(combos) > args.max_runs:
        combos = combos[: args.max_runs]

    if args.dry_run:
        for i, combo in enumerate(combos):
            print(i, combo)
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = Path("sweep_runs") / timestamp
    root.mkdir(parents=True, exist_ok=True)
    summary = []

    for idx, combo in enumerate(combos):
        overrides = [f"{k}={v}" for k, v in combo.items()]
        run_dir = root / f"run_{idx:03d}"
        cmd = ["python", "-m", "codex_ml.cli.main", *overrides]
        subprocess = __import__("subprocess")
        subprocess.run(cmd, check=False)
        run_dir.mkdir(parents=True, exist_ok=True)
        if CODEX_HY_OUT.exists():
            shutil.copytree(CODEX_HY_OUT, run_dir, dirs_exist_ok=True)
        (run_dir / "overrides.txt").write_text("\n".join(overrides))
        metrics_path = run_dir / "metrics.yaml"
        metrics = {}
        if metrics_path.exists():
            try:
                metrics = yaml.safe_load(metrics_path.read_text()) or {}
            except Exception:
                metrics = {}
        summary.append({"run_id": idx, **combo, **metrics})

    if summary:
        csv_path = root / "sweep_summary.csv"
        with csv_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=summary[0].keys())
            writer.writeheader()
            writer.writerows(summary)
        ndjson_path = root / "sweep_summary.ndjson"
        with ndjson_path.open("w") as fh:
            for row in summary:
                fh.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
