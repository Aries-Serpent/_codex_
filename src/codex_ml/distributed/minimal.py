from __future__ import annotations

import os
import warnings
from typing import Iterable

try:  # pragma: no cover - torch is optional
    import torch  # type: ignore
    import torch.distributed as dist  # type: ignore
except Exception:  # pragma: no cover - execution environments without torch
    torch = None  # type: ignore[assignment]
    dist = None  # type: ignore[assignment]

_OPT_IN_VALUES = {"1", "true", "TRUE", "True", "YES", "yes", "on", "ON"}
_FALLBACK_ENV_FLAGS = ("CODEX_DDP_ENABLE",)


def _iter_candidate_flags(primary: str) -> Iterable[str]:
    yield primary
    for alias in _FALLBACK_ENV_FLAGS:
        if alias != primary:
            yield alias


def _env_opted_in(env_flag: str) -> tuple[bool, str | None]:
    for name in _iter_candidate_flags(env_flag):
        value = os.environ.get(name)
        if value is None:
            continue
        return value in _OPT_IN_VALUES, name
    return False, None


def _parse_env_int(name: str) -> int | None:
    value = os.environ.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        warnings.warn(
            f"Ignoring {name}={value!r}; expected integer for distributed setup.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None


def _warn_missing_dist(flag_name: str) -> None:
    warnings.warn(
        (
            "Distributed execution requested via "
            f"{flag_name}, but torch.distributed is unavailable. "
            "Continuing with single-process semantics."
        ),
        RuntimeWarning,
        stacklevel=2,
    )


def _warn_failed_init(backend: str, flag_name: str, error: Exception) -> None:
    warnings.warn(
        (
            f"Failed to initialize distributed backend '{backend}' after "
            f"{flag_name} opt-in; falling back to single-process. "
            f"Error: {error}"
        ),
        RuntimeWarning,
        stacklevel=2,
    )


def _warn_device_set_failed(local_rank: int, error: Exception) -> None:
    warnings.warn(
        (
            f"Unable to set CUDA device for LOCAL_RANK={local_rank}: {error}. "
            "Continuing without device pinning."
        ),
        RuntimeWarning,
        stacklevel=2,
    )


def _dist_available() -> bool:
    return bool(dist is not None and getattr(dist, "is_available", lambda: False)())


def is_distributed_available() -> bool:
    """Return True when torch.distributed APIs are importable and available."""
    return _dist_available()


def init_distributed_if_needed(backend: str = "nccl", env_flag: str = "CODEX_DDP") -> bool:
    """Best-effort initialization gated by an environment flag.

    Returns True if the process group is initialized after the call, False otherwise.
    """
    opted_in, flag_used = _env_opted_in(env_flag)
    if not opted_in:
        return False

    if not _dist_available():
        _warn_missing_dist(flag_used or env_flag)
        return False
    if dist is None:  # pragma: no cover - defensive
        return False
    if dist.is_initialized():
        return True

    chosen_backend = backend
    if backend == "nccl":
        cuda_available = bool(torch and getattr(torch.cuda, "is_available", lambda: False)())
        if not cuda_available:
            chosen_backend = "gloo"
    init_kwargs: dict[str, int] = {}
    world_size = _parse_env_int("WORLD_SIZE")
    rank = _parse_env_int("RANK")
    local_rank = _parse_env_int("LOCAL_RANK")
    if torch is not None and local_rank is not None:
        cuda = getattr(torch, "cuda", None)
        if cuda is not None and getattr(cuda, "is_available", lambda: False)():
            try:
                cuda.set_device(local_rank)
            except Exception as exc:  # pragma: no cover - depends on runtime devices
                _warn_device_set_failed(local_rank, exc)
    if rank is None and local_rank is not None:
        rank = local_rank
    if world_size is not None:
        init_kwargs["world_size"] = world_size
    if rank is not None:
        init_kwargs["rank"] = rank
    try:
        dist.init_process_group(backend=chosen_backend, **init_kwargs)
        return True
    except Exception as exc:
        _warn_failed_init(chosen_backend, flag_used or env_flag, exc)
        return False


def get_rank() -> int:
    if dist is None or not getattr(dist, "is_initialized", lambda: False)():
        return 0
    return int(dist.get_rank())  # type: ignore[call-arg]


def get_world_size() -> int:
    if dist is None or not getattr(dist, "is_initialized", lambda: False)():
        return 1
    return int(dist.get_world_size())  # type: ignore[call-arg]


def barrier() -> None:
    if dist is not None and getattr(dist, "is_initialized", lambda: False)():
        dist.barrier()


def cleanup() -> None:
    if dist is not None and getattr(dist, "is_initialized", lambda: False)():
        dist.destroy_process_group()
