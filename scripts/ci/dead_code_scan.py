#!/usr/bin/env python3
"""dead_code_scan.py — Codebase-wide dead code scanner using vulture.

Formalises the ad-hoc vulture analysis previously run in /tmp/
so that the same logic is reproducible in CI, pre-commit, and locally.

Strategies
----------
- 100% confidence  → auto-safe to fix; used as the CI hard-fail gate
- 60–99% confidence → catalogued for human review; never fail CI

Output formats
--------------
  text      Human-readable (default)
  github    GitHub Actions annotation format  (::warning:: / ::error::)
  json      Machine-readable JSON report

Usage
-----
    # Local: full report, 60%+ confidence
    python scripts/ci/dead_code_scan.py src/ tests/

    # CI gate: only 100% confidence, fail on any finding
    python scripts/ci/dead_code_scan.py src/ tests/ --min-confidence 100 --fail-on-found

    # GitHub Actions mode
    python scripts/ci/dead_code_scan.py src/ --format github --min-confidence 100

    # JSON report
    python scripts/ci/dead_code_scan.py src/ tests/ --format json --output dead_code.json

    # Exclude false-positive patterns
    python scripts/ci/dead_code_scan.py src/ --exclude "TYPE_CHECKING,__all__"

Exit codes
----------
    0   No findings at or above --min-confidence (or --fail-on-found not set)
    1   Findings found and --fail-on-found is set
    2   vulture not installed
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Items with these names are commonly false positives in this codebase
# (TYPE_CHECKING guards, __all__ re-exports, pytest fixtures, etc.)
DEFAULT_EXCLUDE_NAMES = frozenset(
    [
        # TYPE_CHECKING-guarded imports (vulture doesn't resolve conditional blocks)
        "HF_AutoModel",
        "HF_AutoModelForCausalLM",
        "HF_AutoTokenizer",
        "HF_PreTrainedTokenizerBase",
        "HF_PreTrainedModel",
        # pytest fixtures surfaced as "unused"
        "tmp_path",
        "capsys",
        "monkeypatch",
        "capfd",
        "caplog",
    ]
)

# Patterns in file paths to always skip
DEFAULT_SKIP_PATH_PATTERNS = [
    r"__pycache__",
    r"\.egg-info",
    r"node_modules",
    r"\.venv",
    r"\.venv_ci",
    r"\.venv_agent",
    r"migrations/",
    r"alembic/",
]

CATEGORIES = [
    "unused import",
    "unreachable code after",
    "unused variable",
    "unused function",
    "unused method",
    "unused class",
    "unused attribute",
    "unused property",
]


# ---------------------------------------------------------------------------
# vulture invocation
# ---------------------------------------------------------------------------


def ensure_vulture() -> bool:
    """Return True if vulture is importable / executable."""
    rc = subprocess.run(
        [sys.executable, "-m", "vulture", "--version"],
        capture_output=True,
    ).returncode
    return rc == 0


def run_vulture(
    paths: list[str],
    min_confidence: int,
    sort_by_size: bool,
) -> list[str]:
    """Run vulture and return raw output lines."""
    cmd = [
        sys.executable,
        "-m",
        "vulture",
        f"--min-confidence={min_confidence}",
    ]
    if sort_by_size:
        cmd.append("--sort-by-size")
    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=True, text=True)
    # vulture exits 1 when it finds issues — that's expected
    return result.stdout.splitlines()


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

# Regex to parse a vulture output line:
# path:line: <category> '<name>' (N% confidence[, M lines])
_LINE_RE = re.compile(
    r"^(?P<path>[^:]+):(?P<line>\d+): "
    r"(?P<category>unused \w+(?:\s+\w+)?|unreachable.*?)"
    r"\s+['\"](?P<name>[^'\"]*)['\"]"
    r"\s+\((?P<confidence>\d+)%.*?(?:,\s*(?P<size>\d+)\s*lines?)?\)"
)


def parse_line(line: str) -> dict[str, Any] | None:
    m = _LINE_RE.match(line.strip())
    if not m:
        return None
    return {
        "path": m.group("path"),
        "line": int(m.group("line")),
        "category": m.group("category"),
        "name": m.group("name"),
        "confidence": int(m.group("confidence")),
        "size": int(m.group("size") or 1),
    }


def filter_findings(
    findings: list[dict[str, Any]],
    exclude_names: frozenset[str],
    skip_path_patterns: list[str],
    repo_root: str,
) -> list[dict[str, Any]]:
    compiled = [re.compile(p) for p in skip_path_patterns]
    result = []
    for f in findings:
        if f["name"] in exclude_names:
            continue
        rel_path = os.path.relpath(f["path"], repo_root)
        if any(p.search(rel_path) for p in compiled):
            continue
        f["rel_path"] = rel_path
        result.append(f)
    return result


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def format_text(findings: list[dict], repo_root: str) -> str:
    if not findings:
        return "✅  No dead code found at the configured confidence threshold.\n"

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_cat[f["category"]].append(f)

    total_lines = sum(f["size"] for f in findings)
    lines = [
        f"\n{'═'*72}",
        f"  Dead Code Report   ({len(findings)} items, ~{total_lines} lines total)",
        f"  Repo: {repo_root}",
        f"{'═'*72}\n",
    ]

    for cat in CATEGORIES:
        items = by_cat.get(cat, [])
        if not items:
            continue
        items.sort(key=lambda x: -x["size"])
        lines.append(f"{'─'*72}")
        lines.append(f"  {cat.upper()}  ({len(items)} items)")
        lines.append(f"{'─'*72}")
        for item in items:
            conf_str = f"[{item['confidence']:3d}%]"
            size_str = f"{item['size']:4d}L" if item["size"] > 1 else "     "
            lines.append(f"  {conf_str} {size_str}  {item['rel_path']}:{item['line']}  {item['name']}")
        lines.append("")

    return "\n".join(lines)


def format_github(findings: list[dict]) -> str:
    """Emit GitHub Actions annotation lines."""
    if not findings:
        return ""
    lines = []
    for f in findings:
        level = "error" if f["confidence"] == 100 else "warning"
        title = f"Dead code: {f['category']} '{f['name']}'"
        lines.append(
            f"::{level} file={f['rel_path']},line={f['line']},title={title}::"
            f"{f['category']} '{f['name']}' ({f['confidence']}% confidence, {f['size']} line(s))"
        )
    return "\n".join(lines)


def format_json(findings: list[dict], repo_root: str, min_confidence: int) -> str:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_cat[f["category"]].append(f)

    summary: dict[str, int] = {cat: len(items) for cat, items in by_cat.items()}
    summary["total"] = len(findings)
    summary["total_lines"] = sum(f["size"] for f in findings)

    return json.dumps(
        {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "repo_root": repo_root,
            "min_confidence": min_confidence,
            "summary": summary,
            "findings": findings,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Codebase-wide dead code scanner (wraps vulture)",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="*", default=["src/", "tests/"], help="Paths to scan")
    parser.add_argument("--min-confidence", type=int, default=60, metavar="N")
    parser.add_argument("--fail-on-found", action="store_true", help="Exit 1 if any findings")
    parser.add_argument("--format", choices=["text", "github", "json"], default="text")
    parser.add_argument("--output", metavar="PATH", help="Write report to file (default: stdout)")
    parser.add_argument("--sort-by-size", action="store_true", default=True)
    parser.add_argument(
        "--exclude",
        default="",
        metavar="NAMES",
        help="Comma-separated additional names to exclude from results",
    )
    parser.add_argument(
        "--github-summary",
        action="store_true",
        help="Append Markdown summary to GITHUB_STEP_SUMMARY",
    )
    args = parser.parse_args()

    if not ensure_vulture():
        print("❌  vulture is not installed.  Run: pip install vulture", file=sys.stderr)
        return 2

    repo_root = os.path.abspath(
        os.environ.get("GITHUB_WORKSPACE", os.getcwd())
    )

    extra_excludes = frozenset(n.strip() for n in args.exclude.split(",") if n.strip())
    exclude_names = DEFAULT_EXCLUDE_NAMES | extra_excludes

    # Resolve paths relative to repo root
    scan_paths = [
        str(Path(repo_root) / p) if not os.path.isabs(p) else p
        for p in args.paths
    ]
    # Filter to existing paths only
    scan_paths = [p for p in scan_paths if os.path.exists(p)]
    if not scan_paths:
        print("⚠️  No paths to scan (all resolved paths are missing)", file=sys.stderr)
        return 0

    raw_lines = run_vulture(scan_paths, args.min_confidence, args.sort_by_size)
    parsed = [parse_line(ln) for ln in raw_lines]
    findings = [f for f in parsed if f is not None]
    findings = filter_findings(findings, exclude_names, DEFAULT_SKIP_PATH_PATTERNS, repo_root)

    # Generate output
    if args.format == "text":
        report = format_text(findings, repo_root)
    elif args.format == "github":
        report = format_github(findings)
    else:
        report = format_json(findings, repo_root, args.min_confidence)

    # Write output
    if args.output:
        Path(args.output).write_text(report)
        print(f"📄  Report written to {args.output}")
    else:
        print(report)

    # GitHub step summary
    if args.github_summary:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "")
        if summary_path:
            total = len(findings)
            definite = sum(1 for f in findings if f["confidence"] == 100)
            with open(summary_path, "a") as fh:
                fh.write("\n### 🔍 Dead Code Scan\n\n")
                fh.write("| Metric | Count |\n|---|---|\n")
                fh.write(f"| Total findings (≥{args.min_confidence}% confidence) | {total} |\n")
                fh.write(f"| Definite (100% confidence) | {definite} |\n")
                if definite == 0:
                    fh.write("\n✅ No 100%-confidence dead code found.\n")
                else:
                    fh.write(f"\n> ⚠️ {definite} item(s) at 100% confidence should be removed.\n")

    return 1 if (args.fail_on_found and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
