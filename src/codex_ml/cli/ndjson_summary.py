"""CLI wrappers for aggregating rotated ``metrics.ndjson`` shards."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from codex_utils.cli import ndjson_summary as _ndjson_summary_utils


build_parser = _ndjson_summary_utils.build_parser


def summarize(directory: Path, fmt: str, destination: Path | None = None) -> Path:
    """Aggregate metrics shards via :mod:`codex_utils.cli.ndjson_summary`."""

    args: list[str] = [
        "summarize",
        "--input",
        str(directory),
        "--output",
        fmt,
    ]
    if destination is not None:
        args.extend(["--dest", str(destination)])
    exit_code = _ndjson_summary_utils.main(args)
    if exit_code != 0:
        raise SystemExit(exit_code)
    suffix = fmt.lower()
    if destination is not None:
        return Path(destination)
    return Path(directory) / f"metrics_summary.{suffix}"


def main(argv: Sequence[str] | None = None) -> int:
    """Entry-point proxy returning the wrapped CLI's exit code."""

    return _ndjson_summary_utils.main(argv)


__all__ = ["build_parser", "main", "summarize"]

