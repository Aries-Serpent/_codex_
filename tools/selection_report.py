#!/usr/bin/env python
"""Local candidate selection reporter for *codex*.

Reads an assistant summary JSON, computes rubric/evaluator scores,
enforces selection-guard signals, applies deterministic tie-breaks,
and writes SELECTION_REPORT.md.

No CI, no network, local-only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

VERSION = "0.1.0"


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = process.communicate()
    return process.returncode, out, err


def _bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {s}" for s in items)


def _read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_assistant_keys(turn_mapping: Dict[str, object]) -> List[str]:
    return sorted([k for k in turn_mapping.keys() if "~assttrn_" in k and k.startswith("task_e_")])


SIGNALS = {
    "fences": r"tools/validate_fences.py|fence integrity|broken[_-]fence",
    "schema": r"tools/schema_validate.py|jsonschema|schemas/.+.schema.json",
    "evaluator": r"tools/codex_evaluator.py|evaluator",
    "selection_guard": r"tools/selection_guard.py|selection guard",
    "docs_ops": r"docs/ops/(local_gates|status_reports|selection_reports).md",
    "docs_rubric": r"docs/rubrics/|rubric",
    "checklist": r"approval_gate_checklist.md|checklist",
    "negative_sample": r"broken_fence.sample.md|tests/(samples|evaluators)/",
    "tests": r"tests/.*.py",
    "precommit_manual": r"pre-commit|stages:\s*[manual]",
    "adr": r"ADR|docs/decision_records/",
    "why_risk_rollback": r"\b(why|rationale)\b|risk|rollback",
    "local_only": r"\blocal[- ]only\b|\bno CI\b|CI[- ]free",
    "template_mode": r"--template|docs/templates/status_update.md|status_report.py",
}


WEIGHTS = {
    "fences": 3,
    "schema": 3,
    "evaluator": 2,
    "selection_guard": 4,
    "docs_ops": 3,
    "docs_rubric": 2,
    "checklist": 2,
    "negative_sample": 2,
    "tests": 2,
    "precommit_manual": 2,
    "adr": 2,
    "why_risk_rollback": 2,
    "local_only": 2,
    "template_mode": 1,
}


def _score_blob(text_blob: str) -> Tuple[int, Dict[str, bool], List[str]]:
    score = 0
    found: Dict[str, bool] = {}
    for name, pattern in SIGNALS.items():
        hit = re.search(pattern, text_blob, re.IGNORECASE) is not None
        found[name] = hit
        if hit:
            score += WEIGHTS[name]
    penalties: List[str] = []
    if not found.get("selection_guard", False):
        score -= 3
        penalties.append("missing selection_guard signal")
    if not found.get("docs_ops", False):
        score -= 2
        penalties.append("missing ops docs signal")
    return score, found, penalties


def _collect_text(turn: Dict[str, object]) -> str:
    texts: List[str] = []
    worklog = turn.get("worklog") or {}
    messages = worklog.get("messages") or []
    if isinstance(messages, list):
        for message in messages:
            if isinstance(message, dict):
                for key in ("text", "content", "message", "body", "title"):
                    value = message.get(key)
                    if isinstance(value, str):
                        texts.append(value)
    for item in turn.get("output_items") or []:
        if isinstance(item, dict):
            for key in ("title", "pr_message", "message", "text", "body"):
                value = item.get(key)
                if isinstance(value, str):
                    texts.append(value)
            output_diff = item.get("output_diff")
            if isinstance(output_diff, dict):
                diff = output_diff.get("diff")
                if isinstance(diff, str):
                    texts.append(diff)
    return "\n\n".join(texts)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a local SELECTION_REPORT.md")
    parser.add_argument("--summary", required=True, help="Path to assistant summary JSON")
    parser.add_argument("--out", default="SELECTION_REPORT.md", help="Output markdown path")
    args = parser.parse_args(argv)

    # 0) Validate json structure
    path = Path(args.summary)
    if not path.exists():
        sys.stderr.write(f"[selection] summary not found: {path}\n")
        return 1
    data = _read_json(path)
    if "turn_mapping" not in data:
        sys.stderr.write("[selection] invalid summary: missing 'turn_mapping'\n")
        return 1

    turn_mapping = data["turn_mapping"]  # type: ignore[assignment]
    if not isinstance(turn_mapping, dict):
        sys.stderr.write("[selection] invalid summary: 'turn_mapping' not a dict\n")
        return 1

    assistant_keys = _extract_assistant_keys(turn_mapping)
    if not assistant_keys:
        sys.stderr.write("[selection] no assistant variants found in summary\n")
        return 1

    # 1) Evaluator (optional deps guarded in the evaluator module itself)
    eval_rc, eval_out, eval_err = _run(
        [
            sys.executable,
            "tools/codex_evaluator.py",
            "--rules",
            "manifests/codex_eval_rules.v3.json",
            "--input",
            str(path),
        ]
    )
    # Note: non-zero here may just be optional deps missing; keep going to the heuristic layer.

    # 2) Heuristic scoring & selection-guard preference
    rows = []
    for idx, key in enumerate(assistant_keys, start=1):
        candidate = turn_mapping[key]["turn"] if isinstance(turn_mapping.get(key), dict) else {}
        blob = _collect_text(candidate if isinstance(candidate, dict) else {})
        score, found, penalties = _score_blob(blob)
        rows.append(
            {
                "variant": idx,
                "turn_key": key,
                "score": score,
                "signals": found,
                "penalties": penalties,
            }
        )

    rows_sorted = sorted(
        rows,
        key=lambda row: (
            -row["score"],
            0 if row["signals"].get("selection_guard", False) else 1,
            0 if row["signals"].get("docs_ops", False) else 1,
            0 if row["signals"].get("tests", False) else 1,
        ),
    )
    winner = rows_sorted[0]

    # 3) Render markdown
    md: List[str] = []
    md.append(f"# Selection Report — *codex* (v{VERSION})")
    md.append("")
    md.append("## Recommendation")
    md.append(f"- **Chosen variant:** **{winner['variant']}**  ")
    md.append(f"- **Turn key:** `{winner['turn_key']}`  ")
    md.append(f"- **Score:** {winner['score']}")
    md.append("")
    md.append("## Signals & Rationale")
    present = sorted([name for name, value in winner["signals"].items() if value])
    md.append("**Signals present:**")
    md.append(_bullets(present) or "- none")
    if winner["penalties"]:
        md.append("")
        md.append("**Penalties:**")
        md.append(_bullets(winner["penalties"]))
    md.append("")
    md.append("## Top candidates")
    for row in rows_sorted[:4]:
        signals = (
            ", ".join(sorted([name for name, value in row["signals"].items() if value])) or "none"
        )
        md.append(f"- Variant {row['variant']}: score {row['score']} — {signals}")
    md.append("")
    md.append("## Evaluator run")
    md.append(f"- Exit code: {eval_rc}")
    if eval_err.strip():
        md.append("<details><summary>stderr</summary>")
        md.append("")
        md.append("```text")
        md.append(eval_err.strip())
        md.append("```")
        md.append("</details>")
    if eval_out.strip():
        md.append("<details><summary>stdout</summary>")
        md.append("")
        md.append("```text")
        md.append(eval_out.strip())
        md.append("```")
        md.append("</details>")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    # Exit 0 even if evaluator failed (optional deps), but non-zero on structural issues above.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
