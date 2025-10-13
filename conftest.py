"""Global pytest configuration for offline, deterministic runs."""

from __future__ import annotations

import importlib.util
import os as _os
import pathlib
import sys as _sys
from pathlib import Path as _Path

import pytest

# Respect existing user setting; default to disabling plugin autoload for determinism.
_os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

# conftest.py
# Make PyTorch 2.6+ behave like pre-2.6 for our test suite:
# https://pytorch.org/docs/stable/serialization.html#troubleshooting

_SRC_DIR = _Path(__file__).resolve().parent / "src"
if _SRC_DIR.exists():
    # Ensure in-process imports see ``src`` modules without installing the package.
    _src = str(_SRC_DIR)
    if _src not in _sys.path:
        _sys.path.insert(0, _src)
    # Propagate to subprocesses invoked by tests (e.g., ``python -m tokenization.cli``).
    existing = _os.environ.get("PYTHONPATH")
    if existing:
        if _src not in existing.split(_os.pathsep):
            _os.environ["PYTHONPATH"] = _src + _os.pathsep + existing
    else:
        _os.environ["PYTHONPATH"] = _src

_os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")


def _path_requires_torch(path_obj: pathlib.Path) -> bool:
    return "tests" in path_obj.parts and any(
        seg in path_obj.parts for seg in ("checkpointing", "training", "codex_ml")
    )


def _needs_torch(item: pytest.Item) -> bool:
    """Heuristic to detect tests that require torch."""

    p = pathlib.Path(str(getattr(item, "fspath", "")))
    if _path_requires_torch(p):
        return True
    return any(m.name == "requires_torch" for m in getattr(item, "iter_markers", lambda: [])())


def _path_requires_pydantic(path_obj: pathlib.Path) -> bool:
    if "tests" not in path_obj.parts:
        return False
    if "codex_ml" in path_obj.parts or "config" in path_obj.parts:
        return True
    return path_obj.name == "test_codex_export_env.py"


def _needs_pydantic(item: pytest.Item) -> bool:
    p = pathlib.Path(str(getattr(item, "fspath", "")))
    if _path_requires_pydantic(p):
        return True
    return any(m.name == "requires_pydantic" for m in getattr(item, "iter_markers", lambda: [])())


def _torch_available() -> bool:
    torch_spec = importlib.util.find_spec("torch")
    if torch_spec is None:
        return False
    return importlib.util.find_spec("torch.nn") is not None


def _pydantic_available() -> bool:
    return importlib.util.find_spec("pydantic") is not None


collect_ignore: list[str] = []
collect_ignore_glob: list[str] = []
if not _torch_available():
    collect_ignore.extend(
        [
            "tests/checkpointing",
            "tests/training",
            "tests/codex_ml",
        ]
    )
    collect_ignore_glob.extend(
        [
            "tests/checkpointing/*",
            "tests/training/*",
            "tests/codex_ml/*",
            "*/tests/checkpointing/*",
            "*/tests/training/*",
            "*/tests/codex_ml/*",
        ]
    )

if not _pydantic_available():
    collect_ignore.extend(
        [
            "tests/codex_ml",
            "tests/config",
            "tests/cli/test_codex_export_env.py",
        ]
    )
    collect_ignore_glob.extend(
        [
            "tests/codex_ml/*",
            "*/tests/codex_ml/*",
        ]
    )


def pytest_collect_file(path, parent):  # type: ignore[override]
    p = pathlib.Path(str(path))
    if not _torch_available() and _path_requires_torch(p):
        pytest.skip("Optional dependency 'torch' not installed", allow_module_level=True)
    if not _pydantic_available() and _path_requires_pydantic(p):
        pytest.skip("Optional dependency 'pydantic' not installed", allow_module_level=True)
    return None


def pytest_ignore_collect(path, config):  # type: ignore[override]
    p = pathlib.Path(str(path))
    return (not _torch_available() and _path_requires_torch(p)) or (
        not _pydantic_available() and _path_requires_pydantic(p)
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip Torch-only suites when torch is not installed."""

    if not _torch_available():
        skip_torch = pytest.mark.skip(reason="Optional dependency 'torch' not installed")
        for it in items:
            if _needs_torch(it):
                it.add_marker(skip_torch)

    if not _pydantic_available():
        skip_pydantic = pytest.mark.skip(reason="Optional dependency 'pydantic' not installed")
        for it in items:
            if _needs_pydantic(it):
                it.add_marker(skip_pydantic)


def _gpu_available() -> bool:
    try:
        import torch  # type: ignore

        return bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
    except Exception:
        return False


def pytest_report_header(config):
    # If the user *forces* GPU tests (e.g., -m "gpu" or -m "gpu and ..."),
    # but there is no GPU/CUDA available, print a friendly heads-up.
    marker_expr = (config.getoption("-m") or "").strip()
    # Heuristic: "gpu" present and not explicitly negated.
    wants_gpu = ("gpu" in marker_expr) and ("not gpu" not in marker_expr)
    if wants_gpu and not _gpu_available():
        return (
            "⚠️  GPU tests were requested (-m 'gpu'), but no CUDA/GPU was detected.\n"
            "    Running with CPU-only torch; GPU tests may be skipped or slow.\n"
            "    Tip: on GPU runners, include `gpu` in CODEX_SYNC_GROUPS and install a CUDA wheel."
        )
    return None
