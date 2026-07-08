"""Regression tests for the public logging/tracking docstrings."""

from __future__ import annotations

import codex_ml.logging as codex_logging
import codex_ml.tracking as tracking


def _assert_contains(doc: str | None, needle: str) -> None:
    assert doc is not None and doc.strip(), "expected docstring to be present"
    assert needle.lower() in doc.lower(), f"expected '{needle}' in docstring"


def test_tracking_module_docstrings_present() -> None:
    _assert_contains(tracking.__doc__, "experiment tracking")
    _assert_contains(tracking.init_experiment.__doc__, "ExperimentContext")
    _assert_contains(tracking.start_run.__doc__, "context manager")


def test_logging_module_docstrings_present() -> None:
    _assert_contains(codex_logging.__doc__, "structured run logging")
    _assert_contains(codex_logging.RunLogger.__doc__, "params and metrics")
    _assert_contains(codex_logging.FileLogger.__doc__, "structured files")
