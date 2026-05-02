#!/usr/bin/env python3
"""
Validate Documentation Links

Purpose:
    Validates documentation_links

Usage:
    python scripts/validate_documentation_links.py [options]

    Examples:
    $ python scripts/validate_documentation_links.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def extract_markdown_links(content: str) -> list[dict[str, Any]]:
    """Extract all markdown links from content."""
    # Pattern: [text](url)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)

    links = []
    for text, url in matches:
        # Skip external URLs, fragments, mailto
        if url.startswith(('http://', 'https://', 'mailto:', '#')):
            continue

        # Remove fragment identifier if present
        url_without_fragment = url.split('#')[0]

        if url_without_fragment:  # Only process non-empty paths
            links.append({
                'text': text,
                'url': url,
                'url_without_fragment': url_without_fragment,
            })

    return links


def resolve_relative_path(source_file: Path, link_path: str) -> Path:
    """Resolve relative path from source file to linked file."""
    source_dir = source_file.parent
    return (source_dir / link_path).resolve()


def validate_documentation_links() -> int:
    """Validate all documentation links."""
    repo_root = Path('.')

    # Find all markdown files
    md_files = list(repo_root.rglob('*.md'))

    # Exclude certain directories
    exclude_patterns = [
        '.git',
        'node_modules',
        '.venv',
        'venv',
        '__pycache__',
    ]

    md_files = [
        f for f in md_files
        if not any(exclude in str(f) for exclude in exclude_patterns)
    ]

    print(f"📊 Validating {len(md_files)} markdown files...")

    broken_links = []
    total_links = 0

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            links = extract_markdown_links(content)
            total_links += len(links)

            for link in links:
                target_path = resolve_relative_path(md_file, link['url_without_fragment'])

                if not target_path.exists():
                    broken_links.append({
                        'source_file': str(md_file),
                        'link_text': link['text'],
                        'link_url': link['url'],
                        'resolved_path': str(target_path),
                    })

        except Exception as e:
            print(f"⚠️  Error processing {md_file}: {e}")

    print("\n📈 Validation Summary:")
    print(f"   Total markdown files: {len(md_files)}")
    print(f"   Total internal links checked: {total_links}")
    print(f"   Broken links found: {len(broken_links)}")

    if broken_links:
        print(f"\n❌ Broken Links ({len(broken_links)}):\n")

        # Group by source file
        by_file: dict[str, list[dict[str, Any]]] = {}
        for link in broken_links:
            source = link['source_file']
            if source not in by_file:
                by_file[source] = []
            by_file[source].append(link)

        for source_file, links in sorted(by_file.items()):
            print(f"**{source_file}**")
            for link in links:
                print(f"  ❌ [{link['link_text']}]({link['link_url']})")
                print(f"     Resolved to: {link['resolved_path']}")
            print()

        return 1
    print("\n✅ All internal links are valid!")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(validate_documentation_links())
