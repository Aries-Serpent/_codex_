from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, List, Sequence, Tuple

from .jsonl_stream import iter_jsonl


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


RecordTransform = Callable[[dict[str, Any]], Any]
RecordValidator = Callable[[dict[str, Any]], None]


@dataclass
class StreamingDataModule:
    """JSONL-backed continual-learning helper that yields deterministic batches."""

    train_path: str | Path
    eval_path: str | Path | None = None
    test_path: str | Path | None = None
    batch_size: int = 32
    transform: RecordTransform | None = None
    validator: RecordValidator | None = None

    def _stream(self, path: str | Path) -> Iterator[Any]:
        for record in iter_jsonl(path):
            if self.validator:
                self.validator(record)
            yield self.transform(record) if self.transform else record

    def _batched(self, path: str | Path) -> Iterator[tuple[Any, ...]]:
        batch: list[Any] = []
        for record in self._stream(path):
            batch.append(record)
            if len(batch) == self.batch_size:
                yield tuple(batch)
                batch.clear()
        if batch:
            yield tuple(batch)

    def iter_train(self) -> Iterator[tuple[Any, ...]]:
        yield from self._batched(self.train_path)

    def iter_eval(self) -> Iterator[tuple[Any, ...]]:
        if self.eval_path is None:
            return iter(())
        yield from self._batched(self.eval_path)

    def iter_test(self) -> Iterator[tuple[Any, ...]]:
        if self.test_path is None:
            return iter(())
        yield from self._batched(self.test_path)
