"""Standalone evaluation runner emitting NDJSON/CSV metrics."""

from __future__ import annotations

import csv
import json
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Sequence

try:  # pragma: no cover - optional
    import typer
except Exception:  # pragma: no cover - typer optional
    typer = None  # type: ignore

from codex_ml.metrics.registry import get_metric

from .datasets import load_dataset


def _bootstrap(
    fn, preds: Sequence[str], targets: Sequence[str], n: int, seed: int
) -> tuple[float | None, float | None, float | None]:
    """Compute ``fn`` with optional bootstrap confidence interval."""

    val = fn(preds, targets)
    if not isinstance(val, (int, float)):
        return None, None, None
    if n <= 0:
        return float(val), None, None
    rng = random.Random(seed)
    vals: List[float] = []
    for _ in range(n):
        idx = [rng.randrange(len(preds)) for _ in preds]
        sp = [preds[i] for i in idx]
        st = [targets[i] for i in idx]
        vals.append(float(fn(sp, st)))
    vals.sort()
    lo = vals[int(0.025 * n)]
    hi = vals[int(0.975 * n)]
    return float(val), lo, hi


def evaluate_datasets(
    datasets: Sequence[str],
    metrics: Sequence[str],
    output_dir: str | Path,
    *,
    bootstrap: int = 0,
    seed: int = 0,
) -> None:
    """Evaluate ``metrics`` over ``datasets`` and write logs to ``output_dir``."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    ndjson_path = out / "metrics.ndjson"
    csv_path = out / "metrics.csv"
    csv_file = csv_path.open("w", newline="", encoding="utf-8")
    writer = csv.DictWriter(
        csv_file,
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
            "ci_low",
            "ci_high",
        ],
    )
    writer.writeheader()

    for name in datasets:
        examples = load_dataset(name)
        preds = [ex.input for ex in examples]
        targets = [ex.target for ex in examples]
        for metric_name in metrics:
            fn = get_metric(metric_name)
            val, lo, hi = _bootstrap(fn, preds, targets, bootstrap, seed)
            record = {
                "run_id": run_id,
                "dataset": name,
                "split": "eval",
                "step": 0,
                "metric": metric_name,
                "value": val,
                "n": len(examples),
                "timestamp": datetime.utcnow().isoformat(),
                "notes": "",
                "ci_low": lo,
                "ci_high": hi,
            }
            with ndjson_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            writer.writerow(record)
    csv_file.close()


if typer is not None:  # pragma: no cover - CLI glue
    app = typer.Typer()

    @app.command()
    def run(
        datasets: str,
        metrics: str,
        output_dir: str = "runs/eval",
        max_samples: int | None = None,
        batch_size: int = 1,  # unused placeholder
        bootstrap: int = 0,
        seed: int = 0,
    ) -> None:
        _ = max_samples, batch_size  # placeholders for parity with spec
        evaluate_datasets(
            datasets=[d.strip() for d in datasets.split(",") if d.strip()],
            metrics=[m.strip() for m in metrics.split(",") if m.strip()],
            output_dir=output_dir,
            bootstrap=bootstrap,
            seed=seed,
        )

    if __name__ == "__main__":
        app()
