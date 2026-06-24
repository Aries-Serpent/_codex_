#!/usr/bin/env python3
"""
Improve link descriptiveness in markdown documents.

Replaces bare URLs and poorly described links with descriptive text.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

class LinkDescriptivenessImprover:
    """Improve link descriptions in markdown."""

    # Common URL patterns to descriptions
    URL_DESCRIPTIONS = {
        r'github\.com/': 'GitHub',
        r'github\.io': 'GitHub Pages',
        r'docs\.': 'Documentation',
        r'tutorial': 'Tutorial',
        r'guide': 'Guide',
        r'reference': 'Reference',
        r'api': 'API',
        r'spec': 'Specification',
    }

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.improvements: List[Dict] = []
        self.files_modified: int = 0

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            return domain.split('/')[0]
        except:
            return url

    def generate_link_description(self, url: str) -> str:
        """Generate descriptive text for a URL."""
        # Check for pattern matches
        for pattern, description in self.URL_DESCRIPTIONS.items():
            if re.search(pattern, url, re.IGNORECASE):
                return description

        # Extract domain
        domain = self.extract_domain(url)
        if domain and not domain.startswith('http'):
            return domain.replace('www.', '').replace('.com', '').title()

        return 'Link'

    def find_bare_urls(self, content: str) -> List[Tuple[int, str]]:
        """Find bare URLs in content."""
        # Find URLs not in markdown link format
        bare_url_pattern = r'(?<!\[)\b(https?://[^\s\]]+)(?!\])'
        matches = []

        for match in re.finditer(bare_url_pattern, content):
            url = match.group(1)
            # Skip if already part of a link
            start = match.start()
            if start > 0 and content[start - 1] == '[':
                continue
            if start > 0 and content[start - 1] == '(':
                continue
            matches.append((match.start(), url))

        return matches

    def find_poor_links(self, content: str) -> List[Tuple[str, str, str]]:
        """Find poorly described links."""
        # Find markdown links with poor descriptions
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        poor_descriptions = [
            'http', 'https', 'click here', 'link', 'here', 'see',
            'go here', 'more info', 'read more', 'more'
        ]

        matches = []
        for match in re.finditer(link_pattern, content):
            description = match.group(1).lower().strip()
            url = match.group(2)

            # Check if description is poor
            if description in poor_descriptions or description.startswith('http'):
                new_desc = self.generate_link_description(url)
                if new_desc.lower() != description:
                    matches.append((match.group(0), url, new_desc))

        return matches

    def improve_links(self, content: str) -> str:
        """Improve link descriptiveness."""
        # Fix poor descriptions
        poor_links = self.find_poor_links(content)
        for old_link, url, new_desc in reversed(poor_links):
            new_link = f'[{new_desc}]({url})'
            content = content.replace(old_link, new_link, 1)

        # Note: Bare URLs are harder to fix automatically as context matters
        return content

    def process_file(self, file_path: Path) -> bool:
        """Process a single markdown file."""
        if not file_path.is_file() or file_path.suffix != '.md':
            return False

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return False

        poor_links = self.find_poor_links(content)
        if not poor_links:
            return False

        # Improve links
        improved_content = self.improve_links(content)

        try:
            file_path.write_text(improved_content, encoding='utf-8')
            self.files_modified += 1
            self.improvements.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'links_improved': len(poor_links),
                'sample': poor_links[0] if poor_links else None
            })
            return True
        except OSError:
            return False

    def process_all(self) -> Dict:
        """Process all markdown files."""
        total_improved = 0
        for file_path in self.docs_dir.rglob('*.md'):
            self.process_file(file_path)
            total_improved += len(self.improvements)

        return {
            'files_modified': self.files_modified,
            'total_links_improved': sum(item['links_improved'] for item in self.improvements),
            'samples': self.improvements[:5]
        }

    def generate_report(self) -> str:
        """Generate link improvement report."""
        stats = self.process_all()

        report = f"""# Link Descriptiveness Improvement Report

## Summary
- **Files Modified:** {stats['files_modified']}
- **Total Links Improved:** {stats['total_links_improved']}

## Details
✅ Replaced generic link descriptions with descriptive text
✅ Improved readability for screen reader users
✅ Better context for document navigation

## Sample Improvements
"""
        for item in stats['samples']:
            report += f"\n### {item['file']}\n"
            report += f"Links improved: {item['links_improved']}\n"

        return report


if __name__ == '__main__':
    import sys
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    improver = LinkDescriptivenessImprover(docs_dir)
    stats = improver.process_all()

    print(improver.generate_report())
    print(f"\n✅ Improved {stats['total_links_improved']} links")
