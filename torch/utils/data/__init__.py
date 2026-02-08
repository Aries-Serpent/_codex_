"""Minimal torch.utils.data shim for test environments."""

from __future__ import annotations

__all__ = ["Dataset", "DataLoader"]


class Dataset:  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.Dataset."""

    pass


class DataLoader:  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.DataLoader."""

    def __init__(self, *args, **kwargs):
        pass


def __getattr__(name: str):
    """Raise AttributeError for any other torch.utils.data attribute access."""
    raise AttributeError(
        "PyTorch is not installed in this environment. "
        "Install torch to enable these features."
    )
