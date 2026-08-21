"""
Checkpoint Core Module

This module provides functionality for checkpoint core.

Usage:
    from utils.checkpoint_core import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import pickle
import platform
import random
import re
import shutil
import time
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from itertools import count
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import torch

    # Check if this is the shadow stub module (real torch not installed)
    if getattr(torch, "IS_CODEX_STUB", False):
        torch = None  # type: ignore[assignment]
except (ImportError, AttributeError):  # pragma: no cover
    torch = None  # type: ignore[assignment]

try:
    import numpy as np
except (ImportError, AttributeError):  # pragma: no cover
    np = None


try:  # packaging is optional but preferred for version parsing
    from packaging.version import Version
except (ImportError, AttributeError):  # pragma: no cover - treated as unavailable
    Version = None  # type: ignore[misc,assignment]

try:  # provenance extras are optional
    from .provenance import environment_summary as _environment_summary
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - optional dependency failures tolerated
    _environment_summary = None  # type: ignore[assignment]

from .atomic_io import safe_write_bytes, safe_write_text  # noqa: E402
from .runmeta import collect_run_meta  # noqa: E402
from .safe_pickle import safe_pickle_load_bytes, trusted_pickle_dumps  # noqa: E402

try:
    from .checkpoint_integrity import attach_integrity, snapshot_config
except (ImportError, AttributeError):  # pragma: no cover - optional dependency issues tolerated
    attach_integrity = None  # type: ignore[assignment]

    def snapshot_config(_config: object) -> dict[str, Any]:  # type: ignore
        return {}


try:  # runtime metadata sidecar (best-effort)
    from .run_metadata import collect_run_metadata, write_run_manifest
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - optional dependency

    def collect_run_metadata(*_args: object, **_kwargs: object) -> dict[str, Any]:  # type: ignore
        return {}

    def write_run_manifest(*_args: object, **_kwargs: object) -> None:  # type: ignore
        return None


# NOTE: _atomic_write is an internal primitive. Do not call it outside this module.
# All callers must use save_checkpoint(), which enriches metadata integrity and rewrites safely.
__all__ = ["_epoch_dir_sort_key", "save_checkpoint"]  # explicitly export key helpers


SCHEMA_VERSION = "1.0"


def _epoch_dir_sort_key(path: Path | str) -> tuple[int, int | str, str]:
    """Return a sort key ordering numeric epoch directories before ad-hoc entries."""

    name = Path(path).name
    match = re.search(r"(\d+)", name)
    if match:
        return (0, int(match.group(1)), name)
    return (1, name, name)


class CheckpointIntegrityError(RuntimeError):
    pass


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _now() -> int:
    return int(time.time())


def _git_sha_try() -> str | None:
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
        except (IOError, OSError, ModuleNotFoundError, ImportError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            return None
    return None


def _rng_snapshot() -> dict[str, Any]:
    # Convert Python random state to JSON-serializable format
    # Python random.getstate() returns: (version, tuple_of_ints, None)
    python_state = random.getstate()
    snap: dict[str, Any] = {
        "python": {
            "version": python_state[0],
            "keys": list(python_state[1]),  # Convert inner tuple to list explicitly
            "gauss_next": python_state[2],
        }
    }
    if np is not None:
        try:
            # NumPy RNG state is a tuple: (name, array, pos, has_gauss, cached_gauss)
            # Convert to JSON-serializable format
            if np is not None:
                numpy_state = np.random.get_state()
                snap["numpy"] = {
                    "name": numpy_state[0],
                    "keys": numpy_state[1].tolist(),
                    "pos": int(numpy_state[2]),
                    "has_gauss": int(numpy_state[3]),
                    "cached_gauss": float(numpy_state[4]),
                }
        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
    if torch is not None:
        try:
            snap["torch_cpu"] = torch.get_rng_state().tolist()  # tensor → list
        except (ValueError, TypeError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
        try:
            if torch.cuda.is_available():  # pragma: no cover (GPU not in CPU CI)
                # Convert CUDA RNG state tensors to lists for JSON serialization
                # Store both data and dtype to ensure exact restoration
                cuda_states = torch.cuda.get_rng_state_all()
                snap["torch_cuda"] = [
                    {"data": state.tolist(), "dtype": str(state.dtype)} for state in cuda_states
                ]
        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
    return snap


def _rng_restore(snap: Mapping[str, Any]) -> None:
    try:
        if "python" in snap:
            python_state = snap["python"]
            # Support both new dict format and legacy tuple format
            if isinstance(python_state, dict):
                # New format: convert back to tuple
                state_tuple = (
                    python_state["version"],
                    tuple(python_state["keys"]),  # Convert list back to tuple
                    python_state["gauss_next"],
                )
                random.setstate(state_tuple)
            else:
                # Legacy format: use directly (already a tuple or list from JSON)
                # If it's a list from JSON, convert to tuple with inner tuple
                if isinstance(python_state, list):
                    if len(python_state) >= 2 and isinstance(python_state[1], list):
                        python_state = (
                            python_state[0],
                            tuple(python_state[1]),
                            python_state[2],
                        )
                    else:
                        python_state = tuple(python_state)
                random.setstate(python_state)
    except (ValueError, TypeError, RuntimeError) as e:
        logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Exception: %s", e, exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
    if np is not None:
        try:
            if "numpy" in snap:
                numpy_state = snap["numpy"]
                # Support both new dict format and legacy tuple format
                if isinstance(numpy_state, dict):
                    # New format: convert back to tuple
                    state_tuple = (  # type: ignore
                        numpy_state["name"],
                        np.array(numpy_state["keys"], dtype=np.uint32),
                        numpy_state["pos"],
                        numpy_state["has_gauss"],
                        numpy_state["cached_gauss"],
                    )
                    np.random.set_state(state_tuple)

                else:
                    # Legacy format: convert from JSON-deserialized format
                    # If it's a tuple/list from JSON, ensure array element is converted
                    if isinstance(numpy_state, (tuple, list)) and len(numpy_state) >= 5:
                        # Legacy tuple format from JSON: (name, [list_of_ints], pos, has_gauss, cached_gauss)  # noqa: E501
                        state_tuple = (  # type: ignore
                            numpy_state[0],
                            (
                                np.array(numpy_state[1], dtype=np.uint32)
                                if isinstance(numpy_state[1], list)
                                else numpy_state[1]
                            ),
                            numpy_state[2],
                            numpy_state[3],
                            numpy_state[4],
                        )
                        np.random.set_state(state_tuple)

                    else:
                        # Direct tuple format (not from JSON)
                        np.random.set_state(numpy_state)
        except (ValueError, TypeError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
    if torch is not None:
        try:
            if "torch_cpu" in snap:
                torch_state_raw = snap["torch_cpu"]
                if torch_state_raw is not None:
                    torch_cpu_state = torch.tensor(torch_state_raw, dtype=torch.uint8)
                    torch.set_rng_state(torch_cpu_state)
        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
        try:
            if "torch_cuda" in snap and torch.cuda.is_available():  # pragma: no cover
                # Convert lists back to tensors for CUDA RNG state restoration
                # Create tensors on the appropriate CUDA device to maintain determinism
                cuda_states_list = snap["torch_cuda"]
                cuda_states = []
                for i, state_info in enumerate(cuda_states_list):
                    # Support both old format (list) and new format (dict with dtype)
                    if isinstance(state_info, dict):
                        data = state_info["data"]
                        dtype_str = state_info.get("dtype", "torch.uint8")
                        # Parse dtype string like "torch.uint8" to actual dtype
                        dtype = getattr(torch, dtype_str.split(".")[-1], torch.uint8)
                    else:
                        # Legacy format: plain list, assume uint8
                        data = state_info
                        dtype = torch.uint8
                    tensor = torch.tensor(data, dtype=dtype, device=f"cuda:{i}")
                    cuda_states.append(tensor)
                torch.cuda.set_rng_state_all(cuda_states)
        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]


def capture_rng_state() -> dict[str, Any]:
    """Backwards compatible wrapper returning the current RNG state."""

    return _rng_snapshot()


def restore_rng_state(state: Mapping[str, Any]) -> None:
    """Backwards compatible wrapper restoring the provided RNG state."""

    _rng_restore(dict(state))


def capture_environment_summary() -> dict[str, Any]:
    """Collect lightweight environment details for checkpoint metadata.

    Keep this summary compact and stable so metadata.json remains small and
    predictable across environments. The richer provenance report is intentionally
    not used here because it emits very large package inventories that regress
    downstream schema expectations and checkpoint metadata readability.
    """
    summary: dict[str, Any] = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    try:
        summary["timestamp_utc"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover
        logger.debug(
            "Failed to get timestamp: %s", exc
        )  # codeql[py/clear-text-logging-sensitive-data]

    if np is not None:
        try:
            summary["numpy_version"] = str(np.__version__)
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover
            logger.debug(
                "Failed to get numpy version: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
    if torch is not None:
        try:
            summary["torch_version"] = str(torch.__version__)
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover
            logger.debug(
                "Failed to get torch version: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]
        try:
            summary["torch_cuda_available"] = bool(torch.cuda.is_available())
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover
            logger.debug(
                "Failed to check CUDA availability: %s", exc
            )  # codeql[py/clear-text-logging-sensitive-data]

    return summary


@dataclass
class CheckpointMeta:
    schema_version: str
    created_at: int
    git_sha: str | None
    config_hash: str | None
    rng: dict[str, Any]
    env: dict[str, Any]
    metric_key: str | None
    metric_value: float | None
    sha256: str | None  # of the serialized payload (bytes)
    config_snapshot: dict[str, Any] | None = None
    config_version: str | None = None
    dataset_version: str | None = None


def _config_hash(config: dict[str, Any] | None) -> str | None:
    if not config:
        return None
    try:
        payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
    except (ValueError, TypeError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return None


def _serialize_payload(state: dict[str, Any]) -> bytes:
    """
    Serialize trusted checkpoint state to bytes.

    Trust boundary:
    - Input is process-created checkpoint state assembled by save_checkpoint().
    - For new checkpoints we prefer torch.save() because it preserves tensors
      without exposing external deserialization entrypoints at write time.
    - If torch serialization is unavailable, we fall back to the audited
      trusted_pickle_dumps() helper instead of calling pickle directly.
    """
    buf = io.BytesIO()
    torch_save = getattr(torch, "save", None) if torch is not None else None
    if callable(torch_save):
        try:
            torch_save(state, buf)
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            return trusted_pickle_dumps(state)
    else:
        return trusted_pickle_dumps(state)
    return buf.getvalue()


def _digest_payload(payload: dict[str, Any]) -> bytes:
    """Produce a deterministic byte representation for hashing metadata.

    Residual reviewed boundary:
    - Non-JSON-native leaf values still need a stable binary representation for
      integrity hashing.
    - Those leaves are serialized through trusted_pickle_dumps(), which keeps
      the pickle boundary centralized and limited to process-created objects.
    """
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
        if np is not None and isinstance(value, np.ndarray):
            hasher.update(b"ndarray")
            hasher.update(str(value.dtype).encode("utf-8"))
            hasher.update(str(value.shape).encode("utf-8"))
            hasher.update(value.tobytes())
            return
        torch_is_tensor = getattr(torch, "is_tensor", None) if torch is not None else None
        if callable(torch_is_tensor) and torch_is_tensor(value):
            tensor = value.detach().cpu()
            hasher.update(b"tensor")
            hasher.update(str(tensor.dtype).encode("utf-8"))
            hasher.update(str(tuple(tensor.shape)).encode("utf-8"))
            hasher.update(tensor.numpy().tobytes())
            return

        hasher.update(b"pickle")
        hasher.update(trusted_pickle_dumps(value))

    _update(payload)
    return hasher.digest()


def _torch_supports_weights_only() -> bool:
    if torch is None:
        return False
    version = getattr(torch, "__version__", None)
    if not version or Version is None:
        return False
    try:
        # Strip local version identifiers such as "+cpu"
        core_version = version.split("+")[0]
        return Version(core_version) >= Version("2.0.0")
    except (ValueError, TypeError, RuntimeError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return False


def _can_retry_without_weights_only(exc: BaseException) -> bool:
    if not isinstance(exc, TypeError):
        return False
    message = str(exc).lower()
    # Compatibility fallback is only valid when the Torch API itself rejects the
    # `weights_only` keyword. Payload/runtime failures must fail closed.
    return any(
        token in message
        for token in (
            "unexpected keyword argument 'weights_only'",
            "unknown keyword argument 'weights_only'",
            "unexpected keyword: weights_only",
            "unknown keyword: weights_only",
        )
    )


def _deserialize_payload(
    b: bytes, *, map_location: str | torch.device | None = "cpu"
) -> dict[str, Any]:
    """Deserialize checkpoint bytes through the safest available path.

    Security order:
    1. Prefer torch.load(..., weights_only=True) for tensor-first checkpoints.
    2. If torch deserialization is unavailable or rejects the payload, fall
       back to safe_pickle_load_bytes(..., use_restricted_unpickler=True).

    This keeps checkpoint reads on safe-serialization paths by default while
    preserving compatibility with reviewed legacy payloads.
    """
    buf = io.BytesIO(b)
    torch_load = getattr(torch, "load", None) if torch is not None else None
    if callable(torch_load):
        kwargs: dict[str, Any] = {}
        if map_location is not None:
            kwargs["map_location"] = map_location
        use_weights_only = _torch_supports_weights_only()
        if use_weights_only:
            kwargs["weights_only"] = True
        try:
            return torch_load(buf, **kwargs)
        except TypeError as exc:
            logger.debug("torch.load rejected payload: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]
            if use_weights_only and "weights_only" in kwargs and _can_retry_without_weights_only(exc):
                logger.warning(
                    "Rejecting unsafe weights_only retry path for payload failure; keeping restricted loader boundary.",
                    exc_info=False,
                )
                buf.seek(0)
                raise
            buf.seek(0)
        except (ValueError, RuntimeError) as exc:
            logger.debug("torch.load rejected payload: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]
            buf.seek(0)
    # Legacy compatibility fallback: older reviewed checkpoints may not be
    # tensor-first payloads that torch.load(..., weights_only=True) can decode.
    # When that happens, keep the fallback on RestrictedUnpickler so the
    # deserialization boundary stays constrained even for legacy payloads.
    return safe_pickle_load_bytes(buf.getvalue(), use_restricted_unpickler=True)


_CKPT_COUNTER = count()


def _ckpt_name(prefix: str = "ckpt") -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
    suffix = next(_CKPT_COUNTER)
    return f"{prefix}-{timestamp}-{suffix:04d}.pt"


def _read_bytes(p: Path) -> bytes:
    return p.read_bytes()


def _index_path(root: Path) -> Path:
    return root / "index.json"


def _load_index(root: Path) -> dict[str, Any]:
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
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return {
            "schema_version": SCHEMA_VERSION,
            "metric_key": None,
            "mode": "min",
            "top_k": 1,
            "entries": [],
        }


def _write_index(root: Path, idx: dict[str, Any]) -> None:
    safe_write_text(_index_path(root), json.dumps(idx, indent=2, sort_keys=True))


def _metric_sort_key(entry: Mapping[str, Any], *, reverse: bool) -> float:
    metric = entry.get("metric")
    if metric is None:
        return float("-inf") if reverse else float("inf")
    return float(metric)


def _prune_best_k(
    root: Path, idx: dict[str, Any], *, exclude: frozenset[str] | None = None
) -> None:
    entries = idx.get("entries", [])
    top_k = int(idx.get("top_k", 1))
    mode = str(idx.get("mode", "min")).lower()
    reverse = mode == "max"

    entries_sorted = sorted(
        entries, key=lambda e: _metric_sort_key(e, reverse=reverse), reverse=reverse
    )
    keep = entries_sorted[:top_k]
    remove = {e["path"] for e in entries if e not in keep}
    # Delete files/directories that are not in keep
    for rel in remove:
        if exclude and rel in exclude:
            continue
        try:
            target = root / rel
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
    idx["entries"] = keep


def save_checkpoint(
    checkpoint_dir: str | Path,
    state: dict[str, Any] | None = None,
    *,
    payload: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    metric_value: float | None = None,
    metric_key: str = "val_loss",
    best_metric: str | None = None,
    mode: str = "min",
    top_k: int = 3,
    best_k: int | None = None,
    config: dict[str, Any] | None = None,
    prefix: str = "ckpt",
    include_rng: bool = True,
    keep_last: int | None = None,
) -> tuple[Path, CheckpointMeta]:
    """
    Save a checkpoint with atomic IO, metadata, and update best-k retention index.

    Returns: (checkpoint_path, metadata)
    """
    if best_k is not None:
        top_k = best_k
    if best_metric is not None:
        metric_key = best_metric

    root = Path(checkpoint_dir)
    root.mkdir(parents=True, exist_ok=True)
    metadata_sidecar = dict(metadata) if metadata is not None else None

    if metric_value is None and metadata is not None:
        metrics = metadata.get("metrics")
        if isinstance(metrics, dict) and metric_key in metrics:
            try:
                metric_value = float(metrics[metric_key])
            except (ValueError, TypeError, RuntimeError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                metric_value = metrics[metric_key]

    # Build metadata
    snapshot_data: dict[str, Any] | None = None
    if config is not None:
        try:
            candidate = snapshot_config(config)
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            candidate = {}
        if candidate:
            snapshot_data = dict(candidate)

    cfg_version = None
    dataset_version = None
    if isinstance(config, dict):
        cfg_version = str(config.get("config_version")) if "config_version" in config else None
        dataset_version = (
            str(config.get("dataset_version")) if "dataset_version" in config else None
        )

    meta = CheckpointMeta(
        schema_version=SCHEMA_VERSION,
        created_at=_now(),
        git_sha=_git_sha_try(),
        config_hash=_config_hash(config),
        rng=_rng_snapshot() if include_rng else {},
        env=capture_environment_summary(),
        metric_key=metric_key,
        metric_value=metric_value,
        sha256=None,
        config_snapshot=snapshot_data,
        config_version=cfg_version,
        dataset_version=dataset_version,
    )

    # Serialize payload (state + meta stub for verification)
    state_data = payload if payload is not None else (state or {})
    if include_rng and isinstance(state_data, dict):
        # Ensure RNG snapshots are embedded in the serialized state for
        # compatibility with loaders that expect `state["rng"]` rather than
        # reading from metadata only.
        state_data = dict(state_data)
        state_data.setdefault("rng", meta.rng)

    payload_obj = {"state": state_data, "meta": asdict(meta)}
    if metadata:
        payload_obj["meta"]["user_metadata"] = metadata
    if meta.config_snapshot is None:
        payload_obj["meta"].pop("config_snapshot", None)

    # Step 1: compute pre-embed digest (used by verify_checkpoint for integrity)
    payload_obj["meta"]["sha256"] = None
    raw = _serialize_payload(payload_obj)
    digest = hashlib.sha256(raw).hexdigest()
    meta.sha256 = digest

    # Step 2: embed digest and produce final bytes (this is what gets written to disk)
    payload_obj["meta"]["sha256"] = digest
    raw = _serialize_payload(payload_obj)
    file_digest = hashlib.sha256(raw).hexdigest()

    # Emit standalone digest matching the actual file content
    safe_write_text(root / "state.sha256", file_digest)

    if metadata_sidecar is not None:
        sidecar = {
            "schema_version": SCHEMA_VERSION,
            "digest_sha256": file_digest,
            "environment": meta.env,
        }
        sidecar.update(metadata_sidecar)
        safe_write_bytes(root / "metadata.json", lambda: json.dumps(sidecar).encode("utf-8"))

    # Choose name and write atomically
    ckpt_name = _ckpt_name(prefix=prefix)
    ckpt_path = root / ckpt_name
    safe_write_bytes(ckpt_path, lambda: raw)

    # Compatibility alias expected by some tooling/tests
    state_alias = root / "state.pt"
    if not state_alias.exists():
        try:
            shutil.copyfile(ckpt_path, state_alias)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]

    if attach_integrity is not None:
        try:
            attach_integrity(
                ckpt_path,
                metadata=(
                    {"config_snapshot": meta.config_snapshot} if meta.config_snapshot else None
                ),
                relative_to=root,
            )
        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: %s", e, exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]

    if keep_last:
        parent = root.parent
        candidates = sorted([p for p in parent.iterdir() if p.is_dir()], key=_epoch_dir_sort_key)
        for old in candidates[:-keep_last]:
            if old == root:
                continue
            try:
                shutil.rmtree(old)
            except (ValueError, TypeError, RuntimeError) as e:
                logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
                logger.warning(
                    "Exception: %s", e, exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]

    # Update index for this checkpoint directory
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
    # Backwards compatibility alias expected by older callers/tests
    safe_write_text(root / "best_index.json", json.dumps(idx["entries"], indent=2))

    # Aggregate index at the parent checkpoint root (tracks best directories)
    parent_idx = _load_index(root.parent)
    parent_idx["schema_version"] = SCHEMA_VERSION
    parent_idx["metric_key"] = metric_key
    parent_idx["mode"] = "min" if mode.lower().startswith("min") else "max"
    parent_idx["top_k"] = int(top_k)
    parent_idx.setdefault("entries", [])
    # Upsert: replace any existing entry for this directory to prevent duplicate accumulation
    # when save_checkpoint is called multiple times in the same directory (flat-file usage).
    parent_idx["entries"] = [e for e in parent_idx["entries"] if e.get("path") != root.name]
    parent_idx["entries"].append(
        {
            "path": root.name,
            "metric": metric_value,
            "created_at": meta.created_at,
            "sha256": digest,
        }
    )
    _prune_best_k(root.parent, parent_idx, exclude=frozenset({root.name}))
    _write_index(root.parent, parent_idx)
    safe_write_text(root.parent / "best_index.json", json.dumps(parent_idx["entries"], indent=2))

    try:
        manifest = dict(collect_run_metadata())
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        manifest = {}
    try:
        provenance = collect_run_meta()
        if provenance:
            manifest.setdefault("provenance", {}).update(provenance)
    except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
        logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Exception: %s", e, exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
    try:
        write_run_manifest(root, manifest)
    except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
        logger.debug("Exception: %s", e)  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Exception: %s", e, exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]

    return ckpt_path, meta


def verify_checkpoint(path: str | Path) -> CheckpointMeta:
    """
    Verify the checkpoint sha256 against embedded metadata; return parsed metadata if ok.
    """
    p = Path(path)
    raw = _read_bytes(p)
    try:
        obj = _deserialize_payload(raw)
    except (
        IOError,
        OSError,
        ModuleNotFoundError,
        ImportError,
        ValueError,
        EOFError,
        RuntimeError,
        TypeError,
        pickle.UnpicklingError,
    ) as exc:
        raise CheckpointIntegrityError(f"Failed to deserialize checkpoint: {p.name}") from exc
    if not isinstance(obj, dict):
        raise CheckpointIntegrityError(f"Checkpoint payload for {p.name} is not a mapping")
    meta_dict = obj.get("meta", {})
    version = meta_dict.get("schema_version")
    if version is None:
        raise CheckpointIntegrityError("Checkpoint metadata missing schema_version")
    if str(version) != SCHEMA_VERSION:
        raise CheckpointIntegrityError(
            f"Unsupported checkpoint schema_version={version}; expected {SCHEMA_VERSION}"
        )
    expected = meta_dict.get("sha256")
    if not expected:
        raise CheckpointIntegrityError("Missing sha256 in checkpoint metadata.")
    # Re-serialize with sha256=None (same form used during save to compute the digest)
    digest_meta = dict(meta_dict, sha256=None)
    digest_payload = {"state": obj.get("state", {}), "meta": digest_meta}
    actual = hashlib.sha256(_serialize_payload(digest_payload)).hexdigest()
    if actual != expected:
        raise CheckpointIntegrityError(
            f"Checksum mismatch for {p.name}: expected {expected}, got {actual}"
        )
    # Return a dataclass for convenience
    return CheckpointMeta(**{k: meta_dict.get(k) for k in CheckpointMeta.__annotations__})


def load_checkpoint(
    path: str | Path,
    *,
    restore_rng: bool = False,
    map_location: str | torch.device | None = "cpu",
) -> tuple[dict[str, Any], CheckpointMeta]:
    """
    Load a checkpoint file and optionally restore RNG state from metadata.
    """
    p = Path(path)
    if p.is_dir():
        state, meta, _actual = load_best(p)
        if restore_rng and meta.rng:
            _rng_restore(meta.rng)
        return state, meta

    raw = _read_bytes(p)
    try:
        obj = _deserialize_payload(raw, map_location=map_location)
    except (
        IOError,
        OSError,
        ModuleNotFoundError,
        ImportError,
        ValueError,
        EOFError,
        RuntimeError,
        TypeError,
        pickle.UnpicklingError,
    ) as exc:
        raise CheckpointIntegrityError(f"Failed to deserialize checkpoint: {p.name}") from exc
    if not isinstance(obj, dict):
        raise CheckpointIntegrityError(f"Checkpoint payload for {p.name} is not a mapping")
    meta_dict = obj.get("meta", {})
    state = obj.get("state", {})
    meta = CheckpointMeta(**{k: meta_dict.get(k) for k in CheckpointMeta.__annotations__})
    # Integrity verification
    digest_meta = dict(meta_dict, sha256=None)
    expected_digest = meta_dict.get("sha256")
    calc_digest = hashlib.sha256(
        _serialize_payload({"state": state, "meta": digest_meta})
    ).hexdigest()
    if expected_digest and calc_digest != expected_digest:
        raise CheckpointIntegrityError(f"Checksum mismatch for {p.name}")
    if restore_rng and meta.rng:
        _rng_restore(meta.rng)
    return state, meta


def load_best(
    checkpoint_dir: str | Path,
) -> tuple[dict[str, Any], CheckpointMeta, Path]:
    """
    Load the best checkpoint according to index.json (by metric and mode).
    """
    root = Path(checkpoint_dir)
    idx = _load_index(root)
    entries = idx.get("entries", [])
    if not entries:
        raise FileNotFoundError("No checkpoints found in index.")
    mode = idx.get("mode", "min").lower()
    reverse = mode == "max"
    entries_sorted = sorted(
        entries,
        key=lambda e: _metric_sort_key(e, reverse=reverse),
        reverse=reverse,
    )
    best = entries_sorted[0]
    path = root / best["path"]
    state, meta = load_checkpoint(path)
    return state, meta, path
