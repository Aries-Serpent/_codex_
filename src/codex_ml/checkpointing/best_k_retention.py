"""
Best-k checkpoint retention with atomic metadata updates.

Follows specification from reports/specs/_codex__Checkpoint_BestK_Retention_Spec.md
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "CheckpointEntry",
    "CheckpointIndex",
    "prune_checkpoints",
    "save_checkpoint_with_retention",
]

LOGGER = logging.getLogger(__name__)


@dataclass
class CheckpointEntry:
    """Entry in the checkpoint index."""

    path: str
    metric: float
    step: int
    created_at: float


class CheckpointIndex:
    """Manages checkpoint index with atomic updates."""

    def __init__(self, checkpoint_dir: Path):
        """
        Initialize checkpoint index manager.

        Args:
            checkpoint_dir: Directory containing checkpoints and index.json
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.index_path = self.checkpoint_dir / "index.json"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[CheckpointEntry]:
        """Load index from disk, return empty list if not found."""
        if not self.index_path.exists():
            return []

        try:
            with open(self.index_path) as f:
                data = json.load(f)
            return [CheckpointEntry(**entry) for entry in data]
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            LOGGER.warning(f"Failed to load index, using empty: {e}")
            return []

    def save(self, entries: list[CheckpointEntry], atomic: bool = True) -> None:
        """
        Save index to disk with optional atomic write.

        Args:
            entries: list of checkpoint entries to save
            atomic: If True, use temp file + rename for atomicity
        """
        data = [
            {
                "path": e.path,
                "metric": e.metric,
                "step": e.step,
                "created_at": e.created_at,
            }
            for e in entries
        ]

        if atomic:
            # Atomic write: temp file + rename
            temp_path = self.index_path.with_suffix(".json.tmp")
            try:
                with open(temp_path, "w") as f:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp_path, self.index_path)
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                if temp_path.exists():
                    temp_path.unlink()
                raise RuntimeError(f"Failed to save index atomically: {e}") from e
        else:
            # Direct write (for testing)
            with open(self.index_path, "w") as f:
                json.dump(data, f, indent=2)


def prune_checkpoints(
    checkpoint_dir: Path,
    keep_top_k: int = 5,
    metric_lower_better: bool = True,
    keep_last: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Prune checkpoints keeping only top-k by metric.

    Args:
        checkpoint_dir: Directory containing checkpoints
        keep_top_k: Number of checkpoints to retain
        metric_lower_better: If True, lower metrics are better (e.g., loss)
        keep_last: If True, always keep the most recent checkpoint
        dry_run: If True, don't actually delete files

    Returns:
        dict with keys: kept, deleted, errors
    """
    index = CheckpointIndex(checkpoint_dir)
    entries = index.load()

    if not entries:
        return {"kept": [], "deleted": [], "errors": []}

    # Sort by metric (and created_at for ties)
    sorted_entries = sorted(
        entries,
        key=lambda e: (e.metric if metric_lower_better else -e.metric, e.created_at),
    )

    # Keep top-k
    to_keep = sorted_entries[:keep_top_k]
    to_delete = sorted_entries[keep_top_k:]

    # Optional: always keep last (most recent)
    if keep_last and to_delete:
        most_recent = max(entries, key=lambda e: e.created_at)
        if most_recent not in to_keep:
            # Replace oldest kept with most recent
            to_keep = to_keep[:-1] + [most_recent]
            to_delete = [e for e in sorted_entries if e not in to_keep]

    kept_paths = [e.path for e in to_keep]
    deleted_paths = []
    errors = []

    # Delete files not in keep set
    for entry in to_delete:
        file_path = checkpoint_dir / entry.path
        if dry_run:
            LOGGER.info(f"[DRY RUN] Would delete: {file_path}")
            deleted_paths.append(entry.path)
        else:
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted_paths.append(entry.path)
                    LOGGER.info(f"Deleted checkpoint: {file_path}")
                else:
                    LOGGER.warning(f"Checkpoint file not found (already deleted?): {file_path}")
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                errors.append(f"Failed to delete {file_path}: {e}")
                LOGGER.error(f"Failed to delete {file_path}: {e}")

    # Update index with kept entries
    if not dry_run:
        index.save(to_keep)

    return {
        "kept": kept_paths,
        "deleted": deleted_paths,
        "errors": errors,
    }


def save_checkpoint_with_retention(
    checkpoint_dir: Path,
    checkpoint_data: Any,
    metric: float,
    step: int,
    keep_top_k: int = 5,
    metric_lower_better: bool = True,
) -> Path:
    """
    Save checkpoint and automatically prune to keep top-k.

    Args:
        checkpoint_dir: Directory to save checkpoint
        checkpoint_data: Checkpoint data (will be passed to torch.save)
        metric: Metric value for this checkpoint
        step: Global step number
        keep_top_k: Number of checkpoints to retain
        metric_lower_better: If True, lower metrics are better

    Returns:
        Path to saved checkpoint file
    """
    # Lazy import torch
    try:
        import torch
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        raise ImportError("PyTorch required for checkpoint saving") from e

    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Save new checkpoint
    checkpoint_filename = f"checkpoint_step_{step}_metric_{metric:.4f}.pt"
    checkpoint_path = checkpoint_dir / checkpoint_filename

    # Save to temp then rename for atomicity
    temp_path = checkpoint_path.with_suffix(".pt.tmp")
    torch.save(checkpoint_data, temp_path)
    os.replace(temp_path, checkpoint_path)

    # Update index
    index = CheckpointIndex(checkpoint_dir)
    entries = index.load()

    new_entry = CheckpointEntry(
        path=checkpoint_filename,
        metric=metric,
        step=step,
        created_at=time.time(),
    )
    entries.append(new_entry)

    # Sort and keep top-k
    sorted_entries = sorted(
        entries,
        key=lambda e: (e.metric if metric_lower_better else -e.metric, e.created_at),
    )
    kept_entries = sorted_entries[:keep_top_k]

    # Save updated index atomically
    index.save(kept_entries)

    # Delete pruned checkpoints
    kept_paths = {e.path for e in kept_entries}
    for entry in entries:
        if entry.path not in kept_paths:
            file_to_delete = checkpoint_dir / entry.path
            try:
                if file_to_delete.exists():
                    file_to_delete.unlink()
                    LOGGER.info(f"Pruned checkpoint: {file_to_delete}")
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                LOGGER.warning(f"Failed to delete pruned checkpoint {file_to_delete}: {e}")

    return checkpoint_path
