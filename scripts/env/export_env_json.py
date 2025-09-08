#!/usr/bin/env python3
"""Dump environment summary to a JSON file (default: env.json)."""

import json
import platform
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

from codex_ml.monitoring.codex_logging import _codex_sample_system


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


REPO = Path(__file__).resolve().parents[2]
CODEX = REPO / ".codex"
ERRORS = CODEX / "errors.ndjson"


def _ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _q5(step: str, err: str, ctx: str) -> None:
    CODEX.mkdir(exist_ok=True)
    entry = {"ts": _ts(), "step": step, "error": err, "context": ctx}
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    rq = textwrap.dedent(
        f"""
Question for ChatGPT @codex {_ts()}:
While performing [{step}], encountered the following error:
{err}
Context: {ctx}
What are the possible causes, and how can this be resolved while preserving intended functionality?
"""
    )
    sys.stderr.write(rq)


def main() -> None:
    step = "export_env_json:main"
    try:
        info = _codex_sample_system()
        info["platform"] = platform.platform()
        info["python"] = sys.version.split()[0]
        commit = _git_commit()
        if commit:
            info["git_commit"] = commit
        path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("env.json")
        path.write_text(json.dumps(info, indent=2), encoding="utf-8")
        print(path)
    except Exception as exc:  # pragma: no cover - best effort logging
        _q5(step, str(exc), "dump environment summary")
        raise


if __name__ == "__main__":
    main()
