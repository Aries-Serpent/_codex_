#!/usr/bin/env python
"""Lightweight secret scan stub for _codex_.

This is NOT a full secret scanner. It provides a simple, conservative pass
over the working tree to flag obvious high-signal patterns such as:

- "BEGIN PRIVATE KEY"
- "AWS_ACCESS_KEY_ID" / "AWS_SECRET_ACCESS_KEY"
- strings that look like tokens in source files (heuristic)

Design goals:
- No external dependencies.
- Local, offline use only.
- Best-effort detection, false positives acceptable.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

SECRET_PATTERNS = [
    re.compile(r"BEGIN\s+PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"AWS_ACCESS_KEY_ID", re.IGNORECASE),
    re.compile(r"AWS_SECRET_ACCESS_KEY", re.IGNORECASE),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"pk_live_[0-9A-Za-z]{20,}"),
]

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
}


@dataclass
class Finding:
    path: str
    line_no: int
    snippet: str
    pattern: str


def _iter_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in SKIP_DIRS:
                continue
            continue
        if p.suffix.lower() in {".py", ".md", ".yaml", ".yml", ".toml", ".txt", ".json"}:
            files.append(p)
    return files


def _scan_file(path: Path) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings
    for i, line in enumerate(text.splitlines(), start=1):
        for pat in SECRET_PATTERNS:
            if pat.search(line):
                snippet = line.strip()
                if len(snippet) > 120:
                    snippet = snippet[:117] + "..."
                findings.append(
                    Finding(
                        path=str(path),
                        line_no=i,
                        snippet=snippet,
                        pattern=pat.pattern,
                    )
                )
    return findings


def _scan_root(root: Path) -> List[Finding]:
    all_findings: List[Finding] = []
    for f in _iter_files(root):
        all_findings.extend(_scan_file(f))
    return all_findings


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run a lightweight secret scan stub.")
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_secret_scan_report.json",
        help="JSON output path (default: codex_secret_scan_report.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_secret_scan_report.md",
        help="Markdown output path (default: codex_secret_scan_report.md).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()
    findings = _scan_root(root)
    json_out = root / args.json_out
    md_out = root / args.md_out

    data = {
        "total_findings": len(findings),
        "findings": [asdict(f) for f in findings],
    }
    json_out.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    lines: List[str] = []
    lines.append("# _codex_ Secret Scan Stub Report\n")
    lines.append(f"- Total findings: **{len(findings)}**\n")
    if findings:
        lines.append("## Findings\n")
        lines.append("| File | Line | Pattern | Snippet |")
        lines.append("| ---- | ---- | ------- | ------- |")
        for f in findings:
            lines.append(
                f"| `{f.path}` | {f.line_no} | `{f.pattern}` | `{f.snippet}` |"
            )
    else:
        lines.append("No high-signal patterns were detected.\n")

    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote secret scan JSON report to {json_out}")
    print(f"Wrote secret scan Markdown report to {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
