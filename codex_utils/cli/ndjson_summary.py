"""Aggregate Codex NDJSON metric shards into tabular summaries."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Mapping as MappingABC
from pathlib import Path
from typing import Any, Iterable, Sequence


FIELDNAMES: Sequence[str] = (
    "run_id",
    "split",
    "metric",
    "dataset",
    "count",
    "first_step",
    "last_step",
    "first_timestamp",
    "last_timestamp",
    "min_value",
    "max_value",
    "mean_value",
    "last_value",
    "last_manifest_id",
)


def _iter_metric_files(run_dir: Path) -> list[Path]:
    base = run_dir / "metrics.ndjson"
    files: list[Path] = []
    if base.exists():
        files.append(base)
    rotated: list[tuple[int, Path]] = []
    for candidate in run_dir.glob("metrics.ndjson.*"):
        suffix = candidate.name.split("metrics.ndjson.")[-1]
        if suffix.isdigit():
            rotated.append((int(suffix), candidate))
    for _, path in sorted(rotated, key=lambda item: item[0]):
        files.append(path)
    return files


def _load_rows(run_dir: Path) -> list[dict[str, Any]]:
    files = _iter_metric_files(run_dir)
    if not files:
        raise FileNotFoundError(f"No metrics NDJSON files found in {run_dir}")
    rows: list[dict[str, Any]] = []
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                for raw in handle:
                    line = raw.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(payload, dict):
                        rows.append(payload)
        except FileNotFoundError:
            continue
    return rows


def _coerce_numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _summarise_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        run_id = str(row.get("run_id") or "unknown")
        split = str(row.get("split") or "")
        metric = str(row.get("metric") or "")
        dataset_val = row.get("dataset")
        dataset = "" if dataset_val in (None, "") else str(dataset_val)
        key = (run_id, split, metric, dataset)
        entry = summary.get(key)
        if entry is None:
            entry = {
                "run_id": run_id,
                "split": split,
                "metric": metric,
                "dataset": dataset,
                "count": 0,
                "first_step": None,
                "last_step": None,
                "first_timestamp": None,
                "last_timestamp": None,
                "min_value": None,
                "max_value": None,
                "mean_value": None,
                "last_value": None,
                "last_manifest_id": None,
                "_numeric_sum": 0.0,
                "_numeric_count": 0,
                "_last_sort_key": ("", -1),
                "_max_step": None,
            }
            summary[key] = entry

        entry["count"] += 1

        step_val = row.get("step")
        try:
            step_int = int(step_val) if step_val is not None else None
        except (TypeError, ValueError):
            step_int = None
        if step_int is not None:
            if entry["first_step"] is None:
                entry["first_step"] = step_int
            if entry["_max_step"] is None or step_int > entry["_max_step"]:
                entry["_max_step"] = step_int

        timestamp = row.get("timestamp")
        if isinstance(timestamp, str) and timestamp:
            if entry["first_timestamp"] is None:
                entry["first_timestamp"] = timestamp
            sort_key = (timestamp, step_int if step_int is not None else -1)
            if sort_key >= entry["_last_sort_key"]:
                entry["_last_sort_key"] = sort_key
                entry["last_timestamp"] = timestamp
                entry["last_value"] = row.get("value")
                if step_int is not None:
                    entry["last_step"] = step_int

        numeric_value = _coerce_numeric(row.get("value"))
        if numeric_value is not None:
            entry["_numeric_sum"] += numeric_value
            entry["_numeric_count"] += 1
            if entry["min_value"] is None or numeric_value < entry["min_value"]:
                entry["min_value"] = numeric_value
            if entry["max_value"] is None or numeric_value > entry["max_value"]:
                entry["max_value"] = numeric_value

        tags = row.get("tags")
        if isinstance(tags, MappingABC):
            manifest_id = tags.get("manifest_id")
            if manifest_id is not None:
                entry["last_manifest_id"] = str(manifest_id)

    result: list[dict[str, Any]] = []
    for entry in summary.values():
        numeric_count = entry.pop("_numeric_count")
        numeric_sum = entry.pop("_numeric_sum")
        entry.pop("_last_sort_key", None)
        max_step = entry.pop("_max_step", None)
        if entry.get("last_step") is None and max_step is not None:
            entry["last_step"] = max_step
        if numeric_count:
            entry["mean_value"] = numeric_sum / numeric_count
        result.append(entry)

    return sorted(
        result,
        key=lambda item: (item["run_id"], item["split"], item["metric"], item["dataset"]),
    )


def _write_csv(dest: Path, rows: Sequence[dict[str, Any]]) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDNAMES))
        writer.writeheader()
        for row in rows:
            payload = {key: row.get(key, "") for key in FIELDNAMES}
            for key, value in list(payload.items()):
                if value is None:
                    payload[key] = ""
            writer.writerow(payload)
    return dest


def _write_parquet(dest: Path, rows: Sequence[dict[str, Any]]) -> Path:
    try:
        import pandas as pd  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise SystemExit("pandas with parquet support is required for Parquet output") from exc

    dest.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame.from_records(list(rows))
    frame.to_parquet(dest, index=False)
    return dest


def _handle_summarize(args: argparse.Namespace) -> int:
    run_dir = Path(args.input).expanduser().resolve()
    try:
        rows = _load_rows(run_dir)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc
    summary = _summarise_rows(rows)
    suffix = args.output.lower()
    dest = Path(args.dest) if args.dest else run_dir / f"metrics_summary.{suffix}"
    if suffix == "csv":
        output_path = _write_csv(dest, summary)
    elif suffix == "parquet":
        output_path = _write_parquet(dest, summary)
    else:  # pragma: no cover - argparse guards choices
        raise SystemExit(f"Unsupported output format: {args.output}")
    print(f"Wrote {output_path} ({len(summary)} rows)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-ndjson", description=__doc__)
    sub = parser.add_subparsers(dest="command")
    summarize = sub.add_parser("summarize", help="Aggregate NDJSON metric shards")
    summarize.add_argument("--input", required=True, help="Run directory containing metrics.ndjson shards")
    summarize.add_argument(
        "--output",
        choices=("csv", "parquet"),
        default="csv",
        help="Summary output format",
    )
    summarize.add_argument(
        "--dest",
        help="Optional explicit destination path. Defaults to <run_dir>/metrics_summary.<ext>",
    )
    summarize.set_defaults(func=_handle_summarize)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


__all__ = ["build_parser", "main"]

