#!/usr/bin/env python3
"""Compatibility wrapper for the canonical GitHub App token helper."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.tools.github.app_token import *  # noqa: F401,F403

if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
