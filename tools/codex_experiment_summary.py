#!/usr/bin/env python
"""Summarize experiments from `_codex_` runs.

This tool walks `runs/train/**` and `runs/eval/**` and looks for:

- run_manifest.yaml
- experiment_meta.json
- metrics.ndjson

It then produces:

- codex_experiment_summary.json
- codex_experiment_summary.md

The summary groups runs by `experiment_name` (if present), and includes:

- mode, run_id, created_at, seed
- latest metric snapshot (if any)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def _iter_run_dirs(base: Path) -> List[tuple[str, Path]]:
    run_dirs: List[tuple[str, Path]] = []
    for mode in ("train", "eval"):
        root = base / mode
        if not root.exists():
            continue
        for p in root.iterdir():
            if p.is_dir():
                run_dirs.append((mode, p))
    return run_dirs


def _load_manifest(run_dir: Path) -> Dict[str, Any]:
    p = run_dir / "run_manifest.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _load_experiment_meta(run_dir: Path) -> Dict[str, Any]:
    p = run_dir / "experiment_meta.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_last_metric(run_dir: Path) -> Optional[Dict[str, Any]]:
    p = run_dir / "metrics.ndjson"
    if not p.exists():
        return None
    last = None
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            last = line
    if last is None:
        return None
    try:
        return json.loads(last)
    except Exception:
        return {"raw": last}


def build_summary(runs_dir: Path) -> Dict[str, Any]:
    experiments: Dict[str, List[Dict[str, Any]]] = {}
    for mode, run_dir in _iter_run_dirs(runs_dir):
        manifest = _load_manifest(run_dir)
        meta = _load_experiment_meta(run_dir)
        last_metric = _load_last_metric(run_dir)

        ctx = manifest.get("context", {}) or {}
        exp_name = meta.get("experiment_name") or "(unlabeled)"

        entry = {
            "mode": mode,
            "run_id": ctx.get("run_id", run_dir.name),
            "path": str(run_dir),
            "created_at": ctx.get("created_at"),
            "seed": ctx.get("seed"),
            "config_path": ctx.get("config_path"),
            "experiment_name": exp_name,
            "labels": meta.get("labels") or {},
            "last_metric": last_metric,
        }
        experiments.setdefault(exp_name, []).append(entry)

    return {"runs_dir": str(runs_dir), "experiments": experiments}


def _write_json(path: Path, summary: Dict[str, Any]) -> None:
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, summary: Dict[str, Any]) -> None:
    experiments = summary.get("experiments", {}) or {}
    lines: List[str] = []
    lines.append("# `_codex_` Experiment Summary\n")
    lines.append(f"- Base dir: `{summary.get('runs_dir', '.')}`")
    lines.append(f"- Total experiment groups: **{len(experiments)}**\n")

    if not experiments:
        lines.append("No experiments found.\n")
        path.write_text("\n".join(lines), encoding="utf-8")
        return

    for exp_name, runs in sorted(experiments.items(), key=lambda kv: kv[0]):
        lines.append(f"## Experiment: `{exp_name}`\n")
        lines.append("| Mode | Run ID | Created At | Seed | Last Metric |")
        lines.append("| ---- | ------ | ---------- | ---- | ----------- |")
        for e in sorted(runs, key=lambda r: (r.get("mode") or "", r.get("run_id") or "")):
            last = e.get("last_metric") or {}
            if isinstance(last, dict) and any(
                k in last for k in ("loss", "accuracy", "eval_loss", "eval_accuracy")
            ):
                parts = []
                for k in ("loss", "accuracy", "eval_loss", "eval_accuracy"):
                    if k in last:
                        parts.append(f"{k}={last[k]}")
                last_str = ", ".join(parts)
            else:
                last_str = "" if not last else json.dumps(last)[:80]
            lines.append(
                "| {mode} | `{run_id}` | {created} | {seed} | {metric} |".format(
                    mode=e.get("mode"),
                    run_id=e.get("run_id"),
                    created=e.get("created_at") or "",
                    seed=e.get("seed") or "",
                    metric=last_str,
                )
            )
        lines.append("")  # blank line between experiments

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize experiments for `_codex_`.")
    parser.add_argument(
        "--runs-dir",
        type=str,
        default="runs",
        help="Base runs directory (default: runs)",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_experiment_summary.json",
        help="JSON output path (default: codex_experiment_summary.json)",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_experiment_summary.md",
        help="Markdown output path (default: codex_experiment_summary.md)",
    )
    args = parser.parse_args(argv)

    runs_dir = Path(args.runs_dir).expanduser().resolve()
    summary = build_summary(runs_dir)

    json_out = Path(args.json_out).expanduser().resolve()
    md_out = Path(args.md_out).expanduser().resolve()
    _write_json(json_out, summary)
    _write_markdown(md_out, summary)

    print(f"Wrote experiment summary JSON to {json_out}")
    print(f"Wrote experiment summary Markdown to {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
