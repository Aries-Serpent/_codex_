#!/usr/bin/env python
"""Local status reporter for *codex*.

Composes existing local gates and emits a markdown status report.
No CI, no network. All tools are invoked locally.

Example:
python tools/status_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --selected 3 \
  --out STATUS_REPORT.md
Template mode:

python tools/status_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --selected 3 \
  --template docs/templates/status_update.md \
  --branch my/feature \
  --pr 1916 \
  --out STATUS_REPORT.md
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, cast


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err


def _stamp() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def _md_bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {s}" for s in items)


def _scan_repo(root: Path) -> Dict[str, object]:
    """Lightweight, local-only repo scan for top-level signals."""
    entries = sorted([p for p in root.iterdir() if not p.name.startswith(".")])
    top_dirs = [p.name for p in entries if p.is_dir()]
    key_files = {
        "pyproject.toml": (root / "pyproject.toml").exists(),
        "Dockerfile": (root / "Dockerfile").exists(),
        ".pre-commit-config.yaml": (root / ".pre-commit-config.yaml").exists(),
        "tools/validate_fences.py": (root / "tools/validate_fences.py").exists(),
        "tools/codex_evaluator.py": (root / "tools/codex_evaluator.py").exists(),
        "tools/selection_guard.py": (root / "tools/selection_guard.py").exists(),
        "tools/schema_validate.py": (root / "tools/schema_validate.py").exists(),
        "tools/status_report.py": (root / "tools/status_report.py").exists(),
        "schemas/": (root / "schemas").exists(),
        "manifests/": (root / "manifests").exists(),
        "docs/": (root / "docs").exists(),
        "tests/": (root / "tests").exists(),
    }
    return {"top_dirs": top_dirs, "key_files": key_files}


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a local STATUS_REPORT.md")
    ap.add_argument("--summary", help="Path to assistant summary JSON (optional)")
    ap.add_argument("--selected", type=int, help="Chosen candidate id 1..4 (optional)")
    ap.add_argument("--out", default="STATUS_REPORT.md", help="Output markdown path")
    ap.add_argument("--template", help="Path to a markdown template for rich reports (optional)")
    ap.add_argument("--branch", help="Branch name for template substitution (optional)")
    ap.add_argument("--pr", help="PR number or label for template substitution (optional)")
    args = ap.parse_args(argv)

    sections: List[str] = []
    header = f"# Status Report — *codex*  \nGenerated: {_stamp()}\n"
    sections.append(header)
    sections.append("## Gates Summary")

    # 1) Fence integrity
    rc_f, out_f, err_f = _run([sys.executable, "tools/validate_fences.py"])
    sections.append(f"- Fence integrity: {'PASS' if rc_f == 0 else 'FAIL'}")

    # 2) Schema validation (may be skipped gracefully by the tool)
    rc_s, out_s, err_s = _run(
        [
            sys.executable,
            "tools/schema_validate.py",
            "--data",
            "manifests/selection_guard_rules.json",
            "--schema",
            "schemas/selection_guard_rules.schema.json",
            "--data",
            "manifests/codex_eval_rules.v3.json",
            "--schema",
            "schemas/codex_eval_rules.v3.schema.json",
        ]
    )
    schema_state = "PASS" if rc_s == 0 else "FAIL"
    if "jsonschema not installed" in (err_s or "").lower():
        schema_state = "SKIP"
    sections.append(f"- Schema validation: {schema_state}")

    # 3) Evaluator (optional if summary provided)
    eval_state = "SKIP"
    if args.summary:
        rc_e, out_e, err_e = _run(
            [
                sys.executable,
                "tools/codex_evaluator.py",
                "--rules",
                "manifests/codex_eval_rules.v3.json",
                "--input",
                args.summary,
            ]
        )
        eval_state = "PASS" if rc_e == 0 else "FAIL"
    sections.append(f"- Evaluator: {eval_state}")

    # 4) Selection Guard (optional if summary + selected provided)
    guard_state = "SKIP"
    if args.summary and args.selected:
        rc_g, out_g, err_g = _run(
            [
                sys.executable,
                "tools/selection_guard.py",
                "--rules",
                "manifests/selection_guard_rules.json",
                "--input",
                args.summary,
                "--selected",
                str(args.selected),
            ]
        )
        guard_state = "PASS" if rc_g == 0 else ("FAIL" if rc_g == 1 else "SKIP")
    sections.append(f"- Selection Guard (chosen={args.selected or '-'}) : {guard_state}")

    if not args.template:
        sections.append("\n## Highlights\n- Local gates executed; see results above.\n")
        sections.append(
            "## Risks & Mitigations\n- None observed beyond local environment variance.\n"
        )
        sections.append(
            "## Next Steps\n- If any gate is FAIL, inspect tool output and iterate on the change.\n"
        )
        sections.append(
            f"\n> Provenance: generated locally by `tools/status_report.py` at {_stamp()}.\n"
        )
        Path(args.out).write_text("\n".join(sections), encoding="utf-8")
        mandatory_fail = (rc_f != 0) or (schema_state == "FAIL")
        return 1 if mandatory_fail else 0

    root = Path(".").resolve()
    scan = _scan_repo(root)
    repo_map_md: List[str] = []
    top_dirs = cast(List[str], scan["top_dirs"])
    if top_dirs:
        repo_map_md.append("**Top-level directories**:")
        repo_map_md.append(_md_bullets(top_dirs))
    key_files = cast(Dict[str, bool], scan["key_files"])
    signs = [f"`{k}`: {'yes' if v else 'no'}" for k, v in key_files.items()]
    repo_map_md.append("\n**Key files**:")
    repo_map_md.append(_md_bullets(signs))
    repo_map = "\n".join(repo_map_md)

    def status_for(required: List[str], optional: List[str] | None = None) -> str:
        optional = optional or []
        req_hit = sum(1 for p in required if (root / p).exists())
        opt_hit = sum(1 for p in optional if (root / p).exists())
        if req_hit == len(required) and (not optional or opt_hit >= max(1, len(optional) // 2)):
            return "Implemented"
        if req_hit > 0:
            return "Partial"
        return "Missing"

    rows = [
        ("Fence Integrity", status_for(["tools/validate_fences.py"])),
        (
            "Evaluator",
            status_for(
                ["tools/codex_evaluator.py", "manifests/codex_eval_rules.v3.json"],
                ["schemas/codex_eval_rules.v3.schema.json"],
            ),
        ),
        (
            "Selection Guard",
            status_for(
                ["tools/selection_guard.py", "manifests/selection_guard_rules.json"],
                ["tests/guards/test_selection_guard.py"],
            ),
        ),
        (
            "Schema Validation",
            status_for(
                ["tools/schema_validate.py", "schemas/selection_guard_rules.schema.json"],
                ["schemas/codex_eval_rules.v3.schema.json"],
            ),
        ),
        (
            "Status Reporter",
            status_for(
                ["tools/status_report.py", "docs/templates/status_update.md"],
                ["docs/ops/status_reports.md"],
            ),
        ),
        (
            "Docs Surface",
            status_for(
                [
                    "docs/ops/local_gates.md",
                    "docs/rubrics/codex_eval_rubric_v3.md",
                    "docs/checklists/approval_gate_checklist.md",
                ],
                ["docs/samples/intent_validation_example.md"],
            ),
        ),
    ]
    cap_lines = ["| Capability | Status |", "|---|---|"] + [f"| {c} | {s} |" for c, s in rows]
    capability_table = "\n".join(cap_lines)

    gates_summary = _md_bullets(
        [
            f"Fence integrity: {'PASS' if rc_f == 0 else 'FAIL'}",
            f"Schema validation: {schema_state}",
            f"Evaluator: {eval_state}",
            f"Selection Guard (chosen={args.selected or '-'}) : {guard_state}",
        ]
    )

    tmpl_path = Path(args.template)
    tmpl_text = tmpl_path.read_text(encoding="utf-8")
    rendered = (
        tmpl_text.replace("{{branch}}", args.branch or "")
        .replace("{{pr}}", args.pr or "")
        .replace("{{gates_summary}}", gates_summary)
        .replace("{{repo_map}}", repo_map)
        .replace("{{capability_table}}", capability_table)
        .replace("{{timestamp}}", _stamp())
    )
    Path(args.out).write_text(rendered, encoding="utf-8")

    mandatory_fail = (rc_f != 0) or (schema_state == "FAIL")
    return 1 if mandatory_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
