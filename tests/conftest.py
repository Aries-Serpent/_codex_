#!/usr/bin/env python3
"""
Conftest to avoid ImportError during collection when optional heavy dependencies
are not installed in the CI/test environment.
"""
from __future__ import annotations
import sys
import types
import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

HEAVY_MODULES = [
    "numpy",
    "torch",
    "transformers",
    "tensorflow",
    "jax",
    "sentencepiece",
]

OPTIONAL_DEP_MARKERS: dict[str, list[str]] = {
    "requires_torch": ["torch"],
    "requires_transformers": ["transformers"],
    "requires_tensorflow": ["tensorflow"],
    "requires_jax": ["jax"],
    "requires_numpy": ["numpy"],
    "requires_sentencepiece": ["sentencepiece"],
}

def _inject_stub_module(name: str):
    if name in sys.modules:
        return
    m = types.ModuleType(name)
    m.__all__ = []
    setattr(m, "__version__", "0.0.0-stub")
    if name == "numpy":
        class _ndarray_stub:
            def __init__(self, *args, **kwargs):
                pass
            def __array__(self):
                return []
            @property
            def shape(self):
                return ()
        m.ndarray = _ndarray_stub
        m.array = lambda *args, **kwargs: []
    sys.modules[name] = m

for _mod in HEAVY_MODULES:
    if importlib.util.find_spec(_mod) is None:
        _inject_stub_module(_mod)


def _is_stub_module(name: str, spec: importlib.machinery.ModuleSpec | None = None) -> bool:
    """Return True when ``name`` resolves to an in-repo stub instead of the real package."""

    module = sys.modules.get(name)
    if getattr(module, "IS_CODEX_STUB", False):
        return True

    spec = spec or importlib.util.find_spec(name)
    if spec is None:
        return False

    origin = getattr(spec, "origin", None)
    if not origin:
        return False

    origin_path = Path(origin).resolve()
    return origin_path.is_relative_to(REPO_ROOT / name)


def _missing_modules(modules: list[str]) -> list[str]:
    missing: list[str] = []

    for mod in modules:
        spec = importlib.util.find_spec(mod)
        if spec is None or _is_stub_module(mod, spec):
            missing.append(mod)

    return missing

def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker, modules in OPTIONAL_DEP_MARKERS.items():
            if marker in item.keywords:
                missing = _missing_modules(modules)
                if missing:
                    reason = f"skipped: optional dependency missing for {marker}: {', '.join(missing)}"
                    item.add_marker(pytest.mark.skip(reason=reason))

        if 'heavy_dep' in item.keywords:
            missing = _missing_modules(HEAVY_MODULES)
            if missing:
                reason = f"skipped: heavy optional deps missing: {', '.join(missing)}"
                item.add_marker(pytest.mark.skip(reason=reason))
