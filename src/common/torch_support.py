"""Utilities for handling optional PyTorch availability.

These helpers make it easy to guard features that require a real PyTorch
installation.  They surface consistent, actionable guidance when PyTorch is
missing or only a lightweight stub is available, and optionally validate CUDA
support when GPU execution is requested.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Final

from codex_ml.utils.torch_checks import REINSTALL_COMMAND, inspect_torch

__all__ = [
    "MissingTorchError",
    "ensure_torch_install",
    "is_torch_available",
    "maybe_import_torch",
]

_DEFAULT_MESSAGE: Final[str] = (
    "PyTorch is required for this functionality. Install the 'codex-ml[torch]' "
    "extra or run: "
    f"{REINSTALL_COMMAND}"
)


class MissingTorchError(ModuleNotFoundError):
    """Raised when a required PyTorch feature is unavailable."""

    def __init__(self, detail: str | None = None) -> None:
        message = detail or _DEFAULT_MESSAGE
        super().__init__(message)
        self.detail = message


def ensure_torch_install(*, require_cuda: bool = False) -> ModuleType:
    """Return a real :mod:`torch` module or raise :class:`MissingTorchError`.

    Parameters
    ----------
    require_cuda:
        When ``True``, the helper also verifies that ``torch.cuda.is_available``
        returns ``True``.  This is useful for call sites that *must* run on a
        GPU; callers that can gracefully fallback to CPU should keep the default
        ``False``.
    """

    try:
        module = importlib.import_module("torch")
    except ModuleNotFoundError as exc:  # pragma: no cover - defensive guard
        raise MissingTorchError() from exc

    version = getattr(module, "__version__", "")
    if version == "0.0.0-stub":
        raise MissingTorchError(
            "Detected the lightweight 'torch' compatibility shim. Install a "
            "full PyTorch build to enable this feature. Suggested command: "
            f"{REINSTALL_COMMAND}"
        )

    status = inspect_torch(module)
    if not status.ok:
        hint = status.detail
        if status.reinstall_hint:
            hint = f"{status.detail}. Reinstall via: {status.reinstall_hint}"
        raise MissingTorchError(
            "PyTorch installation appears incomplete. " f"{hint}"
        )

    if require_cuda:
        cuda = getattr(module, "cuda", None)
        available = bool(cuda and getattr(cuda, "is_available", lambda: False)())
        if not available:
            raise MissingTorchError(
                "CUDA support was requested but torch.cuda.is_available() is False. "
                "Install a CUDA-enabled PyTorch build or disable CUDA for this "
                "operation."
            )

    return module


def maybe_import_torch(*, require_cuda: bool = False) -> ModuleType | None:
    """Best-effort import of :mod:`torch` returning ``None`` when unavailable."""

    try:
        return ensure_torch_install(require_cuda=require_cuda)
    except MissingTorchError:
        return None


def is_torch_available(*, require_cuda: bool = False) -> bool:
    """Return ``True`` when a suitable PyTorch install is importable."""

    return maybe_import_torch(require_cuda=require_cuda) is not None
