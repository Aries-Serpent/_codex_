#!/usr/bin/env python3
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DuplicateGroup:
    """Group of duplicate files."""
    checksum: str
    file_count: int
    total_size: int
    file_paths: list[str]
    can_deduplicate: bool = True


@dataclass
class DeduplicationReport:
    """Report on deduplication analysis."""
    total_files: int
    unique_files: int
    duplicate_files: int
    duplicate_groups: int
    space_wasted: int
    space_after_dedup: int
    potential_savings: int
    duplicate_sets: list[DuplicateGroup]


class ContentDeduplicator:
    """Analyzes and deduplicates content in datasets."""

    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        self.file_checksums: dict[str, str] = {}  # path -> checksum
        self.checksum_files: dict[str, list[str]] = defaultdict(list)  # checksum -> paths
        self.file_sizes: dict[str, int] = {}  # path -> size

    def calculate_checksum(self, filepath: Path, chunk_size: int = 8192) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
            return ""

    def scan_directory(self, skip_patterns: Optional[set[str]] = None) -> int:
        """Scan directory and build checksum index."""
        if skip_patterns is None:
            skip_patterns = {'.git', '__pycache__', 'node_modules', '.venv'}

        print(f"Scanning directory: {self.root_path}")
        count = 0

        for filepath in self.root_path.rglob("*"):
            if not filepath.is_file():
                continue

            # Skip patterns
            if any(pattern in filepath.parts for pattern in skip_patterns):
                continue

            # Calculate checksum
            checksum = self.calculate_checksum(filepath)
            if checksum:
                relative_path = str(filepath.relative_to(self.root_path))
                self.file_checksums[relative_path] = checksum
                self.checksum_files[checksum].append(relative_path)
                self.file_sizes[relative_path] = filepath.stat().st_size
                count += 1

                if count % 100 == 0:
                    print(f"  Scanned {count} files...", end='\r')

        print(f"✓ Scanned {count} files                    ")
        return count

    def analyze_duplicates(self) -> DeduplicationReport:
        """Analyze duplicate files and calculate potential savings."""
        duplicate_sets = []
        duplicate_file_count = 0
        space_wasted = 0

        for checksum, file_list in self.checksum_files.items():
            if len(file_list) > 1:
                # This is a duplicate group
                file_size = self.file_sizes[file_list[0]] if file_list else 0
                total_size = file_size * len(file_list)
                wasted = file_size * (len(file_list) - 1)

                duplicate_sets.append(DuplicateGroup(
                    checksum=checksum[:16],  # Truncate for display
                    file_count=len(file_list),
                    total_size=total_size,
                    file_paths=file_list,
                    can_deduplicate=True
                ))

                duplicate_file_count += len(file_list) - 1
                space_wasted += wasted

        total_files = len(self.file_checksums)
        unique_files = len(self.checksum_files)
        space_after = sum(self.file_sizes.values()) - space_wasted

        return DeduplicationReport(
            total_files=total_files,
            unique_files=unique_files,
            duplicate_files=duplicate_file_count,
            duplicate_groups=len(duplicate_sets),
            space_wasted=space_wasted,
            space_after_dedup=space_after,
            potential_savings=space_wasted,
            duplicate_sets=sorted(duplicate_sets, key=lambda x: x.total_size, reverse=True)
        )

    def create_dedup_strategy(self, report: DeduplicationReport, strategy: str = "keep_first") -> dict[str, str]:
        """Create deduplication strategy mapping.

        Returns: dict mapping source_path -> target_path (for symlinking/hardlinking)
        """
        dedup_map = {}

        for dup_group in report.duplicate_sets:
            if not dup_group.can_deduplicate:
                continue

            # Keep first file, deduplicate others
            keeper = dup_group.file_paths[0]

            for duplicate in dup_group.file_paths[1:]:
                dedup_map[duplicate] = keeper

        return dedup_map

    def save_report(self, report: DeduplicationReport, output_path: Path):
        """Save deduplication report to JSON."""
        report_dict = asdict(report)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)

        print(f"✓ Saved report: {output_path}")

    def print_summary(self, report: DeduplicationReport):
        """Print deduplication summary."""
        print("\n" + "="*60)
        print("Deduplication Analysis")
        print("="*60)
        print(f"Total Files: {report.total_files}")
        print(f"Unique Files: {report.unique_files}")
        print(f"Duplicate Files: {report.duplicate_files}")
        print(f"Duplicate Groups: {report.duplicate_groups}")
        print("\nSpace Analysis:")
        print(f"  Space Wasted: {report.space_wasted / 1024 / 1024:.2f} MB")
        print(f"  Space After Dedup: {report.space_after_dedup / 1024 / 1024:.2f} MB")
        print(f"  Potential Savings: {report.potential_savings / 1024 / 1024:.2f} MB")
        print(f"  Savings Percentage: {report.potential_savings / max(report.space_wasted + report.space_after_dedup, 1) * 100:.1f}%")

        if report.duplicate_sets:
            print("\nTop 5 Duplicate Groups:")
            for i, dup_group in enumerate(report.duplicate_sets[:5], 1):
                print(f"  {i}. {dup_group.file_count} copies, {dup_group.total_size / 1024:.1f} KB total")
                print(f"     Checksum: {dup_group.checksum}")
                for path in dup_group.file_paths[:3]:  # Show first 3
                    print(f"       - {path}")
                if len(dup_group.file_paths) > 3:
                    print(f"       ... and {len(dup_group.file_paths) - 3} more")

        print("="*60)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Content deduplication analysis")
    parser.add_argument("path", type=Path, help="Directory to analyze")
    parser.add_argument("--output", type=Path,
                       help="Output path for deduplication report")
    parser.add_argument("--skip", nargs="+", default=[],
                       help="Patterns to skip (e.g., .git __pycache__)")

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1

    # Run deduplication analysis
    deduplicator = ContentDeduplicator(args.path)
    skip_patterns = set(args.skip) if args.skip else None
    deduplicator.scan_directory(skip_patterns)

    # Analyze
    report = deduplicator.analyze_duplicates()

    # Save report if requested
    if args.output:
        deduplicator.save_report(report, args.output)

    # Print summary
    deduplicator.print_summary(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
