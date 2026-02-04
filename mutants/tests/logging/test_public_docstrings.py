"""Regression tests ensuring public logging/tracking docstrings stay informative."""

from __future__ import annotations

import inspect

import pytest

import codex_ml.logging as logging_mod
import codex_ml.tracking as tracking_mod

_DOC_TARGETS: list[tuple[object, str]] = [
    (tracking_mod.start_run, "context manager"),
    (tracking_mod.log_metrics, "Record scalar metrics"),
    (tracking_mod.log_artifacts, "Persist files"),
    (tracking_mod.ensure_local_artifacts, "summary.json"),
    (logging_mod.RunLogger, "Stream run metadata"),
    (logging_mod.FileLogger, "Write metric dictionaries"),
]


@pytest.mark.parametrize(("target", "expected_fragment"), _DOC_TARGETS)
def test_public_docstrings_are_present(target: object, expected_fragment: str) -> None:
    """Docstrings should remain present and include a user-facing summary."""

    doc = inspect.getdoc(target)
    assert doc, f"{target!r} is missing a docstring"
    assert expected_fragment in doc, f"{target!r} docstring missing {expected_fragment!r}"
