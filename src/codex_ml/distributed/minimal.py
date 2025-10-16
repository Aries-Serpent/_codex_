from __future__ import annotations

import os

try:  # pragma: no cover - torch is optional
    import torch  # type: ignore
    import torch.distributed as dist  # type: ignore
except Exception:  # pragma: no cover - execution environments without torch
    torch = None  # type: ignore[assignment]
    dist = None  # type: ignore[assignment]


def _dist_available() -> bool:
    return bool(dist is not None and getattr(dist, "is_available", lambda: False)())


def is_distributed_available() -> bool:
    """Return True when torch.distributed APIs are importable and available."""
    return _dist_available()


def init_distributed_if_needed(backend: str = "nccl", env_flag: str = "CODEX_DDP") -> bool:
    """Best-effort initialization gated by an environment flag.

    Returns True if the process group is initialized after the call, False otherwise.
    """
    if not _dist_available() or os.environ.get(env_flag, "0") not in {"1", "true", "TRUE"}:
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
    try:
        dist.init_process_group(backend=chosen_backend)
        return True
    except Exception:
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
