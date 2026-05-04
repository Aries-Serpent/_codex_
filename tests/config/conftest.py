"""
Conftest for tests/config — ensures src/ is on sys.path so that
``from config.openai_client import ...`` resolves to src/config/openai_client.py
and not to any other 'config' package that may exist in site-packages.

This is a belt-and-suspenders guard: the root conftest.py already does this,
but package-level conftest.py files in sub-directories can be loaded in a
different order under pytest-split / pytest-xdist worker processes.

P19 shadow-import fix (S679): tests now use ``from src.config.openai_client import``
so they no longer depend on this conftest's path manipulation.  This guard remains
for any future tests that use the short ``config.openai_client`` form.
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

# Also ensure repo root is on path (at the end) so ``src.config.*`` imports work too.
_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.append(_REPO_ROOT_STR)

# If a different 'config' module is already cached in sys.modules (e.g. from an
# installed 'python-config' or similar package that was imported before this
# conftest ran), evict it so the next 'import config' re-resolves to src/config/.
_cached_config = sys.modules.get("config")
if _cached_config is not None:
    _cached_origin = getattr(_cached_config, "__file__", None) or ""
    if not _cached_origin.startswith(_SRC):
        for _key in list(sys.modules.keys()):
            if _key == "config" or _key.startswith("config."):
                del sys.modules[_key]

pytest.importorskip("yaml")
pytest.importorskip("omegaconf")
