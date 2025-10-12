from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_data_drift(
    reference_csv: Path,
    current_csv: Path,
    out_html: Path,
    out_json: Path,
    tracked_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Build a data drift report and return a JSON-serialisable summary."""

    ref_df = pd.read_csv(reference_csv)
    cur_df = pd.read_csv(current_csv)

    if tracked_columns:
        keep_cols = [
            col for col in tracked_columns if col in ref_df.columns and col in cur_df.columns
        ]
        if keep_cols:
            ref_df = ref_df[keep_cols]
            cur_df = cur_df[keep_cols]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_df, current_data=cur_df)

    _ensure_dir(out_html.parent)
    report.save_html(str(out_html))

    report_dict = report.as_dict()
    _ensure_dir(out_json.parent)
    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(report_dict, handle, indent=2, sort_keys=True)

    dataset_result = report_dict.get("metrics", [{}])[0].get("result", {})
    drift_share = dataset_result.get("dataset_drift", {}).get("share_of_drifted_columns", 0.0)
    per_feature = dataset_result.get("drift_by_columns", {})

    p_values: list[float] = []
    for meta in per_feature.values():
        score = meta.get("drift_score")
        if isinstance(score, int | float):
            p_values.append(float(score))

    p_value_mean = float(sum(p_values) / max(len(p_values), 1)) if p_values else 0.0

    return {
        "drift_share": float(drift_share) if drift_share is not None else 0.0,
        "p_value_mean": p_value_mean,
        "columns": list(per_feature.keys()),
        "per_feature": per_feature,
        "html": str(out_html),
        "json": str(out_json),
    }


def main(args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate data drift report (HTML + JSON) using Evidently."
    )
    parser.add_argument("--reference", type=str, required=True, help="Reference CSV path")
    parser.add_argument("--current", type=str, required=True, help="Current CSV path")
    parser.add_argument(
        "--out_html", type=str, default=".codex/reports/data_drift.html", help="HTML output path"
    )
    parser.add_argument(
        "--out_json", type=str, default=".codex/reports/data_drift.json", help="JSON output path"
    )
    parser.add_argument("--columns", type=str, default="", help="Comma separated column subset")
    parsed = parser.parse_args(args=args)

    cols = [c.strip() for c in parsed.columns.split(",") if c.strip()] if parsed.columns else None
    summary = build_data_drift(
        Path(parsed.reference),
        Path(parsed.current),
        Path(parsed.out_html),
        Path(parsed.out_json),
        tracked_columns=cols,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":  # pragma: no cover - script entry
    main()
