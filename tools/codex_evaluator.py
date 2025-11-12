#!/usr/bin/env python
"""Local-only evaluator for Codex assistant messages/summaries.

- Loads rubric & rules from JSON (manifests/codex_eval_rules.v3.json).
- Accepts a raw text file or a JSON summary; if JSON, tries 'message_text' then falls back to raw text.
- Emits a brief score breakdown and returns non-zero on *hard-fail* cues (e.g., CI activation patterns).

Optional Dependencies Soft-Fail:
- CODEX_OPTIONAL_SOFTFAIL=1 (default): Missing optionals produce warnings + skip support
- CODEX_OPTIONAL_SOFTFAIL=0: Missing optionals raise ImportError

Exports:
    MISSING_OPTIONALS: list[tuple[str, str]]  # (package, error_message)
    OPTIONAL_STATUS: dict[str, bool]          # package -> availability
    has_all_optional() -> bool
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

log = logging.getLogger(__name__)

_OPTIONAL_PACKAGES = ["pydantic", "typer"]

MISSING_OPTIONALS: List[Tuple[str, str]] = []
OPTIONAL_STATUS: Dict[str, bool] = {}
SOFT_FAIL = os.getenv("CODEX_OPTIONAL_SOFTFAIL", "1") == "1"


def _try_import(name: str) -> None:
    """Try to import an optional package and track its status."""
    if importlib.util.find_spec(name) is None:
        OPTIONAL_STATUS[name] = False
        msg = f"Module '{name}' not found"
        MISSING_OPTIONALS.append((name, msg))
    else:
        OPTIONAL_STATUS[name] = True


for _pkg in _OPTIONAL_PACKAGES:
    _try_import(_pkg)

if MISSING_OPTIONALS:
    msg = ", ".join(f"{p} ({err})" for p, err in MISSING_OPTIONALS)
    if SOFT_FAIL:
        sys.stderr.write(
            f"[evaluator] Optional dependencies missing (soft-fail mode): {msg}\n"
            f"Install via: pip install {' '.join(p for p, _ in MISSING_OPTIONALS)}\n"
        )
    else:  # pragma: no cover
        sys.stderr.write(
            f"[evaluator] Required optional dependencies missing: {msg}\n"
            f"Install via: pip install {' '.join(p for p, _ in MISSING_OPTIONALS)}\n"
        )
        raise SystemExit(2)


def has_all_optional() -> bool:
    """Check if all optional dependencies are available."""
    return not MISSING_OPTIONALS


@dataclass
class EvalResult:
    hard_fail: bool
    hard_fail_reasons: List[str]
    score: int
    details: Dict[str, Any]


def load_rules(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_input_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    # Try JSON field if the file is JSON
    try:
        obj = json.loads(data)
        if isinstance(obj, dict):
            # Prefer explicit message_text, otherwise stringify
            return obj.get("message_text") or data
    except Exception:
        pass
    return data


def find_any(patterns: List[str], text: str) -> List[str]:
    found = []
    for pat in patterns:
        if re.search(pat, text):
            found.append(pat)
    return found


def evaluate_text(text: str, rules: Dict[str, Any]) -> EvalResult:
    rubric = rules.get("rubric", {})
    scoring = rules.get("scoring", {})

    hard_fail_cfg = rubric.get("hard_fail", {})
    forbidden_cues = rubric.get("forbidden_cues", [])
    env_guard_re = rubric.get("env_guard_regex")

    hard_fail_reasons: List[str] = []

    # Hard fail: activated CI cues
    activated_ci = False
    if forbidden_cues:
        hits = find_any(forbidden_cues, text)
        if hits:
            activated_ci = True
            hard_fail_reasons.append(f"forbidden_cues: {', '.join(hits)}")

    # Soft scoring example signals (minimal):
    score = 0
    penalties = scoring.get("penalties", {})

    # If pytest is mentioned but env guard missing, apply penalty.
    if re.search(r"\bpytest\b", text, flags=re.IGNORECASE):
        guard_present = False
        if env_guard_re:
            guard_present = bool(re.search(env_guard_re, text, flags=re.MULTILINE))
        if not guard_present and "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1" in text:
            guard_present = True
        if not guard_present:
            score -= int(penalties.get("no_env_guard_when_pytest_present", 0))

    # Return hard-fail if configuration demands it on CI cues
    if hard_fail_cfg.get("activated_ci") and activated_ci:
        return EvalResult(True, hard_fail_reasons, score, {"notes": "CI activation cues detected"})

    return EvalResult(False, hard_fail_reasons, score, {"notes": "ok"})


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Codex local evaluator")
    p.add_argument("--rules", required=True, help="Path to rules JSON")
    p.add_argument("--input", required=True, help="Path to message text or JSON summary")
    args = p.parse_args(argv)

    if not os.path.exists(args.rules):
        print(f"[codex-eval] Rules not found: {args.rules}", file=sys.stderr)
        return 1
    if not os.path.exists(args.input):
        print(f"[codex-eval] Input not found: {args.input}", file=sys.stderr)
        return 1

    rules = load_rules(args.rules)
    text = load_input_text(args.input)
    result = evaluate_text(text, rules)

    print("== Codex Evaluator ==")
    if result.hard_fail:
        print("HARD FAIL:", "; ".join(result.hard_fail_reasons))
        print("Score:", result.score)
        return 1
    print("Status: PASS")
    print("Score:", result.score)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
