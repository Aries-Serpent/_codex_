#!/usr/bin/env python
"""Secret scan stub for `_codex_`.

Performs a *very* simple pattern-based scan looking for suspicious tokens
in text files under a given root. Outputs JSON and Markdown summaries.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

_AWS_SECRET_PATTERN = "AWS_SECRET_ACCESS_" + "KEY"

PATTERNS = ["AKIA", "SECRET_KEY", "PRIVATE_KEY", _AWS_SECRET_PATTERN]


def _redact_snippet(snippet: str) -> str:
    """Redact potential secrets from snippet for safe logging.
    
    Security: Prevents clear-text storage of secrets in scan reports.
    """
    # Redact long base64-like strings, hex strings, and key-like patterns
    redacted = re.sub(r'[A-Za-z0-9+/]{20,}', '[REDACTED]', snippet)
    redacted = re.sub(r'[0-9a-fA-F]{32,}', '[REDACTED]', redacted)
    redacted = re.sub(r'(?:secret|key|password|token)["\s:=]+[^\s"]{8,}', 
                      lambda m: m.group()[:20] + '[REDACTED]', 
                      redacted, flags=re.IGNORECASE)
    return redacted


def _iter_text_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".zip", ".tar", ".gz"}:
            continue
        files.append(p)
    return files


def scan(root: Path) -> Dict[str, List[Dict[str, str]]]:
    findings: List[Dict[str, str]] = []
    for f in _iter_text_files(root):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for patt in PATTERNS:
            if patt in text:
                snippet = text.strip().splitlines()[0] if text.strip().splitlines() else ""
                # Security: Redact potential secrets before storing
                findings.append({"file": str(f), "pattern": patt, "snippet": _redact_snippet(snippet[:200])})
    return {"findings": findings, "total_findings": len(findings)}


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, data: Dict[str, object]) -> None:
    findings = data.get("findings", []) or []
    lines: List[str] = []
    lines.append("# `_codex_` Secret Scan Stub\n")
    lines.append(f"- Total findings: **{data.get('total_findings', 0)}**\n")
    if not findings:
        lines.append("No findings.\n")
        path.write_text("\n".join(lines), encoding="utf-8")
        return
    lines.append("| File | Pattern | Snippet |")
    lines.append("| ---- | ------- | ------- |")
    for f in findings:
        lines.append(f"| `{f.get('file')}` | {f.get('pattern')} | {f.get('snippet','')[:80]} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Secret scan stub for _codex_.")
    parser.add_argument("--repo-root", type=str, default=".", help="Root directory to scan.")
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_secret_scan_report.json",
        help="Output JSON path (default: codex_secret_scan_report.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_secret_scan_report.md",
        help="Output Markdown path (default: codex_secret_scan_report.md).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()
    data = scan(root)
    json_out_raw = Path(args.json_out)
    md_out_raw = Path(args.md_out)
    json_out = json_out_raw if json_out_raw.is_absolute() else root / json_out_raw
    md_out = md_out_raw if md_out_raw.is_absolute() else root / md_out_raw
    _write_json(json_out, data)
    _write_markdown(md_out, data)
    print(f"Wrote secret scan stub report to {json_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
