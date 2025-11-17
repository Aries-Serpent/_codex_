#!/usr/bin/env python
"""Emit a compact PR-body snippet summarizing local gates and selection."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Reuse the subprocess helper from status_report to avoid duplication.
from tools.status_report import (
    _run,  # type: ignore  # circular import for runtime reuse
)


def _gate_state(rc: int) -> str:
    if rc == 0:
        return "PASS"
    if rc == 1:
        return "FAIL"
    return "SKIP"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize local gates for PR bodies")
    parser.add_argument("--summary", required=True, help="Path to assistant summary JSON")
    parser.add_argument("--selected", required=True, help="Chosen candidate id")
    args = parser.parse_args(argv)

    fences_rc, _, _ = _run([sys.executable, "tools/validate_fences.py"])
    schemas_rc, _, _ = _run(
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
    evaluator_rc, _, _ = _run(
        [
            sys.executable,
            "tools/codex_evaluator.py",
            "--rules",
            "manifests/codex_eval_rules.v3.json",
            "--input",
            args.summary,
        ]
    )
    guard_rc, _, _ = _run(
        [
            sys.executable,
            "tools/selection_guard.py",
            "--rules",
            "manifests/selection_guard_rules.json",
            "--input",
            args.summary,
            "--selected",
            args.selected,
        ]
    )

    print("### Local Gates")
    print(f"- Fences: {_gate_state(fences_rc)}")
    print(f"- Schemas: {_gate_state(schemas_rc)}")
    print(f"- Evaluator: {_gate_state(evaluator_rc)}")
    print(f"- Selection Guard (chosen={args.selected}): {_gate_state(guard_rc)}")
    print("\n_Selected summary:_", Path(args.summary).name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
