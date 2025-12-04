#!/usr/bin/env python
"""Local-only secret scanner for `_codex_`.

The scanner is intentionally lightweight and offline. It searches for
common credential patterns and emits both JSON and Markdown reports to help
prevent accidental commits of sensitive material.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Sequence

# Patterns are intentionally conservative to minimize false positives while still
# catching common credential formats.
SECRET_PATTERNS: Dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key": re.compile(r"(?i)aws(.{0,20})?(secret|access).{0,3}([0-9a-zA-Z/+]{40})"),
    "generic_api_key": re.compile(r"(?i)(api_key|apikey|api-key)[\s:=\"]{0,5}([0-9a-zA-Z]{16,})"),
    "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC |DSA |)PRIVATE KEY-----"),
    "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9\-_.]{20,}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
}


@dataclass
class SecretHit:
    path: str
    line_number: int
    pattern: str
    match: str


def _iter_files(root: Path) -> Iterator[Path]:
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", "artifacts", ".codex"}
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in skip_dirs:
                continue
            continue
        if not path.is_file():
            continue
        if path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz"}:
            continue
        yield path


def _scan_file(path: Path, patterns: Dict[str, re.Pattern[str]]) -> List[SecretHit]:
    hits: List[SecretHit] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return hits
    for idx, line in enumerate(content.splitlines(), start=1):
        for name, regex in patterns.items():
            for match in regex.finditer(line):
                hits.append(
                    SecretHit(
                        path=str(path),
                        line_number=idx,
                        pattern=name,
                        match=match.group(0),
                    )
                )
    return hits


def run_scan(repo_root: Path, patterns: Dict[str, re.Pattern[str]] | None = None) -> Dict[str, object]:
    active_patterns = patterns or SECRET_PATTERNS
    all_hits: List[SecretHit] = []
    for file_path in _iter_files(repo_root):
        all_hits.extend(_scan_file(file_path, active_patterns))

    hits_payload = [asdict(h) for h in all_hits]
    summary = {
        "scanned_root": str(repo_root),
        "patterns": list(active_patterns.keys()),
        "total_hits": len(hits_payload),
    }
    return {"summary": summary, "hits": hits_payload}


def _write_json(payload: Dict[str, object], out_path: Path) -> None:
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(payload: Dict[str, object], out_path: Path) -> None:
    lines = ["# Codex Secret Scan", "", f"Scanned root: `{payload['summary']['scanned_root']}`", ""]
    lines.append(f"Total hits: {payload['summary']['total_hits']}")
    lines.append("")
    for hit in payload.get("hits", []):
        lines.append(
            f"- `{hit['path']}` (line {hit['line_number']}): **{hit['pattern']}** → `{hit['match']}`"
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan repository for common secret patterns.")
    parser.add_argument("--repo-root", type=str, default=".", help="Root directory to scan (default: current directory)")
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_secret_scan_report.json",
        help="Path for JSON report (default: codex_secret_scan_report.json)",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_secret_scan_report.md",
        help="Path for Markdown report (default: codex_secret_scan_report.md)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).expanduser().resolve()
    payload = run_scan(root)

    json_out = Path(args.json_out).expanduser().resolve()
    md_out = Path(args.md_out).expanduser().resolve()
    _write_json(payload, json_out)
    _write_markdown(payload, md_out)
    print(f"Wrote secret scan reports to {json_out} and {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
