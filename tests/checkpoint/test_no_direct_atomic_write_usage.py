"""Guard: checkpoint_core's private ``_atomic_write`` primitive stays private.

Other code must use the public ``codex_ml.utils.atomic_io`` helpers
(``safe_write_bytes`` / ``safe_write_text``) or its own differently named
helper, never a call spelled ``_atomic_write(``.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# First-party source trees only: rglob over ROOT also walked virtualenvs
# (.venv_ci/site-packages), mutation-testing archives and caches.
SCAN_DIRS = ("src", "scripts", "tools", "tests")
SKIP_PARTS = frozenset({"__pycache__", "site-packages", "node_modules", "mutants"})
ALLOWED = frozenset(
    {
        "src/codex_ml/utils/checkpoint_core.py",
        "src/codex_ml/checkpointing/checkpoint_core.py",
        # This guard's own pattern self-test spells the call on purpose.
        Path(__file__).resolve().relative_to(ROOT).as_posix(),
    }
)
# Word boundary: ``def test_save_creates_atomic_write(`` is not a call to it.
CALL_PATTERN = re.compile(r"(?<![\w])_atomic_write\s*\(")


def _offenders() -> list[str]:
    offenders: list[str] = []
    for top in SCAN_DIRS:
        base = ROOT / top
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            rel = path.relative_to(ROOT).as_posix()
            if rel in ALLOWED or SKIP_PARTS.intersection(path.parts):
                continue
            if CALL_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
                offenders.append(rel)
    return sorted(offenders)


def test_call_pattern_matches_calls_not_lookalike_names() -> None:
    assert CALL_PATTERN.search("checkpoint_core._atomic_write(path, data)")
    assert CALL_PATTERN.search("    _atomic_write (path, data)")
    assert not CALL_PATTERN.search("def test_checkpoint_save_creates_atomic_write(tmp):")
    assert not CALL_PATTERN.search("write_bytes_atomic(path, data)")


def test_no_external_atomic_write_usage() -> None:
    """Enforce _atomic_write references stay within checkpoint_core."""
    offenders = _offenders()
    assert not offenders, f"_atomic_write used outside checkpoint_core: {offenders}"
