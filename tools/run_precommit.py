#!/usr/bin/env python
"""
Run pre-commit with verbosity, timeout, and selective skipping.
Diagnoses slow hooks; supports cache cleanup fallback.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

__all__ = ["run", "run_cli"]


def run(timeout_s: int = 180, skip: str | None = None) -> int:
    env = os.environ.copy()
    if skip:
        env["SKIP"] = skip
    cmd = ["pre-commit", "run", "--all-files", "--verbose"]
    start = time.time()
    try:
        proc = subprocess.Popen(cmd, env=env)
        while True:
            ret = proc.poll()
            if ret is not None:
                return ret
            if time.time() - start > timeout_s:
                proc.terminate()
                print(
                    "[pre-commit] timeout; cleaning caches and retrying once...",
                    file=sys.stderr,
                )
                subprocess.call(["pre-commit", "clean"], env=env)
                return subprocess.call(cmd, env=env)
            time.sleep(1.0)
    except FileNotFoundError:
        print(
            "pre-commit not found on PATH; please 'pip install pre-commit==4.0.1'",
            file=sys.stderr,
        )
        return 127


def run_cli() -> None:
    skip = os.environ.get("PRECOMMIT_SKIP") or None
    timeout = int(os.environ.get("PRECOMMIT_TIMEOUT", "180"))
    sys.exit(run(timeout_s=timeout, skip=skip))


if __name__ == "__main__":
    run_cli()
