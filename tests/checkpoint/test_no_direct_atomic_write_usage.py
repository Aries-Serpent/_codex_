from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_external_atomic_write_usage() -> None:
    """Enforce _atomic_write references stay within checkpoint_core."""
    offenders: list[str] = []
    pattern = re.compile(r"_atomic_write\s*\(")
    for p in ROOT.rglob("*.py"):
        rel = p.relative_to(ROOT).as_posix()
        if rel.endswith("src/codex_ml/utils/checkpoint_core.py"):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
            offenders.append(rel)
    assert not offenders, f"_atomic_write used outside checkpoint_core: {offenders}"
