"""Smoke tests ensuring operational templates stay discoverable."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "docs" / "templates"
TEMPLATE_FILES = {
    "Migration_PythonFileRelocation.md",
    "Migration_CLIHardening.md",
    "Planning_IntentValidation.md",
    "README.md",
}
TEMPLATE_DOCS = {
    "Migration_PythonFileRelocation.md": "Python File Relocation",
    "Migration_CLIHardening.md": "CLI Hardening",
    "Planning_IntentValidation.md": "Intent Validation",
}


@pytest.mark.templates
def test_templates_directory_exists() -> None:
    """Ensure the templates folder exists for documentation discovery."""
    assert TEMPLATE_DIR.exists() and TEMPLATE_DIR.is_dir(), "docs/templates/ directory is missing"


@pytest.mark.templates
@pytest.mark.parametrize("filename", sorted(TEMPLATE_FILES))
def test_template_file_exists(filename: str) -> None:
    """Every expected template artefact should be present."""
    file_path = TEMPLATE_DIR / filename
    assert file_path.exists(), f"{filename} is missing from docs/templates/"


@pytest.mark.templates
@pytest.mark.parametrize("filename", sorted(TEMPLATE_DOCS))
def test_template_readable(filename: str) -> None:
    """All templates should be readable as UTF-8 without crashing."""
    file_path = TEMPLATE_DIR / filename
    contents = file_path.read_text(encoding="utf-8")
    assert contents.strip(), f"{filename} is empty"


@pytest.mark.templates
@pytest.mark.parametrize("filename", sorted(TEMPLATE_DOCS))
def test_template_has_metadata_header(filename: str) -> None:
    """Templates must expose metadata headers for versioning."""
    contents = (TEMPLATE_DIR / filename).read_text(encoding="utf-8")
    assert contents.splitlines()[0].startswith("# [Template]"), "Missing template title heading"
    assert (
        "Version: v1.0.0" in contents or "**Version:** v1.0.0" in contents
    ), "Template must declare v1.0.0 metadata"


@pytest.mark.templates
def test_readme_index_exists() -> None:
    """Index README should link to every template for navigation."""
    readme = (TEMPLATE_DIR / "README.md").read_text(encoding="utf-8")
    for fragment in TEMPLATE_DOCS.values():
        assert fragment in readme, f"README missing reference to {fragment}"


@pytest.mark.templates
def test_docs_readme_has_templates_section() -> None:
    """docs/README.md should provide a navigation entry to the templates."""
    docs_readme = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    assert (
        "Operational Templates" in docs_readme
    ), "docs/README.md missing Operational Templates section"


@pytest.mark.templates
def test_root_readme_links_to_templates() -> None:
    """Root README should surface the templates index when present."""
    root_readme_path = REPO_ROOT / "README.md"
    if not root_readme_path.exists():  # Repository may omit the root README in some contexts
        pytest.skip("Root README not present in repository")

    contents = root_readme_path.read_text(encoding="utf-8")
    assert "docs/templates" in contents, "Root README should link to docs/templates index"
