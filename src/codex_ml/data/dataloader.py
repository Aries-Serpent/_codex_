"""Data handling scaffolding for _codex_.

Provides a deterministic "shuffle" based on a simple seed for smoke tests.
"""

from typing import List


def deterministic_order(items: List[int], seed: int) -> List[int]:
    return sorted(items, key=lambda x: (x + seed) % 97)
