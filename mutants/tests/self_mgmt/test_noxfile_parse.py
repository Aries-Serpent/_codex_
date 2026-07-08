"""
Test Noxfile Parse

Test module for noxfile parse.
"""

from __future__ import annotations

from pathlib import Path


def test_noxfile_has_expected_sessions() -> None:
    nf = Path("noxfile.py")
    assert nf.exists(), "noxfile.py missing"
    text = nf.read_text(encoding="utf-8")
    for name in ("def gates", "def tests", "def precommit"):
        assert name in text, f"missing session: {name}"


def test_noxfile_sets_pytest_env_guard() -> None:
    text = Path("noxfile.py").read_text(encoding="utf-8")
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD" in text, "pytest env guard not set in tests session"


def test_noxfile_runs_core_tools() -> None:
    text = Path("noxfile.py").read_text(encoding="utf-8").lower()
    assert "tools/validate_fences.py" in text, "fence validator not invoked"
    assert "tools/codex_evaluator.py" in text, "evaluator not invoked"
    assert "tools/selection_guard.py" in text, "selection guard not invoked"
    assert "tools/schema_validate.py" in text, "schema validation not invoked"
