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
from typing import Any, Dict, Mapping, Optional, Tuple

import pickle

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None  # type: ignore

from .atomic_io import safe_write_bytes, safe_write_text

try:  # provenance extras are optional
    from .provenance import environment_summary as _environment_summary  # type: ignore
except Exception:  # pragma: no cover - optional dependency failures tolerated
    _environment_summary = None  # type: ignore[assignment]


__all__ = [
    "CheckpointIntegrityError",
    "capture_environment_summary",
    "capture_rng_state",
    "load_best",
    "load_checkpoint",
    "restore_rng_state",
    "save_checkpoint",
    "verify_checkpoint",
]


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
        try:
            snap["torch_cpu"] = torch.get_rng_state().tolist()  # tensor → list
        except Exception:
            pass
        try:
            if torch.cuda.is_available():  # pragma: no cover (GPU not in CPU CI)
                snap["torch_cuda"] = torch.cuda.get_rng_state_all()
        except Exception:
            pass
    return snap


def _rng_restore(snap: Mapping[str, Any]) -> None:
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
        try:
            if "torch_cpu" in snap:
                torch_state_raw = snap["torch_cpu"]
                if torch_state_raw is not None:
                    torch_cpu_state = torch.tensor(torch_state_raw, dtype=torch.uint8)
                    torch.set_rng_state(torch_cpu_state)  # type: ignore[arg-type]
        except Exception:
            pass
        try:
            if "torch_cuda" in snap and torch.cuda.is_available():  # pragma: no cover
                torch.cuda.set_rng_state_all(snap["torch_cuda"])
        except Exception:
            pass


def capture_rng_state() -> Dict[str, Any]:
    """Backwards compatible wrapper returning the current RNG state."""

    return _rng_snapshot()


def restore_rng_state(state: Mapping[str, Any]) -> None:
    """Backwards compatible wrapper restoring the provided RNG state."""

    _rng_restore(dict(state))


def capture_environment_summary() -> Dict[str, Any]:
    """Collect lightweight environment details for checkpoint metadata."""

    summary: Dict[str, Any] = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    try:
        summary["timestamp_utc"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    except Exception:  # pragma: no cover
        pass

    if np is not None:
        try:
            summary["numpy_version"] = str(np.__version__)
        except Exception:  # pragma: no cover
            pass
    if torch is not None:
        try:
            summary["torch_version"] = str(torch.__version__)
        except Exception:  # pragma: no cover
            pass
        try:
            summary["torch_cuda_available"] = bool(torch.cuda.is_available())
        except Exception:  # pragma: no cover
            pass

    return summary


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
    torch_save = getattr(torch, "save", None) if torch is not None else None
    if callable(torch_save):
        try:
            torch_save(state, buf)  # type: ignore[arg-type]
        except Exception:
            buf.seek(0)
            buf.truncate(0)
            pickle.dump(state, buf, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        pickle.dump(state, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def _digest_payload(payload: Dict[str, Any]) -> bytes:
    """Produce a deterministic byte representation for hashing metadata."""
    hasher = hashlib.sha256()

    def _update(value: Any) -> None:
        if isinstance(value, dict):
            hasher.update(b"dict")
            for key in sorted(value):
                hasher.update(str(key).encode("utf-8"))
                _update(value[key])
            return
        if isinstance(value, list):
            hasher.update(b"list")
            for item in value:
                _update(item)
            return
        if isinstance(value, tuple):
            hasher.update(b"tuple")
            for item in value:
                _update(item)
            return
        if isinstance(value, (str, bytes)):
            hasher.update(b"str")
            if isinstance(value, str):
                hasher.update(value.encode("utf-8"))
            else:
                hasher.update(value)
            return
        if isinstance(value, (int, float, bool)) or value is None:
            hasher.update(b"prim")
            hasher.update(repr(value).encode("utf-8"))
            return
        if np is not None and isinstance(value, np.ndarray):  # type: ignore[attr-defined]
            hasher.update(b"ndarray")
            hasher.update(str(value.dtype).encode("utf-8"))
            hasher.update(str(value.shape).encode("utf-8"))
            hasher.update(value.tobytes())
            return
        torch_is_tensor = getattr(torch, "is_tensor", None) if torch is not None else None
        if callable(torch_is_tensor) and torch_is_tensor(value):  # type: ignore[attr-defined]
            tensor = value.detach().cpu()
            hasher.update(b"tensor")
            hasher.update(str(tensor.dtype).encode("utf-8"))
            hasher.update(str(tuple(tensor.shape)).encode("utf-8"))
            hasher.update(tensor.numpy().tobytes())
            return

        # Fallback: rely on pickle for custom objects (deterministic for stable reprs)
        hasher.update(b"pickle")
        hasher.update(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))

    _update(payload)
    return hasher.digest()


def _deserialize_payload(b: bytes) -> Dict[str, Any]:
    buf = io.BytesIO(b)
    torch_load = getattr(torch, "load", None) if torch is not None else None
    if callable(torch_load):
        try:
            return torch_load(buf, map_location="cpu", weights_only=False)  # type: ignore[no-any-return]
        except Exception:
            buf.seek(0)
    return pickle.load(buf)  # type: ignore[no-any-return]


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


def _metric_sort_key(entry: Mapping[str, Any], *, reverse: bool) -> float:
    metric = entry.get("metric")
    if metric is None:
        return float("-inf") if reverse else float("inf")
    return float(metric)


def _prune_best_k(root: Path, idx: Dict[str, Any]) -> None:
    entries = idx.get("entries", [])
    top_k = int(idx.get("top_k", 1))
    mode = str(idx.get("mode", "min")).lower()
    reverse = True if mode == "max" else False

    entries_sorted = sorted(
        entries, key=lambda e: _metric_sort_key(e, reverse=reverse), reverse=reverse
    )
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
        env=capture_environment_summary(),
        metric_key=metric_key,
        metric_value=metric_value,
        sha256=None,
    )

    # Serialize payload (state + meta stub for verification)
    payload = {"state": state, "meta": asdict(meta)}
    digest = _digest_payload(payload).hex()
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
    digest_meta = {k: v for k, v in meta_dict.items() if k != "sha256"}
    digest_meta.setdefault("sha256", None)
    digest_payload = {"state": obj.get("state", {}), "meta": digest_meta}
    actual = _digest_payload(digest_payload).hex()
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
    digest_meta = {k: v for k, v in meta_dict.items() if k != "sha256"}
    digest_meta.setdefault("sha256", None)
    digest_payload = {"state": state, "meta": digest_meta}
    if _digest_payload(digest_payload).hex() != meta.sha256:
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
        key=lambda e: _metric_sort_key(e, reverse=reverse),
        reverse=reverse,
    )
    best = entries_sorted[0]
    path = root / best["path"]
    state, meta = load_checkpoint(path)
    return state, meta, path
