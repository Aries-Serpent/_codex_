"""Data handling scaffolding for _codex_.

Provides a deterministic "shuffle" based on a simple seed for smoke tests.
"""


def deterministic_order(items: list[int], seed: int) -> list[int]:
    return sorted(items, key=lambda x: (x + seed) % 97)
