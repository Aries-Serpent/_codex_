"""Aggregate experiment runs into a concise summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from codex_ml.tracking.experiments import load_events


def _last_event(events: list[dict[str, Any]], event_type: str) -> dict[str, Any] | None:
    for event in reversed(events):
        if event.get("type") == event_type:
            return event
    return None


def _summarise_run(run_dir: Path) -> dict[str, Any]:
    events = load_events(run_dir)
    info_path = run_dir / "run_info.json"
    meta = json.loads(info_path.read_text(encoding="utf-8")) if info_path.exists() else {}

    metrics: dict[str, float] = {}
    for event in events:
        if event.get("type") == "metric" and "name" in event:
            metrics[event["name"]] = float(event.get("value", 0.0))

    finish = _last_event(events, "finish") or {}
    start = _last_event(events, "start") or {}
    return {
        "run_id": meta.get("run_id") or run_dir.name,
        "experiment": meta.get("experiment_name") or start.get("experiment", "unknown"),
        "status": finish.get("status", "unknown"),
        "metrics": metrics,
    }


def _aggregate_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, list[float]] = {}
    for run in runs:
        for key, value in run.get("metrics", {}).items():
            totals.setdefault(key, []).append(float(value))
    return {k: sum(v) / len(v) for k, v in totals.items() if v}


def _render_markdown(runs: list[dict[str, Any]], aggregates: dict[str, Any]) -> str:
    lines = ["# Experiment Summary", ""]
    lines.append(f"Runs analyzed: {len(runs)}")
    if aggregates:
        agg_parts = ", ".join(f"{k}={v:.4f}" for k, v in aggregates.items())
        lines.append(f"Aggregated metrics: {agg_parts}")
    lines.append("")
    lines.append("| run_id | experiment | status | metrics |")
    lines.append("| --- | --- | --- | --- |")
    for run in runs:
        metrics_str = ", ".join(f"{k}={v}" for k, v in run.get("metrics", {}).items())
        lines.append(
            f"| {run.get('run_id')} | {run.get('experiment')} | {run.get('status')} | {metrics_str or 'n/a'} |"
        )
    lines.append("")
    return "\n".join(lines)


def analyze(base_dir: str | Path = "artifacts/experiments", output_dir: str | Path | None = None) -> dict[str, Any]:
    base_path = Path(base_dir)
    if output_dir is None:
        output_dir = base_path.parent if base_path.parent != base_path else Path("artifacts")
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    runs: list[dict[str, Any]] = []
    if base_path.exists():
        for child in sorted(p for p in base_path.iterdir() if p.is_dir()):
            runs.append(_summarise_run(child))
    aggregates = _aggregate_metrics(runs)

    summary_md = _render_markdown(runs, aggregates)
    md_path = out_dir / "experiment_summary.md"
    md_path.write_text(summary_md, encoding="utf-8")

    json_payload = {"runs": runs, "aggregates": aggregates}
    json_path = out_dir / "experiment_summary.json"
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    return {"runs": runs, "aggregates": aggregates, "markdown_path": md_path, "json_path": json_path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate experiment runs into a summary")
    parser.add_argument("--base-dir", default="artifacts/experiments")
    parser.add_argument("--output-dir")
    args = parser.parse_args(argv)
    analyze(args.base_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
