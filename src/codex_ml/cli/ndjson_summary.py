"""Offline-friendly NDJSON metrics summarization helpers and CLI shims."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable, Mapping as MappingABC, Sequence
from pathlib import Path
from typing import Any

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
    "first_value",
    "last_value",
    "min_value",
    "max_value",
    "mean_value",
    "first_manifest_id",
    "last_manifest_id",
    "first_phase",
    "last_phase",
)


def _iter_metric_files(run_dir: Path, pattern: str | None = None) -> list[Path]:
    if run_dir.is_file():
        return [run_dir]
    if pattern:
        return sorted(run_dir.glob(pattern))
    base = run_dir / "metrics.ndjson"
    rotated: list[tuple[int, Path]] = []
    for candidate in run_dir.glob("metrics.ndjson.*"):
        suffix = candidate.name.split("metrics.ndjson.")[-1]
        if suffix.isdigit():
            rotated.append((int(suffix), candidate))
    ordered: list[Path] = [
        path for _, path in sorted(rotated, key=lambda item: item[0], reverse=True)
    ]
    if base.exists():
        ordered.append(base)
    return ordered


def _load_rows(run_dir: Path, *, pattern: str | None = None) -> list[dict[str, Any]]:
    files = _iter_metric_files(run_dir, pattern)
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


def _sort_key(timestamp: str | None, step: int | None) -> tuple[str, int]:
    ts_key = timestamp or ""
    step_key = step if step is not None else -1
    return ts_key, step_key


def _summarise_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        run_id = str(row.get("run_id") or "unknown")
        split = str(row.get("split") or "")
        metric = str(row.get("metric") or row.get("key") or "")
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
                "first_value": None,
                "last_value": None,
                "min_value": None,
                "max_value": None,
                "mean_value": None,
                "first_manifest_id": None,
                "last_manifest_id": None,
                "first_phase": "",
                "last_phase": "",
                "_numeric_sum": 0.0,
                "_numeric_count": 0,
                "_first_sort_key": None,
                "_last_sort_key": None,
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
            if entry["first_step"] is None or step_int < entry["first_step"]:
                entry["first_step"] = step_int
            if entry["_max_step"] is None or step_int > entry["_max_step"]:
                entry["_max_step"] = step_int

        timestamp = row.get("timestamp")
        sort_key = _sort_key(timestamp if isinstance(timestamp, str) else None, step_int)

        tags = row.get("tags")
        phase_value: str | None = None
        if isinstance(tags, MappingABC):
            manifest_raw = tags.get("manifest_id")
            if manifest_raw is not None:
                manifest_id = str(manifest_raw)
                entry["last_manifest_id"] = manifest_id
                if entry["first_manifest_id"] is None:
                    entry["first_manifest_id"] = manifest_id
            phase_raw = tags.get("phase")
            if phase_raw not in (None, ""):
                phase_value = str(phase_raw)

        first_sort_key = entry.get("_first_sort_key")
        if first_sort_key is None or sort_key <= first_sort_key:
            entry["_first_sort_key"] = sort_key
            if timestamp:
                entry["first_timestamp"] = timestamp
            if step_int is not None and (
                entry["first_step"] is None or step_int < entry["first_step"]
            ):
                entry["first_step"] = step_int
            entry["first_value"] = row.get("value")
            if phase_value is not None:
                entry["first_phase"] = phase_value

        last_sort_key = entry.get("_last_sort_key")
        if last_sort_key is None or sort_key >= last_sort_key:
            entry["_last_sort_key"] = sort_key
            if timestamp:
                entry["last_timestamp"] = timestamp
            if step_int is not None:
                entry["last_step"] = step_int
            entry["last_value"] = row.get("value")
            if phase_value is not None:
                entry["last_phase"] = phase_value

        numeric_value = _coerce_numeric(row.get("value"))
        if numeric_value is not None:
            entry["_numeric_sum"] += numeric_value
            entry["_numeric_count"] += 1
            if entry["min_value"] is None or numeric_value < entry["min_value"]:
                entry["min_value"] = numeric_value
            if entry["max_value"] is None or numeric_value > entry["max_value"]:
                entry["max_value"] = numeric_value

    result: list[dict[str, Any]] = []
    for entry in summary.values():
        numeric_count = entry.pop("_numeric_count")
        numeric_sum = entry.pop("_numeric_sum")
        entry.pop("_first_sort_key", None)
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


class NdjsonSummarizer:
    """Summarise NDJSON metric shards from a run directory."""

    fieldnames: Sequence[str] = FIELDNAMES

    def __init__(self, run_dir: str | Path, *, pattern: str | None = None) -> None:
        self.run_dir = Path(run_dir).expanduser().resolve()
        self.pattern = pattern

    def collect(self) -> list[dict[str, Any]]:
        return _load_rows(self.run_dir, pattern=self.pattern)

    def summarise(self) -> list[dict[str, Any]]:
        rows = self.collect()
        return _summarise_rows(rows)

    def write(self, fmt: str, destination: str | Path | None = None) -> Path:
        summary = self.summarise()
        suffix = fmt.lower()
        dest_path = (
            Path(destination).expanduser().resolve()
            if destination
            else self.run_dir / f"metrics_summary.{suffix}"
        )
        if suffix == "csv":
            return _write_csv(dest_path, summary)
        if suffix == "parquet":
            return _write_parquet(dest_path, summary)
        raise SystemExit(f"Unsupported output format: {fmt}")


def summarize_directory(
    run_dir: str | Path, fmt: str, destination: str | Path | None = None
) -> Path:
    summarizer = NdjsonSummarizer(run_dir)
    return summarizer.write(fmt, destination)


def _handle_summarize(args: argparse.Namespace) -> int:
    run_dir = Path(args.input).expanduser().resolve()
    try:
        summarizer = NdjsonSummarizer(run_dir)
        summary = summarizer.summarise()
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc
    suffix = args.output.lower()
    dest = (
        Path(args.dest).expanduser().resolve()
        if args.dest
        else (run_dir / f"metrics_summary.{suffix}")
    )
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
    summarize.add_argument(
        "--input", required=True, help="Run directory containing metrics.ndjson shards"
    )
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


def summarize(args: argparse.Namespace) -> int:
    inp = Path(args.input).expanduser().resolve()
    pattern = getattr(args, "pattern", "metrics.ndjson*")
    try:
        rows = _load_rows(inp if inp.is_dir() else inp, pattern=pattern if inp.is_dir() else None)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc
    summary_rows = _summarise_rows(rows)
    if args.output == "csv":
        dest_raw = getattr(args, "dest", None)
        if dest_raw:
            dest = Path(dest_raw).expanduser().resolve()
        else:
            base_dir = inp if inp.is_dir() else inp.parent
            dest = base_dir / "metrics_summary.csv"
        _write_csv(dest, summary_rows)
        print(str(dest))
        return 0

    metrics: dict[str, dict[str, Any]] = {}
    for row in summary_rows:
        metric_name = row.get("metric") or "unknown"
        slot = metrics.setdefault(metric_name, {"count": 0, "min": None, "max": None})
        slot["count"] += int(row.get("count") or 0)
        if row.get("min_value") is not None:
            current_min = slot["min"]
            slot["min"] = (
                row["min_value"] if current_min is None else min(current_min, row["min_value"])
            )
        if row.get("max_value") is not None:
            current_max = slot["max"]
            slot["max"] = (
                row["max_value"] if current_max is None else max(current_max, row["max_value"])
            )
    print(json.dumps({"metrics": metrics}, ensure_ascii=False))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


__all__ = [
    "FIELDNAMES",
    "NdjsonSummarizer",
    "build_parser",
    "main",
    "summarize",
    "summarize_directory",
]
