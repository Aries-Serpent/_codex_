from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Iterable, List, Sequence, Tuple


@dataclass
class DataModule:
    """Lightweight container for deterministic dataset iteration in tests."""

    train: List[Any]
    val: List[Any]
    test: List[Any]
    seed: int = 42

    def __post_init__(self) -> None:
        self.shuffle()

    def shuffle(self) -> None:
        random.seed(self.seed)
        random.shuffle(self.train)
        random.shuffle(self.val)
        random.shuffle(self.test)

    def iter_train(self, batch_size: int) -> Iterable[Tuple[Any, ...]]:
        train_seq: Sequence[Any] = self.train
        for index in range(0, len(train_seq), batch_size):
            yield tuple(train_seq[index : index + batch_size])
