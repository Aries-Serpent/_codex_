from __future__ import annotations

import inspect
import os
import random
import tempfile
from contextlib import suppress
from typing import Any

try:  # pragma: no cover - optional dependency
    import numpy as _np
except Exception:  # pragma: no cover - handle missing dependency
    _np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import torch as _torch
except Exception:  # pragma: no cover - handle missing dependency
    _torch = None  # type: ignore[assignment]


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


def _rng_state() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    torch_state = _torch_rng_get_state()
    state: dict[str, Any] = {
        "torch": torch_state.tolist(),
        "python": random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def save_checkpoint(state: dict[str, Any], path: str, archive_latest: bool = True) -> None:
    """Atomically persist a checkpoint along with RNG metadata."""

    if _torch is None:
        raise RuntimeError("torch is required to save checkpoints")

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path) or None)
    os.close(fd)
    augmented = dict(state)
    augmented["_rng"] = _rng_state()
    _torch.save(augmented, tmp_path)
    os.replace(tmp_path, path)
    if archive_latest and os.path.islink(path):
        os.unlink(path)


def load_checkpoint(path: str, device: str = "cpu") -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    state = _torch_load(path, map_location=device)
    rng = state.pop("_rng", None)
    if rng:
        cpu_state = None
        with suppress(Exception):
            cpu_state = _torch.tensor(rng["torch"], dtype=_torch.uint8)
        if cpu_state is not None:
            _torch_rng_set_state(cpu_state)
        if _np is not None:
            with suppress(Exception):
                _np.random.set_state(rng["numpy"])
        with suppress(Exception):
            random.setstate(rng["python"])
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            rng.get("cuda")
            and cuda_mod is not None
            and hasattr(cuda_mod, "is_available")
            and cuda_mod.is_available()
        ):
            # Best-effort restoration for CUDA RNGs. Device mapping is context dependent.
            for idx, tensor_state in enumerate(rng["cuda"]):
                with suppress(Exception):
                    cuda_mod.set_rng_state(
                        _torch.tensor(tensor_state, dtype=_torch.uint8), device=idx
                    )
    return state
