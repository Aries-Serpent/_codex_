#!/usr/bin/env python3
"""
Render a full Markdown report from a v1.2 status JSON.

Usage:
  python scripts/status/render_full_markdown_report.py --json reports/daily/YYYY-MM-DD.json --out reports/daily/YYYY-MM-DD.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def h2(text: str) -> str:
    return f"## {text}\n"


def section_exec(md: list[str], data: dict) -> None:
    md.append(h2("1. Executive Summary"))
    md.append("- Fill in summary highlights, key risks, and next steps.\n")


def section_metadata(md: list[str], meta: dict) -> None:
    md.append(h2("2. Metadata"))
    md.append(f"- Title: {meta.get('title','')}")
    md.append(f"- Generated (UTC): {meta.get('timestamp_utc','')}")
    md.append(f"- Template Version: {meta.get('template_version','')}")
    gc = meta.get("git_context", {})
    md.append(f"- Branch: {gc.get('branch','')} @ {gc.get('commit_sha_short','')}")
    env = meta.get("environment", {})
    md.append(f"- Python: {env.get('python_version','')} | OS: {env.get('os','')}")
    md.append("")


def section_snapshot(md: list[str], snap: dict) -> None:
    md.append(h2("3. Snapshot"))
    caps = snap.get("capabilities", [])
    fnds = snap.get("findings", [])
    tests = snap.get("tests_gates", {})
    md.append(f"- Capabilities: {len(caps)}")
    md.append(f"- Findings: {len(fnds)}")
    md.append(
        f"- Coverage: {tests.get('coverage_percent', 0)}% (threshold {tests.get('coverage_threshold', 0)}%)"
    )
    md.append("")


def section_repro(md: list[str], snap: dict) -> None:
    md.append(h2("4. Reproducibility"))
    reg = snap.get("repro", {}).get("registry", [])
    md.append(f"- Registry items: {len(reg)}")
    md.append("")


def section_patches(md: list[str], patches: list) -> None:
    md.append(h2("5. Patches"))
    for p in patches:
        md.append(f"- {p.get('id','PATCH-XXX')}: {p.get('title','')}")
    if not patches:
        md.append("- N/A")
    md.append("")


def section_security(md: list[str], sec: dict) -> None:
    md.append(h2("6. Security"))
    md.append(f"- Masking applied: {sec.get('masking_applied', False)}")
    md.append(f"- Redactions: {sec.get('redactions_count', 0)}")
    md.append("")


def section_automation(md: list[str], auto: dict) -> None:
    md.append(h2("7. Automation"))
    cov = auto.get("coverage", "")
    md.append(f"- Coverage: {cov if cov != '' else 'N/A'}")
    if "schema_validation" in auto:
        md.append("- Schema validation entries present")
    md.append("")


def section_delta(md: list[str], delta: dict) -> None:
    md.append(h2("8. Delta"))
    tc = delta.get("tests_coverage_delta", {})
    if tc:
        md.append(
            f"- Coverage Δ: {tc.get('delta_percent',0)} (prev {tc.get('previous_percent',0)} → curr {tc.get('current_percent',0)})"
        )
    else:
        md.append("- N/A")
    md.append("")


def build(md: list[str], data: dict) -> None:
    md.append(f"# {data['metadata']['title']}\n")
    section_exec(md, data)
    section_metadata(md, data.get("metadata", {}))
    section_snapshot(md, data.get("snapshot", {}))
    section_repro(md, data.get("snapshot", {}))
    section_patches(md, data.get("patches", []))
    section_security(md, data.get("security", {}))
    section_automation(md, data.get("automation", {}))
    section_delta(md, data.get("delta", {}))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    md: list[str] = []
    build(md, data)
    Path(args.out).write_text("\n".join(md), encoding="utf-8")
    print(f"[OK] Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
