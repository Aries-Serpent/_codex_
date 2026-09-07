"""Compatibility package for legacy `codex.ingest` imports."""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "ingest"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

from aries_serpent_core.ingest import IngestManifest, Snapshot, ingest, parse_manifest

__all__ = ["IngestManifest", "Snapshot", "ingest", "parse_manifest"]
