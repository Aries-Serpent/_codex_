"""CLI wrappers for aggregating rotated ``metrics.ndjson`` shards."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Sequence

from codex_utils.cli import ndjson_summary as _ndjson_summary_utils
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = run_cmd

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

    logger = init_json_logging()
    parser = ArgparseJSONParser(prog=_ndjson_summary_utils.__name__)
    arg_list: List[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=parser.prog, args=arg_list)
        exit_code = _ndjson_summary_utils.main(argv)
        status = "ok" if exit_code == 0 else "error"
        log_event(logger, "cli.finish", prog=parser.prog, status=status, exit_code=exit_code)
        return exit_code


__all__ = ["NdjsonSummarizer", "build_parser", "main", "summarize", "summarize_directory"]
