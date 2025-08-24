#!/usr/bin/env python3
"""Minimal deterministic codex deployment pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    """Return SHA256 hex digest of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _count_jsonl(path: Path) -> int:
    """Count non-empty JSON lines in ``path``.

    Each line is parsed to ensure valid JSON and to avoid relying on ``hash``
    or other non-deterministic behaviour.
    """
    count = 0
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                json.loads(line)
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy codex pipeline")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--demos", type=Path, required=True)
    parser.add_argument("--prefs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "corpus_sha256": _sha256(args.corpus),
        "num_demos": _count_jsonl(args.demos),
        "num_prefs": _count_jsonl(args.prefs),
    }

    (out_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
