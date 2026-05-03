"""Minimal torch.utils.data shim for test environments."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sized
from typing import Any, Generic, TypeVar

__all__ = ["Dataset", "DataLoader", "TensorDataset", "random_split", "Subset"]

_T_co = TypeVar("_T_co", covariant=True)


class Dataset(Generic[_T_co]):  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.Dataset."""

    def __len__(self) -> int:
        return 0

    def __getitem__(self, index: int) -> Any:
        raise NotImplementedError


class DataLoader(Iterable[Any], Sized):  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.DataLoader."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._data: list[Any] = []

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class TensorDataset(Sized):  # pragma: no cover - convenience stub
    """Stub for torch.utils.data.TensorDataset.

    Raises AttributeError at construction time so that
    ``pytest.importorskip("torch")`` users see a clear message when real
    torch is absent rather than a cryptic AttributeError elsewhere.
    """

    def __init__(self, *tensors: Any) -> None:
        raise AttributeError(
            "PyTorch is not installed in this environment. "
            "Install torch to enable these features."
        )

    def __len__(self) -> int:
        return 0


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
