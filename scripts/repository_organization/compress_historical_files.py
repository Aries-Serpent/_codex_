#!/usr/bin/env python3
"""
Historical Files Compression Script

Purpose:
    Compress historical files in offload directories to reduce storage

Usage:
    python scripts/repository_organization/compress_historical_files.py [options]

    Examples:
    $ python scripts/repository_organization/compress_historical_files.py --category historical-coverage
    $ python scripts/repository_organization/compress_historical_files.py --all
    $ python scripts/repository_organization/compress_historical_files.py --dry-run

Arguments:
    --category: Compress files in a specific category
    --all: Compress files in all eligible categories
    --min-age-days: Minimum file age for compression (default: 180)
    --dry-run: Show what would be compressed without making changes
    --log-actions: Log compression to action log (default: True)

Exit Codes:
    0: Success
    1: Error

Author: QA Walkthrough Agent
Last Updated: 2026-01-26
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Canonical archive root after the move; fall back to the legacy root for compatibility.
CANONICAL_OFFLOAD_ROOT = Path(".codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review")
LEGACY_OFFLOAD_ROOT = Path("misc/repo-owner-review")


def resolve_offload_root(repo_root: Path) -> Path:
    canonical = repo_root / CANONICAL_OFFLOAD_ROOT
    legacy = repo_root / LEGACY_OFFLOAD_ROOT
    return canonical if canonical.exists() or not legacy.exists() else legacy


OFFLOAD_ROOT = CANONICAL_OFFLOAD_ROOT

# Categories eligible for compression
COMPRESSIBLE_CATEGORIES = {
    "historical-coverage",
    "historical-logs",
    "historical-artifacts",
}

# File extensions to compress individually
COMPRESS_INDIVIDUALLY = {".json", ".md", ".log", ".txt", ".xml", ".yaml", ".yml"}


def get_file_age_days(file_path: Path) -> int:
    """Get file age in days based on modification time."""
    try:
        mtime = file_path.stat().st_mtime
        age_seconds = datetime.now(timezone.utc).timestamp() - mtime
        return int(age_seconds / 86400)
    except (OSError, ValueError):
        return 0


def compress_file_gzip(source_path: Path, dry_run: bool = False) -> Path | None:
    """Compress a single file with gzip."""
    if source_path.suffix == ".gz":
        return None  # Already compressed

    dest_path = source_path.with_suffix(source_path.suffix + ".gz")

    if dry_run:
        print(f"  [DRY RUN] Would compress: {source_path.name} → {dest_path.name}")
        return dest_path

    try:
        with open(source_path, "rb") as f_in, gzip.open(dest_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        # Capture original size before removing original file
        original_size = source_path.stat().st_size

        # Remove original file
        source_path.unlink()

        # Calculate compression ratio
        compressed_size = dest_path.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        print(f"  ✅ Compressed: {source_path.name} → {dest_path.name} ({ratio:.1f}% reduction)")
        return dest_path

    except Exception as e:
        print(f"  ❌ Failed to compress {source_path.name}: {e}")
        return None


def compress_directory_tarball(
    category: str,
    repo_root: Path,
    dry_run: bool = False,
) -> Path | None:
    """Compress entire category directory into a tarball."""
    category_path = resolve_offload_root(repo_root) / category

    if not category_path.exists():
        return None

    # Create archive name with timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    archive_name = f"{category}_{timestamp}.tar.gz"
    archive_path = category_path.parent / archive_name

    if dry_run:
        print(f"  [DRY RUN] Would create archive: {archive_name}")
        return archive_path

    try:
        # Create tarball
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(category_path, arcname=category)

        # Calculate sizes
        original_size = sum(
            f.stat().st_size for f in category_path.rglob("*") if f.is_file()
        )
        compressed_size = archive_path.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        print(f"  ✅ Created archive: {archive_name}")
        print(f"     Original: {original_size / (1024*1024):.2f}MB")
        print(f"     Compressed: {compressed_size / (1024*1024):.2f}MB")
        print(f"     Reduction: {ratio:.1f}%")

        return archive_path

    except Exception as e:
        print(f"  ❌ Failed to create archive for {category}: {e}")
        return None


def compress_category(
    category: str,
    repo_root: Path,
    min_age_days: int,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Compress files in a category."""
    category_path = resolve_offload_root(repo_root) / category

    if not category_path.exists():
        print(f"❌ Category not found: {category}")
        return {"success": False, "files_compressed": 0}

    print(f"📦 Compressing category: {category}")
    print(f"   Minimum age: {min_age_days} days")
    print()

    files_compressed = 0
    total_original_size = 0
    total_compressed_size = 0

    # Compress individual files
    for file_path in category_path.rglob("*"):
        if not file_path.is_file() or file_path.name == "README.md":
            continue

        # Check age
        age_days = get_file_age_days(file_path)
        if age_days < min_age_days:
            continue

        # Check if file should be compressed
        if file_path.suffix in COMPRESS_INDIVIDUALLY:
            original_size = file_path.stat().st_size
            compressed_path = compress_file_gzip(file_path, dry_run)

            if compressed_path:
                files_compressed += 1
                total_original_size += original_size
                if not dry_run and compressed_path.exists():
                    total_compressed_size += compressed_path.stat().st_size

    # Calculate overall compression ratio
    if total_original_size > 0:
        overall_ratio = (1 - total_compressed_size / total_original_size) * 100
    else:
        overall_ratio = 0

    return {
        "success": True,
        "files_compressed": files_compressed,
        "original_size_mb": round(total_original_size / (1024*1024), 2),
        "compressed_size_mb": round(total_compressed_size / (1024*1024), 2),
        "compression_ratio": round(overall_ratio, 1),
    }


def log_to_action_log(
    category: str,
    results: dict[str, Any],
    repo_root: Path,
) -> None:
    """Log compression to action log."""
    action_log_path = repo_root / ".codex" / "action_log.ndjson"

    action_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "repository-organization-compress",
        "action": "compress_historical_files",
        "category": "repository_organization",
        "details": {
            "category": category,
            "files_compressed": results["files_compressed"],
            "original_size_mb": results.get("original_size_mb", 0),
            "compressed_size_mb": results.get("compressed_size_mb", 0),
            "compression_ratio": results.get("compression_ratio", 0),
        },
        "outcome": "success" if results["files_compressed"] > 0 else "no_action",
        "impact": f"Compressed {results['files_compressed']} file(s) with {results.get('compression_ratio', 0):.1f}% reduction",
    }

    try:
        with open(action_log_path, "a") as f:
            f.write(json.dumps(action_entry) + "\n")
        print(f"✅ Logged to {action_log_path}")
    except Exception as e:
        print(f"⚠️ Failed to log to action log: {e}", file=sys.stderr)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compress historical files in offload directories"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=list(COMPRESSIBLE_CATEGORIES),
        help="Compress files in a specific category",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Compress files in all eligible categories",
    )
    parser.add_argument(
        "--min-age-days",
        type=int,
        default=180,
        help="Minimum file age for compression (default: 180)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be compressed without making changes",
    )
    parser.add_argument(
        "--log-actions",
        action="store_true",
        dest="log_actions",
        help="Log compression to action log (default: True)",
    )
    parser.add_argument(
        "--no-log-actions",
        action="store_false",
        dest="log_actions",
        help="Do not log compression to action log",
    )
    parser.set_defaults(log_actions=True)

    args = parser.parse_args()

    repo_root = Path.cwd()

    # Validate arguments
    if not args.category and not args.all:
        print("❌ Error: Must specify --category or --all", file=sys.stderr)
        parser.print_help()
        return 1

    # Determine categories to compress
    categories = list(COMPRESSIBLE_CATEGORIES) if args.all else [args.category]

    # Compress each category
    total_files = 0
    total_savings_mb = 0.0

    for category in categories:
        results = compress_category(
            category,
            repo_root,
            args.min_age_days,
            args.dry_run,
        )

        if results["success"]:
            total_files += results["files_compressed"]
            if not args.dry_run:
                savings = results.get("original_size_mb", 0) - results.get("compressed_size_mb", 0)
                total_savings_mb += savings

            # Log to action log
            if args.log_actions and not args.dry_run and results["files_compressed"] > 0:
                log_to_action_log(category, results, repo_root)

        print()

    # Print overall summary
    print("📊 Compression Summary:")
    print(f"  ✅ Total files compressed: {total_files}")
    if not args.dry_run:
        print(f"  💾 Total storage saved: {total_savings_mb:.2f} MB")

    if args.dry_run:
        print("\n⚠️  DRY RUN - No files were actually compressed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
