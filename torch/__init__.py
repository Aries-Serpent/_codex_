"""Minimal torch stub for tests that only query CUDA availability."""

from __future__ import annotations

__version__ = "0.0"


def manual_seed(seed: int) -> None:  # pragma: no cover - stub
    return None


class _Cuda:
    @staticmethod
    def is_available() -> bool:
        return False

    @staticmethod
    def manual_seed_all(seed: int) -> None:  # pragma: no cover - stub
        return None


cuda = _Cuda()

__all__ = ["cuda", "manual_seed", "__version__"]
