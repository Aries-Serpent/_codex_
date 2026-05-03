"""
Datamodule Module

This module provides functionality for datamodule.

Usage:
    from data.datamodule import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import random
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableSequence, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
)


@dataclass
class DataModule:
    """Lightweight container for deterministic dataset iteration in tests."""

    train: list[Any]
    val: list[Any]
    test: list[Any]
    seed: int = 42

    def __post_init__(self) -> None:
        self.shuffle()

    def shuffle(self) -> None:
        random.seed(self.seed)
        random.shuffle(self.train)
        random.shuffle(self.val)
        random.shuffle(self.test)

    def iter_train(self, batch_size: int) -> Iterable[tuple[Any, ...]]:
        train_seq: Sequence[Any] = self.train
        for index in range(0, len(train_seq), batch_size):
            yield tuple(train_seq[index : index + batch_size])


ExampleValidator = Callable[[Mapping[str, Any]], None]


def default_example_validator(required_keys: Sequence[str]) -> ExampleValidator:
    required = tuple(required_keys)

    def _validate(example: Mapping[str, Any]) -> None:
        missing = [key for key in required if key not in example]
        if missing:
            raise ValueError(f"example missing keys: {', '.join(missing)}")

    return _validate


@dataclass
class StreamingDataModule:
    """Streaming JSONL/iterable dataset loader with deterministic replay."""

    train_source: str | Path | Iterable[Mapping[str, Any]]
    val_source: str | Path | Iterable[Mapping[str, Any]] | None = None
    test_source: str | Path | Iterable[Mapping[str, Any]] | None = None
    validator: ExampleValidator | None = None
    shuffle_buffer: int = 0
    seed: int = 42
    chunk_size: int = 2048

    def iter_train(self, batch_size: int) -> Iterable[tuple[Mapping[str, Any], ...]]:
        return self._batched(self._stream_split("train"), batch_size)

    def iter_val(self, batch_size: int) -> Iterable[tuple[Mapping[str, Any], ...]]:
        return self._batched(self._stream_split("val"), batch_size)

    def iter_test(self, batch_size: int) -> Iterable[tuple[Mapping[str, Any], ...]]:
        return self._batched(self._stream_split("test"), batch_size)

    def snapshot(self, split: str, limit: int | None = None) -> list[Mapping[str, Any]]:
        examples: list[Mapping[str, Any]] = []
        for index, example in enumerate(self._stream_split(split)):
            examples.append(example)
            if limit is not None and index + 1 >= limit:
                break
        return examples

    def _stream_split(self, split: str) -> Iterator[Mapping[str, Any]]:
        source = {
            "train": self.train_source,
            "val": self.val_source,
            "validation": self.val_source,
            "test": self.test_source,
        }.get(split)
        if source is None:
            return iter(())
        offset = {"train": 0, "val": 1, "validation": 1, "test": 2}.get(split, 0)
        rng = random.Random(self.seed + offset)  # nosec B311 - deterministic data stream shuffle
        iterable = self._coerce_iterable(source)
        return self._shuffle_stream(iterable, rng)

    def _coerce_iterable(
        self, source: str | Path | Iterable[Mapping[str, Any]]
    ) -> Iterator[Mapping[str, Any]]:
        if isinstance(source, (str, Path)):
            path = Path(source)
            if path.is_dir():
                raise ValueError(f"expected file, received directory: {path}")
            suffix = path.suffix.lower()
            if suffix in {".jsonl", ".ndjson"}:
                return self._read_jsonl(path)
            if suffix == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, MutableSequence):
                    return self._wrap_iter(data)
                raise ValueError(f"unsupported JSON structure in {path}")
            raise ValueError(f"unsupported dataset format: {suffix}")
        return self._wrap_iter(source)

    def _wrap_iter(self, iterable: Iterable[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
        for example in iterable:
            mapping = dict(example)
            if self.validator is not None:
                self.validator(mapping)
            yield mapping

    def _read_jsonl(self, path: Path) -> Iterator[Mapping[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                text = raw.strip()
                if not text:
                    continue
                payload = json.loads(text)
                if not isinstance(payload, Mapping):
                    raise ValueError(f"expected mapping entries in {path}")
                mapping = dict(payload)
                if self.validator is not None:
                    self.validator(mapping)
                yield mapping

    def _shuffle_stream(
        self,
        iterable: Iterator[Mapping[str, Any]],
        rng: random.Random,
    ) -> Iterator[Mapping[str, Any]]:
        if self.shuffle_buffer <= 1:
            yield from iterable
            return
        buffer: list[Mapping[str, Any]] = []
        for item in iterable:
            buffer.append(item)
            if len(buffer) >= self.shuffle_buffer:
                index = rng.randrange(len(buffer))
                buffer[index], buffer[-1] = buffer[-1], buffer[index]
                yield buffer.pop()
        while buffer:
            index = rng.randrange(len(buffer))
            yield buffer.pop(index)

    def _batched(
        self,
        iterator: Iterator[Mapping[str, Any]],
        batch_size: int,
    ) -> Iterator[tuple[Mapping[str, Any], ...]]:
        batch: list[Mapping[str, Any]] = []
        for example in iterator:
            batch.append(example)
            if len(batch) == batch_size:
                yield tuple(batch)
                batch.clear()
        if batch:
            yield tuple(batch)


__all__ = ["DataModule", "StreamingDataModule", "default_example_validator"]
