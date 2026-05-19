#!/usr/bin/env python
"""Reproducibility Manifest generator for `_codex_`.

This tool aggregates high-signal artifacts into a single manifest:

Inputs (all optional, best-effort):

- codex_env_snapshot.json          (environment snapshot)
- codex_dependency_report.json     (dependency / package view)
- codex_gap_registry.yaml          (gap registry)
- codex_experiment_index.json      (runs index)
- codex_local_gate_report.json     (local gate summary)

Outputs:

- codex_reproducibility_manifest.json
- codex_reproducibility_manifest.md

Design goals:

- Offline-only.
- Pure summarization and cross-link; no heavy analysis.
- Safe to call repeatedly.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from collections import Counter
from pathlib import Path
from typing import Any, Optional

import yaml


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None


def _summarize_env(snapshot: Any) -> dict[str, Any]:
    if not snapshot or not isinstance(snapshot, dict):
        return {"available": False}

    python_version = snapshot.get("python", {}).get("version")
    os_info = snapshot.get("os", {})
    env_vars = snapshot.get("env", {})

    # Only small, non-sensitive summary.
    codex_vars = {k: v for k, v in env_vars.items() if str(k).upper().startswith("CODEX_")}

    return {
        "available": True,
        "python_version": python_version,
        "os_platform": os_info.get("platform"),
        "os_release": os_info.get("release"),
        "codex_env_var_keys": sorted(codex_vars.keys()),
    }


def _summarize_deps(report: Any) -> dict[str, Any]:
    if not report or not isinstance(report, dict):
        return {"available": False}

    pkgs = report.get("packages") or []
    total = len(pkgs)
    # Try to separate direct vs transitive if represented; if not, just count.
    direct = sum(1 for p in pkgs if p.get("kind") == "direct")
    return {
        "available": True,
        "total_packages": total,
        "direct_dependencies": direct,
    }


def _summarize_gaps(registry: Any) -> dict[str, Any]:
    if not registry or not isinstance(registry, dict):
        return {"available": False}

    gaps = registry.get("gaps", []) or []
    total = len(gaps)
    by_status = Counter()
    by_risk = Counter()
    for g in gaps:
        by_status[str(g.get("status") or "unknown")] += 1
        by_risk[str(g.get("risk_level") or "unknown")] += 1
    return {
        "available": True,
        "total_gaps": total,
        "by_status": dict(sorted(by_status.items())),
        "by_risk_level": dict(sorted(by_risk.items())),
    }


def _summarize_experiments(index: Any) -> dict[str, Any]:
    if not index or not isinstance(index, dict):
        return {"available": False}

    runs = index.get("runs", []) or []
    total = len(runs)
    by_mode = Counter()
    cfg_paths = set()
    for r in runs:
        by_mode[str(r.get("mode") or "unknown")] += 1
        cfg = r.get("config_path")
        if cfg:
            cfg_paths.add(str(cfg))
    return {
        "available": True,
        "total_runs": total,
        "runs_by_mode": dict(sorted(by_mode.items())),
        "unique_config_paths": sorted(cfg_paths),
    }


def _summarize_local_gate(gate: Any) -> dict[str, Any]:
    if not gate or not isinstance(gate, dict):
        return {"available": False}

    overall = int(gate.get("overall_returncode", 0))
    results = gate.get("results", []) or []
    failed = [r for r in results if int(r.get("returncode", 0)) != 0]
    return {
        "available": True,
        "overall_returncode": overall,
        "total_commands": len(results),
        "failed_commands": [f.get("name") for f in failed],
    }


def build_manifest(
    repo_root: Path,
    env_snapshot_path: Path,
    dep_report_path: Path,
    gap_registry_path: Path,
    exp_index_path: Path,
    local_gate_path: Path,
) -> dict[str, Any]:
    env_snapshot = _load_json(env_snapshot_path)
    dep_report = _load_json(dep_report_path)
    gap_registry = _load_yaml(gap_registry_path)
    exp_index = _load_json(exp_index_path)
    local_gate = _load_json(local_gate_path)

    now = _dt.datetime.now(_dt.timezone.utc).isoformat() + "Z"

    return {
        "generated_at": now,
        "repo_root": str(repo_root),
        "inputs": {
            "env_snapshot": str(env_snapshot_path),
            "dependency_report": str(dep_report_path),
            "gap_registry": str(gap_registry_path),
            "experiment_index": str(exp_index_path),
            "local_gate_report": str(local_gate_path),
        },
        "summary": {
            "environment": _summarize_env(env_snapshot),
            "dependencies": _summarize_deps(dep_report),
            "gaps": _summarize_gaps(gap_registry),
            "experiments": _summarize_experiments(exp_index),
            "local_gate": _summarize_local_gate(local_gate),
        },
    }


def _write_json(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, manifest: dict[str, Any]) -> None:
    s = manifest.get("summary", {}) or {}
    env = s.get("environment", {})
    deps = s.get("dependencies", {})
    gaps = s.get("gaps", {})
    exps = s.get("experiments", {})
    gate = s.get("local_gate", {})

    lines: list[str] = []
    lines.append("# `_codex_` Reproducibility Manifest\n")
    lines.append(f"- Generated at: `{manifest.get('generated_at', '')}`")
    lines.append(f"- Repo root   : `{manifest.get('repo_root', '.')}`\n")

    lines.append("## 1. Environment\n")
    if not env.get("available"):
        lines.append("- Environment snapshot: **not available**\n")
    else:
        lines.append(f"- Python version: `{env.get('python_version')}`")
        lines.append(f"- OS: `{env.get('os_platform')}` / `{env.get('os_release')}`")
        keys = env.get("codex_env_var_keys") or []
        if keys:
            lines.append(f"- CODEX_* env vars: {', '.join(keys)}")
        else:
            lines.append("- CODEX_* env vars: (none recorded)")
        lines.append("")

    lines.append("## 2. Dependencies\n")
    if not deps.get("available"):
        lines.append("- Dependency report: **not available**\n")
    else:
        lines.append(f"- Total packages      : {deps.get('total_packages')}")
        lines.append(f"- Direct dependencies : {deps.get('direct_dependencies')}")
        lines.append("")

    lines.append("## 3. Gaps (Gap Registry)\n")
    if not gaps.get("available"):
        lines.append("- Gap registry: **not available**\n")
    else:
        lines.append(f"- Total gaps: **{gaps.get('total_gaps', 0)}**")
        by_status = gaps.get("by_status") or {}
        if by_status:
            lines.append("- By status:")
            for status, count in sorted(by_status.items()):
                lines.append(f"  - **{status}**: {count}")
        by_risk = gaps.get("by_risk_level") or {}
        if by_risk:
            lines.append("- By risk level:")
            for level, count in sorted(by_risk.items()):
                lines.append(f"  - **{level}**: {count}")
        lines.append("")

    lines.append("## 4. Experiments\n")
    if not exps.get("available"):
        lines.append("- Experiment index: **not available**\n")
    else:
        lines.append(f"- Total runs: **{exps.get('total_runs', 0)}**")
        by_mode = exps.get("runs_by_mode") or {}
        if by_mode:
            lines.append("- Runs by mode:")
            for mode, count in sorted(by_mode.items()):
                lines.append(f"  - **{mode}**: {count}")
        cfgs = exps.get("unique_config_paths") or []
        if cfgs:
            lines.append("- Unique config paths:")
            for c in cfgs:
                lines.append(f"  - `{c}`")
        lines.append("")

    lines.append("## 5. Local Gate\n")
    if not gate.get("available"):
        lines.append("- Local gate report: **not available**\n")
    else:
        lines.append(f"- Overall return code: **{gate.get('overall_returncode', 0)}**")
        lines.append(f"- Total commands     : {gate.get('total_commands', 0)}")
        failed = gate.get("failed_commands") or []
        if failed:
            lines.append("- Failed commands:")
            for name in failed:
                lines.append(f"  - `{name}`")
        else:
            lines.append("- Failed commands: (none)")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate `_codex_` reproducibility manifest.")
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--env-snapshot",
        type=str,
        default="codex_env_snapshot.json",
        help="Environment snapshot JSON (default: codex_env_snapshot.json).",
    )
    parser.add_argument(
        "--dep-report",
        type=str,
        default="codex_dependency_report.json",
        help="Dependency report JSON (default: codex_dependency_report.json).",
    )
    parser.add_argument(
        "--gap-registry",
        type=str,
        default="codex_gap_registry.yaml",
        help="Gap registry YAML (default: codex_gap_registry.yaml).",
    )
    parser.add_argument(
        "--experiment-index",
        type=str,
        default="codex_experiment_index.json",
        help="Experiment index JSON (default: codex_experiment_index.json).",
    )
    parser.add_argument(
        "--local-gate",
        type=str,
        default="codex_local_gate_report.json",
        help="Local gate report JSON (default: codex_local_gate_report.json).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_reproducibility_manifest.json",
        help="JSON output path (default: codex_reproducibility_manifest.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_reproducibility_manifest.md",
        help="Markdown output path (default: codex_reproducibility_manifest.md).",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve()
    manifest = build_manifest(
        repo_root=repo_root,
        env_snapshot_path=Path(args.env_snapshot).expanduser().resolve(),
        dep_report_path=Path(args.dep_report).expanduser().resolve(),
        gap_registry_path=Path(args.gap_registry).expanduser().resolve(),
        exp_index_path=Path(args.experiment_index).expanduser().resolve(),
        local_gate_path=Path(args.local_gate).expanduser().resolve(),
    )

    json_out = Path(args.json_out).expanduser().resolve()
    md_out = Path(args.md_out).expanduser().resolve()
    _write_json(json_out, manifest)
    _write_markdown(md_out, manifest)

    print(f"[codex_repro_manifest] Wrote JSON to {json_out}")
    print(f"[codex_repro_manifest] Wrote Markdown to {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
