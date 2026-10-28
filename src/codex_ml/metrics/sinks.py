"""Pluggable metrics sinks for offline logging."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from typing import Any, Protocol, TextIO, runtime_checkable

__all__ = ["CsvSink", "MetricsSink", "NdjsonSink", "NullSink", "create_sink"]


@runtime_checkable
class MetricsSink(Protocol):
    """Runtime-checkable structural interface for synchronous metric writers.

    Implementations accept metric dictionaries through write and finish via
    close. The concrete sinks here flush but do not close caller-owned streams;
    this protocol itself supplies no buffering, validation, or persistence.
    """

    def write(self, row: dict[str, Any]) -> None:
        """Accept a metric row for emission by an implementing sink.

        Args:
            row: Field names mapped to values supported by the sink's serializer.

        Returns:
            None. Concrete writers determine flushing and serialization errors.
        """
        pass

    def close(self) -> None:
        """Finish sink output according to the implementation's ownership policy.

        Returns:
            None. Callers must separately close streams owned by them.
        """
        pass


class NullSink:
    """Sink that discards all metrics."""

    def write(self, row: dict[str, Any]) -> None:  # pragma: no cover - intentionally empty
        """Discard row without serializing it or retaining any values.

        Args:
            row: Metric mapping; ignored even if values are not serializable.

        Returns:
            None.
        """
        return None

    def close(self) -> None:  # pragma: no cover - intentionally empty
        """Return None without flushing or closing any resources."""
        return None


@dataclass
class CsvSink:
    """Write metric dictionaries to a caller-owned CSV text stream.

    Args:
        fp: Writable text stream, preferably opened with newline="".
        fieldnames: Ordered column names for csv.DictWriter.

    The first write emits a header even on an existing nonempty stream.
    Every write flushes; close only flushes, leaving stream ownership with
    the caller. Extra row keys raise ValueError; missing fields are empty.
    """

    fp: TextIO
    fieldnames: list[str]

    def __post_init__(self) -> None:
        self._writer = csv.DictWriter(self.fp, fieldnames=self.fieldnames)
        self._wrote_header = False

    def write(self, row: dict[str, Any]) -> None:
        """Write the first-call header and row, then flush the text stream.

        Args:
            row: Mapping whose keys are limited to the configured fieldnames.

        Raises:
            ValueError: If row has extra keys or the stream is closed.
            OSError: If writing or flushing fails. A header may already be written.
        """
        if not self._wrote_header:
            self._writer.writeheader()
            self._wrote_header = True
        self._writer.writerow(row)
        self.fp.flush()

    def close(self) -> None:
        """Flush pending CSV output without closing the supplied stream.

        Returns:
            None.

        Raises:
            OSError: If the stream cannot be flushed.
            ValueError: If the caller has already closed the stream.
        """
        self.fp.flush()


@dataclass
class NdjsonSink:
    """Serialize metric rows as Unicode JSON lines on a caller-owned stream.

    Args:
        fp: Writable text stream. Each write appends one newline and flushes.

    No schema is imposed. close flushes but never closes fp.
    """

    fp: TextIO

    def write(self, row: dict[str, Any]) -> None:
        """Serialize row with ensure_ascii=False, append a newline, and flush.

        Args:
            row: Metric dictionary containing JSON-serializable values.

        Raises:
            TypeError: If a value is not JSON serializable.
            ValueError: If serialization detects a cycle or the stream is closed.
            OSError: If writing or flushing fails.
        """
        self.fp.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.fp.flush()

    def close(self) -> None:
        """Flush JSON-line output while leaving the caller-owned stream open.

        Returns:
            None.

        Raises:
            OSError: If flushing fails.
            ValueError: If the stream is already closed.
        """
        self.fp.flush()


def create_sink(
    kind: str, fp: TextIO | None = None, *, fieldnames: list[str] | None = None
) -> MetricsSink:
    """Build a CSV, NDJSON, or discard sink without opening a file.

    Args:
        kind: Case-insensitive csv or ndjson; any other value selects NullSink.
            Whitespace is not stripped.
        fp: Caller-owned text stream, required for csv and ndjson.
        fieldnames: Nonempty CSV column list; copied before constructing a sink.

    Returns:
        A MetricsSink. Its close method does not close fp.

    Raises:
        ValueError: If a selected writer lacks fp or CSV lacks fieldnames.

    Example:
        >>> from io import StringIO
        >>> stream = StringIO()
        >>> sink = create_sink("ndjson", stream)
        >>> sink.write({"step": 1})
        >>> sink.close()
        >>> stream.getvalue().splitlines()
        ['{"step": 1}']
        >>> stream.closed
        False
    """
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
