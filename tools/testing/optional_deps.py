"""
Centralized optional dependency probe for tests.

Provides:
    OPTIONALS: dict[str, bool] — availability map
    require(package: str) -> bool
    missing(*packages) -> list[str]
    skip_if_missing(pytest, packages, reason) -> None

Used by tests/conftest.py to skip marked tests cleanly when environment lacks
non-critical libraries (torch, sentencepiece, hydra-core, defusedxml, requests).
"""
from __future__ import annotations

import importlib

_PROBE = [
    "torch",
    "sentencepiece",
    "hydra.core",
    "defusedxml",
    "requests",
    "pydantic",
    "transformers",
]

OPTIONALS: dict[str, bool] = {}
for name in _PROBE:
    try:
        importlib.import_module(name)
        OPTIONALS[name] = True
    except Exception:
        OPTIONALS[name] = False


def require(package: str) -> bool:
    return OPTIONALS.get(package, False)


def missing(*packages: str) -> list[str]:
    return [p for p in packages if not require(p)]


def skip_if_missing(pytest, packages: list[str], reason: str) -> None:
    absent = missing(*packages)
    if absent:
        pytest.skip(f"Skipping due to missing optional deps: {absent} | {reason}")
