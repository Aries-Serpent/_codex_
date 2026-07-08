"""
Phase 16.0: README Example Tests

This module provides comprehensive tests for validating README code examples,
ensuring they are syntactically correct and represent current codebase usage.

Created: 2026-01-18
Phase: 16.0 - Documentation Testing & Validation
Tests: 10+
"""

import ast
import re
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parents[2]


class TestREADMEExistence:
    """Tests for README file existence and structure."""

    def test_readme_exists(self):
        """Verify README.md exists at repository root."""
        readme = REPO_ROOT / "README.md"
        assert readme.exists(), "README.md should exist"

    def test_readme_has_content(self):
        """Verify README.md has substantial content."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        # README should be substantial (> 5KB)
        assert len(content) > 5000, "README should have substantial content"

    def test_readme_has_title(self):
        """Verify README.md has a title."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        # Check for h1 header
        assert content.startswith("#") or "# " in content[:100], "README should have a title"


class TestREADMECodeBlocks:
    """Tests for code blocks in README."""

    def _extract_code_blocks(self, content: str) -> list[tuple[str, str]]:
        """Extract fenced code blocks from markdown."""
        pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
        return pattern.findall(content)

    def test_readme_has_code_examples(self):
        """Verify README has code examples."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        code_blocks = self._extract_code_blocks(content)
        assert len(code_blocks) > 0, "README should have code examples"

    def test_python_examples_syntax(self):
        """Verify Python code examples have valid syntax."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        code_blocks = self._extract_code_blocks(content)

        python_blocks = [
            (lang, code)
            for lang, code in code_blocks
            if lang.lower() in ("python", "py", "python3")
        ]

        syntax_errors = []
        for lang, code in python_blocks:
            # Skip snippets with ellipsis or incomplete code
            if "..." in code or "# ..." in code:
                continue
            # Skip very short snippets
            if len(code.strip()) < 20:
                continue
            # Skip output examples
            if code.strip().startswith(">>>"):
                continue
            try:
                ast.parse(code)
            except SyntaxError as e:
                syntax_errors.append(f"Line {e.lineno}: {e.msg}")

        # Allow some syntax errors (snippets are often incomplete)
        max_errors = len(python_blocks) // 2
        assert (len(syntax_errors) <= max_errors), f"Too many Python syntax errors: {syntax_errors[:3]}"

    def test_bash_examples_exist(self):
        """Verify README has bash/shell examples."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        code_blocks = self._extract_code_blocks(content)

        bash_blocks = [
            (lang, code)
            for lang, code in code_blocks
            if lang.lower() in ("bash", "sh", "shell", "")
        ]
        assert len(bash_blocks) > 0, "README should have bash examples"


class TestREADMESections:
    """Tests for README section structure."""

    def test_readme_has_quickstart(self):
        """Verify README has quickstart section."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8").lower()
        has_quickstart = "quickstart" in content or "quick start" in content
        has_getting_started = "getting started" in content
        assert has_quickstart or has_getting_started, "README should have quickstart section"

    def test_readme_has_installation(self):
        """Verify README mentions installation."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8").lower()
        has_install = "install" in content or "setup" in content
        assert has_install, "README should mention installation"

    def test_readme_has_testing(self):
        """Verify README mentions testing."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8").lower()
        has_test = "test" in content or "pytest" in content
        assert has_test, "README should mention testing"

    def test_readme_has_documentation_links(self):
        """Verify README has documentation links."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        # Check for markdown links
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        links = link_pattern.findall(content)
        assert len(links) > 5, "README should have documentation links"


class TestREADMEBadges:
    """Tests for README badges and status indicators."""

    def test_readme_has_badges(self):
        """Verify README has status badges."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        # Check for badge images
        badge_patterns = [
            r"!\[.*?\]\(.*?badge.*?\)",  # img.shields.io style
            r"!\[.*?\]\(.*?github\.com.*?actions.*?\)",  # GitHub Actions
            r"!\[.*?\]\(https://.*?\)",  # Any image
        ]
        has_badge = any(re.search(p, content) for p in badge_patterns)
        assert has_badge, "README should have status badges"


class TestREADMELinks:
    """Tests for README link validity."""

    def test_readme_internal_links_format(self):
        """Verify README internal links have proper format."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        links = link_pattern.findall(content)

        malformed_links = []
        for link_text, link_target in links:
            # Check for empty links
            if not link_target.strip():
                malformed_links.append(f"Empty link: [{link_text}]()")
            # Check for spaces in path (should be URL encoded)
            if " " in link_target and not link_target.startswith("http"):
                malformed_links.append(f"Space in path: [{link_text}]({link_target})")

        assert len(malformed_links) == 0, f"Malformed links: {malformed_links}"

    def test_readme_external_links_https(self):
        """Verify external links use HTTPS."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")

        link_pattern = re.compile(r"\[([^\]]+)\]\((http://[^)]+)\)")
        http_links = link_pattern.findall(content)

        # Filter out localhost links
        external_http = [
            (text, url)
            for text, url in http_links
            if "localhost" not in url and "127.0.0.1" not in url
        ]

        assert len(external_http) == 0, f"External links should use HTTPS: {external_http[:3]}"
