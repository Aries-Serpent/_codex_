#!/usr/bin/env python3
"""
Add table of contents to long markdown documents.

Identifies markdown files > 2000 words and adds auto-generated TOC.
"""

import re
from pathlib import Path
from typing import Dict, List

class TOCGenerator:
    """Generate table of contents for markdown files."""

    def __init__(self, docs_dir: str = "docs", min_words: int = 2000):
        self.docs_dir = Path(docs_dir)
        self.min_words = min_words
        self.files_processed: int = 0
        self.tocs_added: int = 0

    def extract_headings(self, content: str) -> List[tuple]:
        """Extract headings from markdown content."""
        headings = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            match = re.match(r'^(#+)\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append((level, title, i))

        return headings

    def has_toc(self, content: str) -> bool:
        """Check if file already has a TOC marker."""
        return '## Table of Contents' in content or '## Contents' in content

    def generate_toc_markdown(self, headings: List[tuple]) -> str:
        """Generate TOC markdown."""
        if not headings:
            return ""

        toc_lines = ["## Table of Contents\n"]

        for level, title, _ in headings[1:]:  # Skip first H1
            indent = "  " * (level - 2)
            # Create link-friendly title
            link = title.lower().replace(' ', '-').replace('/', '').replace("'", "")
            link = re.sub(r'[^a-z0-9\-_]', '', link)
            toc_lines.append(indent + "- [" + title + "](#" + link + ")")

        return '\n'.join(toc_lines) + "\n"

    def count_words(self, content: str) -> int:
        """Count words in content."""
        # Remove code blocks
        content = re.sub(r'```[\s\S]*?```', '', content)
        # Remove HTML comments
        content = re.sub(r'<!--[\s\S]*?-->', '', content)
        # Count words
        words = content.split()
        return len(words)

    def process_file(self, file_path: Path) -> bool:
        """Process a single markdown file."""
        if not file_path.is_file() or file_path.suffix != '.md':
            return False

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return False

        self.files_processed += 1

        # Check if file is long enough
        word_count = self.count_words(content)
        if word_count < self.min_words:
            return False

        # Check if already has TOC
        if self.has_toc(content):
            return False

        # Extract headings
        headings = self.extract_headings(content)
        if len(headings) < 2:  # Need at least 2 headings
            return False

        # Generate TOC
        toc = self.generate_toc_markdown(headings)

        # Find insertion point (after first heading)
        lines = content.split('\n')
        insert_at = 0
        for i, line in enumerate(lines):
            if re.match(r'^#\s+', line):
                insert_at = i + 1
                break

        # Insert TOC
        lines.insert(insert_at + 1, toc)
        updated_content = '\n'.join(lines)

        # Save
        try:
            file_path.write_text(updated_content, encoding='utf-8')
            self.tocs_added += 1
            return True
        except OSError:
            return False

    def process_all(self) -> Dict:
        """Process all markdown files."""
        for file_path in self.docs_dir.rglob('*.md'):
            self.process_file(file_path)

        return {
            'files_processed': self.files_processed,
            'tocs_added': self.tocs_added,
            'min_words': self.min_words
        }

    def generate_report(self) -> str:
        """Generate TOC report."""
        stats = self.process_all()

        report = f"""# Table of Contents Addition Report

## Summary
- **Files Scanned:** {stats['files_processed']}
- **TOCs Added:** {stats['tocs_added']}
- **Minimum Word Count:** {stats['min_words']}

## Results
✅ Added table of contents to {stats['tocs_added']} long-form documents
✅ Each TOC links to all section headings for easy navigation
"""

        return report


if __name__ == '__main__':
    import sys
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    generator = TOCGenerator(docs_dir)
    stats = generator.process_all()

    print(generator.generate_report())
    print(f"\n✅ Added TOCs to {stats['tocs_added']} documents")
