"""
Markdown document parsing and extraction.

Classes:
  - MarkdownParser: Parse markdown files into sections and metadata
  - CodeBlockExtractor: Extract and identify code blocks
  - MetadataExtractor: Parse YAML frontmatter and inline directives
"""

import re
from typing import Any, Dict, List, Tuple


class MarkdownParser:
    """Parse markdown files into sections and blocks.

    Supports:
      - H1-H6 heading hierarchy
      - Code blocks with language tags
      - Lists and tables
      - Inline metadata directives
    """

    def __init__(self):
        # Heading pattern: # Title
        self.heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        # Code block pattern: ```language ... ```
        self.code_block_pattern = re.compile(r"```(\w+)?\n(.*?)\n```", re.MULTILINE | re.DOTALL)

    def parse_file(self, filepath: str) -> Tuple[Dict, List[Dict]]:
        """Parse markdown file into sections and metadata.

        Returns:
            (metadata, sections_list)
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = MetadataExtractor.extract_frontmatter(content)
        sections = self._extract_sections(content)

        return metadata, sections

    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections from markdown content."""
        sections = []
        heading_matches = list(self.heading_pattern.finditer(content))

        for idx, match in enumerate(heading_matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start_pos = match.start()
            end_pos = (
                heading_matches[idx + 1].start() if idx + 1 < len(heading_matches) else len(content)
            )

            section_content = content[match.start() : end_pos]

            section = {
                "level": level,
                "title": title,
                "content": section_content,
                "anchor": self._generate_anchor(title),
                "position": idx,
            }

            sections.append(section)

        return sections

    def _generate_anchor(self, title: str) -> str:
        """Generate anchor from section title."""
        anchor = title.lower()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"[-\s]+", "-", anchor)
        return anchor.strip("-")


class CodeBlockExtractor:
    """Extract code blocks from markdown content.

    Identifies:
      - Language tags
      - Executable vs non-executable
      - Line counts
      - Special markers (# tested, # unsafe, etc.)
    """

    def __init__(self):
        self.code_block_pattern = re.compile(r"```(\w+)?\n(.*?)\n```", re.MULTILINE | re.DOTALL)

    def extract_blocks(self, content: str) -> List[Dict]:
        """Extract all code blocks from content."""
        blocks = []

        for match in self.code_block_pattern.finditer(content):
            language = match.group(1) or "plaintext"
            code = match.group(2)

            block = {
                "language": language,
                "code": code,
                "line_count": len(code.split("\n")),
                "executable": self._is_executable(language),
                "tested": self._has_marker(code, "tested"),
                "unsafe": self._has_marker(code, "unsafe"),
            }

            blocks.append(block)

        return blocks

    @staticmethod
    def _is_executable(language: str) -> bool:
        """Check if code block is in an executable language."""
        executable_langs = {
            "python",
            "bash",
            "sh",
            "shell",
            "javascript",
            "js",
            "go",
            "rust",
            "java",
            "cpp",
            "c",
            "ruby",
            "php",
        }
        return language.lower() in executable_langs

    @staticmethod
    def _has_marker(code: str, marker: str) -> bool:
        """Check if code has special marker in comment."""
        # Look for markers like # tested, # unsafe in first 3 lines
        lines = code.split("\n")[:3]
        marker_pattern = f"# {marker}"
        return any(marker_pattern in line for line in lines)


class MetadataExtractor:
    """Extract metadata from markdown documents.

    Handles:
      - YAML frontmatter (--- delimited)
      - Inline directives (!directive: value)
      - Custom fields
    """

    FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
    DIRECTIVE_PATTERN = re.compile(r"!(\w+):\s*(.+)$", re.MULTILINE)

    @classmethod
    def extract_frontmatter(cls, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        match = cls.FRONTMATTER_PATTERN.match(content)
        if not match:
            return {}

        # Simple YAML parsing (enough for basic cases)
        frontmatter_text = match.group(1)
        metadata = {}

        for line in frontmatter_text.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata

    @classmethod
    def extract_directives(cls, content: str) -> Dict[str, Any]:
        """Extract inline directives from markdown."""
        directives: dict[str, list[str]] = {}

        for match in cls.DIRECTIVE_PATTERN.finditer(content):
            key = match.group(1)
            value = match.group(2)
            if key not in directives:
                directives[key] = []
            directives[key].append(value)

        return directives

    @classmethod
    def extract_links(cls, content: str) -> List[Dict]:
        """Extract links from markdown content."""
        # Markdown links: [text](url)
        markdown_pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        links = []

        for match in markdown_pattern.finditer(content):
            link = {
                "text": match.group(1),
                "url": match.group(2),
                "type": cls._classify_link(match.group(2)),
            }
            links.append(link)

        return links

    @staticmethod
    def _classify_link(url: str) -> str:
        """Classify link type."""
        if url.startswith("http://") or url.startswith("https://"):
            return "external"
        elif url.startswith("#"):
            return "anchor"
        else:
            return "internal"

    @classmethod
    def extract_images(cls, content: str) -> List[Dict]:
        """Extract image references from markdown."""
        # Markdown images: ![alt](url)
        image_pattern = re.compile(r"!\[([^\]]*)\]\(([^\)]+)\)")
        images = []

        for match in image_pattern.finditer(content):
            img = {
                "alt_text": match.group(1),
                "url": match.group(2),
            }
            images.append(img)

        return images

    @classmethod
    def extract_metadata_summary(cls, content: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from document."""
        return {
            "frontmatter": cls.extract_frontmatter(content),
            "directives": cls.extract_directives(content),
            "links": cls.extract_links(content),
            "images": cls.extract_images(content),
            "word_count": len(content.split()),
            "heading_count": len(re.findall(r"^#+\s", content, re.MULTILINE)),
            "code_block_count": len(re.findall(r"```", content)) // 2,
        }
