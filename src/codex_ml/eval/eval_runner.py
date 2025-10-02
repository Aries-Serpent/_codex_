"""Standalone evaluation runner emitting NDJSON/CSV metrics with optional CLI."""

from __future__ import annotations

import csv
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence

try:  # pragma: no cover - optional
    import typer
except Exception:  # pragma: no cover
    typer = None  # type: ignore

from codex_ml.eval.datasets import load_dataset
from codex_ml.logging.run_logger import DEFAULT_SCHEMA_VERSION, METRICS_SCHEMA_URI
from codex_ml.metrics.registry import get_metric
from codex_ml.tracking.writers import NdjsonWriter

CSV_FIELDNAMES: Sequence[str] = (
    "run_id",
    "dataset",
    "split",
    "phase",
    "metric",
    "step",
    "value",
    "n",
    "timestamp",
    "notes",
    "ci_low",
    "ci_high",
)


def _bootstrap(
    fn, preds: Sequence[str], targets: Sequence[str], n: int, seed: int
) -> tuple[float | None, float | None, float | None]:
    """Compute fn with optional bootstrap confidence interval."""
    val = fn(preds, targets)
    # Only numeric results can be bootstrapped
    if not isinstance(val, (int, float)):
        return None if val is None else float(val), None, None
    if n <= 0 or len(preds) == 0:
        return float(val), None, None
    rng = random.Random(seed)
    vals: List[float] = []
    for _ in range(n):
        idx = [rng.randrange(len(preds)) for _ in preds]
        sp = [preds[i] for i in idx]
        st = [targets[i] for i in idx]
        sub = fn(sp, st)
        if isinstance(sub, (int, float)):
            vals.append(float(sub))
    if not vals:
        return float(val), None, None
    vals.sort()
    lo = vals[int(0.025 * n)]
    hi = vals[int(0.975 * n) if int(0.975 * n) < len(vals) else -1]
    return float(val), lo, hi


def evaluate_datasets(
    datasets: Sequence[str],
    metrics: Sequence[str],
    output_dir: str | Path,
    *,
    bootstrap: int = 0,
    seed: int = 0,
    max_samples: int = 0,
) -> None:
    """Evaluate metrics over datasets and write NDJSON/CSV logs to output_dir."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    ndjson_path = out / "metrics.ndjson"
    csv_path = out / "metrics.csv"
    ndjson_writer = NdjsonWriter(
        ndjson_path,
        schema_uri=METRICS_SCHEMA_URI,
        schema_version=DEFAULT_SCHEMA_VERSION,
        run_id=run_id,
    )

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(CSV_FIELDNAMES))
        writer.writeheader()

        for name in datasets:
            examples = load_dataset(name, max_samples=max_samples if max_samples > 0 else None)
            preds = [ex.input for ex in examples]
            targets = [ex.target for ex in examples]
            for metric_name in metrics:
                fn = get_metric(metric_name)
                val, lo, hi = _bootstrap(fn, preds, targets, bootstrap, seed)
                ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                record = {
                    "timestamp": ts,
                    "run_id": run_id,
                    "dataset": name,
                    "split": "eval",
                    "metric": metric_name,
                    "step": 0,
                    "value": val,
                    "n": len(examples),
                    "notes": "",
                    "ci_low": lo,
                    "ci_high": hi,
                    "tags": {"phase": "eval"},
                }
                ndjson_writer.log(record)
                writer.writerow(
                    {
                        "run_id": run_id,
                        "dataset": name,
                        "split": "eval",
                        "phase": "eval",
                        "metric": metric_name,
                        "step": 0,
                        "value": val,
                        "n": len(examples),
                        "timestamp": ts,
                        "notes": "",
                        "ci_low": "" if lo is None else lo,
                        "ci_high": "" if hi is None else hi,
                    }
                )

    ndjson_writer.close()


# Typer CLI glue
if typer is not None:  # pragma: no cover
    app = typer.Typer(add_completion=False)

    @app.command()
    def run(
        *,
        datasets: str = typer.Option(..., help="Comma-separated dataset names"),
        metrics: str = typer.Option(..., help="Comma-separated metric names"),
        output_dir: str = typer.Option("runs/eval", help="Output directory"),
        max_samples: int = typer.Option(0, help="Maximum samples per split"),
        seed: int = typer.Option(0, help="Random seed"),
        bootstrap: int = typer.Option(0, help="Bootstrap resamples for CI"),
    ) -> None:
        evaluate_datasets(
            datasets=[d.strip() for d in datasets.split(",") if d.strip()],
            metrics=[m.strip() for m in metrics.split(",") if m.strip()],
            output_dir=output_dir,
            bootstrap=bootstrap,
            seed=seed,
            max_samples=max_samples,
        )

    if __name__ == "__main__":
        app = app  # satisfy linters
