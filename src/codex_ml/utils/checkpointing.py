"""Checkpointing & Resuming Utilities (PyTorch-first, framework-aware).
Standard layout:
  output/checkpoints/epoch-{n}/
    - state.pt (torch) or state.pkl (fallback)
    - meta.json (epoch, metrics)
    - config.yaml/json
    - rng.json
Symlinks/markers:
  output/checkpoints/last -> latest epoch dir
  output/checkpoints/best -> best snapshot(s) tracked in best.json
"""

from __future__ import annotations

import contextlib
import hashlib
import inspect
import io
import json
import logging
import pickle
import platform
import random
import shutil
import subprocess
import sys
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional, Protocol, Union, runtime_checkable

try:  # Align schema metadata with checkpoint_core when available
    from codex_ml.utils import checkpoint_core
    from codex_ml.utils.checkpoint_core import SCHEMA_VERSION as _CORE_SCHEMA_VERSION
except (ImportError, AttributeError):  # pragma: no cover - optional dependency
    _CORE_SCHEMA_VERSION = "1.0"
    checkpoint_core = None

CHECKPOINT_METADATA_SCHEMA_VERSION = str(_CORE_SCHEMA_VERSION)

# Prefer provenance utilities when available
try:
    from codex_ml.utils.provenance import environment_summary as _prov_env_summary
except (ImportError, AttributeError):  # pragma: no cover - provenance optional
    _prov_env_summary = None

from codex_ml.utils import seed_registry as _seed_registry
from codex_ml.utils.seed_registry import (  # DR-001: breaks seeding↔checkpointing cycle
    register_seed_snapshot,
)

# ruff: noqa: E402, I001
from codex_ml.utils.seeding import set_reproducible  # after optional imports

from .checkpoint_event import maybe_emit_checkpoint_saved_event
from .safe_pickle import safe_pickle_dump, safe_pickle_load
from .storage import StorageProvider

logger = logging.getLogger(__name__)

try:
    from codex_ml.utils.provenance import _git_commit as _prov_git_commit
except (ImportError, AttributeError):  # pragma: no cover - provenance optional
    _prov_git_commit = None

try:  # pragma: no cover - optional codex_digest dependency
    from codex_digest.error_capture import log_error as capture_error
except (ImportError, AttributeError):  # pragma: no cover - fallback no-op

    def capture_error(
        step_no: str,
        step_desc: str,
        msg: str,
        ctx: str,
        *,
        errors_path: Optional[Path] = None,
    ) -> str:
        _ = (step_no, step_desc, msg, ctx, errors_path)
        return ""


import re


def _matches_error_pattern(error_msg: str, patterns: list[str]) -> bool:
    """
    Safe error message pattern matching using regex word boundaries.

    Replaces substring checks with regex patterns to prevent bypass vulnerabilities
    while maintaining compatibility with error message matching.

    Args:
        error_msg: The error message string to check
        patterns: List of exact phrases to match (e.g., ["issubclass() arg 2 must be a class"])

    Returns:
        True if any pattern matches the error message, False otherwise

    Security Model:
    - Uses regex word boundaries to match exact phrases
    - Prevents bypass attacks from substring matching
    - Safe for exception handling (untrusted error sources)
    """
    for pattern in patterns:
        # Escape special regex characters and use word boundaries
        escaped = re.escape(pattern)
        # Match the pattern with word boundaries for safety
        if re.search(rf"\b{escaped}\b", error_msg, re.IGNORECASE):
            return True
    return False


try:  # pragma: no cover - optional torch dependency
    import torch

    # Verify torch is actually functional (not just a stub)
    torch.get_rng_state()  # ensure get_rng_state is callable (catches stub modules)
    TORCH_AVAILABLE = True
except (ImportError, AttributeError):  # pragma: no cover - torch missing
    TORCH_AVAILABLE = False

try:  # pragma: no cover - optional numpy dependency
    import numpy as np

    NUMPY_AVAILABLE = True
except (ImportError, AttributeError):  # pragma: no cover - numpy missing
    NUMPY_AVAILABLE = False


_ORIGINAL_RANDOM_SEED = random.seed


def _random_seed_with_snapshot(a: Optional[Any] = None, version: int = 2) -> None:
    """Wrap ``random.seed`` to preserve the pre-draw RNG state for restores."""

    _ORIGINAL_RANDOM_SEED(a, version)
    try:
        register_seed_snapshot(python_state=random.getstate())
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Exception: <ERROR_TYPE>", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]


if getattr(random.seed, "__codex_wrapped__", False) is False:  # pragma: no cover - guard
    _random_seed_with_snapshot.__codex_wrapped__ = True  # type: ignore[attr-defined]
    random.seed = _random_seed_with_snapshot

if TORCH_AVAILABLE:
    _ORIGINAL_TORCH_MANUAL_SEED = torch.manual_seed

    def _torch_manual_seed_with_snapshot(seed: int) -> Any:
        result = _ORIGINAL_TORCH_MANUAL_SEED(seed)
        try:
            cuda_state = None
            if (
                getattr(torch, "cuda", None)
                and getattr(torch.cuda, "is_available", lambda: False)()
            ):
                try:
                    cuda_state = [s.tolist() for s in torch.cuda.get_rng_state_all()]
                except (ValueError, TypeError, RuntimeError):
                    logger.warning(
                        "Exception occurred", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    cuda_state = None
            register_seed_snapshot(
                torch_state=torch.get_rng_state().tolist(),
                torch_cuda_state=cuda_state,
            )
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: <ERROR_TYPE>", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
        return result

    if getattr(torch.manual_seed, "__codex_wrapped__", False) is False:  # pragma: no cover - guard
        _torch_manual_seed_with_snapshot.__codex_wrapped__ = True  # type: ignore[attr-defined]
        torch.manual_seed = _torch_manual_seed_with_snapshot  # type: ignore[assignment]


@runtime_checkable
class StateDictProvider(Protocol):
    def state_dict(self) -> Mapping[str, Any]:
        pass

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        pass


@dataclass
class ModuleStateDictProvider(StateDictProvider):
    module: Optional[Any]

    def state_dict(self) -> Mapping[str, Any]:
        if self.module is None:
            return {}
        state_fn = getattr(self.module, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.module is None:
            return None
        loader = getattr(self.module, "load_state_dict", None)
        if not callable(loader):
            return None
        try:
            return loader(state_dict, strict=strict)
        except TypeError as e:
            type(e).__name__
            logger.debug("TypeError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "TypeError: <ERROR_TYPE>", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            return loader(state_dict)


@dataclass
class OptimizerStateDictProvider(StateDictProvider):
    optimizer: Optional[Any]

    def state_dict(self) -> Mapping[str, Any]:
        if self.optimizer is None:
            return {}
        state_fn = getattr(self.optimizer, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.optimizer is None:
            return None
        loader = getattr(self.optimizer, "load_state_dict", None)
        if callable(loader):
            return loader(state_dict)
        return None


@dataclass
class SchedulerStateDictProvider(StateDictProvider):
    scheduler: Optional[Any]

    def state_dict(self) -> Mapping[str, Any]:
        if self.scheduler is None:
            return {}
        state_fn = getattr(self.scheduler, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.scheduler is None:
            return None
        loader = getattr(self.scheduler, "load_state_dict", None)
        if callable(loader):
            try:
                return loader(state_dict)
            except (ValueError, TypeError, RuntimeError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                return None
        return None


@dataclass
class GradScalerStateDictProvider(StateDictProvider):
    scaler: Optional[Any]

    def state_dict(self) -> Mapping[str, Any]:
        if self.scaler is None:
            return {}
        state_fn = getattr(self.scaler, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.scaler is None:
            return None
        loader = getattr(self.scaler, "load_state_dict", None)
        if callable(loader):
            return loader(state_dict)
        return None


StateMapping = Union[Mapping[str, Any], MutableMapping[str, Any]]


class CheckpointLoadError(RuntimeError):
    """Raised when checkpoint serialization or deserialization fails."""


SaveFormat = Literal["auto", "torch", "pickle"]


def _resolve_format(value: Optional[str]) -> SaveFormat:
    fmt = (value or "auto").lower()
    if fmt not in {"auto", "torch", "pickle"}:
        raise ValueError(f"unsupported checkpoint format: {value}")
    return fmt  # type: ignore[return-value]


def _pickle_dump(path: Path, payload: Mapping[str, Any]) -> None:
    """Dump checkpoint payload to pickle file.

    SECURITY CONTRACT:
    - This function is ONLY called from save_checkpoint() with trusted local state
    - The payload contains model weights/optimizer state created by the current process
    - Files are written to a local checkpoint directory controlled by the application
    - For production deployments, prefer torch.save or safetensors format
    - pickle is used here for compatibility with legacy checkpoints and fallback scenarios

    Trust Boundary: Local process-created state → Local filesystem
    Risk: LOW (trusted source, controlled destination)
    """
    try:
        safe_pickle_dump(dict(payload), str(path))
    except TypeError as e:
        if _matches_error_pattern(
            str(e), ["issubclass() arg 2 must be a class", "isinstance() arg 2 must be a type"]
        ):
            # Use protocol 2 for compatibility with older Python versions.
            safe_pickle_dump(dict(payload), str(path), protocol=2)
        else:
            raise


def _torch_dump(path: Path, payload: Mapping[str, Any]) -> None:
    if not TORCH_AVAILABLE:
        raise CheckpointLoadError("torch checkpoint format requested but torch is not available")
    save_kwargs: dict[str, Any] = {}
    try:
        signature = inspect.signature(torch.save)
    except (
        TypeError,
        ValueError,
    ):  # pragma: no cover - signature may fail on older torch
        signature = None
    if signature and "_use_new_zipfile_serialization" in signature.parameters:
        save_kwargs["_use_new_zipfile_serialization"] = True
    try:
        torch.save(dict(payload), path, **save_kwargs)
    except (TypeError, RuntimeError) as e:
        _msg = str(e)
        if _matches_error_pattern(
            _msg,
            ["issubclass() arg 2 must be a class", "isinstance() arg 2 must be a type", "profiler"],
        ):
            logger.warning(
                "torch.save compat error (PyTorch 2.x + Python 3.12), retrying without extra parameters: %s",  # noqa: E501
                e,
            )
            try:
                # Retry without pickle_protocol which is not a valid torch.save parameter
                # PyTorch 2.x handles pickle protocol automatically
                torch.save(dict(payload), path)
            except (IOError, OSError, ModuleNotFoundError, ImportError) as e2:
                logger.error(
                    "torch.save failed on retry: %s", e2
                )  # codeql[py/clear-text-logging-sensitive-data]
                raise
        else:
            raise


def _save_payload(path: Path, payload: Mapping[str, Any], *, fmt: SaveFormat) -> None:
    errors: list[BaseException] = []
    if fmt in {"auto", "torch"}:
        try:
            _torch_dump(path, payload)
            return
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - torch optional
            errors.append(exc)
            if fmt == "torch":
                raise CheckpointLoadError(f"failed to save torch checkpoint: {exc}") from exc
            fmt = "pickle"
    if fmt == "pickle" or (fmt == "auto" and not TORCH_AVAILABLE):
        try:
            _pickle_dump(path, payload)
            return
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            errors.append(exc)
            raise CheckpointLoadError(f"failed to save checkpoint via pickle: {exc}") from exc
    if errors:
        raise CheckpointLoadError(
            f"failed to save checkpoint; errors encountered: {[type(e).__name__ for e in errors]}"
        )


def _load_payload(path: Path, *, map_location: Optional[str], fmt: SaveFormat) -> Any:
    errors: list[BaseException] = []
    if fmt in {"auto", "torch"} and TORCH_AVAILABLE:
        try:
            kwargs: dict[str, Any] = {}
            if map_location is not None:
                kwargs["map_location"] = map_location
            if "weights_only" in inspect.signature(torch.load).parameters:
                kwargs["weights_only"] = False
            return torch.load(
                path, **kwargs
            )  # nosec B614 - weights_only=False required for optimizer/RNG state
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - torch optional
            errors.append(exc)
            if fmt == "torch":
                raise CheckpointLoadError(f"failed to load torch checkpoint: {exc}") from exc
    if fmt == "torch" and not TORCH_AVAILABLE:
        raise CheckpointLoadError("torch checkpoint format requested but torch is not available")
    try:
        return safe_pickle_load(str(path), use_restricted_unpickler=True)
    except (IOError, OSError, ModuleNotFoundError, ImportError, ValueError, TypeError, RuntimeError, pickle.UnpicklingError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        errors.append(exc)
        raise CheckpointLoadError(f"failed to load checkpoint via pickle: {exc}") from exc


def _standardize_state(state: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(state)
    if "model_state_dict" not in payload and "model" in payload:
        payload["model_state_dict"] = payload["model"]
    if "optimizer_state_dict" not in payload and "optimizer" in payload:
        payload["optimizer_state_dict"] = payload["optimizer"]
    if "scheduler_state_dict" not in payload and "scheduler" in payload:
        payload["scheduler_state_dict"] = payload["scheduler"]
    if payload.get("extra") is None:
        payload["extra"] = {}
    payload.setdefault("epoch", payload.get("step") or payload.get("epoch"))
    return payload


def _load_into_target(target: Any, state_dict: Mapping[str, Any], *, strict: bool = True) -> None:
    loader = getattr(target, "load_state_dict", None)
    if not callable(loader):
        return
    try:
        loader(state_dict, strict=strict)
    except TypeError as e:
        type(e).__name__
        logger.debug("TypeError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "TypeError: <ERROR_TYPE>", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        loader(state_dict)


def _snapshot_state(source: Any | StateMapping | None) -> Optional[dict[str, Any]]:
    if source is None:
        return None
    if isinstance(source, Mapping):
        return dict(source)
    if hasattr(source, "state_dict") and callable(source.state_dict):
        result = source.state_dict()
        if isinstance(result, Mapping):
            return dict(result)
        return dict(result.items()) if hasattr(result, "items") else dict(result)
    return None


def load_checkpoint(
    path: str | Path,
    map_location: Optional[str] = "cpu",
    *,
    format: Optional[str] = None,
    safe: bool = True,
) -> Any:
    """Load a checkpoint payload returning the raw serialized state.

    Args:
        path: Path to checkpoint file.
        map_location: Device mapping for torch tensors (default: "cpu").
        format: Serialization format hint ("torch", "pickle", or "auto").
        safe: When True (default), request ``weights_only=True`` from
            ``torch.load`` to prevent arbitrary code execution.  When the
            running torch version does not support ``weights_only``, raises
            :class:`RuntimeError`.  When False, loads with
            ``weights_only=False`` (legacy behaviour).
    """

    p = Path(path)
    fmt = _resolve_format(format)

    # honour the safe flag when torch is available
    if TORCH_AVAILABLE and fmt in {"auto", "torch"}:
        supports_wo = "weights_only" in inspect.signature(torch.load).parameters
        if safe and not supports_wo:
            raise RuntimeError(
                "load_checkpoint(safe=True) requires torch >= 1.13 which supports "
                "the 'weights_only' parameter; upgrade torch or pass safe=False."
            )
        if safe and supports_wo:
            try:
                kwargs: dict[str, Any] = {"weights_only": True}
                if map_location is not None:
                    kwargs["map_location"] = map_location
                return torch.load(p, **kwargs)  # nosec B614
            except (ValueError, TypeError) as exc:
                raise CheckpointLoadError(f"safe load failed for {p}: {exc}") from exc

    try:
        return _load_payload(p, map_location=map_location, fmt=fmt)
    except CheckpointLoadError as e:
        capture_error(
            step_no="load_checkpoint",
            step_desc="checkpoint load",
            msg=str(e),
            ctx=str(p),
        )
        logger.warning(
            f"CheckpointLoadError: {e}", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - fallback path
        capture_error(
            step_no="load_checkpoint",
            step_desc="checkpoint load unexpected",
            msg=str(exc),
            ctx=str(p),
        )
        raise CheckpointLoadError(f"failed to load checkpoint from {p}: {exc}") from exc


def _write_checksum_manifest(path: Path) -> None:
    """Write SHA256 checksum and size for path into checksums.json."""
    meta = {
        "schema_version": CHECKPOINT_METADATA_SCHEMA_VERSION,
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }
    (path.parent / "checksums.json").write_text(json.dumps(meta), encoding="utf-8")


def _verify_checksum_manifest(directory: Path) -> None:
    """Verify checksum manifest in directory if present."""
    manifest = directory / "checksums.json"
    if not manifest.exists():
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    target = directory / data.get("file", "")
    if not target.exists():
        raise RuntimeError("checkpoint file missing during checksum verify")
    sha = hashlib.sha256(target.read_bytes()).hexdigest()
    if sha != data.get("sha256") or target.stat().st_size != data.get("bytes"):
        raise RuntimeError("checkpoint checksum mismatch")


def _fallback_git_commit() -> Optional[str]:
    """Return current Git commit hash if available (fallback to subprocess)."""
    try:
        repo_root = Path(__file__).resolve().parents[3]
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
        ).strip()
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return None


def _safe_git_commit() -> Optional[str]:
    """Try provenance _git_commit then fallback to subprocess."""
    try:
        if callable(_prov_git_commit):
            return _prov_git_commit()
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.info(
            "checkpointing._safe_git_commit: provenance hook failed: %s",
            exc,
            exc_info=True,
        )
    return _fallback_git_commit()


def _safe_str_value(val: Any) -> Optional[str]:
    """Safely convert a value to a string, handling MagicMock and other non-serializable types.

    Args:
        val: Value to convert

    Returns:
        String representation or None if not safely convertible
    """
    if val is None:
        return None
    # Check if it's a MagicMock or similar test object
    if hasattr(val, "_mock_name") or type(val).__name__ == "MagicMock":
        return None
    # Try to convert to string
    try:
        # Verify it's JSON-serializable by trying to encode it
        json.dumps(str(val))
        return str(val)
    except (TypeError, ValueError):
        return None


def _minimal_env_summary() -> dict[str, Optional[str]]:
    """Collect minimal environment information (lightweight, no heavy deps)."""
    info: dict[str, Optional[str]] = {
        "python": sys.version,
        "platform": platform.platform(),
    }
    if TORCH_AVAILABLE:
        try:
            torch_version = getattr(torch, "__version__", None)
            info["torch"] = _safe_str_value(torch_version)

            cuda_version = None
            if hasattr(torch, "version") and hasattr(torch.cuda, "is_available"):
                try:
                    if torch.cuda.is_available():
                        cuda_version = torch.version.cuda
                except (ValueError, TypeError, RuntimeError):
                    logger.debug(
                        "Suppressed exception in handler", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
            info["cuda"] = _safe_str_value(cuda_version)
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            torch_version = getattr(torch, "__version__", None)
            info["torch"] = _safe_str_value(torch_version)
    if NUMPY_AVAILABLE:
        try:
            np_version = getattr(np, "__version__", None)
            info["numpy"] = _safe_str_value(np_version)
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            info["numpy"] = None
    gc = _safe_git_commit()
    if gc:
        info["git_commit"] = gc
    return info


def _compute_file_checksum(path: Path) -> Optional[str]:
    """Compute SHA-256 checksum of a file.

    Args:
        path: Path to file

    Returns:
        Hex digest of SHA-256 checksum, or None if file doesn't exist or error
    """
    try:
        if not path.exists():
            return None
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.debug(
            "Failed to compute checksum for %s: %s", path, exc
        )  # codeql[py/clear-text-logging-sensitive-data]
        return None


def _capture_dataset_checksums(
    dataset_paths: Optional[list[str | Path]] = None,
) -> dict[str, str]:
    """Capture checksums of dataset files for reproducibility.

    Args:
        dataset_paths: Optional list of dataset file paths

    Returns:
        Dictionary mapping dataset path to SHA-256 checksum
    """
    if not dataset_paths:
        return {}

    checksums: dict[str, str] = {}
    for path_str in dataset_paths:
        path = Path(path_str)
        checksum = _compute_file_checksum(path)
        if checksum:
            checksums[str(path)] = checksum

    return checksums


def _safe_environment_summary() -> dict[str, Any]:
    """Attempt to collect rich environment summary; fallback to minimal if needed."""
    try:
        if callable(_prov_env_summary):
            env = _prov_env_summary()
            if isinstance(env, dict):
                # Ensure git_commit present if known
                gc = env.get("git_commit") or _safe_git_commit()
                if gc:
                    env.setdefault("git_commit", gc)
                # Sanitize: keep only pickle-safe scalar types to prevent
                # MagicMock or other non-serializable objects from leaking in.
                safe_types = (str, int, float, bool, type(None))
                return {k: v for k, v in env.items() if isinstance(v, safe_types)}
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.info(
            "checkpointing._safe_environment_summary: provenance summary failed: %s",
            exc,
            exc_info=True,
        )
    # Fallback to minimal snapshot
    return _minimal_env_summary()


def save_checkpoint(
    path: str | Path,
    model: Optional[StateDictProvider],
    optimizer: Any | StateMapping | None,
    scheduler: Any | StateMapping | None,
    epoch: int,
    extra: Optional[Mapping[str, Any]] = None,
    *,
    format: Optional[str] = None,
    dataset_paths: Optional[list[str | Path]] = None,
) -> None:
    """Save a training checkpoint using ``torch`` when available, ``pickle`` otherwise.

    Args:
        path: Path to save checkpoint
        model: Model state dict provider
        optimizer: Optimizer state
        scheduler: Scheduler state
        epoch: Current epoch number
        extra: Extra metadata to include
        format: Checkpoint format ("auto", "torch", "pickle")
        dataset_paths: Optional list of dataset file paths for checksum tracking
    """

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    env = _safe_environment_summary()
    payload_extra = dict(extra or {})
    payload_extra.setdefault("system", env)
    if env.get("git_commit"):
        payload_extra.setdefault("git_commit", env["git_commit"])

    # Capture dataset checksums for reproducibility
    if dataset_paths:
        dataset_checksums = _capture_dataset_checksums(dataset_paths)
        if dataset_checksums:
            payload_extra.setdefault("dataset_checksums", dataset_checksums)

    state: dict[str, Any] = {
        "model_state_dict": _snapshot_state(model),
        "optimizer_state_dict": _snapshot_state(optimizer),
        "scheduler_state_dict": _snapshot_state(scheduler),
        "epoch": int(epoch),
        "extra": payload_extra,
    }
    if state["model_state_dict"] is not None:
        state["model"] = state["model_state_dict"]
    if state["optimizer_state_dict"] is not None:
        state["optimizer"] = state["optimizer_state_dict"]
    if state["scheduler_state_dict"] is not None:
        state["scheduler"] = state["scheduler_state_dict"]

    save_format = _resolve_format(format)
    try:
        _save_payload(p, state, fmt=save_format)
    except (ValueError, TypeError) as exc:  # pragma: no cover - save failures are rare
        capture_error(
            step_no="save_checkpoint",
            step_desc="checkpoint save",
            msg=str(exc),
            ctx=str(p),
        )
        raise CheckpointLoadError(f"failed to save checkpoint to {p}: {exc}") from exc

    _write_checksum_manifest(p)

    try:
        sidecar = {
            "epoch": epoch,
            "git_commit": env.get("git_commit"),
            "system": env,
        }
        # Include dataset checksums in sidecar if available
        if dataset_paths:
            dataset_checksums = _capture_dataset_checksums(dataset_paths)
            if dataset_checksums:
                sidecar["dataset_checksums"] = dataset_checksums

        p.with_suffix(".meta.json").write_text(
            json.dumps(sidecar, indent=2, sort_keys=True), encoding="utf-8"
        )
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - metadata best effort
        logger.info(
            "save_checkpoint: unable to write metadata sidecar for %s: %s",
            p,
            exc,
            exc_info=True,
        )

    try:
        h = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        maybe_emit_checkpoint_saved_event(
            str(p),
            sha256=h.hexdigest(),
            num_bytes=p.stat().st_size,
            extra={"epoch": epoch},
        )
    except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover - telemetry best effort
        logger.info(
            "save_checkpoint: telemetry emission skipped for %s due to %s",
            p,
            exc,
            exc_info=True,
        )


def load_training_checkpoint(
    path: str | Path,
    model: Optional[Any] = None,
    optimizer: Optional[Any] = None,
    scheduler: Optional[Any] = None,
    map_location: str = "cpu",
    *,
    strict: bool = True,
    format: Optional[str] = None,
) -> dict[str, Any]:
    """Load a training checkpoint and optionally restore state into live objects."""

    p = Path(path)
    if not p.exists():
        raise CheckpointLoadError(f"checkpoint does not exist: {p}")

    try:
        _verify_checksum_manifest(p.parent)
    except RuntimeError as exc:
        type(exc).__name__
        logger.debug("RuntimeError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        raise CheckpointLoadError(str(exc)) from exc
    except (ValueError, TypeError) as exc:  # pragma: no cover - checksum verify is best-effort
        logger.info(
            "load_training_checkpoint: checksum verification skipped for %s: %s",
            p,
            exc,
            exc_info=True,
        )

    try:
        raw = _load_payload(p, map_location=map_location, fmt=_resolve_format(format))
    except CheckpointLoadError as e:
        type(e).__name__
        logger.debug(
            "CheckpointLoadError: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "CheckpointLoadError: <ERROR_TYPE>", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - fallback path
        raise CheckpointLoadError(f"failed to load checkpoint from {p}: {exc}") from exc

    if not isinstance(raw, Mapping):
        raise CheckpointLoadError(
            f"checkpoint at {p} is not a mapping payload (found {type(raw).__name__})"
        )

    data = _standardize_state(raw)
    if data.get("model_state_dict") is not None:
        data.setdefault("model", data["model_state_dict"])
    if data.get("optimizer_state_dict") is not None:
        data.setdefault("optimizer", data["optimizer_state_dict"])
    if data.get("scheduler_state_dict") is not None:
        data.setdefault("scheduler", data["scheduler_state_dict"])

    if data.get("epoch") is not None:
        try:
            data["epoch"] = int(data["epoch"])
        except (
            TypeError,
            ValueError,
        ) as exc:  # pragma: no cover - fallback to raw value
            logger.info(
                "load_training_checkpoint: epoch value %r could not be coerced to int: %s",
                data.get("epoch"),
                exc,
            )

    if model is not None and data.get("model_state_dict") is not None:
        try:
            _load_into_target(model, data["model_state_dict"], strict=strict)
        except (ValueError, TypeError) as exc:  # pragma: no cover - strict mismatches
            raise CheckpointLoadError(f"failed to load model state: {exc}") from exc
    if optimizer is not None and data.get("optimizer_state_dict") is not None:
        try:
            _load_into_target(optimizer, data["optimizer_state_dict"], strict=True)
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as exc:  # pragma: no cover - optimizer mismatch
            raise CheckpointLoadError(f"failed to load optimizer state: {exc}") from exc
    if scheduler is not None and data.get("scheduler_state_dict") is not None:
        try:
            _load_into_target(scheduler, data["scheduler_state_dict"], strict=True)
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as exc:  # pragma: no cover - scheduler load is best effort
            logger.info(
                "load_training_checkpoint: scheduler state not restored: %s",
                exc,
                exc_info=True,
            )

    if not isinstance(data.get("extra"), dict):
        data["extra"] = dict(data.get("extra") or {})

    return data


def verify_ckpt_integrity(path: str) -> None:
    """Verify checkpoint integrity using checksums.json when present."""
    p = Path(path)
    meta_p = p.parent / "checksums.json"
    if not meta_p.exists():
        return
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta.get("file") != p.name:
        return
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if sha != meta.get("sha256"):
        raise RuntimeError(f"Checkpoint checksum mismatch for {p.name}")


def build_payload_bytes(
    model: Any,
    optimizer: Optional[Any] = None,
    scheduler: Optional[Any] = None,
    scaler: Optional[Any] = None,
    *,
    rng_state: bool = False,
) -> bytes:
    """Serialize training state to bytes for atomic checkpoint writes."""
    if not TORCH_AVAILABLE:  # pragma: no cover - torch optional
        raise RuntimeError("torch is required to build checkpoint payloads")
    state: dict[str, Any] = {
        "model": model.state_dict() if model is not None else None,
        "optimizer": optimizer.state_dict() if optimizer is not None else None,
        "scheduler": (
            scheduler.state_dict()
            if scheduler is not None and hasattr(scheduler, "state_dict")
            else None
        ),
    }
    if scaler is not None and hasattr(scaler, "state_dict"):
        state["scaler"] = scaler.state_dict()
    if rng_state:
        state["rng"] = _rng_dump()
    buf = io.BytesIO()
    try:
        torch.save(state, buf)
    except (TypeError, RuntimeError) as e:
        _msg = str(e)
        if _matches_error_pattern(
            _msg,
            [
                "issubclass() arg 2 must be a class",
                "isinstance() arg 2 must be a type",
                "FloatStorage",
            ],
        ):
            logger.warning(
                "torch.save compat error, retrying without extra parameters: %s", e
            )  # codeql[py/clear-text-logging-sensitive-data]
            buf = io.BytesIO()
            # PyTorch 2.x handles pickle protocol automatically; don't pass pickle_protocol
            torch.save(state, buf)
        else:
            raise
    return buf.getvalue()


def load_payload(
    path: str,
    model: Any,
    optimizer: Optional[Any] = None,
    scheduler: Optional[Any] = None,
    scaler: Optional[Any] = None,
) -> dict[str, Any]:
    """Load training state from path into provided objects."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("torch is required to load checkpoints")
    raw: dict[str, Any] = load_checkpoint(path, map_location="cpu")
    meta_block: dict[str, Any] = {}
    if isinstance(raw, dict) and "state" in raw:
        meta_candidate = raw.get("meta")
        if isinstance(meta_candidate, dict):
            meta_block = meta_candidate
        raw = raw.get("state") or {}
    state: dict[str, Any] = raw if isinstance(raw, dict) else {}
    if "rng" not in state and meta_block.get("rng"):
        state["rng"] = meta_block["rng"]
    if model is not None and state.get("model") is not None:
        model.load_state_dict(state["model"])
    if optimizer is not None and state.get("optimizer"):
        optimizer.load_state_dict(state["optimizer"])
    if scheduler is not None and state.get("scheduler"):
        with contextlib.suppress(Exception):
            scheduler.load_state_dict(state["scheduler"])
    if scaler is not None and state.get("scaler"):
        with contextlib.suppress(Exception):
            scaler.load_state_dict(state["scaler"])
    if state.get("rng"):
        _rng_load(state["rng"], prefer_resume=False)
    return state


def _write_json(path: Path, data: dict[str, Any]) -> None:
    class _SafeEncoder(json.JSONEncoder):
        """Fallback encoder: renders non-serializable objects as their repr string."""

        def default(self, o: Any) -> Any:
            try:
                return super().default(o)
            except TypeError:
                return repr(o)

    path.write_text(json.dumps(data, indent=2, sort_keys=True, cls=_SafeEncoder), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _python_state_payload(raw_state: Any) -> list[Any]:
    return [raw_state[0], list(raw_state[1]), raw_state[2]]


def _numpy_state_payload(raw_state: Any) -> list[Any]:
    return [
        raw_state[0],
        raw_state[1].tolist(),
        raw_state[2],
        raw_state[3],
        raw_state[4],
    ]


def _rng_dump() -> dict[str, Any]:
    py_state_current = random.getstate()
    state: dict[str, Any] = {
        "python": _python_state_payload(
            _seed_registry._LAST_SEEDED_PYTHON_STATE
            if _seed_registry._LAST_SEEDED_PYTHON_STATE is not None
            else py_state_current
        ),
        "python_resume": _python_state_payload(py_state_current),
    }

    if NUMPY_AVAILABLE:  # pragma: no branch
        np_state_current = np.random.get_state()
        state["numpy"] = _numpy_state_payload(
            _seed_registry._LAST_SEEDED_NUMPY_STATE
            if _seed_registry._LAST_SEEDED_NUMPY_STATE is not None
            else np_state_current
        )
        state["numpy_resume"] = _numpy_state_payload(np_state_current)

    if TORCH_AVAILABLE:

        def _capture_torch_state() -> dict[str, Any]:
            torch_state: dict[str, Any] = {}
            try:
                torch_random = getattr(torch, "random", None)
                if torch_random is not None and hasattr(torch_random, "get_rng_state"):
                    cpu_state = torch_random.get_rng_state()
                elif hasattr(torch, "get_rng_state"):
                    cpu_state = torch.get_rng_state()
                else:  # pragma: no cover - defensive fallback
                    cpu_state = None
                if cpu_state is not None:
                    torch_state["cpu"] = cpu_state.tolist()
            except Exception:  # pragma: no cover - optional torch stubs
                return {}
            try:
                if (
                    hasattr(torch, "cuda")
                    and hasattr(torch.cuda, "is_available")
                    and torch.cuda.is_available()
                    and hasattr(torch.cuda, "get_rng_state_all")
                ):
                    torch_state["cuda"] = [s.tolist() for s in torch.cuda.get_rng_state_all()]
            except (ValueError, TypeError, RuntimeError):  # pragma: no cover - cuda optional
                logger.debug(
                    "Suppressed exception in handler", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
            return torch_state

        torch_state_current = _capture_torch_state()
        if torch_state_current:
            seed_state = _seed_registry._LAST_SEEDED_TORCH_STATE
            seed_cuda = _seed_registry._LAST_SEEDED_TORCH_CUDA_STATE
            torch_seed_payload: dict[str, Any] = {}
            if isinstance(seed_state, list):
                torch_seed_payload["cpu"] = seed_state
            if isinstance(seed_cuda, list):
                torch_seed_payload["cuda"] = seed_cuda
            state["torch"] = torch_seed_payload if torch_seed_payload else torch_state_current
            state["torch_resume"] = torch_state_current
    return state


def _rng_load(state: dict[str, Any], *, prefer_resume: bool = True) -> None:
    def _python_payload() -> Optional[list[Any]]:
        if prefer_resume and "python_resume" in state:
            return state["python_resume"]
        return state.get("python")

    def _numpy_payload() -> Optional[list[Any]]:
        if prefer_resume and "numpy_resume" in state:
            return state["numpy_resume"]
        return state.get("numpy")

    def _torch_payload() -> Optional[dict[str, Any]]:
        if prefer_resume and "torch_resume" in state:
            return state["torch_resume"]
        if "torch" in state:
            return state["torch"]
        return None

    py_payload = _python_payload()
    if py_payload is not None:
        random.setstate((py_payload[0], tuple(py_payload[1]), py_payload[2]))

    if NUMPY_AVAILABLE:
        np_payload = _numpy_payload()
        if np_payload is not None:
            np.random.set_state(
                (
                    np_payload[0],
                    np.array(np_payload[1], dtype=np.uint32),
                    np_payload[2],
                    np_payload[3],
                    np_payload[4],
                )
            )

    if TORCH_AVAILABLE:
        torch_payload = _torch_payload()
        if torch_payload is not None:
            try:
                torch_random = getattr(torch, "random", None)
                setter = None
                if torch_random is not None and hasattr(torch_random, "set_rng_state"):
                    setter = torch_random.set_rng_state
                elif hasattr(torch, "set_rng_state"):
                    setter = torch.set_rng_state
                tensor_ctor = getattr(torch, "tensor", None)
                if setter is not None and tensor_ctor is not None and "cpu" in torch_payload:
                    setter(tensor_ctor(torch_payload["cpu"], dtype=torch.uint8))
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.warning(
                    "Exception: <ERROR_TYPE>", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
            try:
                if (
                    "cuda" in torch_payload
                    and hasattr(torch, "cuda")
                    and hasattr(torch.cuda, "is_available")
                    and torch.cuda.is_available()
                    and hasattr(torch.cuda, "set_rng_state_all")
                ):  # pragma: no cover
                    tensor_ctor = getattr(torch, "tensor", None)
                    if tensor_ctor is not None:
                        torch.cuda.set_rng_state_all(
                            [tensor_ctor(s, dtype=torch.uint8) for s in torch_payload["cuda"]]
                        )
            except (ValueError, TypeError, RuntimeError):  # pragma: no cover - cuda optional
                logger.debug(
                    "Suppressed exception in handler", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]


def dump_rng_state() -> dict[str, Any]:
    """Public wrapper around internal RNG snapshot."""
    return _rng_dump()


def load_rng_state(state: dict[str, Any], *, prefer_resume: bool = True) -> None:
    """Restore RNG state saved by dump_rng_state."""
    _rng_load(state, prefer_resume=prefer_resume)


def set_seed(
    seed: int,
    out_dir: Optional[Path | str] = None,
    *,
    deterministic: Optional[bool] = None,
) -> dict[str, int]:
    """Set RNG seeds across libraries and optionally persist seeds.json."""
    if deterministic is None:
        set_reproducible(seed)
    else:
        set_reproducible(seed, deterministic=deterministic)
    seeds: dict[str, int] = {"python": seed}
    if NUMPY_AVAILABLE:
        seeds["numpy"] = seed
    if TORCH_AVAILABLE:
        seeds["torch"] = seed
    if out_dir is not None:
        path = Path(out_dir) / "seeds.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(path, seeds)
    return seeds


def save_ckpt(state: dict[str, Any], path: str) -> None:
    """Legacy checkpoint saver for state dicts with checksum metadata."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("torch is required to save checkpoints")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        torch.save(state, p)
    except (TypeError, RuntimeError) as e:
        _msg = str(e)
        if _matches_error_pattern(
            _msg, ["issubclass() arg 2 must be a class", "isinstance() arg 2 must be a type"]
        ):
            logger.warning(
                "torch.save compat error, retrying without extra parameters: %s", e
            )  # codeql[py/clear-text-logging-sensitive-data]
            # PyTorch 2.x handles pickle protocol automatically; don't pass pickle_protocol
            torch.save(state, p)
        else:
            raise
    _write_checksum_manifest(p)


class CheckpointManager:
    """Manage training checkpoints with retention and resume support."""

    def __init__(
        self,
        root: Path,
        keep_last: int = 5,
        keep_best: int = 1,
        *,
        storage: Optional[StorageProvider] = None,
        remote_prefix: Optional[str] = None,
    ) -> None:
        self.root = Path(root)
        self.keep_last = int(keep_last)
        self.keep_best = int(keep_best)
        self.root.mkdir(parents=True, exist_ok=True)
        self.storage = storage
        self.remote_prefix = remote_prefix.strip("/") if remote_prefix else None

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    def save(
        self,
        epoch: int,
        model: Optional[Any] = None,
        optimizer: Optional[Any] = None,
        scheduler: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
        *,
        config: Optional[dict[str, Any]] = None,
        metrics: Optional[dict[str, Any]] = None,
    ) -> Path:
        ep_dir = self.root / f"epoch-{epoch}"
        ep_dir.mkdir(parents=True, exist_ok=True)

        env = _safe_environment_summary()
        _write_json(
            ep_dir / "meta.json",
            {
                "schema_version": CHECKPOINT_METADATA_SCHEMA_VERSION,
                "epoch": epoch,
                "metrics": metrics or {},
                "git_commit": env.get("git_commit"),
            },
        )
        _write_json(ep_dir / "rng.json", _rng_dump())
        _write_json(ep_dir / "system.json", env)
        if config is not None:
            try:  # prefer YAML
                import yaml

                (ep_dir / "config.yaml").write_text(yaml.dump(config), encoding="utf-8")
            except (IOError, OSError, ModuleNotFoundError, ImportError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                _write_json(ep_dir / "config.json", config)

        state: dict[str, Any] = {"model": None, "optimizer": None, "scheduler": None}
        if TORCH_AVAILABLE and model is not None:
            state["model"] = model.state_dict()
            if optimizer is not None:
                state["optimizer"] = optimizer.state_dict()
            if scheduler is not None and hasattr(scheduler, "state_dict"):
                state["scheduler"] = scheduler.state_dict()
            try:
                torch.save(state, ep_dir / "state.pt")
            except (TypeError, RuntimeError) as e:
                _msg = str(e)
                if _matches_error_pattern(
                    _msg,
                    ["issubclass() arg 2 must be a class", "isinstance() arg 2 must be a type"],
                ):
                    logger.warning(
                        "torch.save compat error, retrying without extra parameters: %s",
                        e,
                    )
                    # PyTorch 2.x handles pickle protocol automatically; don't pass pickle_protocol
                    torch.save(state, ep_dir / "state.pt")
                else:
                    raise
        else:  # pragma: no cover - fallback path
            state = {
                "model": getattr(model, "__dict__", None),
                "optimizer": getattr(optimizer, "state_dict", lambda: None)(),
                "scheduler": getattr(scheduler, "state_dict", lambda: None)(),
            }
            from codex_ml.utils.safe_pickle import safe_pickle_dump

            safe_pickle_dump(state, str(ep_dir / "state.pkl"))

        if tokenizer is not None:  # pragma: no cover
            with contextlib.suppress(Exception):
                if hasattr(tokenizer, "save_pretrained"):
                    tokenizer.save_pretrained(str(ep_dir / "tokenizer"))
                else:
                    from codex_ml.utils.safe_pickle import safe_pickle_dump

                    safe_pickle_dump(tokenizer, str(ep_dir / "tokenizer.pkl"))

        state_file = ep_dir / ("state.pt" if (ep_dir / "state.pt").exists() else "state.pkl")
        _write_checksum_manifest(state_file)

        # last marker
        (self.root / "last").write_text(str(ep_dir), encoding="utf-8")

        # best tracking
        if metrics:
            best_file = self.root / "best.json"
            best: list[dict[str, Any]] = []
            if best_file.exists():
                best = _read_json(best_file).get("items", [])
            entry = {"epoch": epoch, "metrics": metrics or {}, "path": str(ep_dir)}
            best.append(entry)

            def keyfn(x: dict[str, Any]) -> tuple:
                m = x.get("metrics", {})
                if "val_loss" in m:
                    return (0, m["val_loss"])  # lower is better
                if "score" in m:
                    return (1, -m["score"])  # higher is better
                return (2, -x["epoch"])  # fallback to latest

            best.sort(key=keyfn)
            _write_json(
                best_file,
                {
                    "schema_version": CHECKPOINT_METADATA_SCHEMA_VERSION,
                    "items": best[: max(1, self.keep_best)],
                },
            )

        self.apply_retention()

        if self.storage is not None and self.remote_prefix is not None:
            remote_path = (
                f"{self.remote_prefix}/{ep_dir.name}" if self.remote_prefix else ep_dir.name
            )
            with contextlib.suppress(Exception):  # pragma: no cover - remote sync best effort
                self.storage.upload_directory(ep_dir, remote_path)
        return ep_dir

    def save_now(
        self,
        step: int,
        payload: Any,
        metrics: Optional[dict[str, Any]] = None,
        prefix: str = "ckpt",
        *,
        rng_state: bool = False,
    ) -> Path:
        """Save an arbitrary payload immediately with retention semantics."""

        metrics = metrics or {}
        metric_key = next(iter(metrics)) if metrics else "val_loss"
        checkpoint_dir = self.root / f"epoch-{step:04d}"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Decode serialized payloads to preserve RNG state fields where possible.
        state_payload: Any = payload
        if isinstance(payload, (bytes, bytearray)):
            try:
                state_payload = torch.load(
                    io.BytesIO(payload), map_location="cpu", weights_only=False
                )  # nosec B614 - RNG state may contain complex objects
            except (IOError, OSError, ModuleNotFoundError, ImportError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                state_payload = {"payload": payload}

        if checkpoint_core is not None:
            ckpt_path, _ = checkpoint_core.save_checkpoint(
                checkpoint_dir,
                state=state_payload if isinstance(state_payload, dict) else None,
                payload=state_payload if isinstance(state_payload, dict) else None,
                metadata={"epoch": step, "metrics": metrics},
                metric_value=None,
                metric_key=metric_key,
                best_metric=metric_key,
                mode="min",
                top_k=self.keep_best or 1,
                best_k=self.keep_best or 1,
                include_rng=rng_state,
                keep_last=self.keep_last,
                prefix=prefix,
            )
        else:
            # Fallback: save using basic serialization
            ckpt_path = checkpoint_dir / "state.pkl"
            from codex_ml.utils.safe_pickle import safe_pickle_dump

            safe_pickle_dump(state_payload, str(ckpt_path))
        meta_sidecar = {
            "step": int(step),
            "metrics": metrics,
        }
        if rng_state:
            if isinstance(state_payload, dict) and "rng" in state_payload:
                meta_sidecar["rng"] = state_payload.get("rng")
            else:
                try:
                    meta_sidecar["rng"] = _rng_dump()
                except (IOError, OSError, ModuleNotFoundError, ImportError):
                    logger.warning(
                        "Exception occurred", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    meta_sidecar["rng"] = {}
        try:
            ckpt_path.with_suffix(".meta.json").write_text(
                json.dumps(meta_sidecar, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            logger.warning(
                "Exception: <ERROR_TYPE>", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
        return ckpt_path

    # ------------------------------------------------------------------
    # Resume
    # ------------------------------------------------------------------
    def resume_from(
        self,
        path: Path,
        model: Optional[Any] = None,
        optimizer: Optional[Any] = None,
        scheduler: Optional[Any] = None,
    ) -> dict[str, Any]:
        path = Path(path)
        if not path.exists():  # pragma: no cover
            raise FileNotFoundError(f"resume path not found: {path}")

        _verify_checksum_manifest(path)
        state = None
        if (path / "state.pt").exists() and TORCH_AVAILABLE:
            state = load_checkpoint(path / "state.pt", map_location="cpu")
            if model is not None and state.get("model") is not None:
                self._verify_state_dict(model.state_dict(), state["model"])
                model.load_state_dict(state["model"])
            if optimizer is not None and state.get("optimizer") is not None:
                try:
                    optimizer.load_state_dict(state["optimizer"])
                except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover
                    raise ValueError(f"optimizer state load failed: {exc}") from exc
            if scheduler is not None and state.get("scheduler") is not None:
                with contextlib.suppress(Exception):
                    scheduler.load_state_dict(state["scheduler"])
        elif (path / "state.pkl").exists():  # pragma: no cover
            # Use safe pickle loading to prevent code execution vulnerabilities
            from codex_ml.utils.safe_pickle import safe_pickle_load

            state = safe_pickle_load(str(path / "state.pkl"), use_restricted_unpickler=True)
            if (
                model is not None
                and hasattr(model, "load_state_dict")
                and state.get("model") is not None
            ):
                with contextlib.suppress(Exception):
                    model.load_state_dict(state["model"])
        else:  # pragma: no cover
            raise RuntimeError(f"no compatible state file found under: {path}")

        rng_path = path / "rng.json"
        if rng_path.exists():
            try:
                rng_state = _read_json(rng_path)
                _rng_load(rng_state)
            except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover
                raise RuntimeError(f"failed to restore RNG state: {exc}") from exc

        meta = _read_json(path / "meta.json") if (path / "meta.json").exists() else {}
        return {"meta": meta, "state": bool(state)}

    def load_latest(
        self,
        model: Optional[Any] = None,
        optimizer: Optional[Any] = None,
        scheduler: Optional[Any] = None,
        *,
        search_path: Optional[Path] = None,
        strict: bool = True,
    ) -> dict[str, Any]:
        """Resume from the most recent checkpoint available.

        Parameters
        ----------
        model, optimizer, scheduler:
            Optional PyTorch objects that will receive the restored
            state_dicts when provided.
        search_path:
            Optional directory to search instead of :attr:`root`. When the
            directory already points to a concrete checkpoint (i.e. contains
            ``state.pt``/``state.pkl``) it is used directly.
        strict:
            When ``True`` (default) a :class:`FileNotFoundError` is raised if
            no checkpoints are discovered.  When ``False`` an empty payload is
            returned instead.

        Returns
        -------
        dict[str, Any]
            The metadata returned from :meth:`resume_from` with the resolved
            checkpoint ``path`` included.
        """

        def _has_state(directory: Path) -> bool:
            return (directory / "state.pt").exists() or (directory / "state.pkl").exists()

        root = Path(search_path) if search_path is not None else self.root
        if root.is_file():
            root = root.parent

        candidates: list[Path] = []
        seen: set[str] = set()

        def _register(candidate: Optional[Path]) -> None:
            if candidate is None:
                return
            try:
                resolved = str(candidate.resolve())
            except (IOError, OSError, ModuleNotFoundError, ImportError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                resolved = str(candidate)
            if resolved in seen:
                return
            if not candidate.exists():
                return
            seen.add(resolved)
            candidates.append(candidate)

        if root.is_dir() and _has_state(root):
            _register(root)

        marker = root / "last"
        if marker.exists():
            marker_path: Optional[Path] = None
            if marker.is_symlink():
                with contextlib.suppress(Exception):
                    marker_path = marker.resolve(strict=False)
            else:
                try:
                    marker_value = marker.read_text(encoding="utf-8").strip()
                except IsADirectoryError as e:
                    type(e).__name__
                    logger.debug(
                        "IsADirectoryError: <ERROR_TYPE>"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    logger.warning(
                        "IsADirectoryError: <ERROR_TYPE>", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    with contextlib.suppress(Exception):
                        marker_path = marker.resolve(strict=False)
                except (IOError, OSError, ModuleNotFoundError, ImportError):
                    logger.warning(
                        "Exception occurred", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    marker_path = None
                else:
                    if marker_value:
                        candidate = Path(marker_value)
                        if not candidate.is_absolute():
                            try:
                                candidate = (root / candidate).resolve(strict=False)
                            except (IOError, OSError, ModuleNotFoundError, ImportError):
                                logger.warning(
                                    "Exception occurred", exc_info=True
                                )  # codeql[py/clear-text-logging-sensitive-data]
                                candidate = root / candidate
                        marker_path = candidate
            if marker_path is not None:
                _register(marker_path)

        for candidate in sorted(
            [p for p in root.glob("epoch-*") if p.is_dir()],
            key=lambda p: int(p.name.split("-")[-1]),
            reverse=True,
        ):
            _register(candidate)

        if not candidates and self.storage is not None and self.remote_prefix is not None:
            candidates.extend(self._sync_remote_candidates())

        if not candidates:
            if strict:
                raise FileNotFoundError(f"no checkpoints found under: {root}")
            return {"meta": {}, "state": False, "path": None}

        for candidate in candidates:
            if _has_state(candidate):
                info = self.resume_from(
                    candidate,
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                )
                info["path"] = candidate
                return info
        raise FileNotFoundError(f"no loadable checkpoint state found under: {root}")

    def _sync_remote_candidates(self) -> list[Path]:
        """Download remote checkpoints to local root and return discovered paths."""
        if self.storage is None or self.remote_prefix is None:
            return []

        discovered: list[Path] = []
        for remote in self.storage.iter_checkpoints(self.remote_prefix):
            name = Path(remote).name
            target = self.root / name
            if target.exists():
                discovered.append(target)
                continue
            try:
                self.storage.download_directory(remote, target)
            except FileNotFoundError as e:
                type(e).__name__
                logger.debug(
                    "FileNotFoundError: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.warning(
                    "FileNotFoundError: <ERROR_TYPE>", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                continue
            discovered.append(target)
        discovered.sort(
            key=lambda path: int(path.name.split("-")[-1]) if "-" in path.name else -1,
            reverse=True,
        )
        return discovered

    # ------------------------------------------------------------------
    # Retention
    # ------------------------------------------------------------------
    def apply_retention(self) -> None:
        entries = [p for p in self.root.glob("epoch-*") if p.is_dir()]
        entries.sort(key=lambda p: int(p.name.split("-")[-1]), reverse=True)
        keep = {e.name for e in entries[: max(1, self.keep_last)]}
        best_file = self.root / "best.json"
        if best_file.exists():
            for item in _read_json(best_file).get("items", []):
                keep.add(Path(item["path"]).name)
        for e in entries:
            if e.name not in keep:
                with contextlib.suppress(Exception):
                    shutil.rmtree(e)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    def _verify_state_dict(
        self, model_sd: dict[str, Any], loaded_sd: dict[str, Any]
    ) -> None:  # pragma: no cover
        missing, unexpected, mismatched = [], [], []
        for k, v in model_sd.items():
            if k not in loaded_sd:
                missing.append(k)
            else:
                lv = loaded_sd[k]
                if (
                    hasattr(v, "shape")
                    and hasattr(lv, "shape")
                    and tuple(v.shape) != tuple(lv.shape)
                ):
                    mismatched.append((k, tuple(v.shape), tuple(lv.shape)))
        for k in loaded_sd:
            if k not in model_sd:
                unexpected.append(k)
        if missing or unexpected or mismatched:
            msgs = []
            if missing:
                msgs.append(f"missing: {missing[:10]}{' ...' if len(missing) > 10 else ''}")
            if unexpected:
                msgs.append(
                    f"unexpected: {unexpected[:10]}{' ...' if len(unexpected) > 10 else ''}"
                )
            if mismatched:
                sample = [(k, exp, lv) for (k, exp, lv) in mismatched[:5]]
                msgs.append(f"mismatched: {sample}{' ...' if len(mismatched) > 5 else ''}")
            raise ValueError("state_dict verification failed: " + "; ".join(msgs))


__all__ = [
    "CheckpointLoadError",
    "CheckpointManager",
    "GradScalerStateDictProvider",
    "ModuleStateDictProvider",
    "OptimizerStateDictProvider",
    "SchedulerStateDictProvider",
    "build_payload_bytes",
    "dump_rng_state",
    "load_checkpoint",
    "load_payload",
    "load_rng_state",
    "load_training_checkpoint",
    "save_checkpoint",
    "save_ckpt",
    "set_seed",
    "verify_ckpt_integrity",
]
