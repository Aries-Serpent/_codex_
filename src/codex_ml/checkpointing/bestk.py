"""
Best‑K checkpoint retention (atomic index update).

Public function:
    update_and_prune(checkpoint_path: Path, metric: float, k: int,
                     index_path: Path, keep_last: bool=False, dry_run: bool=False) -> Dict[str, Any]

Index schema:
    {
        "entries": [
            {"path": "checkpoint_12.pt", "metric": 0.1234, "step": 12, "created_at": 1690000000.0}
        ]
    }
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict


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
    keep_last: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    # Stage file existence check (caller already saved checkpoint)
    entries_before = _read_index(index_path)["entries"]

    new_entry = {
        "path": str(checkpoint_path),
        "metric": metric,
        "step": _infer_step_from_name(checkpoint_path.name),
        "created_at": time.time(),
    }

    entries = entries_before + [new_entry]

    # Sort: lower metric better, then earlier created_at
    entries_sorted = sorted(entries, key=lambda e: (e["metric"], e["created_at"]))

    kept = entries_sorted[:k]

    if keep_last and str(checkpoint_path) not in {e["path"] for e in kept}:
        # Ensure last added retained
        kept.append(new_entry)

    final_paths = {e["path"] for e in kept}
    prune_candidates = [e for e in entries_before if e["path"] not in final_paths]

    if not dry_run:
        _write_index_atomic(index_path, {"entries": kept})

        # Delete pruned checkpoints
        for e in prune_candidates:
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
