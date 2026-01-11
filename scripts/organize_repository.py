#!/usr/bin/env python3
"""
Repository Organization and Archival Script
Organizes root directory markdown files and creates AI-queryable archive
"""
import argparse
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Files to preserve in root (core documentation)
DEFAULT_PRESERVE_FILES = {
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "GOVERNANCE.md",
    "LICENSE",
    "CHANGELOG.md",
    "CHANGES.md",
    "CITATION.cff",
}

# Patterns for files to archive
DEFAULT_ARCHIVE_PATTERNS = [
    "STATUS",
    "REPORT",
    "SUMMARY",
    "COMPLETE",
    "ACHIEVEMENT",
    "PHASE",
    "WAVE",
    "PROGRESS",
    "AUDIT",
    "VALIDATION",
    "VERIFICATION",
    "IMPLEMENTATION",
    "FINAL",
    "NEXT",
    "PROMPT",
    "PLAN",
    "GAP",
    "REMEDIATION",
    "CAPABILITY",
]


def should_archive(filename: str, preserve_files: set[str], archive_patterns: list[str]) -> bool:
    """Determine if a file should be archived"""
    if filename in preserve_files:
        return False

    # Check if filename contains archive patterns
    upper_name = filename.upper()
    for pattern in archive_patterns:
        if pattern in upper_name:
            return True

    return False


def analyze_file(filepath: Path) -> dict:
    """Analyze markdown file and extract metadata"""
    try:
        stat = filepath.stat()
        content = filepath.read_text(encoding="utf-8", errors="ignore")

        # Extract first heading as title
        title = None
        for line in content.split("\n")[:10]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        return {
            "filename": filepath.name,
            "path": str(filepath),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "title": title or filepath.stem,
            "line_count": len(content.split("\n")),
            "word_count": len(content.split()),
        }
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.debug("Exception caught, returning", exc_info=True)
        return {"filename": filepath.name, "path": str(filepath), "error": str(e)}


def create_archive_index(archive_dir: Path, archived_files: list[Path]) -> None:
    """Create searchable index of archived files"""
    index = {
        "created_at": datetime.now().isoformat(),
        "total_files": len(archived_files),
        "files": [],
    }

    for filepath in archived_files:
        if filepath.exists():
            metadata = analyze_file(filepath)
            index["files"].append(metadata)

    # Save index
    index_path = archive_dir / "INDEX.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

    logger.info(f"Created archive index: {index_path}")

    # Create markdown index for human readability
    md_index_path = archive_dir / "INDEX.md"
    with open(md_index_path, "w") as f:
        f.write(f"# Archive Index\n\n")
        f.write(f"Created: {index['created_at']}\n\n")
        f.write(f"Total Files: {index['total_files']}\n\n")
        f.write(f"## Files\n\n")

        # Sort by modified date
        sorted_files = sorted(index["files"], key=lambda x: x.get("modified", ""), reverse=True)

        for file_meta in sorted_files:
            if "error" not in file_meta:
                f.write(f"### {file_meta['title']}\n")
                f.write(f"- **File**: {file_meta['filename']}\n")
                f.write(f"- **Modified**: {file_meta['modified']}\n")
                f.write(f"- **Size**: {file_meta['size']:,} bytes\n")
                f.write(f"- **Lines**: {file_meta.get('line_count', 0):,}\n")
                f.write(f"- **Words**: {file_meta.get('word_count', 0):,}\n")
                f.write(f"\n")

    logger.info(f"Created markdown index: {md_index_path}")


def organize_repository(
    dry_run: bool = False, preserve_files: set[str] = None, archive_patterns: list[str] = None
) -> None:
    """Organize repository by archiving old status/report files"""
    if preserve_files is None:
        preserve_files = DEFAULT_PRESERVE_FILES
    if archive_patterns is None:
        archive_patterns = DEFAULT_ARCHIVE_PATTERNS

    root = Path(".")
    archive_date = datetime.now().strftime("%Y%m%d")
    archive_dir = root / f"archive/historical_docs_{archive_date}"

    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    # Find all markdown files in root
    md_files = list(root.glob("*.md"))
    logger.info(f"Found {len(md_files)} markdown files in root")

    # Categorize files
    to_preserve: list[Path] = []
    to_archive: list[Path] = []

    for md_file in md_files:
        if should_archive(md_file.name, preserve_files, archive_patterns):
            to_archive.append(md_file)
        else:
            to_preserve.append(md_file)

    logger.info(f"\nFiles to preserve: {len(to_preserve)}")
    for f in sorted(to_preserve):
        logger.info(f"  ✓ {f.name}")

    logger.info(f"\nFiles to archive: {len(to_archive)}")
    for f in sorted(to_archive)[:20]:  # Show first 20
        logger.info(f"  → {f.name}")
    if len(to_archive) > 20:
        logger.info(f"  ... and {len(to_archive) - 20} more")

    if dry_run:
        logger.info("\n[DRY RUN] No files were moved")
        return

    # Archive files
    archived_files: list[Path] = []
    for md_file in to_archive:
        try:
            dest = archive_dir / md_file.name
            shutil.move(str(md_file), str(dest))
            archived_files.append(dest)
            logger.info(f"Archived: {md_file.name}")
        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.error(f"File not found - {md_file.name}")
        except PermissionError as e:
            logger.debug(f"PermissionError: {e}")
            logger.warning(f"PermissionError: {e}", exc_info=True)
            logger.error(f"Permission denied - {md_file.name}")
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Unexpected error archiving {md_file.name}: {e}")

    # Create archive index
    if archived_files:
        create_archive_index(archive_dir, archived_files)

    logger.info(f"\n✅ Organization complete!")
    logger.info(f"Preserved {len(to_preserve)} core files")
    logger.info(f"Archived {len(archived_files)} files to {archive_dir}")

    # Create summary
    summary = {
        "organized_at": datetime.now().isoformat(),
        "preserved_count": len(to_preserve),
        "archived_count": len(archived_files),
        "archive_location": str(archive_dir),
    }

    summary_path = root / "REPOSITORY_ORGANIZATION_SUMMARY.md"
    with open(summary_path, "w") as f:
        f.write(f"# Repository Organization Summary\n\n")
        f.write(f"**Date**: {summary['organized_at']}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Files Preserved**: {summary['preserved_count']}\n")
        f.write(f"- **Files Archived**: {summary['archived_count']}\n")
        f.write(f"- **Archive Location**: `{summary['archive_location']}`\n\n")
        f.write(f"## Preserved Files\n\n")
        f.write(f"The following core documentation files remain in the root:\n\n")
        for f_path in sorted(to_preserve):
            f.write(f"- `{f_path.name}`\n")
        f.write(f"\n## Archived Files\n\n")
        f.write(f"Historical status reports, summaries, and documentation have been archived to:\n")
        f.write(f"`{archive_dir}/`\n\n")
        f.write(f"See `{archive_dir}/INDEX.md` for a complete list of archived files.\n\n")
        f.write(f"## AI Query Interface\n\n")
        f.write(f"Archived files remain searchable and queryable by AI Agents through:\n")
        f.write(f"- JSON index: `{archive_dir}/INDEX.json`\n")
        f.write(f"- Markdown index: `{archive_dir}/INDEX.md`\n\n")
        f.write(f"## Accessing Archived Files\n\n")
        f.write(f"To view archived files:\n")
        f.write(f"```bash\n")
        f.write(f"# list archived files\n")
        f.write(f"ls -la {archive_dir}/\n\n")
        f.write(f"# View specific archived file\n")
        f.write(f"cat {archive_dir}/FILENAME.md\n\n")
        f.write(f"# Search archived content\n")
        f.write(f"grep -r 'search term' {archive_dir}/\n")
        f.write(f"```\n")

    logger.info(f"Created summary: {summary_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Organize repository by archiving old status/report files"
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be done without actually moving files",
    )
    parser.add_argument(
        "--preserve", nargs="+", help="Additional files to preserve (beyond defaults)"
    )
    parser.add_argument(
        "--pattern",
        nargs="+",
        help="Additional patterns to match for archiving (e.g., STATUS REPORT)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON config file with preserve_files and archive_patterns",
    )

    args = parser.parse_args()

    # Load configuration
    preserve_files = DEFAULT_PRESERVE_FILES.copy()
    archive_patterns = DEFAULT_ARCHIVE_PATTERNS.copy()

    if args.config and args.config.exists():
        with open(args.config) as f:
            config = json.load(f)
            if "preserve_files" in config:
                preserve_files.update(config["preserve_files"])
            if "archive_patterns" in config:
                archive_patterns.extend(config["archive_patterns"])

    if args.preserve:
        preserve_files.update(args.preserve)

    if args.pattern:
        archive_patterns.extend(args.pattern)

    if args.dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No files will be moved")
        logger.info("=" * 60)

    organize_repository(
        dry_run=args.dry_run, preserve_files=preserve_files, archive_patterns=archive_patterns
    )
