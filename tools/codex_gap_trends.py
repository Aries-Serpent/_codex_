#!/usr/bin/env python
"""codex_gap_trends.py

Compute aggregate statistics over the current codex_gap_registry.yaml and emit
a human-readable markdown report.

This is a snapshot-oriented tool: it only considers the current registry file.
Over-time trends can be built later using git history or timestamped snapshots.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


def load_registry(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with `pip install pyyaml`.")
    if not path.exists():
        raise FileNotFoundError(f"Registry not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or "gaps" not in data:
        raise ValueError(f"Unexpected registry structure in {path}")
    return data


def compute_snapshot_stats(registry: dict[str, Any]) -> dict[str, Any]:
    gaps = registry.get("gaps", []) or []
    status_counter: Counter[str] = Counter()
    capability_counter: Counter[str] = Counter()

    for item in gaps:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "unknown"))
        capability = str(item.get("capability", "unknown"))
        status_counter[status] += 1
        capability_counter[capability] += 1

    return {
        "total_gaps": sum(status_counter.values()),
        "by_status": dict(status_counter),
        "by_capability": dict(capability_counter),
    }


def write_markdown_report(path: Path, stats: dict[str, Any]) -> None:
    lines = []
    lines.append("# codex_gap_trends snapshot\n\n")
    lines.append(f"Total gaps: {stats.get('total_gaps', 0)}\n\n")

    lines.append("## By status\n\n")
    lines.append("| status | count |\n|--------|-------|\n")
    for status, count in sorted(stats.get("by_status", {}).items()):
        lines.append(f"| {status} | {count} |\n")

    lines.append("\n## By capability\n\n")
    lines.append("| capability | count |\n|------------|-------|\n")
    for capability, count in sorted(stats.get("by_capability", {}).items()):
        lines.append(f"| {capability} | {count} |\n")

    path.write_text("".join(lines), encoding="utf-8")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Summarize codex_gap_registry.yaml into a markdown snapshot."
    )
    p.add_argument(
        "--registry",
        type=str,
        default="codex_gap_registry.yaml",
        help="Path to codex_gap_registry.yaml (default: codex_gap_registry.yaml).",
    )
    p.add_argument(
        "--out",
        type=str,
        default="codex_gap_trends.md",
        help="Path to write markdown report (default: codex_gap_trends.md).",
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    registry_path = Path(args.registry).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()

    registry = load_registry(registry_path)
    stats = compute_snapshot_stats(registry)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_markdown_report(out_path, stats)
    print(f"Wrote snapshot report to: {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
