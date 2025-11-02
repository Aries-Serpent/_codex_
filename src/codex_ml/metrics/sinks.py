"""Pluggable metrics sinks for offline logging."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol, TextIO
import csv
import json

__all__ = ["MetricsSink", "CsvSink", "NdjsonSink", "NullSink", "create_sink"]


class MetricsSink(Protocol):
    def write(self, row: Dict) -> None:
        ...

    def close(self) -> None:
        ...


class NullSink:
    """Sink that discards all metrics."""

    def write(self, row: Dict) -> None:  # pragma: no cover - intentionally empty
        return None

    def close(self) -> None:  # pragma: no cover - intentionally empty
        return None


@dataclass
class CsvSink:
    fp: TextIO
    fieldnames: list[str]

    def __post_init__(self) -> None:
        self._writer = csv.DictWriter(self.fp, fieldnames=self.fieldnames)
        self._wrote_header = False

    def write(self, row: Dict) -> None:
        if not self._wrote_header:
            self._writer.writeheader()
            self._wrote_header = True
        self._writer.writerow(row)
        self.fp.flush()

    def close(self) -> None:
        self.fp.flush()


@dataclass
class NdjsonSink:
    fp: TextIO

    def write(self, row: Dict) -> None:
        self.fp.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.fp.flush()

    def close(self) -> None:
        self.fp.flush()


def create_sink(kind: str, fp: TextIO | None = None, *, fieldnames: list[str] | None = None) -> MetricsSink:
    kind = (kind or "").lower()
    if kind == "csv":
        if fp is None:
            raise ValueError("CsvSink requires a file-like object")
        if not fieldnames:
            raise ValueError("CsvSink requires fieldnames")
        return CsvSink(fp=fp, fieldnames=list(fieldnames))
    if kind == "ndjson":
        if fp is None:
            raise ValueError("NdjsonSink requires a file-like object")
        return NdjsonSink(fp=fp)
    return NullSink()
