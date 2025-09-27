"""Smoke tests to ensure the test harness is wired up."""

from __future__ import annotations


def test_import_top_level() -> None:
    """Guard that the main package imports without side effects."""
    __import__("codex_ml")


def test_math_sanity() -> None:
    """Simple deterministic check to validate the runner wiring."""
    assert 2 + 2 == 4
