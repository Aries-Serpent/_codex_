"""Compatibility wrapper for the legacy ``codex.ingest.adapter`` module."""

from aries_serpent_core.ingest.adapter import (  # noqa: F401
    IngestManifest,
    Snapshot,
    _check_size_bounds,
    _clone_git_repo,
    _compute_content_hash,
    _extract_tar,
    _extract_zip,
    _validate_path,
    ingest,
    parse_manifest,
)

__all__ = [
    "IngestManifest",
    "Snapshot",
    "_check_size_bounds",
    "_clone_git_repo",
    "_compute_content_hash",
    "_extract_tar",
    "_extract_zip",
    "_validate_path",
    "ingest",
    "parse_manifest",
]
