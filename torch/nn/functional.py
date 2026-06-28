"""Minimal torch.nn.functional shim for test environments."""

from __future__ import annotations

__all__ = []


def __getattr__(name: str) -> None:
    """Raise AttributeError for any torch.nn.functional attribute access."""
    raise AttributeError(
        "PyTorch is not installed in this environment. "
        "Install torch to enable these features."
    )
