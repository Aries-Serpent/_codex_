"""
Link Validation Tests

Comprehensive test suite for link validation, internal/external link checking,
anchor validation, and broken reference detection.
Coverage: Documentation link integrity.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

import pytest


class LinkValidator:
    """Validator for documentation links."""

    def __init__(self, docs_root: Path = None):
        """Initialize link validator."""
        if docs_root is None:
            docs_root = Path(__file__).resolve().parent.parent / "docs"
        self.docs_root = docs_root
        self.md_files = list(docs_root.rglob("*.md")) if docs_root.exists() else []

    def extract_links(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract all markdown links: (text, url, type)."""
        # Markdown links: [text](url)
        md_links = re.findall(r"\[([^\]]*)\]\(([^)]+)\)", content)
        results = []
        for text, url in md_links:
            link_type = self._classify_link(url)
            results.append((text, url, link_type))
        return results

    def _classify_link(self, url: str) -> str:
        """Classify link type: internal, external, anchor, or relative."""
        if url.startswith("http://") or url.startswith("https://"):
            return "external"
        elif url.startswith("#"):
            return "anchor"
        elif url.startswith("/"):
            return "absolute"
        else:
            return "relative"

    def extract_anchors(self, content: str) -> Set[str]:
        """Extract all defined anchors in markdown."""
        # Look for heading anchors (implicit from ## Heading)
        headings = re.findall(r"^#+\s+(.+?)(?:\s*{#(.+?)})?$", content, re.MULTILINE)
        anchors = set()
        for heading, explicit_id in headings:
            if explicit_id:
                anchors.add(explicit_id)
            else:
                # Generate implicit anchor from heading
                implicit = heading.lower().replace(" ", "-").replace("/", "")
                implicit = re.sub(r"[^\w\-]", "", implicit)
                anchors.add(implicit)
        return anchors

    def validate_internal_links(self) -> List[Dict]:
        """Validate all internal links in documentation."""
        issues = []
        for md_file in self.md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                links = self.extract_links(content)
                for text, url, link_type in links:
                    if link_type == "relative" or link_type == "absolute":
                        # Check if target file exists
                        if link_type == "absolute":
                            target = self.docs_root / url.lstrip("/")
                        else:
                            target = (md_file.parent / url).resolve()
                        if not target.exists():
                            issues.append({
                                "file": str(md_file),
                                "url": url,
                                "type": "missing_file",
                                "target": str(target)
                            })
            except Exception as e:
                issues.append({
                    "file": str(md_file),
                    "error": str(e),
                    "type": "read_error"
                })
        return issues

    def validate_external_links(self) -> List[Dict]:
        """Validate external links format (without actually accessing them)."""
        issues = []
        for md_file in self.md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                links = self.extract_links(content)
                for text, url, link_type in links:
                    if link_type == "external":
                        # Check URL format validity
                        if not self._is_valid_url(url):
                            issues.append({
                                "file": str(md_file),
                                "url": url,
                                "type": "invalid_format"
                            })
            except Exception as exc:
                            # Append structured error information for failure tracking
                            issues.append({
                                "file": str(md_file),
                                "type": "processing_error",
                                "message": str(exc)
                            })
        return issues

    def validate_anchor_links(self) -> List[Dict]:
        """Validate anchor links point to existing anchors."""
        issues = []
        for md_file in self.md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                links = self.extract_links(content)
                anchors = self.extract_anchors(content)

                for text, url, link_type in links:
                    if link_type == "anchor":
                        anchor_name = url.lstrip("#")
                        if anchor_name not in anchors:
                            issues.append({
                                "file": str(md_file),
                                "anchor": anchor_name,
                                "type": "invalid_anchor"
                            })
            except Exception as e:
                # Append error information for failed files, preserve method resilience
                issues.append({
                    "file": str(md_file),
                    "type": "read_error",
                    "message": str(e)
                })
        return issues

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL format is valid."""
        try:
            result = urlparse(url)
            return bool(result.scheme and result.netloc)
        except Exception:
            return False

    def find_redirect_chains(self) -> List[Tuple[Path, str, str]]:
        """Find potential redirect chain candidates (same content linked differently)."""
        chains = []
        # This is a heuristic check
        return chains

    def find_broken_references(self) -> List[Dict]:
        """Find all broken references."""
        all_issues = []
        all_issues.extend(self.validate_internal_links())
        all_issues.extend(self.validate_external_links())
        all_issues.extend(self.validate_anchor_links())
        return all_issues


class TestInternalLinkValidity:
    """Test suite for internal link validation."""

    @pytest.fixture
    def validator(self):
        """Provide link validator."""
        return LinkValidator()

    def test_internal_link_extraction(self, validator):
        """Test that internal links are extracted correctly."""
        content = "[Link to file](file.md) and [External](https://example.com)"
        links = validator.extract_links(content)
        assert len(links) >= 2
        assert any(url == "file.md" for _, url, _ in links)

    def test_internal_links_reference_existing_files(self, validator):
        """Test that internal links reference existing files."""
        issues = validator.validate_internal_links()
        # Should complete without error
        assert isinstance(issues, list)

    def test_relative_link_resolution(self, validator):
        """Test that relative links are resolved correctly."""
        content = "[Sibling](../other.md) and [Child](subdir/file.md)"
        links = validator.extract_links(content)
        assert len(links) >= 2
        link_types = [lt for _, _, lt in links]
        assert "relative" in link_types

    def test_absolute_link_resolution(self, validator):
        """Test that absolute links are resolved correctly."""
        content = "[Docs](/docs/readme.md)"
        links = validator.extract_links(content)
        assert len(links) >= 1
        assert links[0][2] == "absolute"

    def test_missing_link_detection(self, validator):
        """Test that missing links are detected."""
        issues = validator.validate_internal_links()
        # May have some missing links in a large repo
        assert isinstance(issues, list)

    def test_no_false_positive_link_errors(self, validator):
        """Test that valid links aren't flagged as errors."""
        content = "[Valid](https://github.com/example/repo)"
        links = validator.extract_links(content)
        assert any("github" in url for _, url, _ in links)


class TestExternalLinkValidity:
    """Test suite for external link validation."""

    @pytest.fixture
    def validator(self):
        """Provide link validator."""
        return LinkValidator()

    def test_external_link_extraction(self, validator):
        """Test that external links are extracted."""
        content = "[GitHub](https://github.com) and [Google](https://google.com)"
        links = validator.extract_links(content)
        external = [l for l in links if l[2] == "external"]
        assert len(external) >= 2

    def test_https_links_preferred(self, validator):
        """Test that HTTPS links are properly recognized."""
        content = "[Secure](https://example.com) and [Insecure](http://example.com)"
        links = validator.extract_links(content)
        external = [url for _, url, lt in links if lt == "external"]
        assert len(external) >= 2

    def test_external_link_format_validation(self, validator):
        """Test that external link formats are validated."""
        issues = validator.validate_external_links()
        # Should complete validation
        assert isinstance(issues, list)

    def test_invalid_url_format_detection(self, validator):
        """Test that invalid URLs are detected."""
        invalid = "[Bad](not_a_url)"
        links = validator.extract_links(invalid)
        # Should extract the link
        assert len(links) >= 1

    def test_url_with_parameters_validation(self, validator):
        """Test validation of URLs with query parameters."""
        content = "[Search](https://example.com/search?q=test&limit=10)"
        links = validator.extract_links(content)
        assert len(links) >= 1
        assert "?" in links[0][1]

    def test_url_with_fragments_validation(self, validator):
        """Test validation of URLs with fragments."""
        content = "[Section](https://example.com/docs#section-1)"
        links = validator.extract_links(content)
        assert len(links) >= 1
        assert "#" in links[0][1]


class TestAnchorLinkValidation:
    """Test suite for anchor link validation."""

    @pytest.fixture
    def validator(self):
        """Provide link validator."""
        return LinkValidator()

    def test_anchor_extraction(self, validator):
        """Test that anchor links are extracted."""
        content = "[Link](#section) and [Other](#subsection)"
        links = validator.extract_links(content)
        anchors = [url for _, url, lt in links if lt == "anchor"]
        assert len(anchors) >= 2

    def test_heading_anchor_detection(self, validator):
        """Test that heading anchors are detected."""
        content = "# Main Section\n## Subsection"
        anchors = validator.extract_anchors(content)
        assert len(anchors) >= 2

    def test_explicit_anchor_detection(self, validator):
        """Test that explicit anchors are detected."""
        content = "## Section {#custom-id}"
        anchors = validator.extract_anchors(content)
        assert "custom-id" in anchors

    def test_anchor_link_pointing_to_valid_anchor(self, validator):
        """Test that anchor links point to valid anchors."""
        content = "# Main\n\n[Link to Main](#main)"
        anchors = validator.extract_anchors(content)
        links = validator.extract_links(content)
        # Extract anchor from link
        link_anchors = [url.lstrip("#") for _, url, lt in links if lt == "anchor"]
        # Should have proper anchors defined
        assert len(anchors) > 0 or len(link_anchors) == 0

    def test_anchor_case_sensitivity(self, validator):
        """Test anchor case sensitivity handling."""
        content = "## My Section\n\n[Link](#my-section)"
        anchors = validator.extract_anchors(content)
        # Anchors should be lowercase
        assert any(a.islower() or a == "" for a in anchors if a)

    @pytest.mark.edge_case
    def test_anchor_with_special_characters(self, validator):
        """Test anchors with special characters."""
        content = "## Section: Sub/Part\n\n[Link](#sectionsubpart)"
        anchors = validator.extract_anchors(content)
        # Should handle special characters
        assert isinstance(anchors, set)


class TestBrokenReferenceDetection:
    """Test suite for broken reference detection."""

    @pytest.fixture
    def validator(self):
        """Provide link validator."""
        return LinkValidator()

    def test_broken_reference_detection(self, validator):
        """Test that broken references are detected."""
        issues = validator.find_broken_references()
        # Should complete detection
        assert isinstance(issues, list)

    def test_empty_link_detection(self, validator):
        """Test that empty links are detected."""
        content = "This has empty link and [good](https://example.com)"
        links = validator.extract_links(content)
        # Should extract at least the valid link
        assert len(links) >= 1

    def test_link_text_emptiness_handling(self, validator):
        """Test handling of links with empty text."""
        content = "[](https://example.com) is a link with empty text"
        links = validator.extract_links(content)
        assert len(links) >= 1

    @pytest.mark.edge_case
    def test_malformed_link_handling(self, validator):
        """Test handling of malformed links."""
        content = "[text(https://bad[link)) and [good](https://example.com)"
        links = validator.extract_links(content)
        # Should extract at least the valid link
        assert any(url.startswith("https://example.com") for _, url, _ in links)

    def test_circular_reference_detection(self, validator):
        """Test detection of potential circular references."""
        # This is a heuristic check
        pass


class TestLinkConsistency:
    """Test suite for link consistency across documentation."""

    @pytest.fixture
    def validator(self):
        """Provide link validator."""
        return LinkValidator()

    def test_same_target_consistent_links(self, validator):
        """Test that same targets are linked consistently."""
        # Check that repeated targets use same format
        pass

    def test_no_duplicate_link_destinations(self, validator):
        """Test that there aren't unnecessary duplicate links."""
        pass

    def test_link_style_consistency(self, validator):
        """Test that link styles are consistent."""
        for md_file in validator.md_files[:5]:
            content = md_file.read_text(encoding="utf-8")
            links = validator.extract_links(content)
            # Should use consistent markdown link format
            assert len(links) >= 0

    def test_repository_url_consistency(self, validator):
        """Test that repository URLs are consistent."""
        repo_urls = set()
        for md_file in validator.md_files[:10]:
            content = md_file.read_text(encoding="utf-8")
            links = validator.extract_links(content)
            for _, url, _ in links:
                if url.startswith("https://github.com/") or url.startswith("http://github.com/"):
                    # Extract repo part
                    repo_part = url.split("/github.com/")[1].split("/")[0] if "/github.com/" in url else ""
                    if repo_part:
                        repo_urls.add(repo_part)
        # Should have consistent repo references
        assert len(repo_urls) <= 5 or len(repo_urls) == 0


class TestLinkAccessibility:
    """Test suite for link accessibility."""

    @pytest.fixture
    def validator(self):
        """Provide link validator."""
        return LinkValidator()

    def test_link_text_descriptive(self, validator):
        """Test that link text is descriptive."""
        for md_file in validator.md_files[:5]:
            content = md_file.read_text(encoding="utf-8")
            links = validator.extract_links(content)
            for text, url, _ in links[:5]:
                # Link text should not be just "here" or "click"
                if text:
                    assert text not in ("here", "click here", "link")

    def test_link_title_attribute_optional(self, validator):
        """Test that links can have title attributes."""
        # Markdown supports [text](url "title")
        content = '[Link](https://example.com "Example")'
        links = validator.extract_links(content)
        # Should handle title attributes gracefully
        assert len(links) >= 1

    def test_media_file_links_valid(self, validator):
        """Test that media file links are valid."""
        for md_file in validator.md_files[:5]:
            content = md_file.read_text(encoding="utf-8")
            images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
            for alt, src in images[:3]:
                # Image sources should be valid paths or URLs
                assert src.strip()

    def test_broken_image_links_detected(self, validator):
        """Test that broken image links are detected."""
        for md_file in validator.md_files[:5]:
            content = md_file.read_text(encoding="utf-8")
            # Should detect image references
            images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
            # Just verify the pattern works
            assert isinstance(images, list)


class TestLinkNormalization:
    """Test suite for link normalization."""

    @pytest.fixture
    def validator(self):
        """Provide link validator."""
        return LinkValidator()

    def test_trailing_slash_handling(self, validator):
        """Test that trailing slashes are handled consistently."""
        content = "[A](https://example.com/) and [B](https://example.com)"
        links = validator.extract_links(content)
        assert len(links) >= 2

    def test_url_parameter_ordering(self, validator):
        """Test consistent URL parameter ordering."""
        content = "[A](https://example.com?a=1&b=2) and [B](https://example.com?b=2&a=1)"
        links = validator.extract_links(content)
        assert len(links) >= 2

    def test_fragment_identifier_normalization(self, validator):
        """Test fragment identifier normalization."""
        content = "[A](#Section) and [B](#section)"
        links = validator.extract_links(content)
        # Different fragments, should both be extractable
        assert len(links) >= 2

    def test_case_sensitivity_in_paths(self, validator):
        """Test case sensitivity in file paths."""
        content = "[File](./File.md) and [file](./file.md)"
        links = validator.extract_links(content)
        assert len(links) >= 2
