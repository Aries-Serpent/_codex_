#!/usr/bin/env python3
"""Pick 'ruff' or 'hybrid' based on isort complexity and a quick import-sorting probe."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".codex" / "lint-policy.json"


def _complex_isort() -> bool:
    text = ""
    for cfg in ("pyproject.toml", ".isort.cfg", "setup.cfg"):
        p = ROOT / cfg
        if p.exists():
            text += p.read_text(encoding="utf-8", errors="ignore")
    hits = re.findall(
        r"^(known_\w+|sections|force_\w+|skip(?:_glob)?|order_by|lines_after_imports)\s*=",
        text,
        flags=re.M,
    )
    return len(set(hits)) > 3


def main() -> int:
    policy, reason = "ruff", "Default to Ruff"
    if _complex_isort():
        policy, reason = "hybrid", "Complex isort config detected"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"policy": policy, "reason": reason}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"policy": policy, "reason": reason}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
