#!/usr/bin/env python3
"""
Markdown Link Validator with GitHub Context Variable Detection
Validates internal file links and flags dynamic variables for manual review.

Generated: 2026-01-26 | Author: autonomous-codebase-health-agent
Updated: 2026-01-26 | Fixed absolute path handling and skip patterns
Updated: 2026-02-25 | Added --fail-on-errors / STRICT_MODE / JSON report (PR #3365)
Updated: 2026-02-25 | Added HTML comment + inline backtick span stripping (PR #3365 Phase 3)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Patterns to detect GitHub context variables
GITHUB_CONTEXT_PATTERN = re.compile(r'\$\{\{[^}]+\}\}')
# Markdown link pattern: [text](path)
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Pre-processing patterns: strip these spans BEFORE running LINK_PATTERN so
# links appearing inside comments or inline code are never matched.
# HTML comments: <!-- ... --> (single-line and multi-line, non-greedy)
HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)
# Inline backtick spans: `...` (single backtick, does NOT cross newlines)
INLINE_CODE_PATTERN = re.compile(r'`[^`\n]+`')

# Patterns to skip validation for
SKIP_LINK_PATTERNS = [
    r'^mailto:',           # Email links
    r'^tel:',              # Telephone links
    r'^javascript:',       # JavaScript links
    r'^\s*<!--',           # HTML comments
    r'^\*\*kwargs$',       # Python kwargs pattern
    r'^\[',                # Regex character classes like [a-zA-Z0-9]
    r'^items:\s*list\[',   # Type hints
    r'^\d+$',              # Plain numbers
    r'^blob:https?://',    # Blob URLs (ChatGPT, etc.)
    r'^config$',           # Placeholder 'config'
    r'^None$',             # Python None
    r'^self$',             # Python self
    r'^Dockerfile$',       # Single word placeholders without path
    r'^show-trend\.md$',   # Placeholder filename
    r'^store-trend\.md$',  # Placeholder filename
    r'^generate-dashboard\.md$',  # Placeholder filename
    r'^validate-release\.md$',    # Placeholder filename
    r'^\{[^}]+\}$',        # Template variables like {output_file}, {pr_number}
    r'^state\[',           # Python dictionary access patterns
    r'^outputs,\s*state',  # Python code patterns
    r'^\.\./src/',         # Relative imports to src (code, not docs)
    r'^"[^"]*"$',          # Quoted strings like "valid_input"
    r'^""$',               # Empty quotes
    r'^\.\s+github/',      # Malformed paths with spaces
    r'^link/to/',          # Placeholder paths
    r'^\.\./configs/',     # Config file references (code)
    r'^\.\.\./',           # Invalid relative paths
    r'^sitecustomize\.py$', # Python site customization
    r'^path$',             # Standalone 'path' word in table/code examples
    r'^\.\*$',             # Regex wildcard pattern shown as example
    r'^file\.md$',         # Generic placeholder filename
    r'^guide\.md$',        # Placeholder guide filename in doc examples
    r'^\./guide\.md$',     # Placeholder ./guide.md in examples
    r'^docs/guide\.md$',   # Placeholder docs/guide.md in examples
    r'^rag_pipelines\.md$',# Placeholder in github-pages-manager docs
    r'^/tmp/',             # Temporary file/script paths
    r'^.*?correct/path',   # Placeholder "../correct/path.md" in examples
    r'^AGENT_DESIGN\.md$', # Previously in HTML comments (now stripped upstream)
    # Placeholder tokens used in documentation templates — not real file paths:
    r'^URL$',              # e.g. [🔗 Workflow run](URL) — template placeholder, not a link
    r'^RUN_URL$',          # e.g. (RUN_URL) — run-URL template placeholder in workflow docs
]

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

    def should_skip_link(self, link: str) -> bool:
        """Check if link should be skipped based on patterns"""
        for pattern in SKIP_LINK_PATTERNS:
            if re.match(pattern, link.strip()):
                return True
        return False

    def resolve_link_path(self, source_file: Path, link: str) -> Path:
        """
        Resolve link paths correctly handling:
        - Absolute paths starting with '/' (treat as repo-root relative)
        - Relative paths
        - Parent directory traversal
        - Directory links with trailing slashes
        """
        # Remove trailing slash for path resolution
        clean_link = link.rstrip('/')

        # Handle absolute paths (starting with /) as repository root relative
        if clean_link.startswith('/'):
            # Convert absolute path to repository root relative
            clean_link = clean_link.lstrip('/')
            target_path = self.repo_root / clean_link
        else:
            # Handle relative paths from current file location
            source_dir = source_file.parent
            # Handle ./ prefix
            if clean_link.startswith('./'):
                clean_link = clean_link[2:]
            target_path = (source_dir / clean_link).resolve()

        return target_path

    def is_in_code_block(self, content: str, position: int) -> bool:
        """Check if a position in the content is inside a fenced code block.

        This implementation looks for fenced code delimiters (```), only when they
        appear at the start of a line (optionally preceded by whitespace), and
        toggles an `inside` flag each time such a fence is encountered before
        the specified position. This avoids misclassifying inline code spans that
        use backticks.
        """
        before_content = content[:position]
        inside_code_block = False

        # Process content line by line to detect fenced code blocks reliably.
        # A fence is considered any line that starts with optional whitespace
        # followed by at least three backticks, optionally followed by a language
        # identifier (e.g., ```python).
        fence_pattern = re.compile(r'^[ \t]*```')

        for line in before_content.splitlines(keepends=True):
            if fence_pattern.match(line):
                inside_code_block = not inside_code_block

        return inside_code_block

    def _strip_non_prose(self, content: str) -> str:
        """Return a version of *content* with spans that should not be
        link-validated replaced by whitespace-equivalent placeholders.

        Specifically removes:
        - HTML comments (``<!-- ... -->``) — multi-line safe, non-greedy
        - Inline backtick code spans (`` `code` ``) — single-line only

        Fenced code blocks (``` ... ```) are handled separately by
        :meth:`is_in_code_block`; we preserve their line structure so that
        the fence-detection logic in that method still works correctly.
        """
        # Replace HTML comments with spaces of the same length so that
        # character positions for subsequent matches remain stable.
        def blank_match(m: re.Match) -> str:
            # Preserve newlines so line numbers stay correct
            return re.sub(r'[^\n]', ' ', m.group(0))

        content = HTML_COMMENT_PATTERN.sub(blank_match, content)
        return INLINE_CODE_PATTERN.sub(blank_match, content)

    def validate_file(self, file_path: Path) -> None:
        """Validate all links in a single markdown file"""
        if file_path in self.checked_files:
            return
        self.checked_files.add(file_path)

        try:
            raw_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append((str(file_path), "", f"Failed to read file: {e}"))
            return

        # Strip HTML comments and inline backtick spans so links inside them
        # are never matched.  Fenced code blocks are handled by is_in_code_block
        # below; we pass raw_content to that method so fence detection still works.
        content = self._strip_non_prose(raw_content)

        for match in LINK_PATTERN.finditer(content):
            # Skip links inside fenced code blocks (uses original content for fences)
            if self.is_in_code_block(raw_content, match.start()):
                continue

            link_text = match.group(1)
            link_path = match.group(2)

            # Skip external URLs
            if self.is_external_url(link_path):
                continue

            # Skip anchor links
            if self.is_anchor_link(link_path):
                continue

            # Skip patterns that shouldn't be validated
            if self.should_skip_link(link_path):
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
            original_link = link_path
            if '#' in link_path:
                link_path = link_path.split('#')[0]

            # Skip empty links after anchor removal
            if not link_path:
                continue

            # Resolve and validate internal file path
            try:
                target_path = self.resolve_link_path(file_path, link_path)

                # Check if target is within repository
                try:
                    target_path.relative_to(self.repo_root)
                except ValueError:
                    # Path is outside repository, skip it
                    self.warnings.append((
                        str(file_path.relative_to(self.repo_root)),
                        original_link,
                        f"Link points outside repository: {link_path}"
                    ))
                    continue

                # Check if target exists (file or directory)
                if not target_path.exists():
                    self.errors.append((
                        str(file_path.relative_to(self.repo_root)),
                        original_link,
                        f"File not found: {link_path}"
                    ))
            except Exception as e:
                self.errors.append((
                    str(file_path.relative_to(self.repo_root)),
                    original_link,
                    f"Failed to resolve path: {e}"
                ))

    def validate_directory(self, directory: Path, pattern: str = "**/*.md") -> None:
        """Validate all markdown files in directory"""
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                self.validate_file(file_path)

    def report(self, report_file: str = "") -> int:
        """Print validation report, optionally write JSON, and return exit code"""
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

        # Write JSON report when requested
        if report_file:
            report_data = {
                "checked": len(self.checked_files),
                "warnings_count": len(self.warnings),
                "errors_count": len(self.errors),
                "warnings": [
                    {"file": src, "link": lnk, "message": msg}
                    for src, lnk, msg in self.warnings
                ],
                "errors": [
                    {"file": src, "link": lnk, "message": msg}
                    for src, lnk, msg in self.errors
                ],
            }
            try:
                Path(report_file).write_text(
                    json.dumps(report_data, indent=2), encoding="utf-8"
                )
                print(f"📄 Report written: {report_file}")
            except Exception as exc:  # pragma: no cover
                print(f"⚠️  Could not write report file {report_file}: {exc}")

        # Return non-zero exit code only for errors (not warnings)
        return 1 if self.errors else 0

def main():
    parser = argparse.ArgumentParser(description="Validate links in repo markdown files")
    parser.add_argument(
        "--fail-on-errors",
        action="store_true",
        default=False,
        help="Exit non-zero if errors are found (overridden by STRICT_MODE env var)",
    )
    parser.add_argument(
        "--report-file",
        default="",
        help="Optional path to write a JSON summary report",
    )
    args = parser.parse_args()

    # STRICT_MODE env var overrides --fail-on-errors (workflow sets this)
    env_strict = os.getenv("STRICT_MODE", "").lower()
    if env_strict in ("1", "true", "yes"):
        args.fail_on_errors = True
    elif env_strict in ("0", "false", "no"):
        args.fail_on_errors = False

    repo_root = Path(__file__).parent.parent.parent
    validator = LinkValidator(repo_root)

    # Validate specific directories
    validator.validate_directory(repo_root / ".github" / "workflows")
    validator.validate_directory(repo_root / ".github" / "docs")
    validator.validate_directory(repo_root / ".github" / "agents")
    validator.validate_directory(repo_root / "docs")

    exit_code = validator.report(report_file=args.report_file)

    if args.fail_on_errors:
        sys.exit(exit_code)
    else:
        # Always exit 0 unless --fail-on-errors / STRICT_MODE is active
        sys.exit(0)

if __name__ == "__main__":
    main()
