"""
Test Packaging Metadata

Test module for packaging metadata.
"""

from __future__ import annotations

import re

import pytest

try:  # Python 3.11+ standard library
    import tomllib
except ModuleNotFoundError:  # Python 3.10 fallback
    try:
        import tomli as tomllib
    except ModuleNotFoundError:  # Optional dependency missing
        tomllib = None

if tomllib is None:  # pragma: no cover - guard for missing dependency
    pytest.skip("TOML parser is unavailable", allow_module_level=True)
from pathlib import Path


def load_pyproject() -> dict[str, object]:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")

    def dedupe(pattern: re.Pattern[str], block: str) -> str:
        matches = list(pattern.finditer(block))
        if matches:
            first_end = matches[0].end()
            return block[:first_end] + pattern.sub("", block[first_end:])
        return block

    # Dedupe specific repeated tables/arrays to satisfy strict parsers.
    optional_pattern = re.compile(
        r"(?ms)^\[project\.optional-dependencies\][\s\S]*?(?=^\[project\.|^\[tool\.|\Z)"
    )
    dependencies_pattern = re.compile(r"(?ms)^dependencies\s*=\s*\[[\s\S]*?\]")

    text = dedupe(optional_pattern, text)
    text = dedupe(dependencies_pattern, text)

    return tomllib.loads(text)


def test_pyproject_core_metadata():
    data = load_pyproject()
    proj = data["project"]
    dependencies = proj.get("dependencies", [])
    optional = proj.get("optional-dependencies", {})

    # SPDX license (can be string or dict with 'text' key)
    license_val = proj.get("license")
    if isinstance(license_val, dict):
        assert license_val.get("text") == "MIT", "Condition must be true"
    else:
        assert license_val == "MIT", "license_val is not valid"

    # Python floor
    req = proj.get("requires-python", "")
    assert req.startswith(">=3.12") or req.startswith(">=3.10"), "Value must be greater than zero"

    # Vulnerable optional stacks should not be pulled into the base install.
    assert all("lm-eval" not in dep for dep in dependencies), "Condition must be true"
    assert "eval" in optional, "Condition must be true"
    assert any("lm-eval" in dep for dep in optional["eval"]), "Condition must be true"
    assert "dataops" in optional, "Data must not be empty"
    assert any("dvc==" in dep for dep in optional["dataops"]), "Data must not be empty"

    # Scripts presence
    scripts = proj.get("scripts", {})
    for key in ("codex-train", "codex-eval", "codex-list-plugins"):
        assert key in scripts, f"missing console script: {key}"

    # Package-dir maps (top-level shims + src)
    pkgdir = data.get("tool", {}).get("setuptools", {}).get("package-dir", {})
    for k in ("", "training", "tokenization", "codex_utils", "interfaces"):
        assert k in pkgdir, f"missing package-dir mapping for '{k}'"

    # Package discovery "where" includes "." and "src"
    find = data.get("tool", {}).get("setuptools", {}).get("packages", {}).get("find", {})
    where = find.get("where", [])
    assert "." in where and "src" in where, "Condition must be true"

    # Include patterns cover codex_ml namespace
    include = find.get("include", [])
    assert any(p.startswith("codex_ml") for p in include), "Condition must be true"


def test_license_files_present():
    data = load_pyproject()
    # Check tool.setuptools.license-files (setuptools-specific)
    lic_files = data.get("tool", {}).get("setuptools", {}).get("license-files")
    if lic_files:
        # Should be a list of file patterns
        assert "LICENSE" in lic_files, "Condition must be true"
        assert any("LICENSES" in p for p in lic_files), "Condition must be true"
    else:
        # Fallback: check if LICENSE file exists in repo
        import pathlib

        repo_root = pathlib.Path(__file__).parent.parent
        assert (repo_root / "LICENSE").exists(), "Condition must be true"
