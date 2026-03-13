#!/usr/bin/env python3
"""
Cognitive Brain Status Rotation — archives old status files once the count
exceeds a configurable threshold.

Keeps the N most recent files (by filename sort, descending) in place and
moves older files to `.codex/cognitive_brain/status/archive/`.  A manifest
JSON records what was rotated.

Usage
-----
    # Dry-run (preview what would be archived)
    python scripts/ci/rotate_cognitive_brain_status.py --dry-run

    # Rotate keeping 50 most-recent files (default)
    python scripts/ci/rotate_cognitive_brain_status.py

    # Custom threshold
    python scripts/ci/rotate_cognitive_brain_status.py --keep 30 --threshold 40
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATUS_DIR = Path(".codex/cognitive_brain/status")
ARCHIVE_DIR = STATUS_DIR / "archive"
MANIFEST_FILE = ARCHIVE_DIR / "rotation_manifest.json"

DEFAULT_KEEP = 50
DEFAULT_THRESHOLD = 60


def rotate(keep: int = DEFAULT_KEEP, threshold: int = DEFAULT_THRESHOLD, dry_run: bool = False) -> list[str]:
    """Archive old cognitive brain status files.

    Returns list of filenames that were (or would be) archived.
    """
    if not STATUS_DIR.exists():
        print(f"⚠️  {STATUS_DIR} does not exist — skipping rotation")
        return []

    md_files = sorted(
        [f for f in STATUS_DIR.iterdir() if f.is_file() and f.suffix == ".md"],
        key=lambda f: f.name,
        reverse=True,  # newest names last alphabetically → keep most-recent
    )

    total = len(md_files)
    if total <= threshold:
        print(f"ℹ️  {total} status file(s) present — below threshold ({threshold}); no rotation needed.")
        return []

    to_archive = md_files[keep:]  # keep the first `keep` (newest), archive the rest
    print(f"📦 Rotating {len(to_archive)} of {total} status files (keeping newest {keep})...")

    if dry_run:
        for f in to_archive:
            print(f"  [DRY RUN] Would archive: {f.name}")
        return [f.name for f in to_archive]

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    archived: list[str] = []
    for f in to_archive:
        dest = ARCHIVE_DIR / f.name
        if not dest.exists():
            f.rename(dest)
            print(f"  🗄  Archived: {f.name}")
        else:
            print(f"  ⏭  Already in archive: {f.name}")
        archived.append(f.name)

    # Update rotation manifest
    manifest: dict = {}
    if MANIFEST_FILE.exists():
        try:
            manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}

    manifest.setdefault("rotations", []).append(
        {
            "rotated_at": datetime.now(timezone.utc).isoformat(),
            "files_rotated": len(archived),
            "files_kept": keep,
            "total_before": total,
            "filenames": archived,
        }
    )
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"✅ Rotation complete — manifest updated at {MANIFEST_FILE}")
    return archived


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--keep", type=int, default=DEFAULT_KEEP,
                   help=f"Number of most-recent status files to keep active (default: {DEFAULT_KEEP})")
    p.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                   help=f"Only rotate when file count exceeds this threshold (default: {DEFAULT_THRESHOLD})")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Preview rotation without moving any files")
    args = p.parse_args()

    rotated = rotate(keep=args.keep, threshold=args.threshold, dry_run=args.dry_run)
    if args.dry_run and rotated:
        print(f"\nDry-run: {len(rotated)} file(s) would be archived.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
