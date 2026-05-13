#!/usr/bin/env python3
"""
Markdown Table Formatter for GitHub Pages Manager Agent

Detects and fixes markdown table formatting issues:
- Missing blank lines before tables
- Missing blank lines after headers before tables
- Malformed table separators
- Inconsistent table column alignment

Usage:
    python scripts/fix_markdown_tables.py [--check-only] [--file FILE]
"""

import argparse
import re
import sys
from pathlib import Path


class MarkdownTableFixer:
    """Fixes markdown table formatting issues."""

    def __init__(self, root_dir: Path, check_only: bool = False):
        self.root_dir = root_dir
        self.docs_dir = root_dir / "docs"
        self.check_only = check_only
        self.issues_found: list[dict] = []
        self.fixes_applied: list[dict] = []

    def fix_all(self) -> tuple[int, int]:
        """Fix all markdown files. Returns (issues_found, fixes_applied)."""
        print("🔧 GitHub Pages Manager - Markdown Table Formatter\n")
        print(f"📂 Root: {self.root_dir}")
        print(f"📚 Docs: {self.docs_dir}")
        print(f"🔍 Mode: {'Check only' if self.check_only else 'Fix mode'}\n")

        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))
        print(f"📄 Found {len(md_files)} markdown files\n")

        for md_file in md_files:
            self._process_file(md_file)

        # Report results
        self._report_results()

        return len(self.issues_found), len(self.fixes_applied)

    def fix_file(self, file_path: Path) -> tuple[int, int]:
        """Fix a single file. Returns (issues_found, fixes_applied)."""
        print(f"🔧 Processing: {file_path}\n")
        self._process_file(file_path)
        self._report_results()
        return len(self.issues_found), len(self.fixes_applied)

    def _process_file(self, md_file: Path):
        """Process a single markdown file."""
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Failed to read {md_file}: {e}")
            return

        # Find all table patterns
        lines = content.split('\n')
        modified = False
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is a table separator line (e.g., | --- | --- | --- |)
            if self._is_table_separator(line):
                # Check if previous line needs blank line
                if i > 0 and new_lines:
                    prev_line = new_lines[-1]

                    # Check if previous line is a header (starts with #)
                    if self._is_header(prev_line):
                        # Need blank line between header and table
                        if prev_line.strip():  # Not already blank
                            issue = {
                                "type": "missing_blank_before_table",
                                "file": str(md_file.relative_to(self.root_dir)),
                                "line": i,
                                "context": f"Header: {prev_line[:50]}...",
                                "message": "Missing blank line between header and table"
                            }
                            self.issues_found.append(issue)

                            if not self.check_only:
                                # Insert blank line
                                new_lines.append('')
                                modified = True
                                self.fixes_applied.append({
                                    "file": str(md_file.relative_to(self.root_dir)),
                                    "line": i,
                                    "fix": "Added blank line before table"
                                })

                    # Check if previous line is regular text (not blank, not table header)
                    elif prev_line.strip() and not self._is_table_header(prev_line):
                        issue = {
                            "type": "missing_blank_before_table",
                            "file": str(md_file.relative_to(self.root_dir)),
                            "line": i,
                            "context": f"Text: {prev_line[:50]}...",
                            "message": "Missing blank line before table"
                        }
                        self.issues_found.append(issue)

                        if not self.check_only:
                            new_lines.append('')
                            modified = True
                            self.fixes_applied.append({
                                "file": str(md_file.relative_to(self.root_dir)),
                                "line": i,
                                "fix": "Added blank line before table"
                            })

            # Check for table header line followed immediately by separator
            if self._is_table_header(line) and i + 1 < len(lines):
                next_line = lines[i + 1]
                if not self._is_table_separator(next_line):
                    # Possible malformed table - header without separator
                    issue = {
                        "type": "malformed_table",
                        "file": str(md_file.relative_to(self.root_dir)),
                        "line": i + 1,
                        "context": f"Header: {line[:50]}...",
                        "message": "Table header not followed by separator line"
                    }
                    self.issues_found.append(issue)

            new_lines.append(line)
            i += 1

        # Write back if modified
        if modified and not self.check_only:
            try:
                new_content = '\n'.join(new_lines)
                md_file.write_text(new_content, encoding='utf-8')
                print(f"  ✅ Fixed: {md_file.relative_to(self.root_dir)}")
            except Exception as e:
                print(f"  ⚠️  Failed to write {md_file}: {e}")

    def _is_header(self, line: str) -> bool:
        """Check if line is a markdown header (h1-h6)."""
        stripped = line.strip()
        # Match ATX headers: 1–6 '#' characters followed by at least one space and some text
        return bool(re.match(r'#{1,6}\s+\S', stripped))

    def _is_table_header(self, line: str) -> bool:
        """Check if line looks like a table header."""
        stripped = line.strip()
        # Must have at least 2 pipes and some content between them
        if stripped.count('|') < 2:
            return False
        # Check if it has actual content (not just pipes and dashes)
        content = stripped.strip('|').strip()
        if not content or set(content.replace('|', '').replace(' ', '').replace('-', '')) == set():
            return False
        return '|' in stripped

    def _is_table_separator(self, line: str) -> bool:
        """Check if line is a table separator (e.g., | --- | --- |)."""
        stripped = line.strip()
        if not stripped or '|' not in stripped:
            return False

        # Remove pipes and spaces
        content = stripped.replace('|', '').replace(' ', '')

        # Should only contain dashes and colons (for alignment)
        if not content:
            return False

        # Check if it's mostly dashes
        dash_ratio = content.count('-') / len(content) if content else 0
        return dash_ratio > 0.5

    def _report_results(self):
        """Print results."""
        print("\n" + "="*70)
        print("📊 FORMATTING RESULTS")
        print("="*70)

        if self.issues_found:
            print(f"\n⚠️  ISSUES FOUND ({len(self.issues_found)}):")

            # Group by file
            by_file = {}
            for issue in self.issues_found:
                file = issue['file']
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(issue)

            for file, issues in sorted(by_file.items()):
                print(f"\n📄 {file}")
                for issue in issues:
                    print(f"   Line {issue['line']}: {issue['message']}")
                    if 'context' in issue:
                        print(f"   Context: {issue['context']}")

        if self.fixes_applied:
            print(f"\n✅ FIXES APPLIED ({len(self.fixes_applied)}):")

            # Group by file
            by_file = {}
            for fix in self.fixes_applied:
                file = fix['file']
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(fix)

            for file, fixes in sorted(by_file.items()):
                print(f"\n📄 {file}")
                for fix in fixes:
                    print(f"   Line {fix['line']}: {fix['fix']}")

        if not self.issues_found:
            print("\n✅ No table formatting issues found!")
        elif self.check_only:
            print("\n💡 Run without --check-only to apply fixes")

        print("\n" + "="*70)
        print(f"Summary: {len(self.issues_found)} issues, {len(self.fixes_applied)} fixed")
        print("="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix markdown table formatting issues"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for issues, don't fix"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Fix a specific file instead of all files"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory"
    )

    args = parser.parse_args()

    fixer = MarkdownTableFixer(
        root_dir=args.root,
        check_only=args.check_only
    )

    if args.file:
        issues, _fixes = fixer.fix_file(args.file)
    else:
        issues, _fixes = fixer.fix_all()

    # Exit with error code if there are unfixed issues
    sys.exit(1 if (issues > 0 and args.check_only) else 0)


if __name__ == "__main__":
    main()
