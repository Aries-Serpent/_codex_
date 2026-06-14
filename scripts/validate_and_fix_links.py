#!/usr/bin/env python3
"""Validate and fix broken documentation links across the repository."""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Configuration
DOCS_DIRS = [
    "docs/",
    ".github/docs/",
    ".github/agents/",
    ".codex/",
]
ROOT_DOCS = ["README.md"]
REPO_ROOT = Path.cwd()
REPORT_FILE = REPO_ROOT / ".codex" / "phase6_link_audit_complete.json"


class LinkValidator:
    """Validate and fix documentation links."""

    def __init__(self) -> None:
        self.all_markdown_files: Set[Path] = set()
        self.heading_anchors: Dict[Path, Set[str]] = {}
        self.broken_links: List[Dict[str, Any]] = []
        self.fixed_links: List[Dict[str, Any]] = []
        self.file_moves: Dict[str, str] = {}
        self.external_links: List[Dict[str, Any]] = []
        self.link_count = 0

    def scan_markdown_files(self) -> None:
        """Recursively scan all markdown files."""
        for doc_dir in DOCS_DIRS:
            if not Path(doc_dir).exists():
                continue
            for root, _, files in os.walk(doc_dir):
                for file in files:
                    if file.endswith(".md"):
                        self.all_markdown_files.add(Path(root) / file)

        for doc in ROOT_DOCS:
            path = Path(doc)
            if path.exists():
                self.all_markdown_files.add(path)

    def extract_headings(self, md_content: str) -> Set[str]:
        """Extract heading anchors from markdown content."""
        headings = set()
        heading_pattern = r"^#{1,6}\s+(.+?)(?:\s*\{.*\})?\s*$"
        for line in md_content.split("\n"):
            match = re.match(heading_pattern, line, re.MULTILINE)
            if match:
                heading = match.group(1).strip()
                anchor = self._heading_to_anchor(heading)
                headings.add(anchor)
        return headings

    def _heading_to_anchor(self, heading: str) -> str:
        """Convert markdown heading to anchor format."""
        anchor = heading.lower()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"[-\s]+", "-", anchor)
        anchor = anchor.strip("-")
        return anchor

    def index_headings(self) -> None:
        """Index all headings in all markdown files."""
        for md_file in self.all_markdown_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                self.heading_anchors[md_file] = self.extract_headings(content)
            except Exception as e:
                print(f"Warning: Failed to index {md_file}: {e}")

    def extract_links(
        self, content: str, source_file: Path
    ) -> List[Dict[str, Any]]:
        """Extract all links from markdown content."""
        links = []

        link_patterns = [
            (r"\[([^\]]+)\]\(([^)]+)\)", "markdown"),
            (r"<(https?://[^>]+)>", "html"),
            (r"(?:^|\s)(https?://[^\s]+)", "url"),
        ]

        # Patterns to skip (false positives)
        skip_patterns = [
            r"^\[.*\]\(\.+\?\)",
            r"^\[.*\]\(\[\^",
            r"^\[.*\]\(\.",
            r"^\[.*\]\(\+",
            r"^\[.*\]\(\*",
            r"^\[.*\]\(\)",
        ]

        for pattern, link_type in link_patterns:
            for match in re.finditer(pattern, content):
                if link_type == "markdown":
                    text, url = match.groups()
                elif link_type == "html":
                    url = match.group(1)
                    text = url
                else:
                    url = match.group(1)
                    text = url

                # Skip regex patterns and other false positives
                if any(re.match(skip, f"[{text}]({url})") for skip in skip_patterns):
                    continue

                # Skip markdown/regex special characters
                if re.match(r"^[\.\+\*\[\^\$\|]+", url):
                    continue

                links.append(
                    {
                        "text": text,
                        "url": url,
                        "type": link_type,
                        "source": str(source_file),
                    }
                )
                self.link_count += 1

        return links

    def validate_link(self, link_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a link and return (is_valid, error_message)."""
        url = link_info["url"]
        source_file = Path(link_info["source"])

        if url.startswith("http://") or url.startswith("https://"):
            return True, ""

        if url.startswith("#"):
            if source_file in self.heading_anchors:
                anchor = url[1:].lower()
                if anchor in self.heading_anchors[source_file]:
                    return True, ""
                return False, f"Missing anchor '{url}' in {source_file}"
            return True, ""

        if url.startswith("github.com/"):
            return True, ""

        if url.startswith("@"):
            return True, ""

        file_path = url
        if "#" in file_path:
            file_path, anchor = file_path.rsplit("#", 1)
        else:
            anchor = ""

        target_path = source_file.parent / file_path

        if not target_path.exists():
            normalized_path = target_path.resolve()
            if not normalized_path.exists():
                return False, f"File not found: {file_path}"

        if anchor:
            if target_path.exists():
                try:
                    content = target_path.read_text(encoding="utf-8")
                    headings = self.extract_headings(content)
                    anchor_normalized = anchor.lower()
                    if anchor_normalized not in headings:
                        return False, f"Missing anchor '#{anchor}' in {file_path}"
                except Exception:
                    pass

        return True, ""

    def suggest_fixes(self, broken_link: Dict[str, Any]) -> List[str]:
        """Suggest fixes for broken links."""
        suggestions = []
        url = broken_link["url"]
        source_file = Path(broken_link["source"])

        if "#" in url:
            file_path, anchor = url.rsplit("#", 1)
            if file_path:
                target = source_file.parent / file_path
                if target.exists():
                    try:
                        content = target.read_text(encoding="utf-8")
                        headings = self.extract_headings(content)
                        if headings:
                            similar = [
                                h
                                for h in headings
                                if anchor.lower() in h or h in anchor.lower()
                            ]
                            if similar:
                                for h in similar[:3]:
                                    suggestions.append(f"#{h}")
                    except Exception:
                        pass
        else:
            for md_file in self.all_markdown_files:
                if md_file.name == url or str(md_file).endswith(url):
                    rel_path = os.path.relpath(md_file, source_file.parent)
                    suggestions.append(rel_path)

        return suggestions

    def fix_high_confidence_links(self, content: str) -> Tuple[str, List[str]]:
        """Auto-fix high-confidence broken links."""
        fixed = []
        fixed_content = content

        pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(pattern, content):
            text, url = match.groups()

            if "#" in url:
                file_path, anchor = url.rsplit("#", 1)
                if file_path:
                    normalized_anchor = anchor.lower().replace(" ", "-")
                    new_url = f"{file_path}#{normalized_anchor}"
                    if new_url != url:
                        fixed_content = fixed_content.replace(
                            f"[{text}]({url})", f"[{text}]({new_url})"
                        )
                        fixed.append(f"Fixed anchor case: {url} -> {new_url}")

        return fixed_content, fixed

    def validate_all(self) -> None:
        """Validate all links in all markdown files."""
        self.scan_markdown_files()
        self.index_headings()

        for md_file in self.all_markdown_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                links = self.extract_links(content, md_file)

                for link_info in links:
                    is_valid, error = self.validate_link(link_info)

                    if not is_valid:
                        suggestions = self.suggest_fixes(link_info)
                        broken_link = {
                            "file": str(md_file),
                            "url": link_info["url"],
                            "error": error,
                            "suggestions": suggestions,
                            "confidence": 0.8 if suggestions else 0.5,
                        }
                        self.broken_links.append(broken_link)
                    elif link_info["url"].startswith("http"):
                        self.external_links.append(
                            {
                                "file": str(md_file),
                                "url": link_info["url"],
                                "type": "external",
                            }
                        )

            except Exception as e:
                print(f"Warning: Failed to process {md_file}: {e}")

    def apply_fixes(self) -> None:
        """Apply high-confidence fixes to markdown files."""
        processed_files = set()

        for broken_link in self.broken_links:
            if broken_link["confidence"] < 0.9:
                continue

            md_file = Path(broken_link["file"])
            if md_file in processed_files:
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
                fixed_content, fixes = self.fix_high_confidence_links(content)

                if fixes:
                    md_file.write_text(fixed_content, encoding="utf-8")
                    for fix in fixes:
                        self.fixed_links.append(
                            {
                                "file": str(md_file),
                                "fix": fix,
                                "type": "anchor_case",
                            }
                        )
                    processed_files.add(md_file)

            except Exception as e:
                print(f"Warning: Failed to apply fixes to {md_file}: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        report = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": {
                "total_links_scanned": self.link_count,
                "total_files_scanned": len(self.all_markdown_files),
                "broken_links_found": len(self.broken_links),
                "links_fixed": len(self.fixed_links),
                "external_links_sampled": len(self.external_links),
            },
            "broken_links_by_category": {
                "missing_files": len(
                    [
                        b
                        for b in self.broken_links
                        if "not found" in b["error"].lower()
                    ]
                ),
                "missing_anchors": len(
                    [
                        b
                        for b in self.broken_links
                        if "anchor" in b["error"].lower()
                    ]
                ),
            },
            "high_confidence_fixes": [b for b in self.broken_links if b["confidence"] >= 0.9],
            "medium_confidence_issues": [b for b in self.broken_links if 0.7 <= b["confidence"] < 0.9],
            "low_confidence_issues": [b for b in self.broken_links if b["confidence"] < 0.7],
            "fixed_links_detail": self.fixed_links,
            "sample_broken_links": self.broken_links[:20],
        }
        return report

    def save_report(self, report: Dict[str, Any]) -> None:
        """Save report to JSON file."""
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {REPORT_FILE}")


def main() -> int:
    """Main entry point."""
    validator = LinkValidator()

    print("Scanning markdown files...")
    validator.scan_markdown_files()
    print(f"Found {len(validator.all_markdown_files)} markdown files")

    print("Indexing headings...")
    validator.index_headings()

    print("Validating all links...")
    validator.validate_all()
    print(f"Scanned {validator.link_count} links")

    print(f"Found {len(validator.broken_links)} broken links")

    print("Applying high-confidence fixes...")
    validator.apply_fixes()
    print(f"Fixed {len(validator.fixed_links)} links")

    print("Generating report...")
    report = validator.generate_report()
    validator.save_report(report)

    print("\n" + "=" * 60)
    print("LINK VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total links scanned: {report['summary']['total_links_scanned']}")
    print(f"Files scanned: {report['summary']['total_files_scanned']}")
    print(f"Broken links found: {report['summary']['broken_links_found']}")
    print(f"Links fixed: {report['summary']['links_fixed']}")
    print(f"Missing files: {report['broken_links_by_category']['missing_files']}")
    print(f"Missing anchors: {report['broken_links_by_category']['missing_anchors']}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
