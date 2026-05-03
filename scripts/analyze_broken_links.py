#!/usr/bin/env python3
"""
Analyze broken internal links in documentation.
"""

import re
from pathlib import Path


def extract_links(content: str, filepath: Path) -> list[tuple[str, str, int]]:
    """Extract markdown links from content."""
    links = []
    for line_num, line in enumerate(content.split('\n'), 1):
        # Match markdown links: [text](url)
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
            link_text = match.group(1)
            link_url = match.group(2)
            links.append((link_text, link_url, line_num))
    return links


def check_link(link_url: str, source_file: Path, docs_root: Path) -> tuple[bool, str]:
    """Check if a link is valid."""
    # Skip external links
    if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
        return True, "external"

    # Handle anchors
    if '#' in link_url:
        link_path, anchor = link_url.split('#', 1)
        if not link_path:  # Same-file anchor
            return True, "anchor"
        link_url = link_path

    # Resolve relative path
    if link_url.startswith('/'):
        # Absolute from docs root
        target = docs_root / link_url.lstrip('/')
    else:
        # Relative to current file
        target = (source_file.parent / link_url).resolve()

    # Check if file exists
    if target.exists():
        return True, "valid"

    # Try with .md extension if missing
    if not target.suffix and (target.parent / f"{target.name}.md").exists():
        return True, "valid"

    return False, f"not_found: {target}"


def main():
    """Main execution."""
    root = Path.cwd()
    docs_dir = root / 'docs'

    if not docs_dir.exists():
        print(f"Error: docs directory not found at {docs_dir}")
        return

    print("Analyzing documentation links...")
    print(f"Docs directory: {docs_dir}")
    print()

    # Find all markdown files
    md_files = list(docs_dir.rglob('*.md'))
    print(f"Found {len(md_files)} markdown files")
    print()

    # Analyze links
    total_links = 0
    internal_links = 0
    broken_links = []

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            links = extract_links(content, md_file)

            for link_text, link_url, line_num in links:
                total_links += 1

                # Skip external links for internal link count
                if link_url.startswith(('http://', 'https://', 'mailto:')):
                    continue

                internal_links += 1
                is_valid, status = check_link(link_url, md_file, docs_dir)

                if not is_valid:
                    rel_path = md_file.relative_to(docs_dir)
                    broken_links.append({
                        'file': str(rel_path),
                        'line': line_num,
                        'text': link_text,
                        'url': link_url,
                        'status': status,
                    })
        except Exception as e:
            print(f"Warning: Could not analyze {md_file}: {e}")

    # Report results
    print("=" * 80)
    print("LINK ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Total Links Found:        {total_links}")
    print(f"Internal Links:           {internal_links}")
    print(f"Broken Internal Links:    {len(broken_links)}")
    print(f"Link Health Score:        {((internal_links - len(broken_links)) / max(1, internal_links)) * 100:.1f}%")
    print()

    if broken_links:
        print("=" * 80)
        print(f"BROKEN LINKS ({len(broken_links)} total)")
        print("=" * 80)

        # Group by file
        by_file = {}
        for link in broken_links:
            if link['file'] not in by_file:
                by_file[link['file']] = []
            by_file[link['file']].append(link)

        for filepath in sorted(by_file.keys()):
            print(f"\n{filepath}:")
            for link in by_file[filepath]:
                print(f"  Line {link['line']:4d}: [{link['text']}]({link['url']})")
                print(f"            Status: {link['status']}")

    # Save results
    report_path = root / 'BROKEN_LINKS_REPORT.md'
    with open(report_path, 'w') as f:
        f.write("# Broken Links Report\n\n")
        f.write(f"**Total Links:** {total_links}  \n")
        f.write(f"**Internal Links:** {internal_links}  \n")
        f.write(f"**Broken Links:** {len(broken_links)}  \n")
        f.write(f"**Link Health Score:** {((internal_links - len(broken_links)) / max(1, internal_links)) * 100:.1f}%  \n\n")

        if broken_links:
            f.write("## Broken Links by File\n\n")
            for filepath in sorted(by_file.keys()):
                f.write(f"### {filepath}\n\n")
                for link in by_file[filepath]:
                    f.write(f"- Line {link['line']}: `[{link['text']}]({link['url']})`\n")
                    f.write(f"  - Status: {link['status']}\n")
                f.write("\n")

    print(f"\n\n✓ Report saved to: {report_path}")


if __name__ == '__main__':
    main()
