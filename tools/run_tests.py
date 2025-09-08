#!/usr/bin/env python
"""
Run pytest with coverage if plugin is available; degrade gracefully otherwise.
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

__all__ = ["main"]

CODEX = Path(".codex")
ERRORS = CODEX / "errors.ndjson"


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def q5(step: str, err: str, ctx: str) -> None:
    """Append an error entry and emit a ChatGPT-5 research question."""
    CODEX.mkdir(parents=True, exist_ok=True)
    entry = {"ts": ts(), "step": step, "error": err, "context": ctx}
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    rq = textwrap.dedent(
        f"""
        Question for ChatGPT @codex {entry['ts']}:
        While performing {step}, encountered the following error:
        {err}
        Context: {ctx}
        What are the possible causes, and how can this be resolved while preserving intended functionality?
        """
    )
    sys.stderr.write(rq + "\n")


def has_pytest_cov() -> bool:
    try:
        out = subprocess.check_output(
            ["pytest", "--version", "--override-ini", "addopts=''"],
            text=True,
        )
        return "pytest-cov" in out
    except Exception:
        return False


def main() -> int:
    cmd = ["pytest", "-q", "--override-ini", "addopts=''"]
    if has_pytest_cov():
        cmd += ["--cov=src/codex_ml", "--cov-report=term", "--cov-fail-under=70"]
    else:
        print("[tests] pytest-cov not detected; running without coverage.")
    try:
        ret = subprocess.call(cmd)
        if ret != 0:
            q5("1: run pytest", f"exit {ret}", " ".join(cmd))
        return ret
    except Exception as e:  # pragma: no cover - broad except for logging
        q5("1: run pytest", str(e), " ".join(cmd))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
