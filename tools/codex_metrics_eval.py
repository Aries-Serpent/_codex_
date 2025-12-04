#!/usr/bin/env python
"""Evaluate simple metrics over NDJSON/CSV prediction logs.

The tool is intentionally lightweight and relies on ``src/codex_ml/metrics/core``
for metric definitions. It supports NDJSON/JSONL and CSV inputs containing at
minimum ``label`` and ``prediction`` fields.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from codex_ml.metrics import core as metrics_core


LabelPred = Tuple[float, float]


@dataclass
class EvalStats:
    count: int
    metrics: Dict[str, float | None]


def _is_ndjson_like(path: Path) -> bool:
    return path.suffix.lower() in {".ndjson", ".jsonl"}


def _is_csv_like(path: Path) -> bool:
    return path.suffix.lower() == ".csv"


def _load_ndjson(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def _load_csv(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8").splitlines()
    reader = csv.DictReader(text)
    return [dict(row) for row in reader]


def _load_records(path: Path) -> List[Dict[str, Any]]:
    if _is_ndjson_like(path):
        return _load_ndjson(path)
    if _is_csv_like(path):
        return _load_csv(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def _extract_targets(records: Iterable[Dict[str, Any]]) -> Tuple[List[float], List[float]]:
    labels: List[float] = []
    predictions: List[float] = []
    for record in records:
        label = record.get("label") if "label" in record else record.get("target") if "target" in record else record.get("truth")
        pred = record.get("prediction") if "prediction" in record else record.get("pred") if "pred" in record else record.get("output")
        if label is None or pred is None:
            continue
        labels.append(float(label))
        predictions.append(float(pred))
    return labels, predictions


def _write_json(stats: EvalStats, path: Path) -> None:
    payload = {"count": stats.count, "metrics": stats.metrics}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_csv(stats: EvalStats, path: Path) -> None:
    lines = ["metric,value"]
    for name, value in stats.metrics.items():
        val = "" if value is None else str(value)
        lines.append(f"{name},{val}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def evaluate(path: Path, metric_names: Sequence[str]) -> EvalStats:
    records = _load_records(path)
    labels, predictions = _extract_targets(records)
    metrics = metrics_core.compute_metrics(metric_names, labels, predictions)
    return EvalStats(count=len(labels), metrics=dict(metrics))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate metrics for NDJSON/CSV predictions.")
    parser.add_argument("input", type=Path, help="Prediction log file (NDJSON/JSONL/CSV).")
    parser.add_argument(
        "--metrics",
        type=str,
        default="accuracy,mse",
        help="Comma-separated list of metrics to compute (default: accuracy,mse).",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("codex_metrics_summary.json"),
        help="Output JSON path (default: codex_metrics_summary.json).",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=None,
        help="Optional CSV output path (default: none).",
    )
    args = parser.parse_args(argv)

    metric_names = [m.strip() for m in args.metrics.split(",") if m.strip()]
    stats = evaluate(args.input, metric_names)

    json_out = args.json_out.expanduser().resolve()
    _write_json(stats, json_out)
    print(f"Wrote metrics summary to {json_out}")

    if args.csv_out:
        csv_out = args.csv_out.expanduser().resolve()
        _write_csv(stats, csv_out)
        print(f"Wrote metrics CSV summary to {csv_out}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
