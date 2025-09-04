#!/usr/bin/env python3
"""Decide between Ruff-only and hybrid (isort+black) policies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".codex" / "lint-policy.json"
MAX_NON_DEFAULTS = 3  # threshold for customized isort config


def has_complex_isort_config() -> bool:
    """Return True if repo defines multiple non-default isort options."""
    text = ""
    for cfg in ("pyproject.toml", ".isort.cfg", "setup.cfg"):
        p = ROOT / cfg
        if p.exists():
            text += p.read_text(encoding="utf-8", errors="ignore")
    pattern = r"^\s*(known_\w+|sections|force_\w+|skip|skip_glob|order_by|lines_after_imports)\s*="
    non_defaults = re.findall(pattern, text, flags=re.MULTILINE)
    return len(set(non_defaults)) > MAX_NON_DEFAULTS


def main() -> None:
    """Write lint policy decision to .codex/lint-policy.json."""
    policy, reason = ("ruff", "Ruff formatter + import-sort OK")
    if has_complex_isort_config():
        policy, reason = ("hybrid", "Complex isort config detected")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"policy": policy, "reason": reason}, indent=2), encoding="utf-8")
    sys.stdout.write(json.dumps({"policy": policy, "reason": reason}) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
