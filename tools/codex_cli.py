#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import shutil
import subprocess  # nosec B404
import sys
import time

LOG_PATH = pathlib.Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/action_log.ndjson"))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

SKIP_PRECOMMIT = os.getenv("CODEX_CLI_SKIP_PRECOMMIT") == "1"
SKIP_TESTS = os.getenv("CODEX_CLI_SKIP_TESTS") == "1"


def log(event: str, status: str, detail: str = "") -> None:
    rec = {"ts": time.time(), "event": event, "status": status, "detail": detail}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def run(cmd: list[str]) -> int:
    try:
        exe = shutil.which(cmd[0])
        if exe is None:
            raise FileNotFoundError(cmd[0])
        result = subprocess.run([exe, *cmd[1:]], check=True)  # nosec B603
        return result.returncode
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def cmd_lint() -> int:
    if SKIP_PRECOMMIT:
        rc = 0
    else:
        rc = run(["pre-commit", "run", "--all-files"])
    log("lint", "ok" if rc == 0 else "fail")
    return rc


def cmd_test() -> int:
    if SKIP_TESTS:
        rc = 0
    else:
        rc = run(["pytest", "-q"])
    log("test", "ok" if rc == 0 else "fail")
    return rc


def cmd_audit() -> int:
    rc = 0
    if not SKIP_PRECOMMIT:
        rc |= run(["pre-commit", "run", "--all-files"])
    if not SKIP_TESTS:
        rc |= run(["pytest", "-q"])
    log("audit", "ok" if rc == 0 else "fail", "pre-commit+pytest")
    return rc


def main() -> None:
    parser = argparse.ArgumentParser("codex-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lint")
    sub.add_parser("test")
    sub.add_parser("audit")
    args = parser.parse_args()
    if args.cmd == "lint":
        sys.exit(cmd_lint())
    if args.cmd == "test":
        sys.exit(cmd_test())
    if args.cmd == "audit":
        sys.exit(cmd_audit())


if __name__ == "__main__":
    main()
