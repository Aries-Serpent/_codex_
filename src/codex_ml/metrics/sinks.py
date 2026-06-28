"""Pluggable metrics sinks for offline logging."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from typing import Any, Protocol, TextIO, runtime_checkable

__all__ = ["CsvSink", "MetricsSink", "NdjsonSink", "NullSink", "create_sink"]


@runtime_checkable
class MetricsSink(Protocol):
    def write(self, row: dict[str, Any]) -> None:
        pass

    def close(self) -> None:
        pass


class NullSink:
    """Sink that discards all metrics."""

    def write(self, row: dict[str, Any]) -> None:  # pragma: no cover - intentionally empty
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

    def write(self, row: dict[str, Any]) -> None:
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

    def write(self, row: dict[str, Any]) -> None:
        self.fp.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.fp.flush()

    def close(self) -> None:
        self.fp.flush()


def create_sink(
    kind: str, fp: TextIO | None = None, *, fieldnames: list[str] | None = None
) -> MetricsSink:
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


def get_sink(kind: str | None, path: str | None = None) -> MetricsSink | None:
    """Factory for path-based sinks (alternate to create_sink with file handles)."""
    from pathlib import Path

    if not kind or kind == "none":
        return None
    if kind == "csv":
        p = Path(path or "artifacts/metrics/metrics.csv")
        p.parent.mkdir(parents=True, exist_ok=True)
        fp = p.open("a", newline="", encoding="utf-8")
        return CsvSink(fp=fp, fieldnames=["metric", "value", "step"])
    if kind == "ndjson":
        p = Path(path or "artifacts/metrics/metrics.ndjson")
        p.parent.mkdir(parents=True, exist_ok=True)
        fp = p.open("a", encoding="utf-8")
        return NdjsonSink(fp=fp)
    return NullSink()
