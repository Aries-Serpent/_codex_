"""Lightweight structured logging helpers for CLIs."""

from __future__ import annotations

import logging
import sys
from collections.abc import Iterator
from contextlib import contextmanager

from codex_ml.utils.jsonio import print_error_json


def init_logger(
    level: str = "WARNING", *, json_mode: bool = False, name: str = "codex"
) -> logging.Logger:
    """Initialise a stderr logger with optional terse formatting for JSON CLIs."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        if json_mode:
            formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        else:
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.WARNING))
    logger.propagate = False
    return logger


@contextmanager
def capture_exceptions(
    *, exit_code: int = 2, emit_json: bool = False, errmsg: str = "error"
) -> Iterator[None]:
    """Capture unexpected exceptions and exit cleanly with optional JSON."""

    try:
        yield
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - exercised via CLI integration tests
        if emit_json:
            print_error_json(f"{errmsg}: {exc}")
        else:
            sys.stderr.write(f"{errmsg}: {exc}\n")
        raise SystemExit(exit_code) from None


__all__ = ["init_logger", "capture_exceptions"]
