#!/usr/bin/env python3
"""Print environment details for reproducibility."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from codex_ml.utils.env import environment_summary


def _log_error(step: str, err: Exception) -> None:
    """Append an error capture block to ``.codex/errors.ndjson``."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    block = (
        f"Question for ChatGPT @codex {ts}:\n"
        f"While performing [{step}], encountered the following error:\n"
        f"{err}\n"
        "Context: printing environment info\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?"
    )
    path = Path(".codex/errors.ndjson")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        json.dump({"question": block}, fh)
        fh.write("\n")


def main() -> None:
    try:
        info = environment_summary()
        json.dump(info, sys.stdout, indent=2)
        sys.stdout.write("\n")
    except Exception as exc:  # pragma: no cover
        _log_error("print_env_info:collect_environment", exc)
        raise


if __name__ == "__main__":
    main()
