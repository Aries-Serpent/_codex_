#!/usr/bin/env python3
"""
Lightweight checkpoint manager for CI jobs.

This utility enables long-running CI jobs to save and restore progress,
allowing for job recovery in case of interruption or failure.

Usage:
    python checkpoint_manager.py save <iteration> <files_count>
    python checkpoint_manager.py load

Exit codes:
    0: Success
    1: Invalid arguments or error
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT_DIR = Path(".github/checkpoints")


def save_checkpoint(iteration: str, files_count: str) -> int:
    """
    Save a checkpoint marker.

    Args:
        iteration: Iteration identifier (e.g., "1", "2a", "final")
        files_count: Number of files modified in this iteration

    Returns:
        Exit code (0 for success)
    """
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        count = int(files_count)
    except ValueError:
        print(f"❌ Invalid files_count: {files_count}")
        return 1

    checkpoint = {
        "iteration": iteration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "files_modified": count,
    }

    checkpoint_file = CHECKPOINT_DIR / f"iteration_{iteration}.json"
    checkpoint_file.write_text(json.dumps(checkpoint, indent=2))

    print(f"✅ Checkpoint saved: {iteration}")
    return 0


def load_checkpoint() -> int:
    """
    Load and display the most recent checkpoint.

    Checkpoints are sorted by their embedded timestamp to ensure correct
    chronological ordering regardless of iteration naming convention.

    Returns:
        Exit code (0 for success)
    """
    if not CHECKPOINT_DIR.exists():
        print("No checkpoints found")
        return 0

    checkpoint_files = list(CHECKPOINT_DIR.glob("iteration_*.json"))

    if not checkpoint_files:
        print("No checkpoints found")
        return 0

    # Sort by timestamp from file contents for correct chronological ordering
    checkpoints_with_ts = []
    for f in checkpoint_files:
        try:
            data = json.loads(f.read_text())
            checkpoints_with_ts.append((data.get("timestamp", ""), f, data))
        except (json.JSONDecodeError, OSError):
            continue

    if not checkpoints_with_ts:
        print("No valid checkpoints found")
        return 0

    # Sort by timestamp and get the latest
    checkpoints_with_ts.sort(key=lambda x: x[0])
    _, latest_file, data = checkpoints_with_ts[-1]

    print(f"Last checkpoint: {data['iteration']} at {data['timestamp']}")
    print(f"Files modified: {data['files_modified']}")

    return 0


def show_usage() -> None:
    """Display usage information."""
    print("Usage: checkpoint_manager.py <command> [args...]")
    print("")
    print("Commands:")
    print("  save <iteration> <files_count>  Save a checkpoint marker")
    print("  load                            Load and display the most recent checkpoint")
    print("")
    print("Examples:")
    print("  checkpoint_manager.py save iteration_1 5")
    print("  checkpoint_manager.py load")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        show_usage()
        return 1

    command = sys.argv[1]

    if command == "save":
        if len(sys.argv) != 4:
            print("Error: save command requires <iteration> and <files_count> arguments")
            show_usage()
            return 1
        return save_checkpoint(sys.argv[2], sys.argv[3])

    if command == "load":
        return load_checkpoint()

    print(f"Unknown command: {command}")
    show_usage()
    return 1


if __name__ == "__main__":
    sys.exit(main())
