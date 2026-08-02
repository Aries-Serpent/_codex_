#!/usr/bin/env python3
"""Standalone entry point for deterministic living-document synchronization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .update_cognitive_brain import living_doc_sync
except ImportError:
    # Allow direct execution from the repository root without requiring installation.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from update_cognitive_brain import living_doc_sync


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=".codex/session_logs.db")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return living_doc_sync(Path(args.db), args.repo_root, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
