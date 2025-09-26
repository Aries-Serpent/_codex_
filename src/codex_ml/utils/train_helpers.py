"""Lightweight training utilities (AMP autocast & gradient clipping)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable, Iterator, Optional


@contextmanager
def maybe_autocast(enabled: bool, *, dtype: Optional[object] = None) -> Iterator[None]:
    """Enter a torch autocast context when available and enabled.

    The helper gracefully degrades to a no-op when PyTorch or CUDA AMP is not
    available, keeping training code paths import-safe in minimal environments.
    """

    if not enabled:
        yield
        return

    try:  # pragma: no cover - optional dependency
        import torch

        autocast_cls = torch.cuda.amp.autocast  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - dependency missing or AMP unavailable
        yield
        return

    target_dtype = None
    if dtype is not None:
        if isinstance(dtype, str):
            lower = dtype.lower()
            mapping = {
                "float16": getattr(torch, "float16", None),
                "fp16": getattr(torch, "float16", None),
                "half": getattr(torch, "float16", None),
                "bfloat16": getattr(torch, "bfloat16", None),
                "bf16": getattr(torch, "bfloat16", None),
            }
            target_dtype = mapping.get(lower)
        else:
            target_dtype = dtype

    try:
        if target_dtype is not None:
            context = autocast_cls(dtype=target_dtype)
        else:
            context = autocast_cls()
    except Exception:  # pragma: no cover - AMP context creation failed
        yield
        return

    with context:
        yield


def clip_gradients(parameters: Iterable[object], max_norm: float) -> None:
    """Clip gradients using ``torch.nn.utils.clip_grad_norm_`` when possible."""

    if max_norm is None or max_norm <= 0:
        return

    try:  # pragma: no cover - optional dependency
        import torch
    except Exception:  # pragma: no cover - dependency missing
        return

    params = list(parameters)
    if not params:
        return

    try:
        torch.nn.utils.clip_grad_norm_(params, max_norm)  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - clipping best-effort
        return


class _FakeScaler:
    """Fallback ``GradScaler`` implementation used when AMP is unavailable."""

    def scale(self, value):  # type: ignore[no-untyped-def]
        return value

    def unscale_(self, _optimizer):  # type: ignore[no-untyped-def]
        return None

    def step(self, optimizer):  # type: ignore[no-untyped-def]
        optimizer.step()

    def update(self) -> None:  # type: ignore[override]
        return None


def get_amp_scaler(enabled: bool):
    """Return a ``GradScaler`` instance when AMP is enabled and available."""

    if not enabled:
        return _FakeScaler()

    try:  # pragma: no cover - optional dependency
        import torch

        return torch.cuda.amp.GradScaler()  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - AMP unavailable
        return _FakeScaler()


__all__ = ["maybe_autocast", "clip_gradients", "get_amp_scaler"]
