#!/usr/bin/env python
"""Data audit tool for `_codex_`.

This tool inspects one or more data roots and produces a small
inventory:

- Directory tree summary
- Per-root file counts and total size
- A Markdown table for quick inspection

It is intentionally simple and offline-only.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class RootSummary:
    root: str
    num_files: int
    total_bytes: int


def _walk_root(root: Path) -> RootSummary:
    num_files = 0
    total_bytes = 0
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        num_files += 1
        try:
            total_bytes += p.stat().st_size
        except OSError:
            continue
    return RootSummary(root=str(root), num_files=num_files, total_bytes=total_bytes)


def build_report(roots: list[Path]) -> dict[str, object]:
    summaries: list[RootSummary] = []
    for r in roots:
        summaries.append(_walk_root(r))
    return {
        "roots": [asdict(s) for s in summaries],
        "total_roots": len(summaries),
        "total_files": sum(s.num_files for s in summaries),
        "total_bytes": sum(s.total_bytes for s in summaries),
    }


def _write_json(path: Path, report: dict[str, object]) -> None:
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, report: dict[str, object]) -> None:
    roots = report.get("roots", []) or []
    total_files = report.get("total_files", 0)
    total_bytes = report.get("total_bytes", 0)

    lines: list[str] = []
    lines.append("# `_codex_` Data Audit Report\n")
    lines.append(f"- Total roots : **{report.get('total_roots', 0)}**")
    lines.append(f"- Total files : **{total_files}**")
    lines.append(f"- Total bytes : **{total_bytes}**\n")

    if not roots:
        lines.append("No data roots were found or provided.\n")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    lines.append("## Root Summaries\n")
    lines.append("| Root | Num Files | Total Bytes |")
    lines.append("| ---- | --------- | ----------- |")

    for s in roots:
        lines.append(f"| `{s['root']}` | {s['num_files']} | {s['total_bytes']} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Data audit tool for `_codex_`.")
    parser.add_argument(
        "--root",
        action="append",
        default=None,
        help="Data root to scan (may be repeated). If omitted, uses ./data.",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_data_audit.json",
        help="JSON output path (default: codex_data_audit.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_data_audit.md",
        help="Markdown output path (default: codex_data_audit.md).",
    )
    args = parser.parse_args(argv)

    if args.root:
        roots = [Path(r).expanduser().resolve() for r in args.root]
    else:
        roots = [Path("data").expanduser().resolve()]

    report = build_report(roots)

    json_out = Path(args.json_out).expanduser().resolve()
    md_out = Path(args.md_out).expanduser().resolve()
    _write_json(json_out, report)
    _write_markdown(md_out, report)

    print(f"Wrote data audit JSON to {json_out}")
    print(f"Wrote data audit Markdown to {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
