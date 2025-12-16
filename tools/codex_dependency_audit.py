#!/usr/bin/env python
"""Dependency audit stub for `_codex_`.

Parses a requirements-style file under --repo-root (requirements.txt by default)
and emits JSON/Markdown summaries. This is intentionally lightweight and
offline-only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _parse_requirements(path: Path) -> List[Dict[str, str]]:
    deps: List[Dict[str, str]] = []
    if not path.exists():
        return deps
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name_ver = line.replace("==", ":").replace(">=", ":")
        if ":" in name_ver:
            name, ver = name_ver.split(":", 1)
        else:
            name, ver = name_ver, ""
        deps.append({"name": name.strip(), "version": ver.strip()})
    return deps


def build_report(repo_root: Path, requirements_file: str = "requirements.txt") -> Dict[str, Any]:
    req_path = repo_root / requirements_file
    deps = _parse_requirements(req_path)
    summary = {"total_dependencies": len(deps)}
    return {
        "summary": summary,
        "dependencies": deps,
        "source_file": str(req_path),
    }


def _write_json(path: Path, report: Dict[str, Any]) -> None:
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, report: Dict[str, Any]) -> None:
    deps = report.get("dependencies", []) or []
    lines: List[str] = []
    lines.append("# `_codex_` Dependency Audit\n")
    lines.append(
        f"- Total dependencies: **{report.get('summary', {}).get('total_dependencies', 0)}**\n"
    )
    if not deps:
        lines.append("No dependencies found.\n")
        path.write_text("\n".join(lines), encoding="utf-8")
        return
    lines.append("| Name | Version |")
    lines.append("| ---- | ------- |")
    for dep in deps:
        lines.append(f"| {dep.get('name')} | {dep.get('version')} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dependency audit stub for _codex_.")
    parser.add_argument("--repo-root", type=str, default=".", help="Repository root.")
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_dependency_report.json",
        help="Output JSON path (default: codex_dependency_report.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_dependency_report.md",
        help="Output Markdown path (default: codex_dependency_report.md).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()
    report = build_report(root)

    json_out_raw = Path(args.json_out)
    md_out_raw = Path(args.md_out)
    json_out = json_out_raw if json_out_raw.is_absolute() else root / json_out_raw
    md_out = md_out_raw if md_out_raw.is_absolute() else root / md_out_raw
    _write_json(json_out, report)
    _write_markdown(md_out, report)
    print(f"Wrote dependency report to {json_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
