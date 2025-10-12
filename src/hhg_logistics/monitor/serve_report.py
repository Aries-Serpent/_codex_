from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report

from common.ndjson_tools import ndjson_to_csv


def _ensure_csv(src: Path, out_csv: Path) -> Path:
    """Return a CSV path, converting NDJSON sources when necessary."""

    if src.suffix.lower() == ".csv":
        return src

    ndjson_to_csv(src, out_csv)
    return out_csv


def _save_json(payload: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def build_report(
    reference: Path, current: Path, out_html: Path, out_json: Path | None = None
) -> Path:
    """Build an Evidently drift report for latency and generation metadata."""

    ref_df = pd.read_csv(reference)
    cur_df = pd.read_csv(current)

    keep_columns = [
        column
        for column in ["latency_ms", "prompt_len", "gen_len", "model", "source"]
        if column in ref_df.columns and column in cur_df.columns
    ]
    if keep_columns:
        ref_df = ref_df[keep_columns]
        cur_df = cur_df[keep_columns]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_df, current_data=cur_df)

    out_html.parent.mkdir(parents=True, exist_ok=True)
    report.save_html(str(out_html))

    if out_json is not None:
        _save_json(report.as_dict(), out_json)

    return out_html


def main(args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build serve drift report (HTML+JSON) from NDJSON/CSV logs."
    )
    parser.add_argument(
        "--reference",
        type=str,
        default=".codex/metrics/serve-ref.csv",
        help="Reference CSV or NDJSON file/dir",
    )
    parser.add_argument(
        "--current",
        type=str,
        default=".codex/metrics/",
        help="Current NDJSON directory or CSV file",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=".codex/reports/serve_drift.html",
        help="Output HTML path",
    )
    parser.add_argument(
        "--json",
        type=str,
        default=".codex/reports/serve_drift.json",
        help="Output JSON path",
    )
    parsed = parser.parse_args(args=args)

    reference_src = Path(parsed.reference)
    current_src = Path(parsed.current)
    out_path = Path(parsed.out)
    json_path = Path(parsed.json)

    ref_csv = _ensure_csv(reference_src, out_csv=Path(".codex/metrics/serve-ref.csv"))
    cur_csv = _ensure_csv(current_src, out_csv=Path(".codex/metrics/serve-cur.csv"))

    report_path = build_report(ref_csv, cur_csv, out_path, json_path)
    print(f"Wrote report: {report_path}")
    print(f"Wrote JSON: {json_path}")


if __name__ == "__main__":  # pragma: no cover - script entry
    main()
