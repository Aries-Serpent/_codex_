#!/usr/bin/env python3
"""
Review Root Markdown

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/review_root_markdown.py [options]

    Examples:
    $ python scripts/review_root_markdown.py --help

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

import logging

logger = logging.getLogger(__name__)


import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MarkdownFile:
    """Information about a markdown file."""

    path: Path
    size_bytes: int
    last_modified: datetime
    age_days: int
    is_root_level: bool
    category: str  # active, historical, superseded, report, unknown
    references: int  # How many other files reference this
    referenced_by: list[str] = field(default_factory=list)
    recommendation: str = ""  # keep, archive, review
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "size_bytes": self.size_bytes,
            "last_modified": self.last_modified.isoformat(),
            "age_days": self.age_days,
            "is_root_level": self.is_root_level,
            "category": self.category,
            "references": self.references,
            "referenced_by": self.referenced_by[:5],  # Limit to 5
            "recommendation": self.recommendation,
            "confidence": self.confidence,
        }


class MarkdownAnalyzer:
    """Analyzes markdown files for archival recommendations."""

    # Files that should never be archived
    PROTECTED_FILES = {
        "README.md",
        ".codex/archive/deprecated/AGENTS.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "LICENSE.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "pyproject.toml",
        ".gitignore",
    }

    # Patterns indicating superseded content
    SUPERSEDED_PATTERNS = [
        r"superseded",
        r"deprecated",
        r"replaced by",
        r"see instead",
        r"no longer maintained",
        r"archived",
        r"historical",
        r"legacy",
    ]

    # Patterns indicating status reports
    REPORT_PATTERNS = [
        r"status report",
        r"progress report",
        r"weekly update",
        r"daily update",
        r"sprint report",
        r"iteration \d+",
        r"\d{4}-\d{2}-\d{2}.*report",
    ]

    # Patterns indicating active documentation
    ACTIVE_PATTERNS = [
        r"getting started",
        r"installation",
        r"quick start",
        r"api reference",
        r"configuration",
        r"troubleshooting",
        r"faq",
    ]

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.files: list[MarkdownFile] = []
        self.reference_map: dict[str, set[str]] = {}

    def analyze(self) -> list[MarkdownFile]:
        """Analyze all markdown files in the repository."""
        # Find all markdown files
        md_files = list(self.repo_path.glob("*.md"))

        # Build reference map first
        self._build_reference_map()

        # Analyze each file
        for path in md_files:
            if path.name in self.PROTECTED_FILES:
                continue

            file_info = self._analyze_file(path)
            self.files.append(file_info)

        # Sort by recommendation priority
        self.files.sort(
            key=lambda f: (
                0 if f.recommendation == "archive" else 1 if f.recommendation == "review" else 2,
                -f.age_days,
            )
        )

        return self.files

    def _build_reference_map(self) -> None:
        """Build a map of file references."""
        all_md_files = list(self.repo_path.rglob("*.md"))

        for md_file in all_md_files:
            try:
                content = md_file.read_text(errors="ignore")

                # Find all markdown links
                links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

                for _, link in links:
                    # Normalize link path
                    if link.startswith("http"):
                        continue

                    # Handle relative paths
                    try:
                        linked_path = (md_file.parent / link).resolve()
                        rel_path = linked_path.relative_to(self.repo_path)

                        if str(rel_path) not in self.reference_map:
                            self.reference_map[str(rel_path)] = set()
                        self.reference_map[str(rel_path)].add(
                            str(md_file.relative_to(self.repo_path))
                        )
                    except (ValueError, OSError):
                        logger.debug("Suppressed exception in handler", exc_info=True)
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                # Skip files that cannot be processed

    def _analyze_file(self, path: Path) -> MarkdownFile:
        """Analyze a single markdown file."""
        stat = path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        age_days = (datetime.now() - last_modified).days

        # Read content for analysis
        try:
            content = path.read_text(errors="ignore").lower()
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            content = ""

        # Determine category
        category = self._categorize_file(path.name, content)

        # Get reference count
        rel_path = str(path.relative_to(self.repo_path))
        references = len(self.reference_map.get(rel_path, set()))
        referenced_by = list(self.reference_map.get(rel_path, set()))

        # Make recommendation
        recommendation, confidence = self._make_recommendation(
            path.name, content, age_days, references, category
        )

        return MarkdownFile(
            path=path,
            size_bytes=stat.st_size,
            last_modified=last_modified,
            age_days=age_days,
            is_root_level=True,
            category=category,
            references=references,
            referenced_by=referenced_by,
            recommendation=recommendation,
            confidence=confidence,
        )

    def _categorize_file(self, filename: str, content: str) -> str:
        """Categorize a markdown file based on name and content."""
        filename_lower = filename.lower()

        # Check for status reports
        if any(
            re.search(p, filename_lower) or re.search(p, content[:1000])
            for p in self.REPORT_PATTERNS
        ):
            return "report"

        # Check for superseded content
        if any(re.search(p, content[:2000]) for p in self.SUPERSEDED_PATTERNS):
            return "superseded"

        # Check for active documentation
        if any(
            re.search(p, filename_lower) or re.search(p, content[:1000])
            for p in self.ACTIVE_PATTERNS
        ):
            return "active"

        # Check for historical markers
        if "historical" in content[:500] or "archive" in content[:500]:
            return "historical"

        return "unknown"

    def _make_recommendation(
        self,
        filename: str,
        content: str,
        age_days: int,
        references: int,
        category: str,
    ) -> tuple[str, float]:
        """Make archival recommendation."""

        # Protected files
        if filename in self.PROTECTED_FILES:
            return "keep", 1.0

        # High reference count - likely still active
        if references > 5:
            return "keep", 0.8

        # Superseded content
        if category == "superseded":
            return "archive", 0.9

        # Old status reports
        if category == "report" and age_days > 90:
            return "archive", 0.85

        # Very old files with no references
        if age_days > 180 and references == 0:
            return "archive", 0.75

        # Old unknown files
        if category == "unknown" and age_days > 120:
            return "review", 0.6

        # Active documentation
        if category == "active":
            return "keep", 0.85

        # Default: needs review
        if age_days > 60:
            return "review", 0.5

        return "keep", 0.7


def generate_report(files: list[MarkdownFile], format: str = "markdown") -> str:
    """Generate analysis report."""

    if format == "json":
        return json.dumps([f.to_dict() for f in files], indent=2)

    # Markdown format
    lines = [
        "# Root-Level Markdown Review Report",
        "",
        f"**Generated**: {datetime.now().isoformat()[:10]}",
        f"**Total Files Analyzed**: {len(files)}",
        "",
        "## Summary",
        "",
    ]

    # Count by recommendation
    archive_count = sum(1 for f in files if f.recommendation == "archive")
    review_count = sum(1 for f in files if f.recommendation == "review")
    keep_count = sum(1 for f in files if f.recommendation == "keep")

    lines.extend(
        [
            f"- **Archive**: {archive_count} files",
            f"- **Review**: {review_count} files",
            f"- **Keep**: {keep_count} files",
            "",
        ]
    )

    # Archive recommendations
    if archive_count > 0:
        lines.extend(
            [
                "## Recommended for Archival",
                "",
                "| File | Age (days) | Category | Confidence |",
                "|------|------------|----------|------------|",
            ]
        )

        for f in files:
            if f.recommendation == "archive":
                lines.append(
                    f"| `{f.path.name}` | {f.age_days} | {f.category} | {f.confidence:.0%} |"
                )
        lines.append("")

    # Review recommendations
    if review_count > 0:
        lines.extend(
            [
                "## Needs Review",
                "",
                "| File | Age (days) | Category | References |",
                "|------|------------|----------|------------|",
            ]
        )

        for f in files:
            if f.recommendation == "review":
                lines.append(f"| `{f.path.name}` | {f.age_days} | {f.category} | {f.references} |")
        lines.append("")

    # Keep recommendations
    lines.extend(
        [
            "## Active Files (Keep)",
            "",
            "| File | Age (days) | Category | References |",
            "|------|------------|----------|------------|",
        ]
    )

    for f in files:
        if f.recommendation == "keep":
            lines.append(f"| `{f.path.name}` | {f.age_days} | {f.category} | {f.references} |")

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Review and recommend archival for root-level markdown files"
    )
    parser.add_argument(
        "path", type=Path, nargs="?", default=Path("."), help="Repository path to analyze"
    )
    parser.add_argument(
        "--format", "-f", choices=["markdown", "json"], default="markdown", help="Output format"
    )
    parser.add_argument("--output", "-o", type=Path, help="Output file (default: stdout)")
    parser.add_argument(
        "--execute", action="store_true", help="Execute archival (move files to archive)"
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path(".codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review"),
        help="Archive directory",
    )

    args = parser.parse_args()

    # Analyze
    analyzer = MarkdownAnalyzer(args.path)
    files = analyzer.analyze()

    # Generate report
    report = generate_report(files, format=args.format)

    # Output
    if args.output:
        args.output.write_text(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

    # Execute archival if requested
    if args.execute:
        archive_dir = args.path / args.archive_dir
        archive_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            if f.recommendation == "archive":
                dest = archive_dir / f.path.name
                print(f"Archiving: {f.path.name} -> {dest}")
                f.path.rename(dest)


if __name__ == "__main__":
    main()
