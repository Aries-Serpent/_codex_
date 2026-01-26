#!/usr/bin/env python3
"""
Markdown Link Validator with GitHub Context Variable Detection
Validates internal file links and flags dynamic variables for manual review.

Generated: 2026-01-26 | Author: autonomous-codebase-health-agent
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Set

# Patterns to detect GitHub context variables
GITHUB_CONTEXT_PATTERN = re.compile(r'\$\{\{[^}]+\}\}')
# Markdown link pattern: [text](path)
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

class LinkValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: List[Tuple[str, str, str]] = []
        self.warnings: List[Tuple[str, str, str]] = []
        self.checked_files: Set[Path] = set()

    def is_external_url(self, link: str) -> bool:
        """Check if link is external URL"""
        return link.startswith(('http://', 'https://', 'ftp://'))

    def has_github_context(self, link: str) -> bool:
        """Check if link contains unresolved GitHub context variables"""
        return bool(GITHUB_CONTEXT_PATTERN.search(link))

    def is_anchor_link(self, link: str) -> bool:
        """Check if link is an anchor (fragment identifier)"""
        return link.startswith('#')

    def resolve_relative_path(self, source_file: Path, link: str) -> Path:
        """Resolve relative link path from source file location"""
        source_dir = source_file.parent
        # Handle ./ and ../ prefixes
        if link.startswith('./'):
            link = link[2:]
        target_path = (source_dir / link).resolve()
        return target_path

    def validate_file(self, file_path: Path) -> None:
        """Validate all links in a single markdown file"""
        if file_path in self.checked_files:
            return
        self.checked_files.add(file_path)

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append((str(file_path), "", f"Failed to read file: {e}"))
            return

        for match in LINK_PATTERN.finditer(content):
            link_text = match.group(1)
            link_path = match.group(2)

            # Skip external URLs
            if self.is_external_url(link_path):
                continue

            # Skip anchor links
            if self.is_anchor_link(link_path):
                continue

            # Warn about GitHub context variables
            if self.has_github_context(link_path):
                self.warnings.append((
                    str(file_path.relative_to(self.repo_root)),
                    link_path,
                    f"Contains unresolved GitHub context variable: [{link_text}]({link_path})"
                ))
                continue

            # Remove anchor fragment if present
            if '#' in link_path:
                link_path = link_path.split('#')[0]

            # Skip empty links after anchor removal
            if not link_path:
                continue

            # Resolve and validate internal file path
            try:
                target_path = self.resolve_relative_path(file_path, link_path)
                
                # Check if target exists
                if not target_path.exists():
                    self.errors.append((
                        str(file_path.relative_to(self.repo_root)),
                        link_path,
                        f"File not found: {target_path.relative_to(self.repo_root)}"
                    ))
            except Exception as e:
                self.errors.append((
                    str(file_path.relative_to(self.repo_root)),
                    link_path,
                    f"Failed to resolve path: {e}"
                ))

    def validate_directory(self, directory: Path, pattern: str = "**/*.md") -> None:
        """Validate all markdown files in directory"""
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                self.validate_file(file_path)

    def report(self) -> int:
        """Print validation report and return exit code"""
        print("=" * 80)
        print("📋 MARKDOWN LINK VALIDATION REPORT")
        print("=" * 80)

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            print("-" * 80)
            for source, link, message in self.warnings:
                print(f"📄 {source}")
                print(f"   🔗 {link}")
                print(f"   💬 {message}")
                print()

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            print("-" * 80)
            for source, link, message in self.errors:
                print(f"📄 {source}")
                print(f"   🔗 {link}")
                print(f"   💬 {message}")
                print()

        print("=" * 80)
        print(f"✅ Files checked: {len(self.checked_files)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        print("=" * 80)

        # Return non-zero exit code only for errors (not warnings)
        return 1 if self.errors else 0

def main():
    repo_root = Path(__file__).parent.parent.parent
    validator = LinkValidator(repo_root)

    # Validate specific directories
    validator.validate_directory(repo_root / ".github" / "workflows")
    validator.validate_directory(repo_root / ".github" / "docs")
    validator.validate_directory(repo_root / "docs")

    sys.exit(validator.report())

if __name__ == "__main__":
    main()
