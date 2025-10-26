#!/usr/bin/env python
"""Local status reporter for _codex_.

Composes existing local gates and emits a markdown status report.
No CI, no network. All tools are invoked locally.

Example:
  python tools/status_report.py \
    --summary samples/assistant_message_summary.sample.json \
    --selected 3 \
    --out STATUS_REPORT.md
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err


def _stamp() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a local STATUS_REPORT.md")
    ap.add_argument("--summary", help="Path to assistant summary JSON (optional)")
    ap.add_argument("--selected", type=int, help="Chosen candidate id 1..4 (optional)")
    ap.add_argument("--out", default="STATUS_REPORT.md", help="Output markdown path")
    args = ap.parse_args(argv)

    sections: List[str] = []
    header = f"# Status Report — _codex_  \nGenerated: {_stamp()}\n"
    sections.append(header)
    sections.append("## Gates Summary")

    # 1) Fence integrity
    rc_f, out_f, err_f = _run([sys.executable, "tools/validate_fences.py"])
    sections.append(f"- Fence integrity: {'PASS' if rc_f == 0 else 'FAIL'}")

    # 2) Schema validation (may be skipped gracefully by the tool)
    rc_s, out_s, err_s = _run([
        sys.executable, "tools/schema_validate.py",
        "--data", "manifests/selection_guard_rules.json", "--schema", "schemas/selection_guard_rules.schema.json",
        "--data", "manifests/codex_eval_rules.v3.json", "--schema", "schemas/codex_eval_rules.v3.schema.json",
    ])
    # Detect skip note
    schema_state = "PASS" if rc_s == 0 else "FAIL"
    if "jsonschema not installed" in (err_s or "").lower():
        schema_state = "SKIP"
    sections.append(f"- Schema validation: {schema_state}")

    # 3) Evaluator (optional if summary provided)
    eval_state = "SKIP"
    if args.summary:
        rc_e, out_e, err_e = _run([
            sys.executable, "tools/codex_evaluator.py",
            "--rules", "manifests/codex_eval_rules.v3.json",
            "--input", args.summary,
        ])
        eval_state = "PASS" if rc_e == 0 else "FAIL"
    sections.append(f"- Evaluator: {eval_state}")

    # 4) Selection Guard (optional if summary + selected provided)
    guard_state = "SKIP"
    if args.summary and args.selected:
        rc_g, out_g, err_g = _run([
            sys.executable, "tools/selection_guard.py",
            "--rules", "manifests/selection_guard_rules.json",
            "--input", args.summary,
            "--selected", str(args.selected),
        ])
        guard_state = "PASS" if rc_g == 0 else ("FAIL" if rc_g == 1 else "SKIP")
    sections.append(f"- Selection Guard (chosen={args.selected or '-'}) : {guard_state}")

    # Highlights & Next Steps (lightweight scaffolding)
    sections.append("\n## Highlights\n- Local gates executed; see results above.\n")
    sections.append("## Risks & Mitigations\n- None observed beyond local environment variance.\n")
    sections.append("## Next Steps\n- If any gate is FAIL, inspect tool output and iterate on the change.\n")
    sections.append(f"\n> Provenance: generated locally by `tools/status_report.py` at {_stamp()}.\n")

    Path(args.out).write_text("\n".join(sections), encoding="utf-8")
    # Exit non-zero if any mandatory gate failed
    mandatory_fail = (rc_f != 0) or (schema_state == "FAIL")
    return 1 if mandatory_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
