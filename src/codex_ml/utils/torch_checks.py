"""Utilities for validating local PyTorch installations.

These helpers guard against partial "stub" wheels that lack
``torch.utils.data.Dataset`` while still allowing ``import torch`` to succeed.
The recommended recovery path follows the official "Start Locally" guidance for
CPU-only wheels, which instructs using the dedicated PyTorch index when
reinstalling offline builds.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Final

__all__ = [
    "OFFICIAL_CPU_INDEX_URL",
    "REINSTALL_COMMAND",
    "TorchStatus",
    "diagnostic_report",
    "inspect_torch",
]

OFFICIAL_CPU_INDEX_URL: Final[str] = "https://download.pytorch.org/whl/cpu"
REINSTALL_COMMAND: Final[str] = (
    "python -m pip install torch torchvision torchaudio --index-url " f"{OFFICIAL_CPU_INDEX_URL}"
)


@dataclass(frozen=True)
class TorchStatus:
    """Details about the currently importable PyTorch module."""

    ok: bool
    detail: str
    reinstall_hint: str | None
    version: str | None
    location: str | None

    def summary(self) -> str:
        parts: list[str] = []
        if self.version:
            parts.append(f"version={self.version}")
        if self.location:
            parts.append(f"path={self.location}")
        if not parts:
            return self.detail
        return f"{self.detail} ({', '.join(parts)})"


def _load_torch(module: ModuleType | None = None) -> ModuleType:
    if module is not None:
        return module
    spec = importlib.util.find_spec("torch")
    if spec is None:
        raise ModuleNotFoundError("torch module not importable")
    return importlib.import_module("torch")


def inspect_torch(module: ModuleType | None = None) -> TorchStatus:
    """Return diagnostics describing whether a real PyTorch install is available."""

    try:
        torch_mod = _load_torch(module)
    except Exception as exc:  # pragma: no cover - best-effort guard
        return TorchStatus(
            ok=False,
            detail=f"torch import failed: {exc!r}",
            reinstall_hint=REINSTALL_COMMAND,
            version=None,
            location=None,
        )

    version = getattr(torch_mod, "__version__", None)
    location = getattr(torch_mod, "__file__", None)
    utils = getattr(torch_mod, "utils", None)
    if utils is None:
        return TorchStatus(
            ok=False,
            detail="torch.utils attribute missing",
            reinstall_hint=REINSTALL_COMMAND,
            version=version,
            location=location,
        )

    try:
        data_module = importlib.import_module("torch.utils.data")
    except Exception as exc:
        return TorchStatus(
            ok=False,
            detail=f"torch.utils.data import failed: {exc!r}",
            reinstall_hint=REINSTALL_COMMAND,
            version=version,
            location=location,
        )

    if not hasattr(data_module, "Dataset"):
        return TorchStatus(
            ok=False,
            detail="torch.utils.data.Dataset missing",
            reinstall_hint=REINSTALL_COMMAND,
            version=version,
            location=location,
        )

    return TorchStatus(
        ok=True,
        detail="PyTorch utilities available",
        reinstall_hint=None,
        version=version if isinstance(version, str) else None,
        location=location if isinstance(location, str) else None,
    )


def diagnostic_report(status: TorchStatus | None = None) -> str:
    """Format a human-readable diagnostic summary for logs or gate output."""

    status = status or inspect_torch()
    lines = [status.summary()]
    if status.reinstall_hint:
        lines.append(f"Reinstall via: {status.reinstall_hint}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover - manual diagnostic entry point
    report = diagnostic_report()
    print(report)
    if not inspect_torch().ok:
        sys.exit(1)
