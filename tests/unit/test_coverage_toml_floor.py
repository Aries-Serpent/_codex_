"""
Test Coverage Toml Floor

Test module for coverage toml floor.

The root ``noxfile.py`` is a thin wrapper; the canonical session registry (and
``_toml_fail_under_from_str``) lives in ``configs/development/noxfile.py`` and is
exposed by the wrapper as ``noxfile._dev_noxfile``.
"""

from __future__ import annotations

from types import ModuleType


def _canonical_noxfile() -> ModuleType:
    import noxfile  # type: ignore

    return noxfile._dev_noxfile  # type: ignore[attr-defined]


def test_toml_fail_under_from_str_parses_valid_value() -> None:
    noxfile = _canonical_noxfile()

    text = """
    [tool.coverage.report]
    fail_under = 73
    """
    got = noxfile._toml_fail_under_from_str(text)  # type: ignore[attr-defined]
    assert got == "73", "got is not valid"


def test_toml_fail_under_from_str_absent_returns_none() -> None:
    noxfile = _canonical_noxfile()

    text = """
    [tool.coverage.report]
    show_missing = true
    """
    got = noxfile._toml_fail_under_from_str(text)  # type: ignore[attr-defined]
    assert got is None, "got is not valid"


def test_toml_fail_under_from_str_non_int_returns_none() -> None:
    noxfile = _canonical_noxfile()

    text = """
    [tool.coverage.report]
    fail_under = "eighty"
    """
    got = noxfile._toml_fail_under_from_str(text)  # type: ignore[attr-defined]
    assert got is None, "got is not valid"
