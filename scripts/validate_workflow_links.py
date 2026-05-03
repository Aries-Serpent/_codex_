#!/usr/bin/env python3
"""
Workflow Documentation Link Validator

Validates markdown links in GitHub Actions workflow documentation to ensure
all references are correct and files exist.

Usage:
    python scripts/validate_workflow_links.py [--verbose]

Exit codes:
    0 - All links valid
    1 - Broken links found
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


def find_markdown_links(content: str) -> list[tuple[str, str]]:
    """Find all markdown links in content.

    Args:
        content: The markdown content to search

    Returns:
        List of (text, url) tuples
    """
    # Match [text](url) and [text]: url
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)|\[([^\]]+)\]:\s*(\S+)'
    matches = re.findall(pattern, content)
    links = []
    for match in matches:
        if match[1]:
            links.append((match[0], match[1]))
        elif match[3]:
            links.append((match[2], match[3]))
    return links


def validate_local_link(link: str, base_path: Path) -> tuple[bool, Optional[str]]:
    """Validate a local file link.

    Args:
        link: The link to validate
        base_path: The base path of the file containing the link

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove anchors
    link = link.split('#')[0]

    # Skip external URLs
    if link.startswith(('http://', 'https://', 'mailto:')):
        return True, None

    # Skip empty or anchor-only links
    if not link or link.startswith('#'):
        return True, None

    # Resolve relative path
    full_path = Path(link[1:]) if link.startswith('/') else (base_path.parent / link).resolve()

    # Check if file exists
    if full_path.exists():
        return True, None
    return False, f"File not found: {full_path}"


def validate_workflow_links(verbose: bool = False) -> int:
    """Validate all workflow documentation links.

    Args:
        verbose: Print verbose output

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Scan workflow documentation
    workflow_dir = Path('.github/workflows')

    broken_links: dict[str, list[dict[str, str]]] = defaultdict(list)
    total_links = 0

    # Check workflow markdown files
    for md_file in workflow_dir.rglob('*.md'):
        content = md_file.read_text()
        links = find_markdown_links(content)

        for text, link in links:
            total_links += 1
            valid, error = validate_local_link(link, md_file)
            if not valid:
                broken_links[str(md_file)].append({
                    'text': text,
                    'link': link,
                    'error': error
                })
                if verbose:
                    print(f"❌ {md_file}: [{text}]({link}) - {error}")

    # Check YAML workflow files for documentation URLs
    workflow_files = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
    for yml_file in workflow_files:
        try:
            content = yml_file.read_text()
            links = find_markdown_links(content)

            for text, link in links:
                total_links += 1
                valid, error = validate_local_link(link, yml_file)
                if not valid:
                    broken_links[str(yml_file)].append({
                        'text': text,
                        'link': link,
                        'error': error
                    })
                    if verbose:
                        print(f"❌ {yml_file}: [{text}]({link}) - {error}")
        except Exception as e:
            if verbose:
                print(f"⚠️  Warning: Could not parse {yml_file}: {e}")

    # Generate report
    print(f"\n{'='*60}")
    print("WORKFLOW DOCUMENTATION LINK VALIDATION")
    print(f"{'='*60}\n")
    print(f"Total links checked: {total_links}")
    print(f"Broken links found: {sum(len(v) for v in broken_links.values())}\n")

    if broken_links:
        print("BROKEN LINKS:\n")
        for file, links in broken_links.items():
            print(f"\n{file}:")
            for link in links:
                print(f"  - [{link['text']}]({link['link']})")
                print(f"    Error: {link['error']}")

        # Write to GitHub step summary if available
        github_step_summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
        if github_step_summary_path:
            github_step_summary = Path(github_step_summary_path)
            with github_step_summary.open('a') as f:
                f.write("## ❌ Broken Links Found\n\n")
                for file, links in broken_links.items():
                    f.write(f"### {file}\n\n")
                    for link in links:
                        f.write(f"- `[{link['text']}]({link['link']})` - {link['error']}\n")
                    f.write("\n")

        return 1
    print("✅ All links are valid!")

    # Write to GitHub step summary if available
    github_step_summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if github_step_summary_path:
        github_step_summary = Path(github_step_summary_path)
        with github_step_summary.open('a') as f:
            f.write("## ✅ All Links Valid\n\n")
            f.write(f"Validated {total_links} links in workflow documentation.\n")

    return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate workflow documentation links')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    exit_code = validate_workflow_links(args.verbose)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
