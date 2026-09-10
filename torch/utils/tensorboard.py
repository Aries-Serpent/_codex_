"""Minimal torch.utils.tensorboard stub."""

from __future__ import annotations


class SummaryWriter:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def add_scalar(self, *args, **kwargs) -> None:
        return None

    def flush(self) -> None:
        return None

    def close(self) -> None:
        return None


__all__ = ["SummaryWriter"]
