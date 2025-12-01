#!/usr/bin/env python
"""Lightweight dependency audit for _codex_.

This tool inspects common dependency declaration files:

- pyproject.toml (if present)
- requirements.txt (if present)
- requirements-dev.txt (if present)

and emits a JSON + Markdown report with:

- discovered packages (name + version spec where available)
- source file they came from
- simple flags (e.g. "unversioned", "pinned")

It is intentionally small and not a full SBOM generator.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    tomllib = None  # type: ignore


@dataclass
class Dependency:
    name: str
    spec: str
    source: str
    pinned: bool


def _parse_requirements(path: Path) -> List[Dependency]:
    deps: List[Dependency] = []
    if not path.exists():
        return deps
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        spec = ""
        name = line
        for sep in ["==", ">=", "<=", "~=", ">", "<"]:
            if sep in line:
                parts = line.split(sep, 1)
                name = parts[0].strip()
                spec = sep + parts[1].strip()
                break
        pinned = "==" in line
        deps.append(Dependency(name=name, spec=spec, source=str(path), pinned=pinned))
    return deps


def _parse_pyproject(path: Path) -> List[Dependency]:
    deps: List[Dependency] = []
    if not path.exists() or tomllib is None:
        return deps
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    proj = data.get("project") or {}
    for sec_key in ("dependencies",):
        items = proj.get(sec_key) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, str):
                continue
            line = item.strip()
            if not line:
                continue
            name = line
            spec = ""
            for sep in ["==", ">=", "<=", "~=", ">", "<"]:
                if sep in line:
                    parts = line.split(sep, 1)
                    name = parts[0].strip()
                    spec = sep + parts[1].strip()
                    break
            pinned = "==" in line
            deps.append(Dependency(name=name, spec=spec, source=str(path), pinned=pinned))
    return deps


def _collect_dependencies(repo_root: Path) -> List[Dependency]:
    deps: List[Dependency] = []
    pyproject = repo_root / "pyproject.toml"
    req = repo_root / "requirements.txt"
    req_dev = repo_root / "requirements-dev.txt"
    deps.extend(_parse_pyproject(pyproject))
    deps.extend(_parse_requirements(req))
    deps.extend(_parse_requirements(req_dev))
    seen = set()
    uniq: List[Dependency] = []
    for d in deps:
        key = (d.name, d.spec, d.source)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(d)
    return uniq


def _build_summary(deps: List[Dependency]) -> Dict[str, Any]:
    by_source: Dict[str, List[Dict[str, Any]]] = {}
    for d in deps:
        by_source.setdefault(d.source, []).append(asdict(d))
    return {
        "total_dependencies": len(deps),
        "by_source": by_source,
    }


def _write_json(path: Path, deps: List[Dependency]) -> None:
    data = {
        "dependencies": [asdict(d) for d in deps],
        "summary": _build_summary(deps),
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, deps: List[Dependency]) -> None:
    lines: List[str] = []
    lines.append("# _codex_ Dependency Audit\n")
    if not deps:
        lines.append("No dependency files were found or parsed.\n")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    summary = _build_summary(deps)
    lines.append("## Summary\n")
    lines.append(f"- Total dependencies: **{summary['total_dependencies']}**\n")
    lines.append("## Details by source\n")

    for src, entries in summary["by_source"].items():
        lines.append(f"### {src}\n")
        lines.append("| Name | Spec | Pinned |")
        lines.append("| ---- | ---- | ------ |")
        for e in entries:
            lines.append(
                f"| `{e['name']}` | `{e['spec']}` | "
                f"{'yes' if e['pinned'] else 'no'} |"
            )
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit _codex_ dependencies.")
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_dependency_report.json",
        help="JSON output path (default: codex_dependency_report.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_dependency_report.md",
        help="Markdown output path (default: codex_dependency_report.md).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()
    deps = _collect_dependencies(root)
    json_out = root / args.json_out
    md_out = root / args.md_out
    _write_json(json_out, deps)
    _write_markdown(md_out, deps)
    print(f"Wrote dependency JSON report to {json_out}")
    print(f"Wrote dependency Markdown report to {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
