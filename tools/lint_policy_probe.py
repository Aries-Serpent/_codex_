#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".codex" / "lint-policy.json"


def has_complex_isort_config() -> bool:
    text = ""
    for cfg in ("pyproject.toml", ".isort.cfg", "setup.cfg"):
        p = ROOT / cfg
        if p.exists():
            text += p.read_text(encoding="utf-8", errors="ignore")
    non_defaults = re.findall(
        r"^\s*(known_\w+|sections|force_\w+|skip|skip_glob|order_by|lines_after_imports)\s*=",
        text,
        flags=re.M,
    )
    return len(set(non_defaults)) > 3


def main():
    policy, reason = ("ruff", "Ruff formatter + import-sort OK")
    if has_complex_isort_config():
        policy, reason = ("hybrid", "Complex isort config detected")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"policy": policy, "reason": reason}, indent=2), encoding="utf-8")
    print(json.dumps({"policy": policy, "reason": reason}))


if __name__ == "__main__":
    raise SystemExit(main())
