#!/usr/bin/env python
"""Dependency pinning checker for `_codex_`.

Scans common dependency manifests to flag unpinned requirements. Outputs both
JSON and Markdown summaries for easy review.
"""
from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import tomllib
import yaml

PINNED_OPERATORS = ("==", ">=", "<=", "~=", ">", "<")


@dataclass
class DepIssue:
    path: str
    line_number: int
    requirement: str
    reason: str


def _is_pinned(req: str) -> bool:
    return any(op in req for op in PINNED_OPERATORS)


def _scan_requirements(path: Path) -> list[DepIssue]:
    issues: list[DepIssue] = []
    if not path.exists():
        return issues
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not _is_pinned(line):
            issues.append(DepIssue(str(path), idx, line, "unpinned requirement"))
    return issues


def _scan_pyproject(path: Path) -> list[DepIssue]:
    issues: list[DepIssue] = []
    if not path.exists():
        return issues
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    deps = data.get("project", {}).get("dependencies", [])
    for dep in deps:
        if isinstance(dep, str) and not _is_pinned(dep):
            issues.append(DepIssue(str(path), 0, dep, "unpinned dependency entry"))
    return issues


def _scan_env_yml(path: Path) -> list[DepIssue]:
    issues: list[DepIssue] = []
    if not path.exists():
        return issues
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    deps = data.get("dependencies", [])
    for idx, dep in enumerate(deps, start=1):
        if isinstance(dep, str):
            if not _is_pinned(dep):
                issues.append(DepIssue(str(path), idx, dep, "unpinned conda dependency"))
        elif isinstance(dep, dict) and "pip" in dep:
            for pip_idx, pip_dep in enumerate(dep["pip"], start=1):
                if not _is_pinned(pip_dep):
                    issues.append(
                        DepIssue(
                            str(path),
                            pip_idx,
                            pip_dep,
                            "unpinned pip dependency in environment.yml",
                        )
                    )
    return issues


def run_check(repo_root: Path) -> dict[str, object]:
    manifests = [
        repo_root / "requirements.txt",
        repo_root / "requirements-dev.txt",
        repo_root / "pyproject.toml",
        repo_root / "environment.yml",
    ]

    issues: list[DepIssue] = []
    for manifest in manifests:
        if manifest.name.startswith("requirements"):
            issues.extend(_scan_requirements(manifest))
        elif manifest.name == "pyproject.toml":
            issues.extend(_scan_pyproject(manifest))
        elif manifest.name == "environment.yml":
            issues.extend(_scan_env_yml(manifest))

    return {
        "scanned_root": str(repo_root),
        "issue_count": len(issues),
        "issues": [asdict(i) for i in issues],
    }


def _write_json(payload: dict[str, object], out_path: Path) -> None:
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(payload: dict[str, object], out_path: Path) -> None:
    lines = [
        "# Codex Dependency Pinning Report",
        "",
        f"Scanned root: `{payload['scanned_root']}`",
        "",
    ]
    lines.append(f"Issues found: {payload['issue_count']}")
    lines.append("")
    for issue in payload.get("issues", []):
        lines.append(
            f"- `{issue['path']}` (line {issue['line_number']}): `{issue['requirement']}` → {issue['reason']}"
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check dependency manifests for pinned versions.")
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_dep_pin_report.json",
        help="Path for JSON report (default: codex_dep_pin_report.json)",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_dep_pin_report.md",
        help="Path for Markdown report (default: codex_dep_pin_report.md)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).expanduser().resolve()
    payload = run_check(root)

    json_out = Path(args.json_out).expanduser().resolve()
    md_out = Path(args.md_out).expanduser().resolve()
    _write_json(payload, json_out)
    _write_markdown(payload, md_out)
    print(f"Wrote dependency pinning reports to {json_out} and {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
