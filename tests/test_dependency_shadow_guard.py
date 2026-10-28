from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


def test_source_package_precedes_same_named_test_package(monkeypatch: pytest.MonkeyPatch):
    """A test-directory path insertion must not replace the installed source namespace."""
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(repo_root / "tests"))
    monkeypatch.delitem(sys.modules, "codex_ml", raising=False)

    shadow = importlib.machinery.PathFinder.find_spec("codex_ml")
    assert shadow is not None
    assert shadow.origin == str(repo_root / "tests" / "codex_ml" / "__init__.py")

    canonical = importlib.util.find_spec("codex_ml")
    assert canonical is not None
    assert canonical.origin == str(repo_root / "src" / "codex_ml" / "__init__.py")


@pytest.mark.parametrize("module_name", ["datasets", "torch", "sentencepiece", "transformers"])
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
        if entry
        and Path(entry).resolve() != repo_root
        and Path(entry).resolve() != repo_root / module_name
    ]
    monkeypatch.setattr(sys, "path", real_search_path)
    sys.modules.pop(module_name, None)
    for submodule in [
        key for key in list(sys.modules) if key == module_name or key.startswith(f"{module_name}.")
    ]:
        sys.modules.pop(submodule, None)

    spec = importlib.machinery.PathFinder.find_spec(module_name, real_search_path)
    if spec is None:
        pytest.skip(
            f"{module_name} is not installed outside the repo root; stub fallback is allowed."
        )

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
        # The loaded module must not be the repo-local stub itself. Real
        # installs may legitimately live under the repo root when CI uses an
        # in-repo virtualenv (e.g. ``.venv_ci/.../site-packages``), so we only
        # reject the stub path ``<repo_root>/<module_name>/__init__.py`` rather
        # than any path merely "relative to the repo root".
        stub_init = (repo_root / module_name / "__init__.py").resolve()
        assert (
            resolved != stub_init
        ), f"{module_name} resolved to the repo-local stub instead of the installed package: {resolved}"
