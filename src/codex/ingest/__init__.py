"""
Codex Ingest Module

Handles artifact ingestion from files, ZIP archives, and Git URLs.
Creates immutable snapshots with full provenance tracking.

Safeguards:
- Input validation on all sources
- Path traversal prevention
- Size bounds checking
- Deterministic hashing
"""

from __future__ import annotations

from .adapter import Snapshot, ingest
from .manifest import IngestManifest, parse_manifest

__all__ = [
    "IngestManifest",
    "Snapshot",
    "ingest",
    "parse_manifest",
]
