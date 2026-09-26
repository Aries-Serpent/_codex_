from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "module_name", ["datasets", "torch", "sentencepiece", "transformers"]
)
def test_repo_root_stubs_do_not_mask_real_installs(
    module_name: str, monkeypatch: pytest.MonkeyPatch
):
    """Only fail when a real install is present and a repo-local stub masks it."""
    repo_root = Path(__file__).resolve().parents[1]

    # When the package is only provided by the repo-local compatibility stub,
    # the guard should skip rather than fail; this is intentionally supported for
    # lightweight CI/doc environments that do not install the real dependency.
    real_search_path = [
        entry
        for entry in sys.path
        if entry and Path(entry).resolve() != repo_root and Path(entry).resolve() != repo_root / module_name
    ]
    monkeypatch.setattr(sys, "path", real_search_path)
    sys.modules.pop(module_name, None)
    for submodule in [
        key
        for key in list(sys.modules)
        if key == module_name or key.startswith(f"{module_name}.")
    ]:
        sys.modules.pop(submodule, None)

    spec = importlib.machinery.PathFinder.find_spec(module_name, real_search_path)
    if spec is None:
        pytest.skip(f"{module_name} is not installed outside the repo root; stub fallback is allowed.")

    try:
        loaded = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        message = str(exc)
        assert (
            "pytest.importorskip" in message
            or "repo-local" in message
            or "not a Python package" in message
        ), "Condition must be true"
        return

    imported_file = getattr(loaded, "__file__", "")
    if imported_file:
        resolved = Path(imported_file).resolve()
        assert not resolved.is_relative_to(repo_root), (
            f"{module_name} resolved inside repo root instead of the installed package: {resolved}"
        )
