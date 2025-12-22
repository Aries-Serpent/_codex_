"""
Best‑K checkpoint retention (atomic index update).

Public function:
    update_and_prune(checkpoint_path: Path, metric: float, k: int, index_path: Path,
                     keep_last: bool=False, dry_run: bool=False) -> Dict[str, Any]

Index schema:
{
  "entries": [
      {"path": "checkpoint_12.pt", "metric": 0.1234, "step": 12, "created_at": 1690000000.0}
  ]
}
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _read_index(index_path: Path) -> Dict[str, Any]:
    if not index_path.exists():
        return {"entries": []}
    try:
        return json.loads(index_path.read_text())
    except Exception:
        return {"entries": []}


def _write_index_atomic(index_path: Path, data: Dict[str, Any]) -> None:
    tmp = index_path.with_suffix(index_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, index_path)


def update_and_prune(
    checkpoint_path: Path,
    metric: float,
    k: int,
    index_path: Path,
    keep_best: str | None = None,
    keep_last: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    strategy = "max" if (keep_best or "") == "max" else "min"

    # Stage file existence check (caller already saved checkpoint)
    entries_before = _read_index(index_path)["entries"]

    new_entry = {
        "path": str(checkpoint_path),
        "metric": metric,
        "step": _infer_step_from_name(checkpoint_path.name),
        "created_at": time.time(),
    }

    # Remove prior entries for the same checkpoint when keep_last is requested so the
    # newest metadata wins and the older index rows count as pruned for reporting.
    duplicate_entries: List[Dict[str, Any]] = []
    if keep_last:
        remaining_entries = []
        for entry in entries_before:
            if entry["path"] == new_entry["path"]:
                duplicate_entries.append(entry)
            else:
                remaining_entries.append(entry)
        entries_before = remaining_entries

    entries = entries_before + [new_entry]

    # Sort best-first depending on strategy
    kept = _select_top_k(entries, k=k, strategy=strategy)

    # Force newest checkpoint retention if requested
    if keep_last and str(checkpoint_path) not in {e["path"] for e in kept}:
        kept.append(new_entry)
        kept = _select_top_k_with_protection(
            kept, k=k, strategy=strategy, protected_path=str(checkpoint_path)
        )
    else:
        # When keep_last=True and the path is already present, replace older copies
        kept = _dedupe_keep_latest(kept, str(checkpoint_path))

    final_paths = {e["path"] for e in kept}
    prune_candidates: List[Dict[str, Any]] = [
        e for e in entries_before if e["path"] not in final_paths
    ]
    prune_candidates.extend(duplicate_entries)

    if not dry_run:
        _write_index_atomic(index_path, {"entries": kept, "k": k, "keep_best": strategy})
        # Delete pruned checkpoints (skip if same as current path to avoid deleting
        # freshly written checkpoint that was overwritten in place)
        for e in prune_candidates:
            if e["path"] == str(checkpoint_path):
                continue
            try:
                p = Path(e["path"])
                if p.exists():
                    p.unlink()
            except Exception:
                # Log or ignore; failure leaves extra file (acceptable fallback)
                pass

    return {
        "index_path": str(index_path),
        "added": str(checkpoint_path),
        "kept": kept,
        "pruned": prune_candidates,
        "dry_run": dry_run,
    }


def _infer_step_from_name(name: str) -> int:
    # heuristic: checkpoint_{step}.pt
    if "checkpoint_" in name:
        try:
            core = name.split("checkpoint_")[1]
            num_part = core.split(".")[0]
            return int(num_part)
        except Exception:
            return -1
    return -1


def _select_top_k(entries: Iterable[Dict[str, Any]], k: int, strategy: str) -> List[Dict[str, Any]]:
    reverse = strategy == "max"
    sorted_entries = sorted(entries, key=lambda e: (e["metric"], e["created_at"]), reverse=reverse)
    return list(sorted_entries[:k])


def _select_top_k_with_protection(
    entries: Iterable[Dict[str, Any]],
    k: int,
    strategy: str,
    protected_path: str,
) -> List[Dict[str, Any]]:
    reverse = strategy == "max"
    protected_entries = [e for e in entries if e["path"] == protected_path]
    protected_entry = None
    if protected_entries:
        # Prefer the newest metadata for the protected checkpoint
        protected_entry = max(protected_entries, key=lambda e: e["created_at"])

    others = [e for e in entries if e["path"] != protected_path]
    others_sorted = sorted(others, key=lambda e: (e["metric"], e["created_at"]), reverse=reverse)

    kept: List[Dict[str, Any]] = []
    if protected_entry is not None:
        kept.append(protected_entry)

    for entry in others_sorted:
        if len(kept) >= k:
            break
        kept.append(entry)

    return _select_top_k(kept, k=k, strategy=strategy)


def _dedupe_keep_latest(
    entries: Iterable[Dict[str, Any]], target_path: str
) -> List[Dict[str, Any]]:
    """Ensure at most one entry per path; for target_path prefer the newest copy."""

    latest: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        path = entry["path"]
        if path not in latest or entry["created_at"] > latest[path]["created_at"]:
            latest[path] = entry
    return list(latest.values())
