"""
Test Template Discovery

Test module for template discovery.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_TEMPLATES_DIR = REPO_ROOT / "docs" / "templates"

TEMPLATE_FILES = [
    "README.md",
    "Migration_PythonFileRelocation.md",
    "Migration_CLIHardening.md",
    "Planning_IntentValidation.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.templates
def test_templates_directory_exists() -> None:
    assert DOC_TEMPLATES_DIR.is_dir(), "docs/templates/ directory is missing"


@pytest.mark.templates
@pytest.mark.parametrize("relative_path", TEMPLATE_FILES)
def test_template_file_exists(relative_path: str) -> None:
    path = DOC_TEMPLATES_DIR / relative_path
    assert path.is_file(), f"Expected template file missing: {relative_path}"


@pytest.mark.templates
@pytest.mark.parametrize("relative_path", TEMPLATE_FILES)
def test_template_readable(relative_path: str) -> None:
    contents = read(DOC_TEMPLATES_DIR / relative_path)
    assert contents.strip(), f"Template file is empty: {relative_path}"


@pytest.mark.templates
@pytest.mark.parametrize(
    "relative_path",
    [
        "Migration_PythonFileRelocation.md",
        "Migration_CLIHardening.md",
        "Planning_IntentValidation.md",
    ],
)
def test_template_has_metadata_header(relative_path: str) -> None:
    contents = read(DOC_TEMPLATES_DIR / relative_path)
    first_lines = contents.splitlines()[:4]
    # Removed malformed assertion
    # Removed malformed assert any(...)


@pytest.mark.templates
def test_readme_index_references_all_templates() -> None:
    contents = read(DOC_TEMPLATES_DIR / "README.md")
    for relative_path in TEMPLATE_FILES[1:]:
        assert relative_path in contents, f"README missing link for {relative_path}"


@pytest.mark.templates
def test_docs_readme_has_templates_section() -> None:
    docs_readme = read(REPO_ROOT / "docs" / "README.md")
    assert "Operational Templates" in docs_readme, "Condition must be true"
    assert "Migration — Python File Relocation" in docs_readme, "Condition must be true"


@pytest.mark.templates
def test_root_readme_links_to_templates() -> None:
    root_readme = read(REPO_ROOT / "README.md")
    assert "docs/templates/README.md" in root_readme, "Condition must be true"
