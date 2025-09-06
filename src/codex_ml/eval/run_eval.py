from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, List

from .evaluator import run_evaluator


def _load_texts(path: str) -> List[str]:
    """Load text records from ``path``.

    Supports plain text files (one example per line), NDJSON/JSONL with a
    ``text`` field and CSV files with a ``text`` column.
    """
    p = Path(path)
    if p.suffix in {".txt"}:
        return [line for line in p.read_text(encoding="utf-8").splitlines() if line]
    if p.suffix in {".ndjson", ".jsonl"}:
        return [
            json.loads(line)["text"] for line in p.read_text(encoding="utf-8").splitlines() if line
        ]
    if p.suffix == ".csv":
        with p.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            column = "text" if "text" in reader.fieldnames else reader.fieldnames[0]
            return [row[column] for row in reader]
    raise ValueError(f"Unsupported data format: {p.suffix}")


def _summarise_log(path: str) -> None:
    """Read a metrics log and print per-epoch averages."""
    p = Path(path)
    if p.suffix in {".ndjson", ".jsonl"}:
        records = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line]
    elif p.suffix == ".csv":
        with p.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            records = list(reader)
    else:
        raise ValueError(f"Unsupported log format: {p.suffix}")
    summary: dict[int, List[float]] = {}
    for rec in records:
        epoch = int(rec.get("epoch", 0))
        # Pick first numeric metric value in record
        val = None
        for key, value in rec.items():
            try:
                val = float(value)
                break
            except (TypeError, ValueError):
                continue
        if val is None:
            continue
        summary.setdefault(epoch, []).append(val)
    for epoch, vals in sorted(summary.items()):
        avg = sum(vals) / len(vals)
        print(json.dumps({"epoch": epoch, "metric": avg}))


def main(argv: Iterable[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Evaluate a model on a text dataset")
    ap.add_argument("--model", required=True, help="Model name or path")
    ap.add_argument("--data", required=True, help="Path to dataset (txt, ndjson, csv)")
    ap.add_argument("--metrics-log", dest="metrics_log", help="Optional metrics log to summarise")
    ap.add_argument("--safety", action="store_true", help="Enable prompt sanitisation")
    args = ap.parse_args(argv)

    texts = _load_texts(args.data)
    if args.safety:
        from codex_ml.safety import SafetyConfig, sanitize_prompt

        cfg = SafetyConfig()
        texts = [sanitize_prompt(t, cfg)["text"] for t in texts]
    metrics = run_evaluator(args.model, texts)
    print(json.dumps(metrics))
    if args.metrics_log:
        _summarise_log(args.metrics_log)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
