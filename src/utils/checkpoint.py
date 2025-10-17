"""
Legacy checkpoint helpers (compat shim).

This module remains for backward-compatibility only. Prefer:
  - codex_ml.utils.checkpoint_core
  - codex_ml.utils.checkpointing (CheckpointManager)
"""

from __future__ import annotations

import inspect
import os
import random as _random
import tempfile
import warnings as _warnings
from contextlib import suppress
from pathlib import Path
from typing import Any, Mapping

_warnings.warn(
    "src.utils.checkpoint is legacy; use codex_ml.utils.checkpointing or "
    "codex_ml.utils.checkpoint_core for new code.",
    DeprecationWarning,
    stacklevel=2,
)

# If a local legacy implementation exists in the repository, import it.
# Otherwise provide minimal stubs or re-export from canonical APIs.
try:  # pragma: no cover - legacy path
    from training.checkpoint_manager import CheckpointManager  # type: ignore # noqa: F401
except Exception:  # pragma: no cover - fallback to canonical
    from codex_ml.utils.checkpointing import CheckpointManager  # type: ignore # noqa: F401

try:  # pragma: no cover - optional numpy
    import numpy as _np
except Exception:  # pragma: no cover - numpy optional
    _np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional torch
    import torch as _torch
except Exception:  # pragma: no cover - torch optional
    _torch = None  # type: ignore[assignment]

try:  # pragma: no cover - prefer canonical RNG helpers
    from codex_ml.utils.checkpoint_core import (
        capture_rng_state as _capture_rng_state,  # type: ignore
    )
    from codex_ml.utils.checkpoint_core import restore_rng_state as _restore_rng_state
except Exception:  # pragma: no cover - canonical helpers unavailable
    _capture_rng_state = None  # type: ignore[assignment]
    _restore_rng_state = None  # type: ignore[assignment]


def _ensure_torch_available() -> None:
    if _torch is None:  # pragma: no cover - defensive
        raise RuntimeError("torch is required to use src.utils.checkpoint")


def _torch_supports_weights_only() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


_TORCH_SUPPORTS_WEIGHTS_ONLY = _torch_supports_weights_only()


def _torch_rng_get_state() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def _torch_rng_set_state(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def _legacy_capture_rng_state() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def _legacy_restore_rng_state(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError:
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def _capture_rng() -> dict[str, Any]:
    if _capture_rng_state is not None:
        return _capture_rng_state()
    return _legacy_capture_rng_state()


def _restore_rng(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception:  # pragma: no cover - fall back to legacy behaviour
            pass
    _legacy_restore_rng_state(state)


def _torch_load(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        kwargs["weights_only"] = False
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def save_checkpoint(state: dict[str, Any], path: str, archive_latest: bool = True) -> None:
    """Atomically persist ``state`` to ``path`` while capturing RNG metadata."""

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    _ensure_torch_available()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    parent_str = str(target.parent)
    dir_arg = parent_str if parent_str not in {"", "."} else None
    fd, tmp_path = tempfile.mkstemp(dir=dir_arg)
    os.close(fd)
    rng_state = _capture_rng()
    payload = dict(state)
    payload["_rng"] = rng_state
    try:
        _torch.save(payload, tmp_path)
    except Exception:
        with suppress(FileNotFoundError):
            os.unlink(tmp_path)
        raise
    os.replace(tmp_path, target)
    if archive_latest and target.is_symlink():
        with suppress(OSError):
            target.unlink()


def load_checkpoint(path: str, device: str = "cpu") -> dict[str, Any]:
    """Load a checkpoint created by :func:`save_checkpoint`."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    _ensure_torch_available()
    state = _torch_load(path, map_location=device)
    rng_state = state.pop("_rng", None)
    if isinstance(rng_state, Mapping):
        _restore_rng(rng_state)
    return state


__all__ = ["CheckpointManager", "save_checkpoint", "load_checkpoint"]
