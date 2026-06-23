#!/usr/bin/env python3
"""
Cross-reference validator for Markdown documentation.

Scans Markdown files for internal links and validates that:
- File paths exist
- Anchor references are valid (if applicable)
- Links follow consistency patterns
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI colors for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class CrossReferenceValidator:
    """Validates cross-references in Markdown documentation."""

    # Pattern to match [text](path) links
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    # Pattern to match markdown headers for anchor extraction
    HEADER_PATTERN = re.compile(r"^#{1,6}\s+(.+)$")

    # Files to ignore in validation
    IGNORE_FILES = {".codex/docs/AGENTS.md.original", ".codex/change_log.md"}

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.files_checked = 0
        self.links_checked = 0

    def _normalize_anchor(self, text: str) -> str:
        """Convert heading text to anchor format (lowercase, hyphens)."""
        # Remove special characters and convert to lowercase with hyphens
        anchor = re.sub(r"[^\w\s-]", "", text.lower())
        anchor = re.sub(r"\s+", "-", anchor)
        anchor = re.sub(r"-+", "-", anchor)
        return anchor.strip("-")

    def _extract_anchors(self, content: str) -> set:
        """Extract all valid anchors from markdown content."""
        anchors = set()
        for line in content.split("\n"):
            match = self.HEADER_PATTERN.match(line.strip())
            if match:
                heading_text = match.group(1)
                anchors.add(self._normalize_anchor(heading_text))
        return anchors

    def _resolve_link_path(self, link: str, source_file: Path) -> Tuple[Path, str]:
        """
        Resolve a link path relative to the source file.
        Returns (resolved_path, anchor).
        """
        # Separate path from anchor
        if "#" in link:
            path_part, anchor = link.split("#", 1)
        else:
            path_part, anchor = link, ""

        # Skip absolute URLs and mailto links
        if (
            path_part.startswith("http://")
            or path_part.startswith("https://")
            or path_part.startswith("mailto:")
        ):
            return None, ""

        # Skip empty paths (just anchors)
        if not path_part:
            return source_file, anchor

        # Resolve relative path
        if path_part.startswith("/"):
            resolved = self.repo_root / path_part.lstrip("/")
        else:
            resolved = (source_file.parent / path_part).resolve()

        return resolved, anchor

    def _check_link(self, link: str, source_file: Path) -> Tuple[bool, str]:
        """Check if a link is valid. Returns (is_valid, message)."""
        resolved_path, anchor = self._resolve_link_path(link, source_file)

        if resolved_path is None:
            # External URL
            return True, "external"

        # Check file exists
        if not resolved_path.exists():
            try:
                if resolved_path.is_relative_to(self.repo_root):
                    display_path = resolved_path.relative_to(self.repo_root)
                else:
                    display_path = resolved_path
            except (ValueError, TypeError):
                display_path = resolved_path
            return False, f"File not found: {display_path}"

        # Check anchor if specified
        if anchor:
            try:
                with open(resolved_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    valid_anchors = self._extract_anchors(content)
                    normalized_anchor = self._normalize_anchor(anchor)

                    if normalized_anchor not in valid_anchors:
                        # List available anchors for debugging
                        available = ", ".join(sorted(list(valid_anchors)[:5]))
                        msg = (
                            f"Anchor not found: #{anchor} in {resolved_path.name} "
                            f"(available: {available}...)"
                        )
                        return False, msg
            except Exception as e:
                return False, f"Error reading file: {e}"

        return True, "valid"

    def validate_file(self, file_path: Path) -> None:
        """Validate all cross-references in a markdown file."""
        try:
            if file_path.is_relative_to(self.repo_root):
                relative_path = file_path.relative_to(self.repo_root)
            else:
                relative_path = file_path
        except (ValueError, TypeError):
            relative_path = file_path

        # Skip ignored files
        if str(relative_path) in self.IGNORE_FILES:
            return

        self.files_checked += 1

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.errors.append(
                {
                    "file": str(relative_path),
                    "line": 0,
                    "type": "read_error",
                    "message": str(e),
                }
            )
            return

        # Find all links
        for line_num, line in enumerate(content.split("\n"), 1):
            for match in self.LINK_PATTERN.finditer(line):
                link_text, link_path = match.groups()
                self.links_checked += 1

                # Skip image alt text validation (handled separately)
                if line.strip().startswith("!"):
                    continue

                is_valid, message = self._check_link(link_path, file_path)

                if not is_valid:
                    self.errors.append(
                        {
                            "file": str(relative_path),
                            "line": line_num,
                            "link": link_path,
                            "text": link_text,
                            "message": message,
                        }
                    )
                elif message == "external":
                    # External links are just warnings
                    self.warnings.append(
                        {
                            "file": str(relative_path),
                            "line": line_num,
                            "link": link_path,
                            "type": "external_url",
                        }
                    )

    def validate_directory(self, directory: Path = None) -> None:
        """Validate all markdown files in directory."""
        if directory is None:
            directory = self.repo_root

        for md_file in sorted(directory.rglob("*.md")):
            # Skip node_modules, .git, and other non-doc directories
            if any(
                part in md_file.parts
                for part in [
                    "node_modules",
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".pytest_cache",
                ]
            ):
                continue

            self.validate_file(md_file)

    def generate_report(self, output_format: str = "text") -> str:
        """Generate validation report."""
        if output_format == "json":
            return json.dumps(
                {
                    "files_checked": self.files_checked,
                    "links_checked": self.links_checked,
                    "errors": self.errors,
                    "warnings": self.warnings,
                    "status": "passed" if not self.errors else "failed",
                }
            )

        # Text format
        lines = []
        lines.append(
            f"\n{BOLD}Cross-Reference Validation Report{RESET}\n"
            f"{'='*70}"
        )
        lines.append(f"Files checked: {self.files_checked}")
        lines.append(f"Links validated: {self.links_checked}")
        lines.append(f"Errors found: {len(self.errors)}")
        lines.append(f"Warnings: {len(self.warnings)}")
        lines.append("=" * 70)

        if self.errors:
            lines.append(f"\n{RED}{BOLD}❌ BROKEN LINKS ({len(self.errors)}){RESET}")
            for error in sorted(self.errors, key=lambda x: (x.get("file"), x.get("line", 0))):
                lines.append(
                    f"\n  {RED}✗{RESET} {error['file']}:{error.get('line', '?')}"
                )
                lines.append(f"    Link: [{error.get('text', '?')}]({error.get('link', '?')})")
                lines.append(f"    Error: {error['message']}")

        if self.warnings:
            lines.append(f"\n{YELLOW}{BOLD}⚠️  WARNINGS ({len(self.warnings)}){RESET}")
            for warning in self.warnings[:10]:  # Limit warnings shown
                lines.append(
                    f"  {YELLOW}→{RESET} {warning['file']}:{warning.get('line', '?')} "
                    f"({warning['type']})"
                )
            if len(self.warnings) > 10:
                lines.append(f"  ... and {len(self.warnings) - 10} more warnings")

        if not self.errors:
            lines.append(f"\n{GREEN}{BOLD}✓ All cross-references are valid!{RESET}")

        lines.append("\n")
        return "\n".join(lines)

    def print_github_annotations(self) -> None:
        """Print errors as GitHub Actions annotations."""
        for error in self.errors:
            file_path = error["file"]
            line = error.get("line", 0)
            message = error["message"]
            print(
                f"::error file={file_path},line={line},title=Broken Link:: "
                f"{message}"
            )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate cross-references in Markdown files"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--github-annotations",
        action="store_true",
        help="Output GitHub Actions annotations",
    )
    parser.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="Exit with status 1 if errors found",
    )

    args = parser.parse_args()

    validator = CrossReferenceValidator(args.repo_root)
    validator.validate_directory()

    # Output report
    if args.format == "json":
        print(validator.generate_report("json"))
    else:
        print(validator.generate_report("text"))

    if args.github_annotations:
        validator.print_github_annotations()

    if args.fail_on_errors and validator.errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
