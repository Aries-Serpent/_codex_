"""Checkpoint Core (Schema v2)

Features:
 - save_checkpoint / load_checkpoint
 - Environment & RNG capture
 - Schema version tagging
 - SHA256 digest sidecar for state artifact
 - Basic retention (keep_last, best_k based on metric key)
"""

from __future__ import annotations

import json
import platform
import random
import time
import tempfile
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

try:  # pragma: no cover
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore

from codex_ml.checkpointing.atomic_io import atomic_write_bytes, atomic_write_fileobj, file_sha256
from codex_ml.utils.checkpoint_retention import RetainSpec, retain

SCHEMA_VERSION = 2


def capture_rng_state() -> Dict[str, Any]:
    state: Dict[str, Any] = {"python": random.getstate()}
    try:
        import numpy as np  # type: ignore
    except Exception:
        np = None  # type: ignore
    if np is not None:
        try:
            state["numpy"] = np.random.get_state()
        except Exception:
            pass
    if torch is not None:
        try:
            state["torch"] = torch.random.get_rng_state().tolist()
            if torch.cuda.is_available():
                state["torch_cuda_all"] = [t.tolist() for t in torch.cuda.get_rng_state_all()]
        except Exception:
            pass
    return state


def restore_rng_state(state: Mapping[str, Any]) -> None:
    try:
        random.setstate(state["python"])  # type: ignore
    except Exception:
        pass
    try:
        import numpy as np  # type: ignore

        if "numpy" in state:
            np.random.set_state(state["numpy"])
    except Exception:
        pass
    if torch is not None:
        try:
            if "torch" in state:
                torch.random.set_rng_state(torch.tensor(state["torch"], dtype=torch.uint8))
            if "torch_cuda_all" in state and torch.cuda.is_available():
                torch.cuda.set_rng_state_all(
                    [torch.tensor(x, dtype=torch.uint8) for x in state["torch_cuda_all"]]
                )
        except Exception:
            pass


def capture_environment_summary() -> Dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "schema_version": SCHEMA_VERSION,
    }


def save_checkpoint(
    out_dir: str | Path,
    *,
    payload: Mapping[str, Any],
    metadata: Optional[Mapping[str, Any]] = None,
    include_rng: bool = True,
    keep_last: int = 3,
    best_k: int = 0,
    best_metric: str = "val_loss",
) -> Path:
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    state_file = p / "state.pt"
    meta_file = p / "metadata.json"

    full_payload = dict(payload)
    if include_rng:
        full_payload["_rng"] = capture_rng_state()
    full_payload["_schema_version"] = SCHEMA_VERSION

    # Serialize
    serialized = False
    try:
        if torch is None:
            raise RuntimeError("torch not available")
        with tempfile.TemporaryFile() as tmp:
            torch.save(full_payload, tmp)  # type: ignore[arg-type]
            tmp.flush()
            tmp.seek(0)
            atomic_write_fileobj(state_file, tmp)
        serialized = True
    except Exception:
        pass

    if not serialized:
        import pickle

        with tempfile.TemporaryFile() as tmp:
            pickle.dump(full_payload, tmp)
            tmp.flush()
            tmp.seek(0)
            atomic_write_fileobj(state_file, tmp)

    digest = file_sha256(state_file)
    meta = {
        "schema_version": SCHEMA_VERSION,
        "digest_sha256": digest,
        "environment": capture_environment_summary(),
        **(metadata or {}),
    }
    atomic_write_bytes(meta_file, json.dumps(meta, indent=2).encode("utf-8"))
    digest_bytes = (digest + "\n").encode("utf-8")
    atomic_write_bytes(p / "state.sha256", digest_bytes)
    atomic_write_bytes(state_file.with_suffix(state_file.suffix + ".sha256"), digest_bytes)

    try:
        manifest_meta = {"kind": "checkpoint"}
        if metadata:
            try:
                manifest_meta.update(dict(metadata))
            except Exception:
                pass
        _update_manifest(
            p.parent / "manifest.json",
            str(state_file.relative_to(p.parent)),
            digest,
            meta=manifest_meta,
        )
    except Exception:
        pass

    spec = RetainSpec(keep_last=keep_last, best_k=best_k, best_metric=best_metric)
    retain(p.parent, spec)
    if spec.best_k > 0:
        _refresh_best_index(p.parent, spec.best_metric, spec.best_k)

    return state_file


def _update_manifest(
    manifest_path: Path,
    rel_path: str,
    digest: str,
    meta: Optional[Mapping[str, Any]] = None,
) -> None:
    manifest: Dict[str, Any] = {"schema_version": 2, "artifacts": []}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    entry: Dict[str, Any] = {
        "path": rel_path,
        "sha256": digest,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if meta:
        try:
            entry["meta"] = dict(meta)
        except Exception:
            entry["meta"] = meta
    artifacts = manifest.get("artifacts") or []
    artifacts = [a for a in artifacts if a.get("path") != rel_path]
    artifacts.append(entry)
    manifest["artifacts"] = artifacts
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(manifest_path, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))


def load_checkpoint(path_or_dir: str | Path) -> Dict[str, Any]:
    pd = Path(path_or_dir)
    if pd.is_dir():
        pd = pd / "state.pt"
    if not pd.exists():
        raise FileNotFoundError(f"Checkpoint not found: {pd}")
    if torch is not None:
        try:
            return torch.load(pd, map_location="cpu")  # type: ignore
        except Exception:
            pass
    import pickle

    with pd.open("rb") as fh:
        return pickle.load(fh)


def _epoch_dir_sort_key(path: Path) -> tuple[float, str]:
    """Return a numeric-aware sort key for epoch directories."""

    name = path.name
    try:
        suffix = name.rsplit("-", 1)[-1]
        return (float(int(suffix)), name)
    except (ValueError, TypeError):
        return (float("inf"), name)


def _metric_from_meta(dir_path: Path, metric_name: str) -> Optional[float]:
    meta_path = dir_path / "metadata.json"
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    value = meta.get(metric_name)
    if value is None and isinstance(meta.get("metrics"), dict):
        value = meta["metrics"].get(metric_name)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _refresh_best_index(root: Path, metric_name: str, k: int) -> None:
    index_file = root / "best_index.json"
    dirs = [p for p in root.iterdir() if p.is_dir()]
    scored = []
    for directory in dirs:
        metric_val = _metric_from_meta(directory, metric_name)
        if metric_val is None:
            continue
        scored.append(
            {
                "path": directory.name,
                "metric": metric_val,
                "metric_name": metric_name,
            }
        )
    scored.sort(key=lambda item: item.get("metric", float("inf")))
    best = scored[: max(0, k)]
    index_file.write_text(json.dumps(best, indent=2) + "\n", encoding="utf-8")


__all__ = [
    "save_checkpoint",
    "load_checkpoint",
    "capture_rng_state",
    "restore_rng_state",
    "capture_environment_summary",
    "SCHEMA_VERSION",
]
