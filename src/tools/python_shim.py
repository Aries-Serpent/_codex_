#!/usr/bin/env python3
"""Invoke the first available Python interpreter, preferring `python`."""

from __future__ import annotations

import os
import shutil
import sys
from collections.abc import Sequence
from typing import NoReturn


def _find_python(candidates: Sequence[str]) -> str:
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    raise SystemExit(
        "Unable to locate a Python interpreter from candidates: " + ", ".join(candidates)
    )


def main(argv: list[str]) -> NoReturn:
    interpreter = _find_python(("python", "python3"))
    os.execv(interpreter, [interpreter, *argv])  # noqa: S606 - deterministic hand-off


if __name__ == "__main__":
    main(sys.argv[1:])
