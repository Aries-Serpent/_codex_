"""Checkpoint helpers with checksum verification and RNG persistence."""

from __future__ import annotations

import hashlib
import json
import pickle
import random as _random
import shutil
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

try:  # Keep schema alignment with checkpoint_core when available
    from codex_ml.utils.checkpoint_core import SCHEMA_VERSION as _CORE_SCHEMA_VERSION
except Exception:  # pragma: no cover - checkpoint_core optional in minimal installs
    _CORE_SCHEMA_VERSION = "1.0"

CHECKPOINT_METADATA_SCHEMA_VERSION = str(_CORE_SCHEMA_VERSION)

try:  # pragma: no cover - optional torch dependency in lightweight environments
    import torch  # type: ignore
except Exception:  # pragma: no cover - allow checkpoint utilities without torch
    torch = None  # type: ignore[assignment]

try:  # pragma: no cover - numpy is optional for deployments
    import numpy as _np  # type: ignore
except Exception:  # pragma: no cover - gracefully handle absence
    _np = None  # type: ignore[assignment]

__all__ = ["save_checkpoint", "load_checkpoint", "restore_into", "prune_best_k"]


def _sha256_file(path: str, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _dump_payload(path: Path, payload: Any) -> None:
    if torch is not None:
        torch.save(payload, path)
    else:  # pragma: no cover - torchless deployments rely on pickle
        with path.open("wb") as fh:
            pickle.dump(payload, fh, protocol=pickle.HIGHEST_PROTOCOL)


def _load_payload(path: Path, map_location: str | None = None) -> Any:
    if torch is not None:
        return torch.load(path, map_location=map_location)
    with path.open("rb") as fh:  # pragma: no cover - pickle fallback
        return pickle.load(fh)


def _capture_rng_state_raw() -> dict[str, Any]:
    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        try:
            state["numpy"] = _np.random.get_state()
        except Exception:  # pragma: no cover - numpy edge cases
            pass
    if torch is not None:
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


def _serialize_rng_state(raw: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    py_state = raw.get("python")
    if py_state is not None:
        try:
            version, sequence, gauss = py_state
            payload["python"] = {
                "version": int(version),
                "state": list(sequence),
                "gauss": gauss,
            }
        except Exception:  # pragma: no cover - defensive against malformed tuples
            pass

    np_state = raw.get("numpy")
    if np_state is not None:
        try:
            key, keys, pos, has_gauss, cached = np_state
            payload["numpy"] = {
                "key": str(key),
                "state": list(keys.tolist() if hasattr(keys, "tolist") else list(keys)),
                "pos": int(pos),
                "has_gauss": int(has_gauss),
                "cached_gaussian": float(cached),
            }
        except Exception:
            pass

    torch_state = raw.get("torch_cpu")
    if torch_state is not None:
        try:
            if hasattr(torch_state, "tolist"):
                payload["torch_cpu"] = list(torch_state.tolist())
        except Exception:  # pragma: no cover
            pass

    cuda_state = raw.get("torch_cuda_all")
    if cuda_state is not None:
        try:
            payload["torch_cuda_all"] = [
                list(state.tolist()) if hasattr(state, "tolist") else list(state)
                for state in cuda_state
            ]
        except Exception:  # pragma: no cover - tolerate CUDA edge cases
            pass

    return payload


def _deserialize_rng_state(data: Mapping[str, Any]) -> dict[str, Any]:
    restored: dict[str, Any] = {}

    py_state = data.get("python")
    if isinstance(py_state, Mapping):
        try:
            restored["python"] = (
                int(py_state.get("version", 3)),
                tuple(int(item) for item in py_state.get("state", [])),
                py_state.get("gauss"),
            )
        except Exception:
            pass

    np_state = data.get("numpy")
    if isinstance(np_state, Mapping) and _np is not None:
        try:
            restored["numpy"] = (
                str(np_state.get("key", "MT19937")),
                _np.array(np_state.get("state", []), dtype=_np.uint32),
                int(np_state.get("pos", 0)),
                int(np_state.get("has_gauss", 0)),
                float(np_state.get("cached_gaussian", 0.0)),
            )
        except Exception:
            pass

    torch_cpu = data.get("torch_cpu")
    if torch is not None and isinstance(torch_cpu, list):
        try:
            restored["torch_cpu"] = torch.tensor(torch_cpu, dtype=torch.uint8)
        except Exception:
            pass

    cuda_states = data.get("torch_cuda_all")
    if torch is not None and isinstance(cuda_states, list):
        tensors = []
        for entry in cuda_states:
            if isinstance(entry, list):
                try:
                    tensors.append(torch.tensor(entry, dtype=torch.uint8))
                except Exception:
                    continue
        if tensors:
            restored["torch_cuda_all"] = tensors

    return restored


def _restore_rng_state(state: Mapping[str, Any]) -> None:
    try:
        py_state = state.get("python")
        if py_state is not None:
            _random.setstate(py_state)  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - corrupt payloads ignored
        pass

    if _np is not None:
        try:
            np_state = state.get("numpy")
            if np_state is not None:
                _np.random.set_state(np_state)  # type: ignore[arg-type]
        except Exception:  # pragma: no cover
            pass

    if torch is not None:
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
    for name in ("model.pt", "optimizer.pt", "scheduler.pt", "rng.pt", "rng.json", "metadata.json"):
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
        "schema_version": CHECKPOINT_METADATA_SCHEMA_VERSION,
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
    filtered: list[dict[str, Any]] = [rec for rec in existing if rec.get("path") != out_dir.name]
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


def _verify_checksums(out_dir: Path, *, strict: bool) -> None:
    verified = False
    model_file = out_dir / "model.pt"
    sha_file = model_file.with_suffix(model_file.suffix + ".sha256")
    if model_file.exists() and sha_file.exists():
        expected = sha_file.read_text(encoding="utf-8").strip()
        actual = _sha256_file(str(model_file))
        verified = True
        if expected != actual and strict:
            raise ValueError(f"checkpoint checksum mismatch: {model_file}")
    checksum_file = _checksum_path(out_dir)
    if checksum_file.exists():
        expected = checksum_file.read_text(encoding="utf-8").strip()
        actual = _compute_directory_digest(out_dir)
        verified = True
        if expected != actual and strict:
            raise ValueError(f"checkpoint checksum mismatch: {checksum_file}")
    if strict and not verified:
        raise ValueError(f"missing checksum for checkpoint: {out_dir}")


def prune_best_k(checkpoint_dir: str | Path, k: int = 3) -> None:
    if k <= 0:
        return
    root = Path(checkpoint_dir)
    if not root.exists():
        return

    candidates: list[tuple[float, Path]] = []
    for item in root.iterdir():
        if item.is_dir() and (item / "model.pt").exists() or item.is_file() and item.suffix == ".pt":
            candidates.append((item.stat().st_mtime, item))

    candidates.sort(key=lambda pair: pair[0], reverse=True)
    for _, path in candidates[k:]:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                path.unlink()
            except FileNotFoundError:  # pragma: no cover - already gone
                pass
            for suffix in (".sha256", ".rng.json", ".metadata.json"):
                sidecar = path.with_suffix(path.suffix + suffix)
                try:
                    sidecar.unlink()
                except FileNotFoundError:
                    continue


def save_checkpoint(
    *,
    model: Any,
    optimizer: Any | None,
    scheduler: Any | None,
    out_dir: Path | str,
    metadata: dict[str, Any] | None = None,
    metric_name: str = "eval_loss",
    metric_value: float | None = None,
    metric: float | None = None,
    best_k: int | None = None,
) -> Path:
    """Persist training state and emit checksum information."""

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    state_dict = getattr(model, "state_dict", lambda: model)()
    model_path = out_dir / "model.pt"
    _dump_payload(model_path, state_dict)

    if optimizer is not None:
        opt_state = getattr(optimizer, "state_dict", lambda: optimizer)()
        _dump_payload(out_dir / "optimizer.pt", opt_state)

    if scheduler is not None and hasattr(scheduler, "state_dict"):
        try:
            sched_state = scheduler.state_dict()
        except Exception:  # pragma: no cover - scheduler without state
            sched_state = None
        if sched_state is not None:
            _dump_payload(out_dir / "scheduler.pt", sched_state)

    raw_rng = _capture_rng_state_raw()
    (out_dir / "rng.json").write_text(
        json.dumps(_serialize_rng_state(raw_rng), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    if torch is not None:
        try:
            _dump_payload(out_dir / "rng.pt", raw_rng)
        except Exception:  # pragma: no cover - torch serialization edge case
            pass

    model_sha_path = model_path.with_suffix(model_path.suffix + ".sha256")
    model_sha_path.write_text(_sha256_file(str(model_path)), encoding="utf-8")

    digest = _compute_directory_digest(out_dir)
    _checksum_path(out_dir).write_text(digest, encoding="utf-8")

    if metric_value is None and metric is not None:
        metric_value = metric

    meta_payload: dict[str, Any] = {
        "version": 3,
        "checkpoint_sha256": digest,
        "schema_version": CHECKPOINT_METADATA_SCHEMA_VERSION,
    }
    if metadata:
        meta_payload.update(metadata)
    if metric_value is not None:
        metrics = meta_payload.setdefault("metrics", {})
        if isinstance(metrics, dict):
            metrics[metric_name] = float(metric_value)

    (out_dir / "metadata.json").write_text(
        json.dumps(meta_payload, indent=2, sort_keys=True), encoding="utf-8"
    )

    if metric_value is not None and best_k is not None:
        try:
            _update_best_k(out_dir, digest, metric_name, float(metric_value), int(best_k))
        except Exception:
            pass
    elif best_k is not None:
        try:
            prune_best_k(out_dir.parent, int(best_k))
        except Exception:
            pass

    return out_dir


def restore_into(
    model: Any, optimizer: Any | None, scheduler: Any | None, payload: Mapping[str, Any]
) -> None:
    try:
        model_state = payload.get("model")
        if model is not None and model_state is not None:
            load_state = getattr(model, "load_state_dict", None)
            if callable(load_state):
                load_state(model_state)  # type: ignore[arg-type]
    except Exception:
        pass

    try:
        opt_state = payload.get("optimizer")
        if optimizer is not None and opt_state is not None:
            load_state = getattr(optimizer, "load_state_dict", None)
            if callable(load_state):
                load_state(opt_state)  # type: ignore[arg-type]
    except Exception:
        pass

    try:
        sched_state = payload.get("scheduler")
        if scheduler is not None and sched_state is not None:
            load_state = getattr(scheduler, "load_state_dict", None)
            if callable(load_state):
                load_state(sched_state)  # type: ignore[arg-type]
    except Exception:
        pass


def load_checkpoint(
    *,
    model: Any,
    optimizer: Any | None,
    scheduler: Any | None,
    ckpt_dir: Path | str,
    map_location: str | None = "cpu",
    strict: bool = False,
) -> dict[str, Any]:
    """Load training state from ``ckpt_dir`` and restore RNG state."""

    ckpt_dir = Path(ckpt_dir)
    try:
        _verify_checksums(ckpt_dir, strict=strict)
    except ValueError:
        if strict:
            raise

    model_path = ckpt_dir / "model.pt"
    if model_path.exists():
        try:
            state = _load_payload(model_path, map_location if torch is not None else None)
            loader = getattr(model, "load_state_dict", None)
            if callable(loader):
                loader(state)
        except Exception:
            pass

    opt_path = ckpt_dir / "optimizer.pt"
    if optimizer is not None and opt_path.exists():
        try:
            opt_state = _load_payload(opt_path, map_location if torch is not None else None)
            loader = getattr(optimizer, "load_state_dict", None)
            if callable(loader):
                loader(opt_state)
        except Exception:
            pass

    sched_path = ckpt_dir / "scheduler.pt"
    if scheduler is not None and sched_path.exists():
        try:
            sched_state = _load_payload(sched_path, map_location if torch is not None else None)
            loader = getattr(scheduler, "load_state_dict", None)
            if callable(loader):
                loader(sched_state)
        except Exception:
            pass

    rng_json = ckpt_dir / "rng.json"
    if rng_json.exists():
        try:
            data = json.loads(rng_json.read_text(encoding="utf-8"))
            _restore_rng_state(_deserialize_rng_state(data))
        except Exception:
            pass
    else:
        rng_pt = ckpt_dir / "rng.pt"
        if rng_pt.exists():
            try:
                raw = _load_payload(rng_pt, map_location="cpu" if torch is not None else None)
                if isinstance(raw, Mapping):
                    _restore_rng_state(raw)
            except Exception:
                pass

    meta_path = ckpt_dir / "metadata.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
