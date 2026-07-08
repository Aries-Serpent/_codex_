"""
Ingest Module

This module provides functionality for ingest.

Usage:
    from pipeline_nodes.ingest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import csv
from pathlib import Path


def ingest_rows(path: Path) -> list[dict]:
    """
    Read CSV with columns at least: id, value.
    If file does not exist, create a tiny synthetic input.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "value"])
            for i in range(10):
                writer.writerow([i, i % 3])

    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(r) for r in reader]
