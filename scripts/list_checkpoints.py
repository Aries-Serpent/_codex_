#!/usr/bin/env python3
"""Checkpoint management CLI for listing and cleaning checkpoints.

Provides commands for:
- Listing all checkpoints
- Filtering by pattern, age, size
- Dry-run deletion with retention policies
- Checkpoint metadata inspection
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def list_checkpoints(
    checkpoint_dir: Path,
    pattern: str = "*.pt",
    min_age_days: Optional[int] = None,
    max_age_days: Optional[int] = None,
) -> list[dict]:
    """list checkpoints with metadata."""
    if not checkpoint_dir.exists():
        return []

    checkpoints = []
    now = datetime.now()

    for ckpt_file in checkpoint_dir.rglob(pattern):
        if not ckpt_file.is_file():
            continue

        stat = ckpt_file.stat()
        age_days = (now.timestamp() - stat.st_mtime) / 86400

        # Filter by age
        if min_age_days and age_days < min_age_days:
            continue
        if max_age_days and age_days > max_age_days:
            continue

        checkpoints.append(
            {
                "path": str(ckpt_file),
                "size_mb": stat.st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "age_days": round(age_days, 1),
            }
        )

    return sorted(checkpoints, key=lambda x: x["age_days"], reverse=True)


def apply_retention_policy(
    checkpoints: list[dict],
    keep_last_n: int = 5,
    keep_days: int = 30,
) -> tuple[list[dict], list[dict]]:
    """Apply retention policy and return (to_keep, to_delete)."""
    # Sort by age (newest first)
    sorted_ckpts = sorted(checkpoints, key=lambda x: x["age_days"])

    to_keep = []
    to_delete = []

    for idx, ckpt in enumerate(sorted_ckpts):
        # Keep last N checkpoints
        if idx < keep_last_n:
            to_keep.append(ckpt)
            continue

        # Keep if younger than retention period
        if ckpt["age_days"] <= keep_days:
            to_keep.append(ckpt)
            continue

        to_delete.append(ckpt)

    return to_keep, to_delete


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Checkpoint management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list command
    list_parser = subparsers.add_parser("list", help="list checkpoints")
    list_parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=Path("artifacts/checkpoints"),
        help="Checkpoint directory",
    )
    list_parser.add_argument(
        "--pattern",
        default="*.pt",
        help="File pattern",
    )
    list_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean old checkpoints")
    clean_parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=Path("artifacts/checkpoints"),
        help="Checkpoint directory",
    )
    clean_parser.add_argument(
        "--keep-last-n",
        type=int,
        default=5,
        help="Keep last N checkpoints",
    )
    clean_parser.add_argument(
        "--keep-days",
        type=int,
        default=30,
        help="Keep checkpoints newer than N days",
    )
    clean_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "list":
        checkpoints = list_checkpoints(args.checkpoint_dir, args.pattern)

        if args.format == "json":
            print(json.dumps(checkpoints, indent=2))
        else:
            print(f"\nCheckpoints in {args.checkpoint_dir}:\n")
            print(f"{'Path':<60} {'Size (MB)':<12} {'Age (days)':<12}")
            print("-" * 84)
            for ckpt in checkpoints:
                print(f"{ckpt['path']:<60} {ckpt['size_mb']:<12.2f} {ckpt['age_days']:<12.1f}")
            print(f"\nTotal: {len(checkpoints)} checkpoint(s)")

    elif args.command == "clean":
        checkpoints = list_checkpoints(args.checkpoint_dir)
        to_keep, to_delete = apply_retention_policy(
            checkpoints,
            keep_last_n=args.keep_last_n,
            keep_days=args.keep_days,
        )

        print(
            f"\nRetention policy: keep last {args.keep_last_n}, keep if < {args.keep_days} days old\n"
        )
        print(f"Checkpoints to keep: {len(to_keep)}")
        print(f"Checkpoints to delete: {len(to_delete)}\n")

        if to_delete:
            print("To be deleted:")
            for ckpt in to_delete:
                print(f"  - {ckpt['path']} ({ckpt['age_days']} days old, {ckpt['size_mb']:.2f} MB)")

            if args.dry_run:
                print("\n[DRY RUN] No files deleted. Remove --dry-run to delete.")
            else:
                for ckpt in to_delete:
                    Path(ckpt["path"]).unlink()
                print(f"\nDeleted {len(to_delete)} checkpoint(s)")
        else:
            print("No checkpoints to delete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
