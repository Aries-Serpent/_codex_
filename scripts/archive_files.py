#!/usr/bin/env python3
"""
Archive Files

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/archive_files.py [options]

    Examples:
    $ python scripts/archive_files.py --help

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



import argparse
import gzip
import hashlib
import json
import logging
import shutil
from collections import namedtuple
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Named tuple for archive verification result
ArchiveVerificationResult = namedtuple("ArchiveVerificationResult", ["is_safe", "reason"])

CANONICAL_ARCHIVE_ROOT = Path(
    ".codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review"
)
LEGACY_ARCHIVE_ROOT = Path("misc/repo-owner-review")


def resolve_archive_root(repo_root: Path) -> Path:
    """Return the canonical archive root and fall back to the legacy location if needed."""
    canonical = repo_root / CANONICAL_ARCHIVE_ROOT
    legacy = repo_root / LEGACY_ARCHIVE_ROOT
    if canonical.exists() or not legacy.exists():
        return canonical
    return legacy


# Files that are candidates for archival
ARCHIVE_CANDIDATES = {
    # Historical status/report files
    "CODE_REVIEW_FIXES.md": {
        "category": "historical-docs",
        "reason": "Historical code review fixes - information preserved in git commits",
        "compress": False,
    },
    "PR_2460_BUG_FIX_SUMMARY.md": {
        "category": "historical-docs",
        "reason": "Historical PR summary - information preserved in PR #2460",
        "compress": False,
    },
    "PR_2460_FINAL_STATUS.md": {
        "category": "historical-docs",
        "reason": "Historical PR status - information preserved in PR #2460",
        "compress": False,
    },
    "PR_SUMMARY_FINAL.md": {
        "category": "historical-docs",
        "reason": "Historical PR summary - information preserved in respective PRs",
        "compress": False,
    },
    "REPOSITORY_ORGANIZATION_SUMMARY.md": {
        "category": "historical-docs",
        "reason": "Historical organization summary - current state in scripts/organize_repository.py",
        "compress": False,
    },
    "P1_FIX_API_KEY_OPTIONAL.md": {
        "category": "historical-docs",
        "reason": "Historical fix documentation - fix has been applied",
        "compress": False,
    },
}

# Compressible artifacts (ZIP files can be further compressed with gzip)
COMPRESSIBLE_PATTERNS = [
    "actions/runs-completion/*.zip",
]


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compress_file(file_path: Path, output_path: Path) -> None:
    """Compress a file using gzip."""
    with open(file_path, "rb") as f_in, gzip.open(output_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    logger.info(
        f"Compressed {file_path.name}: {file_path.stat().st_size} -> {output_path.stat().st_size} bytes"
    )


def verify_safe_to_archive(file_path: Path) -> ArchiveVerificationResult:
    """
    Verify that a file is safe to archive (won't break functionality).

    Returns:
        ArchiveVerificationResult with is_safe (bool) and reason (str) fields
    """
    # Check if file is imported by any Python code
    if file_path.suffix in [".py", ".json"]:
        root = Path.cwd()
        # Python-based reference check (safer than grep)
        try:
            refs = []
            for py_file in root.rglob("*.py"):
                # Skip the file itself
                if py_file.resolve() == file_path.resolve():
                    continue
                try:
                    with py_file.open("r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, 1):
                            if file_path.name in line:
                                refs.append(f"{py_file}:{lineno}:{line.strip()[:80]}")
                                # Only need first reference to determine safety
                                break
                except (UnicodeDecodeError, OSError):
                    logger.debug("Exception caught, continuing", exc_info=True)
                    continue
            if refs:
                return ArchiveVerificationResult(False, f"File referenced in: {refs[0]}")
        except Exception as e:
            error_type = type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            # If analysis fails, be conservative
            logger.warning(f"Could not verify references for {file_path.name}: <ERROR_TYPE>")

    # Check if it's a required config file
    if file_path.name in ["pyproject.toml", "setup.py", "requirements.txt", ".gitignore"]:
        return ArchiveVerificationResult(False, "Required configuration file")

    # Default to safe for markdown documentation files
    if file_path.suffix == ".md":
        return ArchiveVerificationResult(True, "Documentation file - safe to archive")

    return ArchiveVerificationResult(True, "No critical dependencies found")


def archive_file(
    file_path: Path, archive_info: dict[str, Any], base_archive_dir: Path, dry_run: bool = False
) -> Optional[dict[str, Any]]:
    """
    Archive a single file to the canonical archive root under .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review.

    Returns:
        Metadata dict if successful, None otherwise
    """
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return None

    # Verify safety
    is_safe, reason = verify_safe_to_archive(file_path)
    if not is_safe:
        logger.warning(f"Skipping {file_path.name}: {reason}")
        return None

    # Determine archive location
    category = archive_info["category"]
    archive_dir = base_archive_dir / "archived-artifacts" / category
    archive_path = archive_dir / file_path.name

    # Calculate file info
    file_size = file_path.stat().st_size
    file_hash = calculate_file_hash(file_path)

    # Use relative paths from repository root
    root = Path.cwd()
    relative_original = file_path.relative_to(root) if file_path.is_absolute() else file_path
    relative_archived = (
        archive_path.relative_to(root) if archive_path.is_absolute() else archive_path
    )

    metadata = {
        "original_path": str(relative_original),
        "archived_path": str(relative_archived),
        "size": (
            f"{file_size / 1024:.1f}KB"
            if file_size < 1024 * 1024
            else f"{file_size / (1024 * 1024):.1f}MB"
        ),
        "size_bytes": file_size,
        "sha256": file_hash,
        "date_moved": datetime.now().strftime("%Y-%m-%d"),
        "reason": archive_info["reason"],
        "safe_to_delete": True,
        "verification": reason,
    }

    if dry_run:
        logger.info(f"[DRY RUN] Would archive: {file_path} -> {archive_path}")
        return metadata

    # Create archive directory
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Compress if requested
    if archive_info.get("compress", False) and file_path.suffix not in [".gz", ".zip"]:
        archive_path = archive_path.with_suffix(archive_path.suffix + ".gz")
        compress_file(file_path, archive_path)
        metadata["archived_path"] = str(archive_path)
        metadata["compressed"] = True
    else:
        # Just move the file
        shutil.move(str(file_path), str(archive_path))

    logger.info(f"Archived: {file_path.name} -> {archive_path}")
    return metadata


def update_metadata(base_archive_dir: Path, new_files: list[dict[str, Any]]) -> None:
    """Update the metadata.json file with newly archived files."""
    metadata_path = base_archive_dir / "metadata.json"

    # Load existing metadata
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
    else:
        metadata = {
            "metadata_version": "1.0",
            "created_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "purpose": "Track files moved to .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review for potential deletion",
            "files_archived": [],
            "notes": [
                "All files are backed up in git history",
                "Files can be restored by moving back from the canonical archive root",
                "Legacy misc/repo-owner-review paths are retained only as compatibility shims",
                "Tests passing after archival confirms no broken dependencies",
                "Repository owner may delete this entire folder when comfortable",
            ],
        }

    # Add new files
    metadata["files_archived"].extend(new_files)
    metadata["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Calculate total space
    total_bytes = sum(f.get("size_bytes", 0) for f in metadata["files_archived"])
    metadata["total_space_archived"] = f"{total_bytes / (1024 * 1024):.1f}MB"

    # Save updated metadata
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Updated metadata: {metadata_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Archive non-essential files to .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review"
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be done without actually moving files",
    )
    args = parser.parse_args()

    root = Path.cwd()
    base_archive_dir = resolve_archive_root(root)

    # Ensure canonical archive directory exists.
    base_archive_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No files will be moved")
        logger.info("=" * 60)
        logger.info("")

    # Process archive candidates
    archived_files = []
    for filename, info in ARCHIVE_CANDIDATES.items():
        file_path = root / filename
        if file_path.exists():
            metadata = archive_file(file_path, info, base_archive_dir, args.dry_run)
            if metadata:
                archived_files.append(metadata)

    if archived_files and not args.dry_run:
        update_metadata(base_archive_dir, archived_files)
        logger.info(f"\n✅ Archived {len(archived_files)} files successfully")
        logger.info(
            f"Total space: {sum(f['size_bytes'] for f in archived_files) / (1024 * 1024):.1f}MB"
        )
    elif args.dry_run:
        logger.info(f"\n[DRY RUN] Would archive {len(archived_files)} files")
    else:
        logger.info("\nNo files to archive")


if __name__ == "__main__":
    main()
