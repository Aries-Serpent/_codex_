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
import json
import subprocess
import sys
import textwrap
from collections.abc import Iterable
from pathlib import Path
from typing import Optional, cast

VERSION = "1.2.0"


def _run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err


def _stamp() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def _md_bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {s}" for s in items)


def _write_log(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _artifacts_root() -> Path:
    return Path(".codex/status")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _scan_repo(root: Path) -> dict[str, object]:
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a local STATUS_REPORT.md")
    ap.add_argument("--summary", help="Path to assistant summary JSON (optional)")
    ap.add_argument("--selected", type=int, help="Chosen candidate id 1..4 (optional)")
    ap.add_argument("--out", default="STATUS_REPORT.md", help="Output markdown path")
    ap.add_argument("--template", help="Path to a markdown template for rich reports (optional)")
    ap.add_argument("--branch", help="Branch name for template substitution (optional)")
    ap.add_argument("--pr", help="PR number or label for template substitution (optional)")
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Embed tool outputs (stdout/stderr) in the report body",
    )
    ap.add_argument(
        "--save-logs",
        action="store_true",
        help="Write per-tool logs under .codex/status/ and reference them at the end of the report",
    )
    ap.add_argument(
        "--emit-md",
        help="Optional path to write the Markdown report (in addition to --out)",
    )
    ap.add_argument(
        "--emit-json",
        help="Optional path to write a JSON ledger with gate statuses",
    )
    args = ap.parse_args(argv)

    generated_at = _stamp()

    sections: list[str] = []
    header = f"# Status Report — _codex_ (v{VERSION})  \nGenerated: {generated_at}\n"
    sections.append(header)
    sections.append("## Gates Summary")

    gate_results: list[tuple[str, str]] = []

    # 1) Fence integrity
    cmd_f = [sys.executable, "tools/validate_fences.py"]
    rc_f, out_f, err_f = _run(cmd_f)
    fence_state = "PASS" if rc_f == 0 else "FAIL"
    gate_results.append(("Fence integrity", fence_state))
    sections.append(f"- Fence integrity: {fence_state}")
    if args.verbose:
        sections.append("\n### Fences — Output\n")
        sections.append(textwrap.indent((out_f or "") + (err_f or ""), "    "))
    if args.save_logs:
        _write_log(_artifacts_root() / "fences.out", out_f or "")
        _write_log(_artifacts_root() / "fences.err", err_f or "")

    # 2) Schema validation (may be skipped gracefully by the tool)
    cmd_s = [
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
    rc_s, out_s, err_s = _run(cmd_s)
    # Detect skip note
    schema_state = "PASS" if rc_s == 0 else "FAIL"
    if "jsonschema not installed" in (err_s or "").lower():
        schema_state = "SKIP"
    sections.append(f"- Schema validation: {schema_state}")
    gate_results.append(("Schema validation", schema_state))
    if args.verbose:
        sections.append("\n### Schemas — Output\n")
        sections.append(textwrap.indent((out_s or "") + (err_s or ""), "    "))
    if args.save_logs:
        _write_log(_artifacts_root() / "schemas.out", out_s or "")
        _write_log(_artifacts_root() / "schemas.err", err_s or "")

    # 3) Evaluator (optional if summary provided)
    eval_state = "SKIP"
    out_e = err_e = ""
    rc_e: Optional[int] = None
    if args.summary:
        cmd_e = [
            sys.executable,
            "tools/codex_evaluator.py",
            "--rules",
            "manifests/codex_eval_rules.v3.json",
            "--input",
            args.summary,
        ]
        rc_e, out_e, err_e = _run(cmd_e)
        eval_state = "PASS" if rc_e == 0 else "FAIL"
    sections.append(f"- Evaluator: {eval_state}")
    gate_results.append(("Evaluator", eval_state))
    if args.summary and args.verbose:
        sections.append("\n### Evaluator — Output\n")
        sections.append(textwrap.indent((out_e or "") + (err_e or ""), "    "))
    if args.summary and args.save_logs:
        _write_log(_artifacts_root() / "evaluator.out", out_e or "")
        _write_log(_artifacts_root() / "evaluator.err", err_e or "")

    # 4) Selection Guard (optional if summary + selected provided)
    guard_state = "SKIP"
    out_g = err_g = ""
    rc_g: Optional[int] = None
    if args.summary and args.selected:
        cmd_g = [
            sys.executable,
            "tools/selection_guard.py",
            "--rules",
            "manifests/selection_guard_rules.json",
            "--input",
            args.summary,
            "--selected",
            str(args.selected),
        ]
        rc_g, out_g, err_g = _run(cmd_g)
        guard_state = "PASS" if rc_g == 0 else "FAIL"
    sections.append(f"- Selection Guard (chosen={args.selected or '-'}) : {guard_state}")
    gate_results.append((f"Selection Guard (chosen={args.selected or '-'})", guard_state))
    if args.summary and args.selected and args.verbose:
        sections.append("\n### Selection Guard — Output\n")
        sections.append(textwrap.indent((out_g or "") + (err_g or ""), "    "))
    if args.summary and args.selected and args.save_logs:
        _write_log(_artifacts_root() / "selection_guard.out", out_g or "")
        _write_log(_artifacts_root() / "selection_guard.err", err_g or "")

    # Optional: embed a short selection summary when a summary is provided
    if args.summary:
        sections.append("\n## Selection (summary)")
        rc_sel, sel_out, sel_err = _run(
            [
                sys.executable,
                "tools/selection_report.py",
                "--summary",
                args.summary,
                "--out",
                str(Path(_artifacts_root(), "SELECTION_REPORT.md")),
            ]
        )
        sections.append(f"- selection_report: {'PASS' if rc_sel == 0 else 'FAIL'}")
        if args.verbose:
            sections.append(textwrap.indent((sel_out or "") + (sel_err or ""), "    "))

    if not args.template:
        sections.append("\n## Highlights\n- Local gates executed; see results above.\n")
        sections.append(
            "## Risks & Mitigations\n- None observed beyond local environment variance.\n"
        )
        sections.append(
            "## Next Steps\n- If any gate is FAIL, inspect tool output and iterate on the change.\n"
        )
        if args.save_logs:
            sections.append("\n**Artifacts:** logs saved under `.codex/status/`.\n")
        sections.append(
            f"\n> Provenance: generated locally by `tools/status_report.py` (v{VERSION}) at {generated_at}.\n"
        )
        report_text = "\n".join(sections)
    else:
        template_path = Path(args.template)
        template_text = template_path.read_text(encoding="utf-8")
        repo_info = _scan_repo(Path.cwd())
        top_dirs = cast(list[str], repo_info.get("top_dirs", []))
        key_files = cast(dict[str, bool], repo_info.get("key_files", {}))
        repo_map_lines: list[str] = []
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
            "{{timestamp}}": generated_at,
            "{{gates_summary}}": gates_summary,
            "{{repo_map}}": repo_map,
            "{{capability_table}}": capability_table,
        }
        for placeholder, value in replacements.items():
            template_text = template_text.replace(placeholder, value)

        footer = ""
        if args.save_logs:
            footer = "\n\n**Artifacts:** logs saved under `.codex/status/`.\n"

        report_text = template_text + footer

    print(report_text)

    out_path = Path(args.out)
    _ensure_parent(out_path)
    out_path.write_text(report_text, encoding="utf-8")

    report_json = {
        "version": VERSION,
        "generated": generated_at,
        "gates": [{"name": name, "status": state} for name, state in gate_results],
        "artifacts": {
            "out": str(out_path),
            "emit_md": args.emit_md,
            "emit_json": args.emit_json,
        },
    }
    if args.summary:
        report_json["summary_input"] = args.summary
    if args.selected is not None:
        report_json["selected_candidate"] = args.selected
    if args.branch:
        report_json["branch"] = args.branch
    if args.pr:
        report_json["pr"] = args.pr
    if args.template:
        report_json["template"] = str(args.template)

    if args.emit_md:
        md_path = Path(args.emit_md)
        _ensure_parent(md_path)
        md_path.write_text(
            f"<!-- generated {generated_at} UTC -->\n{report_text}", encoding="utf-8"
        )

    if args.emit_json:
        json_path = Path(args.emit_json)
        _ensure_parent(json_path)
        json_path.write_text(
            json.dumps(report_json, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # Exit non-zero if any mandatory gate failed
    guard_failed = rc_g is not None and rc_g != 0
    evaluator_failed = rc_e is not None and rc_e != 0
    mandatory_fail = (rc_f != 0) or (schema_state == "FAIL") or guard_failed or evaluator_failed
    return 1 if mandatory_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
