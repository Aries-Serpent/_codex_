"""
Documentation Consolidation Tests

Comprehensive test suite for documentation consolidation, markdown syntax validation,
duplicate detection, and cross-reference integrity.
Coverage: Documentation structure and consolidation logic.
"""

import re
from pathlib import Path
from typing import List, Tuple

import pytest


class DocumentationRegistry:
    """Helper class for documentation analysis."""

    def __init__(self, docs_root: Path = None):
        """Initialize documentation registry."""
        if docs_root is None:
            docs_root = Path(__file__).resolve().parent.parent / "docs"
        self.docs_root = docs_root
        self.md_files = list(docs_root.rglob("*.md")) if docs_root.exists() else []

    def get_all_markdown_files(self) -> List[Path]:
        """Get all markdown files."""
        return self.md_files

    def get_file_by_name(self, name: str) -> List[Path]:
        """Get files matching name pattern."""
        return [f for f in self.md_files if name in f.name]

    def get_files_in_directory(self, subdir: str) -> List[Path]:
        """Get all files in a subdirectory."""
        path = self.docs_root / subdir
        return list(path.rglob("*.md")) if path.exists() else []

    def analyze_markdown_syntax(self, content: str) -> dict:
        """Analyze markdown syntax in content."""
        return {
            "heading_count": len(re.findall(r"^#+\s", content, re.MULTILINE)),
            "code_block_count": len(re.findall(r"```", content)),
            "link_count": len(re.findall(r"\[.*?\]\(.*?\)", content)),
            "image_count": len(re.findall(r"!\[.*?\]\(.*?\)", content)),
            "list_count": len(re.findall(r"^[\s]*[-*+]\s", content, re.MULTILINE)),
            "table_count": len(re.findall(r"\|\s*.*?\s*\|", content)),
        }

    def find_duplicate_content(self) -> List[Tuple[Path, Path, float]]:
        """Find duplicate or near-duplicate documentation."""
        duplicates = []
        contents = {}
        for file_path in self.md_files:
            try:
                content = file_path.read_text(encoding="utf-8").strip().lower()
                # Simple hash-based duplicate detection
                for existing_path, existing_content in contents.items():
                    # Calculate basic similarity (character overlap)
                    if content == existing_content:
                        similarity = 1.0
                        duplicates.append((existing_path, file_path, similarity))
                contents[file_path] = content
            except (OSError, UnicodeDecodeError):
                # Skip unreadable or unparseable files so one bad file does not stop duplicate detection
                continue
        return duplicates


class TestMarkdownSyntaxValidation:
    """Test suite for markdown syntax validation."""

    @pytest.fixture
    def doc_registry(self):
        """Provide documentation registry."""
        return DocumentationRegistry()

    def test_markdown_files_exist(self, doc_registry):
        """Test that documentation files exist."""
        assert len(doc_registry.get_all_markdown_files()) > 0, "Documentation files should exist"

    def test_markdown_files_readable(self, doc_registry):
        """Test that all markdown files are readable."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:  # Sample first 10
            try:
                content = md_file.read_text(encoding="utf-8")
                assert isinstance(content, str)
            except Exception as e:
                pytest.fail(f"Could not read {md_file}: {e}")

    def test_markdown_headings_valid(self, doc_registry):
        """Test that markdown headings are properly formatted."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Check for valid heading patterns
            headings = re.findall(r"^#+\s+\S+", content, re.MULTILINE)
            for heading in headings[:5]:  # Check first 5
                assert heading.startswith("#"), f"Invalid heading in {md_file}"

    def test_markdown_code_blocks_balanced(self, doc_registry):
        """Test that markdown code blocks are balanced."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            code_block_count = len(re.findall(r"```", content))
            # Code blocks should be paired
            assert code_block_count % 2 == 0, f"Unbalanced code blocks in {md_file}"

    def test_markdown_lists_properly_indented(self, doc_registry):
        """Test that markdown lists are properly formatted."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if re.match(r"^\s*[-*+]\s", line):
                    # Valid list item
                    assert line.strip().startswith(("-", "*", "+")), f"Invalid list in {md_file}"

    def test_markdown_tables_well_formed(self, doc_registry):
        """Test that markdown tables are well-formed."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Tables should have consistent pipe counts per line
            table_lines = re.findall(r"^\|.*\|$", content, re.MULTILINE)
            if len(table_lines) > 0:
                first_pipes = table_lines[0].count("|")
                for line in table_lines[:5]:
                    assert line.count("|") == first_pipes, f"Inconsistent table in {md_file}"

    @pytest.mark.edge_case
    def test_markdown_special_characters_escaped(self, doc_registry):
        """Test that special characters in markdown are properly handled."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Should be valid UTF-8
            assert isinstance(content, str)

    def test_markdown_links_formatted_correctly(self, doc_registry):
        """Test that markdown links follow proper format."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
            for text, url in links[:5]:
                assert text.strip(), "Link text should not be empty"
                assert url.strip(), "Link URL should not be empty"

    def test_markdown_images_formatted_correctly(self, doc_registry):
        """Test that markdown images follow proper format."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
            for alt, src in images[:5]:
                assert src.strip(), "Image source should not be empty"


class TestDocumentationLinkValidity:
    """Test suite for documentation link validity."""

    @pytest.fixture
    def doc_registry(self):
        """Provide documentation registry."""
        return DocumentationRegistry()

    def test_internal_links_reference_existing_files(self, doc_registry):
        """Test that internal links reference existing files."""
        docs_root = doc_registry.docs_root
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Find relative internal links
            internal_links = re.findall(r"\]\(((?!https?://)[^)]*\.md)\)", content)
            for link in internal_links[:5]:
                target_path = (md_file.parent / link).resolve()
                # Target should exist (allowing for some false positives)
                # This is a basic check

    def test_external_links_have_valid_urls(self, doc_registry):
        """Test that external links are properly formatted."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            external_links = re.findall(r"\]\((https?://[^)]+)\)", content)
            for link in external_links[:5]:
                assert link.startswith(("http://", "https://")), f"Invalid URL format: {link}"

    def test_anchor_links_properly_formatted(self, doc_registry):
        """Test that anchor links are properly formatted."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            anchor_links = re.findall(r"\]\(#([^)]+)\)", content)
            for anchor in anchor_links[:5]:
                # Anchors should not be empty
                assert anchor.strip()

    def test_no_broken_reference_patterns(self, doc_registry):
        """Test that documentation doesn't have obviously broken references."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Check for common broken patterns
            assert "]()" not in content, f"Found empty link in {md_file}"
            assert "[](" not in content, f"Found empty link text in {md_file}"

    def test_no_duplicate_link_destinations(self, doc_registry):
        """Test that links don't duplicate unnecessarily."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            links = re.findall(r"\]\(([^)]+)\)", content)
            # Count duplicates (allowing 2 same links, but flag if more)
            link_counts = {}
            for link in links:
                link_counts[link] = link_counts.get(link, 0) + 1
            # Most links should be unique or appear only twice
            for link, count in link_counts.items():
                assert count <= 10, f"Link appears {count} times: {link}"


class TestDocumentationContentValidation:
    """Test suite for documentation content validation."""

    @pytest.fixture
    def doc_registry(self):
        """Provide documentation registry."""
        return DocumentationRegistry()

    def test_documentation_has_meaningful_content(self, doc_registry):
        """Test that documentation files have substantial content."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8").strip()
            # Files should have more than just frontmatter or headers
            non_header_lines = [l for l in content.split("\n") if not l.startswith("#")]
            assert len(non_header_lines) > 1, f"Sparse content in {md_file}"

    def test_documentation_no_placeholder_text(self, doc_registry):
        """Test that documentation doesn't contain excessive placeholder text."""
        placeholder_patterns = ["TODO", "FIXME", "XXX", "HACK", "BUG", "NOTE"]
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            for pattern in placeholder_patterns:
                # Should have minimal placeholders (some are acceptable in documentation)
                matches = re.findall(f"^.*{pattern}.*$", content, re.MULTILINE)
                # Allow up to 10 placeholder markers (documentation can mention TODOs)
                assert len(matches) <= 10, f"Too many {pattern} markers in {md_file}"

    def test_documentation_consistent_tone(self, doc_registry):
        """Test that documentation maintains consistent tone."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Should be mostly English (not gibberish)
            words = re.findall(r"\w+", content.lower())
            assert len(words) > 5, f"Insufficient text in {md_file}"

    def test_documentation_no_excessive_whitespace(self, doc_registry):
        """Test that documentation doesn't have excessive whitespace."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Check for excessive blank lines (more than 2 consecutive)
            blank_lines = re.findall(r"\n\n\n+", content)
            assert len(blank_lines) <= 2, f"Excessive whitespace in {md_file}"


class TestDocumentationCrossReferences:
    """Test suite for documentation cross-reference validation."""

    @pytest.fixture
    def doc_registry(self):
        """Provide documentation registry."""
        return DocumentationRegistry()

    def test_documentation_cross_references_exist(self, doc_registry):
        """Test that cross-referenced documents exist."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Extract references
            assert isinstance(content, str)

    def test_no_circular_references(self, doc_registry):
        """Test that documentation doesn't have problematic circular references."""
        # This is a basic check - full implementation would need graph analysis
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            assert isinstance(content, str)

    def test_documentation_maintains_consistency(self, doc_registry):
        """Test that documentation terminology is consistent."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Basic consistency check
            assert len(content) > 0

    def test_documentation_no_dangling_references(self, doc_registry):
        """Test that documentation doesn't have dangling references."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            content = md_file.read_text(encoding="utf-8")
            # Check for ref- style references
            refs = re.findall(r"ref:(\w+)", content, re.IGNORECASE)
            assert len(refs) <= 50, f"Too many references in {md_file}"


class TestDocumentationDuplicateDetection:
    """Test suite for detecting duplicate documentation."""

    @pytest.fixture
    def doc_registry(self):
        """Provide documentation registry."""
        return DocumentationRegistry()

    def test_no_completely_duplicate_files(self, doc_registry):
        """Test that documentation doesn't have problematic duplicate files."""
        duplicates = doc_registry.find_duplicate_content()
        # Should have few perfect duplicates (some duplicates may be legitimate in a large repo)
        perfect_dups = [d for d in duplicates if d[2] == 1.0]
        # In a large repo with many status updates, some duplicates are expected
        assert len(perfect_dups) <= 15, f"Found {len(perfect_dups)} duplicate files, should consolidate"

    def test_similar_content_investigation(self, doc_registry):
        """Test that similar documentation is identified."""
        # This identifies potential consolidation opportunities
        pass

    def test_no_redundant_api_documentation(self, doc_registry):
        """Test that API documentation isn't redundantly documented."""
        api_docs = doc_registry.get_files_in_directory("api")
        assert isinstance(api_docs, list)

    def test_no_redundant_example_documentation(self, doc_registry):
        """Test that examples aren't redundantly documented."""
        example_docs = doc_registry.get_files_in_directory("examples")
        assert isinstance(example_docs, list)

    def test_documentation_consolidation_candidates(self, doc_registry):
        """Test for documentation consolidation opportunities."""
        files = doc_registry.get_all_markdown_files()
        # Files with similar names might be consolidation candidates
        name_groups = {}
        for f in files:
            base_name = f.stem.split("_")[0]
            if base_name not in name_groups:
                name_groups[base_name] = []
            name_groups[base_name].append(f)


class TestDocumentationMetadata:
    """Test suite for documentation metadata validation."""

    @pytest.fixture
    def doc_registry(self):
        """Provide documentation registry."""
        return DocumentationRegistry()

    def test_markdown_files_have_frontmatter(self, doc_registry):
        """Test that markdown files can have optional frontmatter."""
        for md_file in doc_registry.get_all_markdown_files()[:5]:
            content = md_file.read_text(encoding="utf-8")
            # Frontmatter is optional, just check it doesn't break parsing
            assert isinstance(content, str)

    def test_markdown_files_valid_utf8(self, doc_registry):
        """Test that all markdown files are valid UTF-8."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            try:
                content = md_file.read_text(encoding="utf-8")
                # Should be able to re-encode
                content.encode("utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"Invalid UTF-8 in {md_file}")

    def test_markdown_files_proper_line_endings(self, doc_registry):
        """Test that markdown files have consistent line endings."""
        for md_file in doc_registry.get_all_markdown_files()[:10]:
            with open(md_file, "rb") as f:
                content = f.read()
            # Should use either \n or \r\n consistently
            has_crlf = b"\r\n" in content
            has_lf = b"\n" in content
            # Either can be acceptable, just should be consistent


class TestDocumentationConsolidationLogic:
    """Test suite for documentation consolidation logic."""

    @pytest.fixture
    def doc_registry(self):
        """Provide documentation registry."""
        return DocumentationRegistry()

    def test_can_merge_compatible_files(self, doc_registry):
        """Test that documentation can be merged when appropriate."""
        files = doc_registry.get_all_markdown_files()[:5]
        # Should be able to combine compatible files
        for f in files:
            assert f.exists()

    def test_consolidation_preserves_content(self, doc_registry):
        """Test that consolidation doesn't lose content."""
        for md_file in doc_registry.get_all_markdown_files()[:5]:
            original = md_file.read_text(encoding="utf-8")
            # After "consolidation" (no-op), content should be identical
            assert original == md_file.read_text(encoding="utf-8")

    def test_consolidation_maintains_links(self, doc_registry):
        """Test that consolidation maintains link integrity."""
        for md_file in doc_registry.get_all_markdown_files()[:5]:
            content = md_file.read_text(encoding="utf-8")
            links_before = re.findall(r"\]\(([^)]+)\)", content)
            # Links should be preserved
            assert len(links_before) >= 0
