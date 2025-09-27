from __future__ import annotations

from pathlib import Path

import pytest

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for 3.10
    try:
        import tomli as tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError:  # pragma: no cover - skip when parser missing
        tomllib = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(tomllib is None, reason="tomllib/tomli not available")


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_pyproject() -> dict:
    pyproject = PROJECT_ROOT / "pyproject.toml"
    return tomllib.loads(pyproject.read_text())


def test_project_name_and_script_exist() -> None:
    data = _load_pyproject()
    project = data.get("project", {})
    assert project.get("name") == "codex-ml"
    scripts = project.get("scripts", {})
    assert "codex-train" in scripts


def test_build_system_is_setuptools() -> None:
    data = _load_pyproject()
    build_system = data.get("build-system", {})
    assert build_system.get("build-backend") == "setuptools.build_meta"
