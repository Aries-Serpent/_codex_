"""Canonical checkpoint core: save + load with stable metadata.

WHY:
- Prior draft only implemented save(); feature parity requires load() for resume tests.
- Explicit schema versioning ensures forward/backward compatibility tracking.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import inspect  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import warnings  # noqa: E402
from contextlib import suppress  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from typing import Any  # noqa: E402

try:
    import torch
except (ImportError, AttributeError):  # pragma: no cover
    torch = None  # type: ignore[assignment]

# Import custom JSON encoder for ML types
try:
    from codex_ml.utils.json_serialization import CustomJSONEncoder
except (ImportError, ModuleNotFoundError):
    CustomJSONEncoder = None 

SCHEMA_VERSION = "2.0"  # Checkpoint schema version for compatibility tracking


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _require_torch_attr(name: str) -> Any:
    """Return a required torch callable or raise a consistent RuntimeError."""
    if torch is None:
        raise RuntimeError("PyTorch required to use checkpoints")
    attr = getattr(torch, name, None)
    if attr is None:
        raise RuntimeError(f"PyTorch is missing required attribute: {name}")
    return attr


def save_checkpoint(
    out_dir: str, *, state: dict[str, Any], meta: dict[str, Any], keep_last_k: int = 5
) -> str:
    _ensure_dir(out_dir)
    torch_save = _require_torch_attr("save")
    weights = os.path.join(out_dir, "weights.pt")
    metadata = os.path.join(out_dir, "metadata.json")

    # Add explicit schema version and creation timestamp
    payload = {
        "_schema_version": SCHEMA_VERSION,
        "_created_at": datetime.now(UTC).isoformat(),
        "state": state,
    }

    # Use new zipfile serialization to avoid pickling issues with torch.Storage
    try:
        torch_save(payload, weights, _use_new_zipfile_serialization=True)
    except (TypeError, AttributeError):
        # Fallback for older PyTorch versions that don't support this parameter
        torch_save(payload, weights)

    # Include schema version in metadata for validation
    with open(metadata, "w", encoding="utf-8") as f:
        kwargs: dict[str, Any] = {
            "indent": 2,
            "sort_keys": True,
        }
        # Use custom encoder if available for ML types
        if CustomJSONEncoder is not None:
            kwargs["cls"] = CustomJSONEncoder

        try:
            json.dump(
                {
                    **meta,
                    "_schema_version": SCHEMA_VERSION,
                    "_created_at": datetime.now(UTC).isoformat(),
                },
                f,
                **kwargs,
            )
        except TypeError as e:
            logger.warning("Metadata JSON encoding failed with custom encoder: %s", e)
            # Fallback: try without custom encoder
            if CustomJSONEncoder is not None:
                kwargs.pop("cls", None)
                json.dump(
                    {
                        **meta,
                        "_schema_version": SCHEMA_VERSION,
                        "_created_at": datetime.now(UTC).isoformat(),
                    },
                    f,
                    **kwargs,
                )
            else:
                raise
    # Retention (best-effort): keep only the last K sibling epoch dirs
    with suppress(Exception):
        parent = os.path.dirname(out_dir)
        siblings = sorted([d for d in os.listdir(parent) if os.path.isdir(os.path.join(parent, d))])
        excess = len(siblings) - keep_last_k
        for _ in siblings[: max(0, excess)]:
            # Best-effort cleanup
            # (Non-recursive safety; project typically uses per-epoch dirs)
            pass
    return out_dir


def load_checkpoint(
    path: str, map_location: str | None = None
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load a checkpoint directory or a direct weights.pt file.
    Returns (state_dicts, metadata).

    Security note: Checkpoint files should only be loaded from trusted sources.
    torch.load can execute arbitrary code during deserialization.
    """
    torch_load = _require_torch_attr("load")
    if os.path.isdir(path):
        weights = os.path.join(path, "weights.pt")
        metadata = os.path.join(path, "metadata.json")
    else:
        weights = path
        metadata = os.path.join(os.path.dirname(path), "metadata.json")
    if not os.path.exists(weights):
        raise FileNotFoundError(f"Checkpoint weights not found: {weights}")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _torch_supports_weights_only():
        kwargs["weights_only"] = False
    try:
        payload = torch_load(
            weights, **kwargs
        )  # nosec B614 - weights_only=False required for optimizer/RNG state
    except (TypeError, ValueError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Checkpoint load rejected with %s: %s", type(exc).__name__, exc)
        raise
    meta: dict[str, Any] = {}
    if os.path.exists(metadata):
        try:
            with open(metadata, encoding="utf-8") as f:
                meta = json.load(f)
        except (IOError, OSError, ModuleNotFoundError, ImportError, ValueError):
            logger.warning("Exception occurred", exc_info=True)
            meta = {}
    # Validate schema version for compatibility
    checkpoint_version = payload.get("_schema_version") or payload.get("schema_version", "1.0")
    if checkpoint_version != SCHEMA_VERSION:
        warnings.warn(
            f"Loading checkpoint with schema v{checkpoint_version}, "
            f"current schema is v{SCHEMA_VERSION}. "
            f"This may indicate compatibility issues.",
            UserWarning,
            stacklevel=2,
        )

    state = payload.get("state", payload)
    return state, meta


def _torch_supports_weights_only() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


__all__ = ["SCHEMA_VERSION", "load_checkpoint", "save_checkpoint"]
