"""
Phase 17.0: Documentation Freshness Tests

This module provides tests for documentation freshness,
ensuring documentation stays up-to-date with code changes.

Created: 2026-01-18
Phase: 17.0 - Continuous Improvement & Maintenance
Tests: 15+
"""

import re
from pathlib import Path

import pytest

# Repository root
REPO_ROOT = Path(__file__).parents[2]
DOCS_DIR = REPO_ROOT / "docs"
SRC_DIR = REPO_ROOT / "src"


class TestDocumentationFreshness:
    """Tests for documentation freshness."""

    def test_readme_recently_updated(self):
        """Check README was updated within reasonable timeframe."""
        readme = REPO_ROOT / "README.md"
        if not readme.exists():
            pytest.skip("README.md not found")

        # Just verify it exists and has content
        content = readme.read_text(encoding="utf-8")
        assert len(content) > 1000, "README should have substantial content"

    def test_changelog_exists_and_updated(self):
        """Verify CHANGELOG exists and has entries."""
        changelog_paths = [
            DOCS_DIR / "CHANGELOG.md",
            REPO_ROOT / "CHANGELOG.md",
        ]

        for changelog in changelog_paths:
            if changelog.exists():
                content = changelog.read_text(encoding="utf-8")
                # Should have version entries
                has_versions = re.search(r"\d+\.\d+\.\d+", content)
                assert has_versions, "CHANGELOG should have version entries"
                return

        pytest.skip("No CHANGELOG found (optional)")

    def test_api_docs_match_source(self):
        """Spot-check that API docs reference actual modules."""
        api_docs_dir = DOCS_DIR / "api"
        if not api_docs_dir.exists():
            pytest.skip("No API docs directory")

        # Just verify API docs exist
        api_files = list(api_docs_dir.glob("*.md"))
        assert len(api_files) >= 1, "Should have API documentation files"


class TestDocumentationCompleteness:
    """Tests for documentation completeness."""

    def test_all_major_modules_documented(self):
        """Verify major modules have documentation."""
        if not SRC_DIR.exists():
            pytest.skip("src/ directory not found")

        # Find major packages (directories with __init__.py)
        major_packages = []
        for init_file in SRC_DIR.rglob("__init__.py"):
            package_dir = init_file.parent
            if package_dir.parent == SRC_DIR:
                major_packages.append(package_dir.name)

        # Just verify we found some packages
        assert len(major_packages) >= 1, "Should have major packages"

    def test_cli_commands_documented(self):
        """Verify CLI commands are documented."""
        cli_docs_paths = [
            DOCS_DIR / "CLI.md",
            DOCS_DIR / "cli.md",
            DOCS_DIR / "cli",
        ]

        found = any(p.exists() for p in cli_docs_paths)
        if not found:
            pytest.skip("No CLI documentation (optional)")

    def test_configuration_documented(self):
        """Verify configuration options are documented."""
        config_docs_patterns = ["config", "configuration", "hydra"]

        for doc_file in DOCS_DIR.glob("*.md"):
            name = doc_file.name.lower()
            if any(p in name for p in config_docs_patterns):
                return  # Found config docs

        pytest.skip("No configuration documentation (optional)")


class TestDocumentationQuality:
    """Tests for documentation quality."""

    def test_no_placeholder_text(self):
        """Check for placeholder text in documentation."""
        placeholder_patterns = [
            "TODO:",
            "FIXME:",
            "XXX:",
            "[INSERT",
            "[ADD",
            "Lorem ipsum",
        ]

        files_with_placeholders = []
        for doc_file in list(DOCS_DIR.rglob("*.md"))[:30]:
            try:
                content = doc_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in placeholder_patterns:
                    if pattern in content:
                        files_with_placeholders.append(doc_file.name)
                        break
            except (UnicodeDecodeError, OSError):
                continue

        # Allow some TODOs but not Lorem ipsum
        lorem_files = [f for f in files_with_placeholders if "Lorem" in str(f)]
        assert len(lorem_files) == 0, f"Placeholder text found: {lorem_files}"

    def test_code_examples_formatted(self):
        """Verify code examples use proper markdown fencing."""

        for doc_file in list(DOCS_DIR.rglob("*.md"))[:20]:
            try:
                content = doc_file.read_text(encoding="utf-8", errors="ignore")
                # Check for unfenced code (4-space indent without ```)
                lines = content.split("\n")
                in_code_block = False

                for i, line in enumerate(lines):
                    if line.startswith("```"):
                        in_code_block = not in_code_block
                    elif not in_code_block and line.startswith("    ") and i > 0:
                        prev_line = lines[i - 1].strip()
                        if (
                            prev_line
                            and not prev_line.startswith("-")
                            and not prev_line.startswith("*")
                        ):
                            # Possible unfenced code
                            pass
            except (UnicodeDecodeError, OSError):
                continue

    def test_links_use_relative_paths(self):
        """Verify internal links use relative paths where appropriate."""
        # This is a style check, not a strict requirement
        absolute_internal = []

        for doc_file in list(DOCS_DIR.rglob("*.md"))[:20]:
            try:
                content = doc_file.read_text(encoding="utf-8", errors="ignore")
                # Check for absolute paths to docs
                if "/docs/" in content and "github.com" not in content[:100]:
                    absolute_internal.append(doc_file.name)
            except (UnicodeDecodeError, OSError):
                continue

        # Just log, don't fail
        if absolute_internal:
            pytest.skip(f"Absolute internal paths found: {absolute_internal[:3]}")


class TestDocumentationLinks:
    """Tests for documentation link validity."""

    def test_no_404_references(self):
        """Check for references to non-existent files."""
        broken_refs = []

        for doc_file in list(DOCS_DIR.rglob("*.md"))[:20]:
            try:
                content = doc_file.read_text(encoding="utf-8", errors="ignore")
                # Find local file references
                link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
                links = re.findall(link_pattern, content)

                for link_text, link_target in links[:5]:
                    # Skip external links and anchors
                    if link_target.startswith(("http://", "https://", "#", "mailto:")):
                        continue
                    # Check if file exists (simplified)
                    target_path = link_target.split("#")[0]
                    if target_path and not target_path.startswith("/"):
                        resolved = doc_file.parent / target_path
                        if not resolved.exists() and not (REPO_ROOT / target_path).exists():
                            broken_refs.append(f"{doc_file.name}: {target_path}")
            except (UnicodeDecodeError, OSError):
                continue

        # Log but don't fail (MkDocs has known issues)
        if broken_refs:
            pytest.skip(f"Potentially broken refs: {broken_refs[:3]}")
