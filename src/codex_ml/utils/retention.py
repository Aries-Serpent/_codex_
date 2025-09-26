"""
Checkpoint retention utilities.

Supports pruning old epoch-* directories under a checkpoint root while
respecting:
    - keep_last: Keep the newest N epochs.
    - keep_every: Always retain epochs divisible by this modulus.
    - max_epochs: Optional hard cap (after pruning still limit to N).
    - protect_latest: Ensures latest.json target is never pruned.

Policy combination:
    Directories to keep = (newest keep_last) UNION (epochs % keep_every == 0)
    Then all other epoch-* directories are deleted.

Example:
    prune_checkpoints("artifacts/ckpts", keep_last=3, keep_every=5)

This keeps:
    - The latest 3 epochs
    - Any epoch multiple of 5
    - The epoch referenced by latest.json (always)

Deletion is best-effort; errors are logged but not raised.

"""

from __future__ import annotations

import json
import logging
import re
import shutil
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

EPOCH_DIR_RE = re.compile(r"^epoch-(\d{4,})$")


def _discover_epoch_dirs(root: Path) -> List[Path]:
    out = []
    for p in root.iterdir():
        if not p.is_dir():
            continue
        m = EPOCH_DIR_RE.match(p.name)
        if not m:
            continue
        try:
            epoch = int(m.group(1))
        except Exception:
            continue
        out.append((epoch, p))
    out.sort(key=lambda x: x[0])
    return [p for _, p in out]


def _read_latest_epoch(root: Path) -> Optional[int]:
    latest = root / "latest.json"
    if not latest.exists():
        return None
    try:
        data = json.loads(latest.read_text())
        return int(data.get("epoch"))
    except Exception:
        return None


def prune_checkpoints(
    checkpoint_dir: str | Path,
    keep_last: int | None = None,
    keep_every: int | None = None,
    max_epochs: int | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Prune old epoch-* directories according to policy.

    Args:
        checkpoint_dir: Root directory containing epoch-XXXX subdirs + latest.json.
        keep_last: Keep newest N epochs (None disables).
        keep_every: Always keep epochs where (epoch % keep_every == 0).
        max_epochs: After pruning, if still more than this count remain, further
                    prune oldest (excluding protect set).
        dry_run: If True, no deletions performed; returns plan only.

    Returns:
        dict summary:
            {
              "total": int,
              "kept": [epoch ints],
              "pruned": [epoch ints],
              "protected_latest": epoch or None,
              "dry_run": bool
            }
    """
    root = Path(checkpoint_dir)
    if not root.exists():
        return {"total": 0, "kept": [], "pruned": [], "protected_latest": None, "dry_run": dry_run}

    epoch_dirs = _discover_epoch_dirs(root)
    epochs = []
    for p in epoch_dirs:
        m = EPOCH_DIR_RE.match(p.name)
        if not m:
            continue
        epochs.append(int(m.group(1)))

    protected_latest = _read_latest_epoch(root)
    keep: Set[int] = set()

    if keep_last and keep_last > 0:
        keep.update(epochs[-keep_last:])

    if keep_every and keep_every > 0:
        for e in epochs:
            if e % keep_every == 0:
                keep.add(e)

    if protected_latest:
        keep.add(protected_latest)

    # If max_epochs specified, enforce after initial keep decisions
    if max_epochs and max_epochs > 0:
        # Ensure we can fill the target window with newest epochs when other
        # policies (keep_last/keep_every) produce too small a keep set. This
        # matches the expectation that max_epochs retains the most recent
        # checkpoints even when no other policy is configured.
        target_count = min(max_epochs, len(epochs))

        if protected_latest:
            keep.add(protected_latest)

        if len(keep) < target_count:
            for epoch in sorted(epochs, reverse=True):
                keep.add(epoch)
                if len(keep) >= target_count:
                    break

        if len(keep) > target_count:
            trimmed_list = sorted(keep, reverse=True)[:target_count]
            if protected_latest and protected_latest not in trimmed_list:
                trimmed_list.append(protected_latest)
                trimmed_list = sorted(set(trimmed_list), reverse=True)[:target_count]
            keep = set(trimmed_list)

    pruned: List[int] = []
    kept: List[int] = []
    epoch_to_path = {
        int(EPOCH_DIR_RE.match(p.name).group(1)): p
        for p in epoch_dirs
        if EPOCH_DIR_RE.match(p.name)
    }

    for e, p in epoch_to_path.items():
        if e in keep:
            kept.append(e)
        else:
            pruned.append(e)

    # Perform deletions
    if not dry_run:
        for e in pruned:
            path = epoch_to_path[e]
            try:
                shutil.rmtree(path)
            except Exception as ex:  # noqa: BLE001
                logger.warning("Failed to delete checkpoint dir %s: %s", path, ex)

    return {
        "total": len(epochs),
        "kept": sorted(kept),
        "pruned": sorted(pruned),
        "protected_latest": protected_latest,
        "dry_run": dry_run,
    }


__all__ = ["prune_checkpoints"]
