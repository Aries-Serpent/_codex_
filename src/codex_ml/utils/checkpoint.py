"""Checkpoint helpers with checksum verification and RNG persistence."""

from __future__ import annotations

import hashlib
import json
import random
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

import torch

try:  # pragma: no cover - numpy is optional for deployments
    import numpy as _np
except Exception:  # pragma: no cover - gracefully handle absence
    _np = None  # type: ignore[assignment]

__all__ = ["save_checkpoint", "load_checkpoint"]


def _capture_rng_state() -> Dict[str, Any]:
    state: Dict[str, Any] = {"python": random.getstate()}
    if _np is not None:
        try:
            state["numpy"] = _np.random.get_state()
        except Exception:  # pragma: no cover - numpy edge cases
            pass
    try:
        state["torch_cpu"] = torch.random.get_rng_state()
    except Exception:  # pragma: no cover - guard against torch quirks
        pass
    if torch.cuda.is_available():  # pragma: no cover - optional GPU support
        try:
            state["torch_cuda_all"] = torch.cuda.get_rng_state_all()
        except Exception:
            pass
    return state


def _restore_rng_state(state: Mapping[str, Any]) -> None:
    try:
        py_state = state.get("python")
        if py_state is not None:
            random.setstate(py_state)
    except Exception:  # pragma: no cover - corrupt payloads ignored
        pass
    if _np is not None:
        try:
            np_state = state.get("numpy")
            if np_state is not None:
                _np.random.set_state(np_state)
        except Exception:  # pragma: no cover
            pass
    try:
        torch_state = state.get("torch_cpu")
        if torch_state is not None:
            torch.random.set_rng_state(torch_state)
    except Exception:  # pragma: no cover
        pass
    if torch.cuda.is_available():  # pragma: no cover - optional GPU
        try:
            cuda_state = state.get("torch_cuda_all")
            if cuda_state is not None:
                torch.cuda.set_rng_state_all(cuda_state)
        except Exception:
            pass


def _component_paths(out_dir: Path) -> Iterable[Path]:
    for name in ("model.pt", "optimizer.pt", "scheduler.pt", "rng.pt"):
        candidate = out_dir / name
        if candidate.exists():
            yield candidate


def _compute_directory_digest(out_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(_component_paths(out_dir), key=lambda item: item.name):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb", buffering=0) as handle:
            while True:
                chunk = handle.read(128 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    return digest.hexdigest()


def _checksum_path(out_dir: Path) -> Path:
    return out_dir / "checkpoint.sha256"


def _index_path(out_dir: Path) -> Path:
    return out_dir.parent / "index.json"


def _update_best_k(
    out_dir: Path,
    digest: str,
    metric_name: str,
    metric_value: float,
    best_k: int,
) -> None:
    if best_k <= 0:
        return
    index_path = _index_path(out_dir)
    entry = {
        "path": out_dir.name,
        "metric": float(metric_value),
        "metric_name": metric_name,
        "checksum": digest,
    }
    try:
        existing = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            existing = []
    except Exception:
        existing = []
    filtered: list[Dict[str, Any]] = [rec for rec in existing if rec.get("path") != out_dir.name]
    filtered.append(entry)
    filtered.sort(key=lambda rec: float(rec.get("metric", float("inf"))))
    keep_count = max(1, int(best_k))
    keep = filtered[:keep_count]
    to_remove = filtered[keep_count:]
    index_path.write_text(json.dumps(keep, indent=2), encoding="utf-8")
    for rec in to_remove:
        rel = rec.get("path")
        if not isinstance(rel, str):
            continue
        target = out_dir.parent / rel
        shutil.rmtree(target, ignore_errors=True)


def save_checkpoint(
    *,
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    scheduler: Optional[Any],
    out_dir: Path,
    metadata: Optional[Dict[str, Any]] = None,
    metric_name: str = "eval_loss",
    metric_value: Optional[float] = None,
    best_k: Optional[int] = None,
) -> Path:
    """Persist training state and emit checksum information."""

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), out_dir / "model.pt")
    if optimizer is not None:
        torch.save(optimizer.state_dict(), out_dir / "optimizer.pt")
    if scheduler is not None and hasattr(scheduler, "state_dict"):
        torch.save(scheduler.state_dict(), out_dir / "scheduler.pt")

    torch.save(_capture_rng_state(), out_dir / "rng.pt")

    digest = _compute_directory_digest(out_dir)
    _checksum_path(out_dir).write_text(digest, encoding="utf-8")

    meta_payload: Dict[str, Any] = {"version": 2, "checkpoint_sha256": digest}
    if metadata:
        meta_payload.update(metadata)
    (out_dir / "metadata.json").write_text(
        json.dumps(meta_payload, indent=2, sort_keys=True), encoding="utf-8"
    )

    if metric_value is not None and best_k is not None:
        try:
            _update_best_k(out_dir, digest, metric_name, float(metric_value), int(best_k))
        except Exception:
            pass

    return out_dir


def _verify_checksum(out_dir: Path) -> None:
    checksum_file = _checksum_path(out_dir)
    if not checksum_file.exists():
        return
    expected = checksum_file.read_text(encoding="utf-8").strip()
    actual = _compute_directory_digest(out_dir)
    if expected != actual:
        raise ValueError("checkpoint checksum mismatch")


def load_checkpoint(
    *,
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    scheduler: Optional[Any],
    ckpt_dir: Path,
    map_location: Optional[str] = "cpu",
) -> Dict[str, Any]:
    """Load training state from ``ckpt_dir`` and restore RNG state."""

    ckpt_dir = Path(ckpt_dir)
    _verify_checksum(ckpt_dir)

    state = torch.load(ckpt_dir / "model.pt", map_location=map_location)
    model.load_state_dict(state)

    opt_path = ckpt_dir / "optimizer.pt"
    if optimizer is not None and opt_path.exists():
        optimizer.load_state_dict(torch.load(opt_path, map_location=map_location))

    sched_path = ckpt_dir / "scheduler.pt"
    if scheduler is not None and sched_path.exists():
        scheduler.load_state_dict(torch.load(sched_path, map_location=map_location))

    rng_path = ckpt_dir / "rng.pt"
    if rng_path.exists():
        try:
            rng_state = torch.load(rng_path, map_location="cpu")
            if isinstance(rng_state, Mapping):
                _restore_rng_state(rng_state)
        except Exception:
            pass

    meta_path = ckpt_dir / "metadata.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
