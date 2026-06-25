"""
Test Template Structure

Test module for template structure.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_TEMPLATES_DIR = REPO_ROOT / "docs" / "templates"


def read(relative_path: str) -> str:
    return (DOC_TEMPLATES_DIR / relative_path).read_text(encoding="utf-8")


@pytest.mark.templates
def test_python_file_relocation_has_required_sections() -> None:
    contents = read("Migration_PythonFileRelocation.md")
    for heading in [
        "## Executive Summary",
        "## Prerequisites",
        "## Phase 1",
        "## Phase 2",
        "## Phase 3",
        "## Phase 4",
        "## Phase 5",
        "## Phase 6",
        "## Success Criteria",
        "## Rollback Procedure",
        "## Customization Guide",
    ]:
        assert heading in contents, f"Missing heading '{heading}' in relocation template"


@pytest.mark.templates
def test_cli_hardening_has_required_sections() -> None:
    contents = read("Migration_CLIHardening.md")
    for heading in [
        "## Executive Summary",
        "## Baseline Assessment",
        "## Hardening Task 1",
        "## Hardening Task 2",
        "## Hardening Task 3",
        "## Hardening Task 4",
        "## Commit Strategy",
        "## Final Checklist",
        "## Customization Guide",
    ]:
        assert heading in contents, f"Missing heading '{heading}' in CLI hardening template"


@pytest.mark.templates
def test_migration_templates_have_placeholders() -> None:
    for filename in [
        "Migration_PythonFileRelocation.md",
        "Migration_CLIHardening.md",
    ]:
        contents = read(filename)
        assert "[PLACEHOLDER:" in contents, f"Placeholders missing in {filename}"


@pytest.mark.templates
def test_intent_plan_has_required_sections() -> None:
    contents = read("Planning_IntentValidation.md")
    for heading in [
        "## Template Overview",
        "## Intent Brief",
        "## Discovery Inputs",
        "## Validation Activities",
        "## Decision Gates",
        "## Risk Register",
        "## Customization Guide",
        "## Example Instantiations",
        "## Usage Pattern",
        "## Key Benefits",
    ]:
        assert heading in contents, f"Missing heading '{heading}' in planning template"


@pytest.mark.templates
def test_intent_plan_has_examples() -> None:
    contents = read("Planning_IntentValidation.md")
    assert contents.count("**") >= 3, "Expected at least three example instantiations"


@pytest.mark.templates
def test_intent_plan_has_customization_guide() -> None:
    contents = read("Planning_IntentValidation.md")
    assert "## Customization Guide" in contents
    assert "[PLACEHOLDER:" in contents, "Customization guide should describe placeholders"


@pytest.mark.templates
def test_templates_have_version_metadata() -> None:
    for filename in [
        "Migration_PythonFileRelocation.md",
        "Migration_CLIHardening.md",
        "Planning_IntentValidation.md",
    ]:
        contents = read(filename)
        assert "Version:** v1.0.0" in contents, f"Version metadata missing in {filename}"
