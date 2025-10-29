#!/usr/bin/env python3
"""CLI entry point for Markdown fence validation.

This thin wrapper delegates to ``tools.validate_fences`` so the validator can
be invoked as ``python3 validate_fences.py`` while preserving the legacy module
API consumed throughout the repository.
"""
from __future__ import annotations

import sys

from tools import validate_fences


def main() -> int:
    """Run the fence validator using command line arguments from ``sys.argv``."""
    return validate_fences.main(sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover - exercised via CLI smoke tests
    raise SystemExit(main())
