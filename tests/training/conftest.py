from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Iterable

import pytest


_TRAINING_STACK_MODULES: tuple[str, ...] = (
    "yaml",
    "omegaconf",
    "torch",
    "transformers",
    "sentencepiece",
    "hydra",
    "numpy",
)


def _missing_modules(modules: Iterable[str]) -> list[str]:
    """Return a list of modules that cannot be imported."""

    missing: list[str] = []
    for name in modules:
        if importlib.util.find_spec(name) is None:
            missing.append(name)
    return missing


_ALLOWLIST_FILENAMES: frozenset[str] = frozenset(
    {
        "test_checkpoint_integrity.py",
        "test_checkpoint_rng_restore.py",
    }
)

_TRAINING_DIR = Path(__file__).parent.resolve()
_MISSING_STACK_MODULES = _missing_modules(_TRAINING_STACK_MODULES)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip complex training tests when optional dependencies are unavailable.

    Historically the training suite enforced the full dependency stack via
    ``pytest.importorskip`` at module import time.  That caused ``pytest`` to
    exit with a non-zero status before it could collect lightweight tests such
    as the checkpoint integrity checks.  By deferring the skip decision until
    collection we can still run the subset of tests that only relies on the
    standard library when optional dependencies like ``transformers`` are not
    installed.
    """

    if not _MISSING_STACK_MODULES:
        return

    skip_reason = "missing training dependencies: " + ", ".join(_MISSING_STACK_MODULES)
    skip_marker = pytest.mark.skip(reason=skip_reason)

    for item in items:
        try:
            path = Path(item.fspath).resolve()
        except Exception:  # pragma: no cover - defensive
            continue
        if not path.is_relative_to(_TRAINING_DIR):
            continue
        if path.name not in _ALLOWLIST_FILENAMES:
            item.add_marker(skip_marker)
