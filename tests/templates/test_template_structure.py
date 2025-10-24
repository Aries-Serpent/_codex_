"""Structural tests validating operational template content."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "docs" / "templates"


def _read(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text(encoding="utf-8")


@pytest.mark.templates
def test_python_file_relocation_has_required_sections() -> None:
    contents = _read("Migration_PythonFileRelocation.md")
    required_sections = [
        "## Executive Summary",
        "## Prerequisites",
        "### Phase 1",
        "### Phase 2",
        "### Phase 3",
        "### Phase 4",
        "### Phase 5",
        "### Phase 6",
        "## Success Criteria",
        "## Rollback Procedure",
        "## Customization Guide",
    ]
    for section in required_sections:
        assert section in contents, f"Missing section '{section}' in Python relocation template"


@pytest.mark.templates
def test_cli_hardening_has_required_sections() -> None:
    contents = _read("Migration_CLIHardening.md")
    expected_tokens = [
        "## Executive Summary",
        "## Prerequisites",
        "### Task 1",
        "### Task 2",
        "### Task 3",
        "### Task 4",
        "## Commit Strategy",
        "## Final Checklist",
        "## Customization Guide",
    ]
    for token in expected_tokens:
        assert token in contents, f"CLI hardening template missing '{token}'"


@pytest.mark.templates
def test_migration_templates_have_placeholders() -> None:
    for name in ("Migration_PythonFileRelocation.md", "Migration_CLIHardening.md"):
        contents = _read(name)
        assert "[PLACEHOLDER:" in contents, f"Template {name} lacks placeholder markers"


@pytest.mark.templates
def test_intent_plan_has_required_sections() -> None:
    contents = _read("Planning_IntentValidation.md")
    for heading in (
        "## Generic Intent Validation Template",
        "## Customization Guide",
        "## Example Instantiations",
        "## Usage Pattern",
        "## Key Benefits",
        "## Repository Context",
    ):
        assert heading in contents, f"Intent planning template missing '{heading}'"


@pytest.mark.templates
def test_intent_plan_has_examples() -> None:
    contents = _read("Planning_IntentValidation.md")
    assert (
        contents.count("**") >= 6
    ), "Intent planning template should list multiple example scenarios"


@pytest.mark.templates
def test_templates_have_version_metadata() -> None:
    for name in (
        "Migration_PythonFileRelocation.md",
        "Migration_CLIHardening.md",
        "Planning_IntentValidation.md",
    ):
        contents = _read(name)
        assert (
            "Version: v1.0.0" in contents or "**Version:** v1.0.0" in contents
        ), f"Template {name} missing version metadata"
        assert "Last Updated:" in contents, f"Template {name} missing last updated metadata"
