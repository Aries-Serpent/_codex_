"""CLI wrappers for aggregating rotated ``metrics.ndjson`` shards."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from codex_utils.cli import ndjson_summary as _ndjson_summary_utils

NdjsonSummarizer = _ndjson_summary_utils.NdjsonSummarizer
build_parser = _ndjson_summary_utils.build_parser
summarize_directory = _ndjson_summary_utils.summarize_directory


def summarize(directory: Path, fmt: str, destination: Path | None = None) -> Path:
    """Aggregate metrics shards via :mod:`codex_utils.cli.ndjson_summary`."""

    try:
        path = _ndjson_summary_utils.summarize_directory(directory, fmt, destination)
    except FileNotFoundError as exc:  # pragma: no cover - propagates CLI semantics
        raise SystemExit(str(exc)) from exc
    return Path(path)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry-point proxy returning the wrapped CLI's exit code."""

    return _ndjson_summary_utils.main(argv)


__all__ = ["NdjsonSummarizer", "build_parser", "main", "summarize", "summarize_directory"]
