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
    """The repo root may contain stub packages, but real installs must still win."""
    repo_root = Path(__file__).resolve().parents[1]
    repo_path = [str(repo_root)] + [
        entry for entry in sys.path if entry and Path(entry).resolve() != repo_root
    ]
    monkeypatch.setattr(sys, "path", repo_path)
    sys.modules.pop(module_name, None)
    for submodule in [
        key
        for key in list(sys.modules)
        if key == module_name or key.startswith(f"{module_name}.")
    ]:
        sys.modules.pop(submodule, None)

    try:
        loaded = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        message = str(exc)
        assert (
            "pytest.importorskip" in message
            or "repo-local" in message
            or "not a Python package" in message
        )
        return

    imported_file = getattr(loaded, "__file__", "")
    if imported_file:
        resolved = Path(imported_file).resolve()
        assert not resolved.is_relative_to(repo_root), (
            f"{module_name} resolved inside repo root instead of the installed package: {resolved}"
        )
