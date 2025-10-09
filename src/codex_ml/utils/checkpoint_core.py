from __future__ import annotations

import io
import json
import hashlib
import platform
import random
import time
from datetime import datetime
from itertools import count
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pickle

from .atomic_io import safe_write_bytes, safe_write_text
from .optional import optional_import

torch, _HAS_TORCH = optional_import("torch")
if torch is not None and not all(hasattr(torch, attr) for attr in ("save", "load")):
    torch = None  # type: ignore[assignment]

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None  # type: ignore


SCHEMA_VERSION = "1.0"


class CheckpointIntegrityError(RuntimeError):
    pass


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _now() -> int:
    return int(time.time())


def _git_sha_try() -> Optional[str]:
    # Best-effort; offline and without invoking subprocess if .git absent.
    head = Path(".git/HEAD")
    if head.exists():
        try:
            ref = head.read_text(encoding="utf-8").strip()
            if ref.startswith("ref:"):
                ref_path = Path(".git") / ref.split(" ", 1)[1]
                if ref_path.exists():
                    return ref_path.read_text(encoding="utf-8").strip()[:40]
            return ref[:40]
        except Exception:
            return None
    return None


def _rng_snapshot() -> Dict[str, Any]:
    snap: Dict[str, Any] = {"python": random.getstate()}
    if np is not None:
        try:
            snap["numpy"] = np.random.get_state()
        except Exception:
            pass
    if torch is not None:
        if hasattr(torch, "get_rng_state"):
            try:
                snap["torch_cpu"] = torch.get_rng_state().tolist()  # tensor → list
            except Exception:
                pass
        if hasattr(torch, "cuda"):
            try:
                if torch.cuda.is_available():  # pragma: no cover (GPU not in CPU CI)
                    snap["torch_cuda"] = torch.cuda.get_rng_state_all()
            except Exception:
                pass
    return snap


def _rng_restore(snap: Dict[str, Any]) -> None:
    try:
        if "python" in snap:
            random.setstate(snap["python"])
    except Exception:
        pass
    if np is not None:
        try:
            if "numpy" in snap:
                np.random.set_state(snap["numpy"])
        except Exception:
            pass
    if torch is not None:
        if hasattr(torch, "tensor") and hasattr(torch, "set_rng_state"):
            try:
                if "torch_cpu" in snap:
                    torch_cpu_state = torch.tensor(snap["torch_cpu"], dtype=torch.uint8)
                    torch.set_rng_state(torch_cpu_state)  # type: ignore[arg-type]
            except Exception:
                pass
        if hasattr(torch, "cuda"):
            try:
                if "torch_cuda" in snap and torch.cuda.is_available():  # pragma: no cover
                    torch.cuda.set_rng_state_all(snap["torch_cuda"])
            except Exception:
                pass


@dataclass
class CheckpointMeta:
    schema_version: str
    created_at: int
    git_sha: Optional[str]
    config_hash: Optional[str]
    rng: Dict[str, Any]
    env: Dict[str, Any]
    metric_key: Optional[str]
    metric_value: Optional[float]
    sha256: Optional[str]  # of the serialized payload (bytes)


def _config_hash(config: Optional[Dict[str, Any]]) -> Optional[str]:
    if not config:
        return None
    try:
        payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
    except Exception:
        return None


def _serialize_payload(state: Dict[str, Any]) -> bytes:
    """
    Serialize the checkpoint state to bytes. Prefer torch.save if available, otherwise pickle.
    """
    buf = io.BytesIO()
    if torch is not None and hasattr(torch, "save"):
        torch.save(state, buf)  # type: ignore[arg-type]
    else:
        pickle.dump(state, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def _deserialize_payload(b: bytes) -> Dict[str, Any]:
    buf = io.BytesIO(b)
    if torch is not None and hasattr(torch, "load"):
        try:
            return torch.load(buf, map_location="cpu")  # type: ignore[no-any-return]
        except Exception:
            buf.seek(0)
    return pickle.load(buf)  # type: ignore[no-any-return]


def _digest_view(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Return a payload view with checksum field cleared for hashing consistency."""

    state = obj.get("state", {})
    meta = dict(obj.get("meta", {}))
    meta["sha256"] = None
    return {"state": state, "meta": meta}


_CKPT_COUNTER = count()


def _ckpt_name(prefix: str = "ckpt") -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
    suffix = next(_CKPT_COUNTER)
    return f"{prefix}-{timestamp}-{suffix:04d}.pt"


def _read_bytes(p: Path) -> bytes:
    return p.read_bytes()


def _index_path(root: Path) -> Path:
    return root / "index.json"


def _load_index(root: Path) -> Dict[str, Any]:
    p = _index_path(root)
    if not p.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "metric_key": None,
            "mode": "min",
            "top_k": 1,
            "entries": [],
        }
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {
            "schema_version": SCHEMA_VERSION,
            "metric_key": None,
            "mode": "min",
            "top_k": 1,
            "entries": [],
        }


def _write_index(root: Path, idx: Dict[str, Any]) -> None:
    safe_write_text(_index_path(root), json.dumps(idx, indent=2, sort_keys=True))


def _prune_best_k(root: Path, idx: Dict[str, Any]) -> None:
    entries = idx.get("entries", [])
    top_k = int(idx.get("top_k", 1))
    mode = str(idx.get("mode", "min")).lower()
    reverse = True if mode == "max" else False

    def _metric_key(entry: Dict[str, Any]) -> float:
        metric = entry.get("metric")
        if metric is None:
            return float("-inf") if reverse else float("inf")
        return float(metric)

    entries_sorted = sorted(entries, key=_metric_key, reverse=reverse)
    keep = entries_sorted[:top_k]
    remove = {e["path"] for e in entries if e not in keep}
    # Delete files that are not in keep
    for rel in remove:
        try:
            (root / rel).unlink(missing_ok=True)
        except Exception:
            pass
    idx["entries"] = keep


def save_checkpoint(
    checkpoint_dir: str | Path,
    state: Dict[str, Any],
    *,
    metric_value: Optional[float] = None,
    metric_key: str = "val_loss",
    mode: str = "min",
    top_k: int = 3,
    config: Optional[Dict[str, Any]] = None,
    prefix: str = "ckpt",
) -> Tuple[Path, CheckpointMeta]:
    """
    Save a checkpoint with atomic IO, metadata, and update best-k retention index.

    Returns: (checkpoint_path, metadata)
    """
    root = Path(checkpoint_dir)
    root.mkdir(parents=True, exist_ok=True)

    # Build metadata
    meta = CheckpointMeta(
        schema_version=SCHEMA_VERSION,
        created_at=_now(),
        git_sha=_git_sha_try(),
        config_hash=_config_hash(config),
        rng=_rng_snapshot(),
        env={"python": platform.python_version(), "platform": platform.platform()},
        metric_key=metric_key,
        metric_value=metric_value,
        sha256=None,
    )

    # Serialize payload (state + meta stub for verification)
    payload = {"state": state, "meta": asdict(meta)}
    digest = _sha256_bytes(_serialize_payload(_digest_view(payload)))
    meta.sha256 = digest
    # Re-embed meta with sha for persistence
    payload["meta"]["sha256"] = digest
    raw = _serialize_payload(payload)

    # Choose name and write atomically
    ckpt_name = _ckpt_name(prefix=prefix)
    ckpt_path = root / ckpt_name
    safe_write_bytes(ckpt_path, lambda: raw)

    # Update index
    idx = _load_index(root)
    idx["schema_version"] = SCHEMA_VERSION
    idx["metric_key"] = metric_key
    idx["mode"] = "min" if mode.lower().startswith("min") else "max"
    idx["top_k"] = int(top_k)
    idx.setdefault("entries", [])
    idx["entries"].append(
        {
            "path": ckpt_name,
            "metric": metric_value,
            "created_at": meta.created_at,
            "sha256": digest,
        }
    )
    _prune_best_k(root, idx)
    _write_index(root, idx)

    return ckpt_path, meta


def verify_checkpoint(path: str | Path) -> CheckpointMeta:
    """
    Verify the checkpoint sha256 against embedded metadata; return parsed metadata if ok.
    """
    p = Path(path)
    raw = _read_bytes(p)
    obj = _deserialize_payload(raw)
    meta_dict = obj.get("meta", {})
    expected = meta_dict.get("sha256")
    if not expected:
        raise CheckpointIntegrityError("Missing sha256 in checkpoint metadata.")
    # Re-serialize state+meta (as stored) to compute digest in same form
    raw2 = _serialize_payload(_digest_view(obj))
    actual = _sha256_bytes(raw2)
    if actual != expected:
        raise CheckpointIntegrityError(
            f"Checksum mismatch for {p.name}: expected {expected}, got {actual}"
        )
    # Return a dataclass for convenience
    return CheckpointMeta(**{k: meta_dict.get(k) for k in CheckpointMeta.__annotations__.keys()})  # type: ignore[arg-type]


def load_checkpoint(
    path: str | Path, *, restore_rng: bool = False
) -> Tuple[Dict[str, Any], CheckpointMeta]:
    """
    Load a checkpoint file and optionally restore RNG state from metadata.
    """
    p = Path(path)
    raw = _read_bytes(p)
    obj = _deserialize_payload(raw)
    meta_dict = obj.get("meta", {})
    state = obj.get("state", {})
    meta = CheckpointMeta(**{k: meta_dict.get(k) for k in CheckpointMeta.__annotations__.keys()})  # type: ignore[arg-type]
    # Integrity verification
    raw2 = _serialize_payload(_digest_view({"state": state, "meta": meta_dict}))
    if _sha256_bytes(raw2) != meta.sha256:
        raise CheckpointIntegrityError(f"Checksum mismatch for {p.name}")
    if restore_rng and meta.rng:
        _rng_restore(meta.rng)
    return state, meta


def load_best(checkpoint_dir: str | Path) -> Tuple[Dict[str, Any], CheckpointMeta, Path]:
    """
    Load the best checkpoint according to index.json (by metric and mode).
    """
    root = Path(checkpoint_dir)
    idx = _load_index(root)
    entries = idx.get("entries", [])
    if not entries:
        raise FileNotFoundError("No checkpoints found in index.")
    mode = idx.get("mode", "min").lower()
    reverse = True if mode == "max" else False
    entries_sorted = sorted(
        entries,
        key=lambda e: (float("inf") if e["metric"] is None else e["metric"]),
        reverse=reverse,
    )
    best = entries_sorted[0]
    path = root / best["path"]
    state, meta = load_checkpoint(path)
    return state, meta, path
