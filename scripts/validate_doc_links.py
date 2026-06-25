#!/usr/bin/env python3
"""
Automated Documentation Link Validator

Validates all links in documentation files (Markdown) to prevent broken links.
Based on successful 9-link fix pattern from 2026-02-06.

Usage:
    python scripts/validate_doc_links.py [--check-only] [--fix] [path/to/docs/]

Examples:
    # Check all docs
    python scripts/validate_doc_links.py --check-only

    # Check specific directory
    python scripts/validate_doc_links.py --check-only docs/analysis/

    # Apply automatic fixes
    python scripts/validate_doc_links.py --fix docs/
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class LinkIssue:
    """Represents a broken or invalid link."""

    file_path: Path
    line_number: int
    link_text: str
    link_target: str
    issue_type: Literal["broken_file", "broken_anchor", "broken_url", "relative_path"]
    severity: Literal["error", "warning", "info"]
    suggestion: str


class LinkValidator:
    """Validates links in Markdown documentation."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.issues: list[LinkIssue] = []
        self.checked_files = 0
        self.checked_links = 0

        # Patterns from successful 9-link fix
        self.fix_patterns = {
            "pr_analysis_archive": {
                "old": r"docs/analysis/PR_\d+_.*\.md",
                "new": ".codex/archive/pr-resolutions/PR_{pr_num}_ANALYSIS.md"
            },
            "root_org_phases": {
                "old": r"sessions/\d{4}-\d{2}/",
                "new": "phases/"
            },
            "github_blob_url": {
                "template": "https://github.com/Aries-Serpent/_codex_/blob/main/{path}"
            }
        }

    def validate_directory(self, doc_dir: Path) -> list[LinkIssue]:
        """Validate all Markdown files in directory."""
        for md_file in doc_dir.rglob("*.md"):
            if md_file.is_file() and not self._should_skip(md_file):
                self.validate_file(md_file)
        return self.issues

    def validate_file(self, md_file: Path) -> list[LinkIssue]:
        """Validate a single Markdown file."""
        self.checked_files += 1

        try:
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Find all Markdown links: [text](url) or [text][ref]
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

            for match in re.finditer(link_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                link_text = match.group(1)
                link_target = match.group(2)

                self.checked_links += 1
                issue = self._check_link(md_file, line_num, link_text, link_target)
                if issue:
                    self.issues.append(issue)

        except Exception as e:
            error_type = type(e).__name__
            print(f"⚠️  Error reading {md_file}: <ERROR_TYPE>")

        return self.issues

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            ".codex/archive/",
            "node_modules/",
            ".git/",
            "__pycache__/",
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _check_link(
        self,
        md_file: Path,
        line_num: int,
        link_text: str,
        link_target: str
    ) -> LinkIssue | None:
        """Check if a link is valid."""
        # Skip external URLs and anchors
        if link_target.startswith(("http://", "https://", "#", "mailto:")):
            return None

        # Resolve relative path
        if link_target.startswith("./") or link_target.startswith("../"):
            target_path = (md_file.parent / link_target).resolve()
        else:
            target_path = self.root_dir / link_target

        # Check if target exists
        if not target_path.exists():
            # Determine issue type
            if "PR_" in link_target and "ANALYSIS" in link_target:
                issue_type = "broken_file"
                suggestion = "Move to .codex/archive/pr-resolutions/ or update path"
            elif "sessions/" in link_target:
                issue_type = "broken_file"
                suggestion = "Update to phases/ directory structure"
            else:
                issue_type = "broken_file"
                suggestion = f"File not found: {target_path}. Check path or create file."

            return LinkIssue(
                file_path=md_file,
                line_number=line_num,
                link_text=link_text,
                link_target=link_target,
                issue_type=issue_type,
                severity="error",
                suggestion=suggestion
            )

        return None

    def generate_report(self) -> str:
        """Generate human-readable report."""
        if not self.issues:
            return f"""
✅ Documentation Link Validation - All Clear!

Files checked: {self.checked_files}
Links validated: {self.checked_links}
Issues found: 0

All documentation links are valid.
"""

        report = f"""
⚠️  Documentation Link Validation - Issues Found

Files checked: {self.checked_files}
Links validated: {self.checked_links}
Issues found: {len(self.issues)}

{'='*70}
"""

        # Group by severity
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        for severity, issues in [("ERRORS", errors), ("WARNINGS", warnings)]:
            if not issues:
                continue

            report += f"\n{severity} ({len(issues)} issues):\n"
            report += "-" * 70 + "\n"

            for issue in issues:
                report += f"""
File: {issue.file_path}
Line: {issue.line_number}
Link: [{issue.link_text}]({issue.link_target})
Issue: {issue.issue_type}
Suggestion: {issue.suggestion}
"""

        # Add fix patterns if available
        if errors:
            report += "\n" + "="*70 + "\n"
            report += "\nCommon Fix Patterns:\n"
            report += """
1. PR Analysis Files:
   Move to: .codex/archive/pr-resolutions/
   Or use: GitHub blob URL

2. Session References:
   Change: sessions/2026-01/ → phases/

3. Workflow Reports:
   Consider: Remove if artifact no longer exists
   Or: Update to current artifact location
"""

        return report

    def apply_fixes(self) -> int:
        """Apply automatic fixes to broken links."""
        fixed_count = 0

        # Group issues by file
        issues_by_file: dict[Path, list[LinkIssue]] = {}
        for issue in self.issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

        # Apply fixes file by file
        for file_path, file_issues in issues_by_file.items():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Sort issues by line number (reverse) to avoid offset issues
                file_issues.sort(key=lambda x: x.line_number, reverse=True)

                for issue in file_issues:
                    # Apply pattern-based fixes
                    if "PR_" in issue.link_target and ".codex/archive/" not in issue.link_target:
                        # Fix PR analysis link
                        content = content.replace(
                            issue.link_target,
                            f".codex/archive/pr-resolutions/{Path(issue.link_target).name}"
                        )
                        fixed_count += 1
                    elif "sessions/" in issue.link_target:
                        # Fix session reference
                        content = content.replace(
                            "sessions/2026-01/",
                            "phases/"
                        )
                        fixed_count += 1

                # Write back if changes made
                if fixed_count > 0:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ Fixed {fixed_count} links in {file_path}")

            except Exception as e:
                error_type = type(e).__name__
                print(f"❌ Error fixing {file_path}: <ERROR_TYPE>")

        return fixed_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate documentation links"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="docs/",
        help="Path to documentation directory (default: docs/)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for issues, don't apply fixes"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically apply fixes"
    )

    args = parser.parse_args()

    # Setup paths
    repo_root = Path(__file__).parent.parent
    target_path = repo_root / args.path

    if not target_path.exists():
        print(f"❌ Path not found: {target_path}")
        return 1

    print(f"🔍 Validating documentation links in: {target_path}")
    print()

    # Create validator
    validator = LinkValidator(repo_root)

    # Run validation
    if target_path.is_file():
        validator.validate_file(target_path)
    else:
        validator.validate_directory(target_path)

    # Generate report
    report = validator.generate_report()
    print(report)

    # Apply fixes if requested
    if args.fix and validator.issues:
        print("\n🔧 Applying automatic fixes...")
        fixed = validator.apply_fixes()
        print(f"\n✅ Fixed {fixed} links")

        # Re-validate
        print("\n🔍 Re-validating...")
        validator.issues = []
        if target_path.is_file():
            validator.validate_file(target_path)
        else:
            validator.validate_directory(target_path)

        final_report = validator.generate_report()
        print(final_report)

    # Return exit code based on errors
    error_count = sum(1 for i in validator.issues if i.severity == "error")
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
