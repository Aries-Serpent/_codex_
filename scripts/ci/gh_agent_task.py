#!/usr/bin/env python3
"""Thin wrapper for the Copilot agent task CLI."""

from __future__ import annotations

import sys

try:
    from scripts.ci.copilot_agent_task import main
except ImportError:  # pragma: no cover - direct-script compatibility
    from copilot_agent_task import main  # type: ignore[no-redef]


if __name__ == "__main__":
    raise SystemExit(main())
