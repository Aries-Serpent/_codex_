"""Minimal torch.utils.data stub."""

from __future__ import annotations

from typing import Any


class Dataset:
    pass


class TensorDataset(Dataset):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.tensors = args


class DataLoader:
    def __init__(self, dataset: Any = None, *args: Any, **kwargs: Any) -> None:
        self.dataset = dataset

    def __iter__(self):
        if self.dataset is None:
            return iter(())
        return iter(self.dataset)

    def __len__(self) -> int:
        return 0


def random_split(dataset: Any, lengths: Any, *args: Any, **kwargs: Any) -> list[Any]:
    return [dataset] if not isinstance(lengths, (list, tuple)) else list(lengths)


__all__ = ["Dataset", "DataLoader", "TensorDataset", "random_split"]
