#! /usr/bin/env python3
"""
Check Doc Links

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/maintenance/check_doc_links.py [options]

    Examples:
    $ python scripts/maintenance/check_doc_links.py --help

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



import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class LinkChecker:
    """Check and validate documentation links."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.docs_dir = root_dir / "docs"
        self.broken_links: List[Tuple[Path, str, str]] = []
        self.all_files: Set[Path] = set()
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

    def scan_all_files(self) -> None:
        """Build index of all documentation files."""
        print("📁 Scanning documentation files...")
        for md_file in self.root_dir.rglob('*.md'):
            # Skip node_modules, .git, etc.
            if any(skip in str(md_file) for skip in ['.git', 'node_modules', '.nox', '__pycache__']):
                continue
            self.all_files.add(md_file)
        print(f"   Found {len(self.all_files)} markdown files")

    def check_link(self, source: Path, link: str) -> bool:
        """Check if a link target exists."""
        # Skip external URLs
        if link.startswith(('http://', 'https://', 'mailto:', 'tel:')):
            return True

        # Skip anchors
        if link.startswith('#'):
            return True

        # Remove anchor from link
        link_path = link.split('#')[0]
        if not link_path:
            return True

        # Resolve relative path
        try:
            target = (source.parent / link_path).resolve()
            return target.exists()
        except (ValueError, OSError):
            return False

    def scan_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """Scan a file for links and check validity."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError) as e:
            print(f"⚠️  Warning: Could not read {file_path}: {e}")
            return []

        broken = []
        matches = self.link_pattern.findall(content)

        for text, link in matches:
            if not self.check_link(file_path, link):
                broken.append((text, link))
                self.broken_links.append((file_path, text, link))

        return broken

    def categorize_broken_links(self) -> Dict[str, List[Tuple[Path, str, str]]]:
        """Categorize broken links by type."""
        categories = defaultdict(list)

        for source, text, link in self.broken_links:
            if '/tmp/' in link or link.startswith('/tmp/'):
                categories['tmp_violations'].append((source, text, link))
            elif link.startswith('../'):
                categories['relative_up'].append((source, text, link))
            elif '.' not in Path(link).name:
                categories['missing_extension'].append((source, text, link))
            else:
                categories['missing_file'].append((source, text, link))

        return categories

    def suggest_fix(self, source: Path, link: str) -> str:
        """Suggest a fix for a broken link."""
        link_name = Path(link).name

        # Search for files with similar names
        candidates = []
        for file in self.all_files:
            if file.name == link_name:
                try:
                    rel_path = file.relative_to(source.parent)
                    candidates.append(str(rel_path))
                except ValueError:
                    # File outside source directory
                    try:
                        common = Path(*file.parts[:5])  # Root directory
                        rel_path = file.relative_to(common)
                        candidates.append(f"../../{rel_path}")
                    except (ValueError, IndexError):
                        # If we cannot compute a reasonable relative path from this
                        # heuristic common root, just skip this candidate and continue.
                        # Suggestion generation is best-effort and should not fail hard.
                        pass
                        _ = None  # noqa: BLE001

        if candidates:
            return f"Possible: {candidates[0]}"
        return "No suggestion"

    def generate_report(self) -> str:
        """Generate a detailed report."""
        report = []
        report.append("# Documentation Link Validation Report\n")
        report.append(f"**Total Files**: {len(self.all_files)}\n")
        report.append(f"**Broken Links**: {len(self.broken_links)}\n")
        report.append("\n---\n\n")

        categories = self.categorize_broken_links()

        for category, links in sorted(categories.items()):
            report.append(f"## {category.replace('_', ' ').title()} ({len(links)})\n\n")

            # Group by source file
            by_source = defaultdict(list)
            for source, text, link in links:
                by_source[source].append((text, link))

            for source, link_list in sorted(by_source.items())[:10]:  # Show top 10
                try:
                    rel_source = source.relative_to(self.root_dir)
                except ValueError:
                    rel_source = source
                report.append(f"### {rel_source}\n\n")
                for text, link in link_list[:5]:  # Show top 5 per file
                    suggestion = self.suggest_fix(source, link)
                    report.append(f"- `[{text}]({link})` → {suggestion}\n")
                if len(link_list) > 5:
                    report.append(f"  _... and {len(link_list) - 5} more_\n")
                report.append("\n")

            if len(by_source) > 10:
                report.append(f"_... and {len(by_source) - 10} more files_\n\n")

        return ''.join(report)

    def run(self, report_file: Path = None) -> int:
        """Run the link checker."""
        print("🔍 Documentation Link Checker")
        print("=" * 50)

        self.scan_all_files()

        print("\n🔗 Checking links...")
        checked = 0
        for file_path in self.all_files:
            broken = self.scan_file(file_path)
            if broken:
                checked += 1
                if checked <= 10:  # Show first 10 files with issues
                    try:
                        rel_path = file_path.relative_to(self.root_dir)
                    except ValueError:
                        rel_path = file_path
                    print(f"   ⚠️  {rel_path}: {len(broken)} broken link(s)")

        print("\n📊 Results:")
        print(f"   Total files checked: {len(self.all_files)}")
        print(f"   Files with broken links: {checked}")
        print(f"   Total broken links: {len(self.broken_links)}")

        if self.broken_links:
            categories = self.categorize_broken_links()
            print("\n📋 Categories:")
            for category, links in sorted(categories.items()):
                print(f"   {category.replace('_', ' ').title()}: {len(links)}")

        if report_file:
            report = self.generate_report()
            report_file.write_text(report)
            print(f"\n📄 Report saved to: {report_file}")

        return 0 if not self.broken_links else 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Check documentation links')
    parser.add_argument('--report', type=str, help='Generate report file')
    parser.add_argument('--json', type=str, help='Export JSON report')
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent.parent
    checker = LinkChecker(root_dir)

    report_file = Path(args.report) if args.report else None
    exit_code = checker.run(report_file)

    if args.json:
        # Export JSON for programmatic use
        json_data = {
            'total_files': len(checker.all_files),
            'broken_links': [
                {
                    'source': str(src.relative_to(root_dir)) if src.is_relative_to(root_dir) else str(src),
                    'text': text,
                    'link': link
                }
                for src, text, link in checker.broken_links
            ]
        }
        Path(args.json).write_text(json.dumps(json_data, indent=2))
        print(f"📄 JSON report saved to: {args.json}")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
