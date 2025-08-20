#!/usr/bin/env python3
"""Run lint/tests and log results for Codex self-management."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time


LOG_PATH = pathlib.Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/action_log.ndjson"))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_PATH.touch(exist_ok=True)


def log(event: str, status: str, detail: str | None = None) -> None:
    rec = {"ts": time.time(), "event": event, "status": status}
    if detail:
        rec["detail"] = detail
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def run(cmd: list[str]) -> int:
    if os.getenv("CODEX_CLI_SKIP") == "1":
        return 0
    return subprocess.run(cmd, check=False).returncode


def cmd_lint() -> int:
    rc = run(["pre-commit", "run", "--all-files"])
    log("lint", "ok" if rc == 0 else "fail")
    return rc


def cmd_test() -> int:
    rc = run(["pytest", "-q"])
    log("test", "ok" if rc == 0 else "fail")
    return rc


def cmd_audit() -> int:
    rc_lint = run(["pre-commit", "run", "--all-files"])
    rc_test = run(["pytest", "-q"])
    rc = rc_lint or rc_test
    log("audit", "ok" if rc == 0 else "fail", "pre-commit+pytest")
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(prog="codex-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lint")
    sub.add_parser("test")
    sub.add_parser("audit")
    args = parser.parse_args()

    if args.cmd == "lint":
        return cmd_lint()
    if args.cmd == "test":
        return cmd_test()
    if args.cmd == "audit":
        return cmd_audit()
    parser.error("unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())

