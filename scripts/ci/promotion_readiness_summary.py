#!/usr/bin/env python3
"""
scripts/ci/promotion_readiness_summary.py
─────────────────────────────────────────
Renders a Markdown step-summary table from the JSON report emitted by
``promotion_readiness_gate.py``.  Called by the ``promotion-readiness-gate.yml``
workflow to write to ``GITHUB_STEP_SUMMARY``.

Usage
-----
  python scripts/ci/promotion_readiness_summary.py \\
    --json-in <report.json> \\
    --output <path-or-env-var-value>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def render(report: dict) -> str:
    ready = report.get("ready", False)
    icon = "✅" if ready else "❌"
    lines = [
        f"## {icon} Promotion Readiness Gate: 0D_base_ → main",
        "",
        f"**Status:** {'READY' if ready else 'BLOCKED'}  "
        f"| Passed: {report.get('passed', 0)} "
        f"| Failed: {report.get('failed', 0)} "
        f"| Total: {report.get('total', 0)}",
        "",
        "| Status | Check | Detail |",
        "|--------|-------|--------|",
    ]
    for c in report.get("checks", []):
        status = "✅ PASS" if c["pass"] else "❌ FAIL"
        detail = c.get("detail") or ""
        detail_cell = detail[:80] if detail else ""
        lines.append(f"| {status} | `{c['check']}` | {detail_cell} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render promotion readiness step summary")
    parser.add_argument("--json-in", required=True, metavar="FILE",
                        help="Path to promotion-readiness-report.json")
    parser.add_argument("--output", required=True, metavar="FILE",
                        help="Path to write the Markdown summary (e.g. $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args()

    json_path = Path(args.json_in)
    if not json_path.exists():
        print(f"⚠  {json_path} not found", file=sys.stderr)
        return 2

    report = json.loads(json_path.read_text(encoding="utf-8"))
    md = render(report)

    out_path = Path(args.output)
    with out_path.open("a", encoding="utf-8") as fh:
        fh.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
