"""Compatibility helpers for snapshot metadata and listing APIs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ["list_snapshots", "get_snapshot", "show_snapshot"]


def _snapshot_root(root: str | Path | None = None) -> Path:
    if root is not None:
        return Path(root)
    return Path.cwd() / "artifacts"


def list_snapshots(root: str | Path | None = None, *, status: str | None = None) -> list[dict[str, Any]]:
    """Return snapshot metadata dictionaries from an artifacts directory."""
    base = _snapshot_root(root)
    if not base.exists():
        return []

    snapshots: list[dict[str, Any]] = []
    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue
        meta_file = item / "snapshot-meta.json"
        if meta_file.exists():
            with meta_file.open("r", encoding="utf-8") as handle:
                meta = json.load(handle)
        else:
            meta = {"snapshot_id": item.name, "name": item.name}
        if status is not None and meta.get("status") != status:
            continue
        snapshots.append(meta)
    return snapshots


def get_snapshot(snapshot_id: str, root: str | Path | None = None) -> dict[str, Any]:
    """Return snapshot metadata for the given snapshot ID."""
    base = _snapshot_root(root)
    snapshot_dir = base / snapshot_id
    meta_file = snapshot_dir / "snapshot-meta.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found")
    with meta_file.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def show_snapshot(snapshot_id: str, root: str | Path | None = None) -> dict[str, Any]:
    return get_snapshot(snapshot_id, root=root)
