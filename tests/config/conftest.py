"""
Conftest for tests/config — ensures src/ is on sys.path so that
``from config.openai_client import ...`` resolves to src/config/openai_client.py
and not to any other 'config' package that may exist in site-packages.

This is a belt-and-suspenders guard: the root conftest.py already does this,
but package-level conftest.py files in sub-directories can be loaded in a
different order under pytest-split / pytest-xdist worker processes.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

# Belt-and-suspenders: guarantee src/ is first on sys.path so 'config'
# unambiguously resolves to src/config/ rather than any installed package.
#
# Directory depth: this file is at tests/config/conftest.py, so:
#   parent   → tests/config/
#   parent.parent → tests/
#   parent.parent.parent → repo root
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_SRC = str(_REPO_ROOT / "src")
# Ensure _SRC is first on sys.path: remove any existing occurrences, then insert at index 0.
sys.path[:] = [p for p in sys.path if p != _SRC]
sys.path.insert(0, _SRC)

pytest.importorskip("yaml")
pytest.importorskip("omegaconf")
