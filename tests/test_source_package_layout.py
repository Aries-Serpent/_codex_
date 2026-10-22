"""Keep installed package names and full-source type-check discovery aligned."""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_mypy_discovers_canonical_packages_without_reducing_source_scope(
    monkeypatch,
) -> None:
    from mypy.main import process_options

    monkeypatch.chdir(ROOT)
    sources, _ = process_options(["src/"])
    by_path = {Path(source.path).resolve(): source.module for source in sources}
    assert by_path[ROOT / "src/agent/core.py"] == "agent.core"
    assert by_path[ROOT / "src/utils/log_sanitizer.py"] == "utils.log_sanitizer"
    assert by_path[ROOT / "src/services/workflow_backup/parser.py"] == (
        "services.workflow_backup.parser"
    )

    resources = ROOT / "src/agents/prompts/self-healing"
    backup = ROOT / "src/services/workflow.backup"
    omitted = set((ROOT / "src").rglob("*.py")) - set(by_path)
    intentional_omissions = set(resources.glob("*.py")) | set(backup.glob("*.py"))
    # Mypy follows Python's package-before-module and stub-before-source rules.
    # These pre-existing same-name legacy files are not configuration excludes.
    shadowed = {
        path
        for path in (ROOT / "src").rglob("*.py")
        if path.with_suffix(".pyi").exists() or (path.with_suffix("") / "__init__.py").exists()
    }
    assert omitted == intentional_omissions | shadowed
    assert {path.name for path in resources.glob("*.py")} == {"__init__.py"}
    assert (resources / "__init__.py").read_text().strip() == '"""Package module."""'
    for path in backup.glob("*.py"):
        canonical = ROOT / "src/services/workflow_backup" / path.name
        assert path.read_bytes() == canonical.read_bytes()


def test_packaged_compatibility_dependencies_are_discovered() -> None:
    from setuptools import find_namespace_packages

    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    discovery = project["tool"]["setuptools"]["packages"]["find"]
    packages = find_namespace_packages(
        where=str(ROOT / "src"),
        include=discovery["include"],
        exclude=discovery["exclude"],
    )
    assert {"agent", "agent.adapters", "utils", "services.msp_gateway"} <= set(packages)
    assert "agents.prompts.self-healing" not in packages
    assert "services.workflow.backup" not in packages
    assert "prompts/**/*.md" in project["tool"]["setuptools"]["package-data"]["agents"]
    excluded_data = project["tool"]["setuptools"]["exclude-package-data"]
    assert "prompts/self-healing/*.py" in excluded_data["agents"]
    assert "self-healing/*.py" in excluded_data["agents.prompts"]
    assert "workflow.backup/*.py" in excluded_data["services"]


def test_agent_compatibility_wrapper_uses_the_canonical_class() -> None:
    from agent.core import AgentConfig, AgentCore
    from aries_serpent_core.agent import core

    assert core.AgentConfig is AgentConfig
    assert core.AgentCore is AgentCore


def test_legacy_sanitizer_path_remains_compatible() -> None:
    canonical = importlib.import_module("utils.log_sanitizer")
    legacy = importlib.import_module("src.utils.log_sanitizer")
    value = "tenant\nforged\x1b[31m"
    assert canonical.sanitize_log_input(value) == legacy.sanitize_log_input(value) == "tenantforged"
