#!/usr/bin/env python3
"""
Fix broken documentation links.

This script identifies and fixes broken internal links in documentation files.
"""

import datetime
import re
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent
DOCS_ROOT = REPO_ROOT / "docs"


class BrokenLink:
    """Represents a broken link."""

    def __init__(self, file_path: Path, line_num: int, link_text: str, link_target: str, reason: str):
        self.file_path = file_path
        self.line_num = line_num
        self.link_text = link_text
        self.link_target = link_target
        self.reason = reason

    def __repr__(self):
        return f"{self.file_path.relative_to(REPO_ROOT)}:{self.line_num} -> {self.link_target} ({self.reason})"


def find_markdown_links(content: str) -> list[tuple[str, str, int]]:
    """Extract all markdown links from content.

    Returns: List of (link_text, link_target, line_number)
    """
    links = []
    lines = content.split('\n')

    # Match markdown links: [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

    for line_num, line in enumerate(lines, 1):
        for match in link_pattern.finditer(line):
            link_text = match.group(1)
            link_target = match.group(2)
            links.append((link_text, link_target, line_num))

    return links


def is_external_link(link: str) -> bool:
    """Check if link is external (http/https)."""
    return link.startswith(('http://', 'https://'))


def resolve_relative_path(base_file: Path, link_target: str) -> Path:
    """Resolve relative path from base file to target."""
    # Remove anchor if present
    if '#' in link_target:
        link_target = link_target.split('#')[0]

    if not link_target:  # Just an anchor
        return base_file

    base_dir = base_file.parent
    return (base_dir / link_target).resolve()



def check_file_exists(file_path: Path, link_target: str) -> tuple[bool, str]:
    """Check if the target of a relative link exists.

    Returns: (exists, reason)
    """
    if is_external_link(link_target):
        return (True, "External link - not checked")

    target_path = resolve_relative_path(file_path, link_target)

    if target_path.exists():
        return (True, "OK")
    return (False, f"File not found: {target_path.relative_to(REPO_ROOT)}")


def scan_file(file_path: Path) -> list[BrokenLink]:
    """Scan a markdown file for broken links."""
    broken_links = []

    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return broken_links

    links = find_markdown_links(content)

    for link_text, link_target, line_num in links:
        exists, reason = check_file_exists(file_path, link_target)

        if not exists:
            broken_links.append(
                BrokenLink(file_path, line_num, link_text, link_target, reason)
            )

    return broken_links


def scan_documentation() -> dict[str, list[BrokenLink]]:
    """Scan all documentation for broken links.

    Returns: Dictionary mapping file paths to lists of broken links
    """
    all_broken_links = {}

    # Find all markdown files
    for md_file in DOCS_ROOT.rglob("*.md"):
        broken_links = scan_file(md_file)

        if broken_links:
            all_broken_links[str(md_file.relative_to(REPO_ROOT))] = broken_links

    return all_broken_links


def generate_report(broken_links: dict[str, list[BrokenLink]]) -> str:
    """Generate a report of broken links."""
    report_lines = [
        "# Broken Documentation Links Report",
        "",
        f"**Generated**: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        f"**Total Files with Broken Links**: {len(broken_links)}",
        f"**Total Broken Links**: {sum(len(links) for links in broken_links.values())}",
        "",
        "---",
        ""
    ]

    for file_path, links in sorted(broken_links.items()):
        report_lines.append(f"## {file_path}")
        report_lines.append("")
        report_lines.append(f"**Broken Links**: {len(links)}")
        report_lines.append("")

        for link in links:
            report_lines.append(f"- **Line {link.line_num}**: `[{link.link_text}]({link.link_target})`")
            report_lines.append(f"  - **Reason**: {link.reason}")

        report_lines.append("")

    return '\n'.join(report_lines)


def main():
    """Main entry point."""
    print("Scanning documentation for broken links...")
    print(f"Documentation root: {DOCS_ROOT}")
    print()

    broken_links = scan_documentation()

    if not broken_links:
        print("✅ No broken links found!")
        return

    print(f"Found {len(broken_links)} files with broken links")
    print()

    # Print summary
    for file_path, links in sorted(broken_links.items()):
        print(f"  {file_path}: {len(links)} broken links")

    print()
    print("Generating detailed report...")

    report = generate_report(broken_links)

    # Save report
    report_path = REPO_ROOT / "docs" / "analysis" / "BROKEN_LINKS_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Report saved to: {report_path.relative_to(REPO_ROOT)}")

    # Print report to stdout
    print()
    print("=" * 80)
    print(report)
    print("=" * 80)


if __name__ == "__main__":
    main()
