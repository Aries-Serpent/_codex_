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

    stamp = _stamp()

    sections: List[str] = []
    header = f"# Status Report — _codex_  \nGenerated: {stamp}\n"
    sections.append(header)
    sections.append("## Gates Summary")

    gate_results: List[Tuple[str, str]] = []

    # 1) Fence integrity
    rc_f, out_f, err_f = _run([sys.executable, "tools/validate_fences.py"])
    fence_state = "PASS" if rc_f == 0 else "FAIL"
    gate_results.append(("Fence integrity", fence_state))
    sections.append(f"- Fence integrity: {fence_state}")

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
    # Detect skip note
    schema_state = "PASS" if rc_s == 0 else "FAIL"
    if "jsonschema not installed" in (err_s or "").lower():
        schema_state = "SKIP"
    sections.append(f"- Schema validation: {schema_state}")
    gate_results.append(("Schema validation", schema_state))

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
    gate_results.append(("Evaluator", eval_state))

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
        if rc_g == 0:
            guard_state = "PASS"
        else:
            err_lower = (err_g or "").lower()
            guard_state = "SKIP" if "jsonschema not installed" in err_lower else "FAIL"
    sections.append(f"- Selection Guard (chosen={args.selected or '-'}) : {guard_state}")
    gate_results.append((f"Selection Guard (chosen={args.selected or '-'})", guard_state))

    # Highlights & Next Steps (lightweight scaffolding)
    sections.append("\n## Highlights\n- Local gates executed; see results above.\n")
    sections.append("## Risks & Mitigations\n- None observed beyond local environment variance.\n")
    sections.append(
        "## Next Steps\n- If any gate is FAIL, inspect tool output and iterate on the change.\n"
    )
    sections.append(f"\n> Provenance: generated locally by `tools/status_report.py` at {stamp}.\n")

    if args.template:
        template_path = Path(args.template)
        template_text = template_path.read_text(encoding="utf-8")
        repo_info = _scan_repo(Path.cwd())
        top_dirs = cast(List[str], repo_info.get("top_dirs", []))
        key_files = cast(Dict[str, bool], repo_info.get("key_files", {}))
        repo_map_lines: List[str] = []
        if top_dirs:
            repo_map_lines.append("### Top-level directories")
            repo_map_lines.append(_md_bullets(top_dirs))
        if key_files:
            if repo_map_lines:
                repo_map_lines.append("")
            repo_map_lines.append("### Key files")
            key_items = [
                f"{name}: {'✅' if present else '❌'}" for name, present in key_files.items()
            ]
            repo_map_lines.append(_md_bullets(key_items))
        if not repo_map_lines:
            repo_map_lines.append("(no repository signals detected)")
        repo_map = "\n".join(repo_map_lines)

        gates_summary = _md_bullets([f"{name}: {state}" for name, state in gate_results])
        capability_rows = "\n".join(f"| {name} | {state} |" for name, state in gate_results)
        capability_table = "| Capability | Status |\n|---|---|"
        if capability_rows:
            capability_table = f"{capability_table}\n{capability_rows}"

        replacements = {
            "{{branch}}": args.branch or "-",
            "{{pr}}": args.pr or "-",
            "{{timestamp}}": stamp,
            "{{gates_summary}}": gates_summary,
            "{{repo_map}}": repo_map,
            "{{capability_table}}": capability_table,
        }
        for placeholder, value in replacements.items():
            template_text = template_text.replace(placeholder, value)
        Path(args.out).write_text(template_text, encoding="utf-8")
    else:
        Path(args.out).write_text("\n".join(sections), encoding="utf-8")

    # Exit non-zero if any mandatory gate failed
    mandatory_fail = (
        (rc_f != 0) or (schema_state == "FAIL") or (eval_state == "FAIL") or (guard_state == "FAIL")
    )
    return 1 if mandatory_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
