"""Streaming dataset helpers for continual-learning style ingestion."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, List, Tuple

Validator = Callable[[Any], None]


def iter_jsonl_chunks(
    path: str | Path,
    *,
    chunk_size: int = 1024,
    validator: Validator | None = None,
) -> Iterator[Tuple[dict[str, Any], ...]]:
    """Yield tuples of records from a JSONL file without loading the entire file."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    p = Path(path)
    buffer: List[dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except Exception as exc:  # pragma: no cover - surfaced in tests
                raise ValueError(f"Invalid JSON on line {line_number} of {p}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"Line {line_number} of {p} must be a JSON object (got {type(record).__name__})"
                )
            if validator is not None:
                validator(record)
            buffer.append(record)
            if len(buffer) >= chunk_size:
                yield tuple(buffer)
                buffer.clear()
    if buffer:
        yield tuple(buffer)


@dataclass
class StreamingDataModule:
    """Batch data from iterables or JSONL files without materialising them in memory."""

    train_source: Iterable[Any] | str | Path
    val_source: Iterable[Any] | str | Path | None = None
    test_source: Iterable[Any] | str | Path | None = None
    batch_size: int = 32
    ingest_chunk_size: int = 1024
    validator: Validator | None = None

    def iter_train(self) -> Iterator[Tuple[Any, ...]]:
        return self._batched(self._iterate(self.train_source))

    def iter_val(self) -> Iterator[Tuple[Any, ...]]:
        if self.val_source is None:
            return iter(())
        return self._batched(self._iterate(self.val_source))

    def iter_test(self) -> Iterator[Tuple[Any, ...]]:
        if self.test_source is None:
            return iter(())
        return self._batched(self._iterate(self.test_source))

    def _iterate(self, source: Iterable[Any] | str | Path) -> Iterator[Any]:
        if isinstance(source, (str, Path)):
            for chunk in iter_jsonl_chunks(
                source,
                chunk_size=self.ingest_chunk_size,
                validator=self.validator,
            ):
                for record in chunk:
                    yield record
            return
        for item in source:
            if self.validator is not None:
                self.validator(item)
            yield item

    def _batched(self, iterable: Iterable[Any]) -> Iterator[Tuple[Any, ...]]:
        batch: List[Any] = []
        for item in iterable:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield tuple(batch)
                batch.clear()
        if batch:
            yield tuple(batch)
