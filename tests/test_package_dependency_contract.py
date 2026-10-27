"""Dependency manifest invariants required for reproducible repository installs."""

from __future__ import annotations

import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]


def test_locked_wheels_match_package_identity() -> None:
    """A lock entry must not claim a different version than its wheel artifacts."""
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    for package in lock["package"]:
        for wheel in package.get("wheels", []):
            filename = unquote(urlsplit(wheel["url"]).path.rsplit("/", 1)[-1])
            name, version, _, _ = parse_wheel_filename(filename)
            assert name == canonicalize_name(package["name"]), filename
            assert version == Version(package["version"]), filename


def test_contracts_remain_a_real_dependency_with_a_local_development_source() -> None:
    """Source checkouts use local contracts without removing wheel dependencies."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dependencies = {Requirement(value).name for value in project["project"]["dependencies"]}
    assert "codex-contracts" in dependencies
    source = project["tool"]["uv"]["sources"]["codex-contracts"]
    manifest = tomllib.loads((ROOT / source["path"] / "pyproject.toml").read_text())
    assert manifest["project"]["name"] == "codex-contracts"


def test_standalone_test_requirements_include_configured_async_plugin() -> None:
    """Both documented test installs must support pytest's configured asyncio mode."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dev_requirement = next(
        Requirement(value)
        for value in project["project"]["optional-dependencies"]["dev"]
        if Requirement(value).name == "pytest-asyncio"
    )
    for filename in ("requirements-dev.txt", "requirements-test.txt"):
        requirements = [
            Requirement(line)
            for line in (ROOT / filename).read_text().splitlines()
            if line.startswith("pytest-asyncio")
        ]
        assert len(requirements) == 1, filename
        assert requirements[0].specifier == dev_requirement.specifier, filename
