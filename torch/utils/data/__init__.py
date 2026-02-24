"""Minimal torch.utils.data shim for test environments."""

from __future__ import annotations

__all__ = ["Dataset", "DataLoader", "TensorDataset", "random_split", "Subset"]


class Dataset:  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.Dataset."""

    pass


class DataLoader:  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.DataLoader."""

    def __init__(self, *args, **kwargs):
        pass


class TensorDataset:  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.TensorDataset.

    Raises AttributeError at construction time so that
    ``pytest.importorskip("torch")`` users see a clear message when real
    torch is absent rather than a cryptic AttributeError elsewhere.
    """

    def __init__(self, *tensors):
        raise AttributeError(
            "PyTorch is not installed in this environment. "
            "Install torch to enable these features."
        )


class Subset:  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.Subset."""

    def __init__(self, dataset, indices):
        raise AttributeError(
            "PyTorch is not installed in this environment. "
            "Install torch to enable these features."
        )


def random_split(*args, **kwargs):  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.random_split."""
    raise AttributeError(
        "PyTorch is not installed in this environment. "
        "Install torch to enable these features."
    )


def __getattr__(name: str):
    """Raise AttributeError for any other torch.utils.data attribute access."""
    raise AttributeError(
        "PyTorch is not installed in this environment. "
        "Install torch to enable these features."
    )
