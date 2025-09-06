from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import typer

from codex_ml.eval.datasets import load_dataset
from codex_ml.metrics.registry import get_metric

app = typer.Typer(add_completion=False)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_row(nd_f, csv_writer, row: dict) -> None:
    nd_f.write(json.dumps(row) + "\n")
    csv_writer.writerow(row)


@app.command()
def run(
    *,
    datasets: str = typer.Option(..., help="Comma-separated dataset names"),
    metrics: str = typer.Option(..., help="Comma-separated metric names"),
    output_dir: str = typer.Option("runs/eval", help="Output directory"),
    max_samples: int = typer.Option(0, help="Maximum samples per split"),
    seed: int = typer.Option(0, help="Random seed"),  # noqa: ARG001 - placeholder
    bootstrap: int = typer.Option(0, help="Bootstrap resamples"),  # noqa: ARG001
) -> None:
    """Evaluate ``metrics`` on ``datasets`` and write NDJSON/CSV reports."""
    ds_names = [d.strip() for d in datasets.split(",") if d.strip()]
    metric_names = [m.strip() for m in metrics.split(",") if m.strip()]
    out = Path(output_dir)
    _ensure_dir(out)
    run_id = str(int(time.time()))
    nd_path = out / "metrics.ndjson"
    csv_path = out / "metrics.csv"
    with (
        nd_path.open("w", encoding="utf-8") as nd_f,
        csv_path.open("w", newline="", encoding="utf-8") as csv_f,
    ):
        writer = csv.DictWriter(
            csv_f,
            fieldnames=[
                "run_id",
                "dataset",
                "split",
                "step",
                "metric",
                "value",
                "n",
                "timestamp",
                "notes",
            ],
        )
        writer.writeheader()
        timestamp = int(time.time())
        for ds_name in ds_names:
            dataset = load_dataset(ds_name)
            for split, rows in dataset.items():
                if max_samples:
                    rows = rows[:max_samples]
                preds = [r["target"] for r in rows]
                targets = [r["target"] for r in rows]
                n = len(preds)
                for metric_name in metric_names:
                    metric_fn = get_metric(metric_name)
                    value = metric_fn(preds, targets)
                    row = {
                        "run_id": run_id,
                        "dataset": ds_name,
                        "split": split,
                        "step": 0,
                        "metric": metric_name,
                        "value": value if value is not None else "",
                        "n": n,
                        "timestamp": timestamp,
                        "notes": "",
                    }
                    _write_row(nd_f, writer, row)


if __name__ == "__main__":
    app()
