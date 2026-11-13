"""Unified Codex namespace package.

This package maps `from codex.*` imports to actual modules in src/.
"""

from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

# Re-export version if available
try:
    __version__ = version("codex-ml")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]

# Include both the live `codex` package directory and the migrated
# `aries_serpent_core` namespace so legacy `codex.*` imports continue to work
# while the codebase is being transitioned.
_src_root = Path(__file__).resolve().parent.parent
_legacy_root = _src_root / "aries_serpent_core"
__path__ = [str(Path(__file__).resolve().parent)]
if _legacy_root.is_dir():
    __path__.append(str(_legacy_root))

# Ensure src/ is in sys.path so relative imports work
if str(_src_root) not in sys.path:
    sys.path.insert(0, str(_src_root))


# ---------------------------------------------------------------------------
# Identity-preserving aliases for migrated sub-packages.
#
# Resolving ``codex.<pkg>`` through ``__path__`` above executes the files under
# ``aries_serpent_core/<pkg>`` a *second* time under a different module name,
# so classes and module-level singletons obtained via ``codex.<pkg>.<mod>`` are
# distinct objects from the ones the package itself uses (e.g.
# ``codex.cognitive.brain`` is not an instance of
# ``codex.cognitive.agent_brain_api.CognitiveBrain``).  For the sub-packages
# listed here, ``codex.<pkg>[.<mod>]`` is served from the already-imported
# ``aries_serpent_core.<pkg>[.<mod>]`` module object instead.
# ---------------------------------------------------------------------------
import importlib as _importlib  # noqa: E402
import importlib.abc as _importlib_abc  # noqa: E402
import importlib.util as _importlib_util  # noqa: E402

_ALIASED_SUBPACKAGES = frozenset({"cognitive"})


class _CanonicalAliasLoader(_importlib_abc.Loader):
    def __init__(self, target: str) -> None:
        self._target = target
        self._original_spec = None

    def create_module(self, spec):  # type: ignore[no-untyped-def]
        module = _importlib.import_module(self._target)
        self._original_spec = module.__spec__
        return module

    def exec_module(self, module) -> None:  # type: ignore[no-untyped-def]
        # importlib overwrites ``__spec__`` when it initialises the module;
        # restore the canonical spec so reload/pickling keep working.
        if self._original_spec is not None:
            module.__spec__ = self._original_spec


class _CanonicalAliasFinder(_importlib_abc.MetaPathFinder):
    _prefix = f"{__name__}."

    def find_spec(self, fullname, path=None, target=None):  # type: ignore[no-untyped-def]
        if not fullname.startswith(self._prefix):
            return None
        rest = fullname[len(self._prefix) :]
        if rest.split(".", 1)[0] not in _ALIASED_SUBPACKAGES:
            return None
        canonical = f"aries_serpent_core.{rest}"
        try:
            if _importlib_util.find_spec(canonical) is None:
                return None
        except (ImportError, ValueError):
            return None
        return _importlib_util.spec_from_loader(fullname, _CanonicalAliasLoader(canonical))


if not any(isinstance(_finder, _CanonicalAliasFinder) for _finder in sys.meta_path):
    sys.meta_path.insert(0, _CanonicalAliasFinder())
