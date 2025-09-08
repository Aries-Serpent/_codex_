#!/usr/bin/env python3
"""Dump environment variables and version info in JSON."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys

from codex_ml.monitoring.codex_logging import _codex_sample_system


def _log_error(step: str, err: Exception, ctx: str) -> None:
    """Record errors in the standard research question format."""
    import textwrap
    from datetime import datetime
    from pathlib import Path

    ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    msg = textwrap.dedent(
        f"""\
        Question for ChatGPT @codex {ts}:
        While performing [{step}], encountered the following error:
        {err}
        Context: {ctx}
        What are the possible causes, and how can this be resolved while preserving intended functionality?
        """
    )
    codex_dir = Path(__file__).resolve().parents[1] / ".codex"
    codex_dir.mkdir(exist_ok=True)
    errors = codex_dir / "errors.ndjson"
    with errors.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ts, "step": step, "error": str(err), "context": ctx}) + "\n")
    sys.stderr.write(msg + "\n")


def main() -> None:
    info = {
        "python": sys.version,
        "platform": platform.platform(),
        "env": dict(os.environ),
        "system": _codex_sample_system(),
    }
    try:
        info["git_commit"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception as exc:  # pragma: no cover - logging path
        _log_error("1:git_rev_parse", exc, "collecting git commit")
        info["git_commit"] = None
    try:
        info["pip_freeze"] = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True
        )
    except Exception as exc:  # pragma: no cover - logging path
        _log_error("2:pip_freeze", exc, "collecting dependencies")
        info["pip_freeze"] = ""
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
