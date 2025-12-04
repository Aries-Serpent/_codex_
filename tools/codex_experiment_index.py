#!/usr/bin/env python
"""Build a lightweight experiment index from `runs/` for `_codex_`."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def _load_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    return data


def _summarize_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"num_records": 0, "last_step": None, "last_metrics": {}}
    last = None
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        last = rec
        count += 1
    if last is None:
        return {"num_records": 0, "last_step": None, "last_metrics": {}}
    return {
        "num_records": count,
        "last_step": last.get("step"),
        "last_metrics": last.get("metrics", {}),
    }


def _iter_run_dirs(base: Path, mode: str) -> List[Path]:
    root = base / mode
    if not root.exists():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir()])


def build_index(runs_dir: Path) -> Dict[str, Any]:
    runs_dir = runs_dir.expanduser().resolve()
    records: List[Dict[str, Any]] = []

    for mode in ("train", "eval"):
        for run_dir in _iter_run_dirs(runs_dir, mode):
            manifest = _load_manifest(run_dir / "run_manifest.yaml")
            ctx = manifest.get("context") or {}
            summary = _summarize_metrics(run_dir / "metrics.ndjson")
            records.append(
                {
                    "mode": mode,
                    "run_id": ctx.get("run_id", run_dir.name),
                    "run_dir": str(run_dir),
                    "seed": ctx.get("seed"),
                    "created_at": ctx.get("created_at"),
                    "config_path": ctx.get("config_path"),
                    "metrics": summary,
                }
            )

    return {"runs_dir": str(runs_dir), "total_runs": len(records), "runs": records}


def _write_json(path: Path, index: Dict[str, Any]) -> None:
    path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, index: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# _codex_ Experiment Index\n")
    lines.append(f"- Runs directory: `{index['runs_dir']}`")
    lines.append(f"- Total runs: **{index['total_runs']}**\n")

    if not index["runs"]:
        lines.append("No runs were found under `runs/train` or `runs/eval`.\n")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    lines.append("## Runs\n")
    lines.append("| Mode | Run ID | Seed | Last Step | Last Metrics | Run Dir |")
    lines.append("| ---- | ------ | ---- | --------- | ------------ | ------- |")
    for rec in index["runs"]:
        metric_str = ", ".join(f"{k}={v}" for k, v in rec["metrics"].get("last_metrics", {}).items())
        lines.append(
            f"| `{rec['mode']}` | `{rec['run_id']}` | `{rec.get('seed', '')}` | "
            f"`{rec['metrics'].get('last_step')}` | `{metric_str}` | `{rec['run_dir']}` |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build experiment index from runs/.")
    parser.add_argument("--runs-dir", type=str, default="runs", help="Runs directory (default: runs).")
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_experiment_index.json",
        help="JSON output path (default: codex_experiment_index.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_experiment_index.md",
        help="Markdown output path (default: codex_experiment_index.md).",
    )
    args = parser.parse_args(argv)

    runs_dir = Path(args.runs_dir).expanduser().resolve()
    index = build_index(runs_dir)

    base_dir = runs_dir.parent
    json_out = Path(args.json_out)
    if not json_out.is_absolute():
        json_out = (base_dir / json_out).resolve()
    else:
        json_out = json_out.expanduser().resolve()

    md_out = Path(args.md_out)
    if not md_out.is_absolute():
        md_out = (base_dir / md_out).resolve()
    else:
        md_out = md_out.expanduser().resolve()

    _write_json(json_out, index)
    _write_markdown(md_out, index)
    print(f"Wrote experiment index JSON to {json_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
