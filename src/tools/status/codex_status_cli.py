#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime, timezone


def run(*args):
    try:
        subprocess.check_call(list(args))
    except Exception as e:
        error_type = type(e).__name__
        print(f"[warn] {error_type}", file=sys.stderr)
        return False
    return True


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prefix = "reports/daily/_codex_status_update"
    json_path = f"{prefix}-{today}.json"
    ok = True
    ok &= run(
        sys.executable,
        "src/tools/status/generate_status_update.py",
        "--author",
        "codex",
        "--date",
        today,
        "--write",
    )
    ok &= run(sys.executable, "src/tools/status/validate_status_update.py", json_path)
    ok &= run(sys.executable, "src/tools/status/capability_autodiscovery.py")
    ok &= run(sys.executable, "src/tools/docs/harvest_open_questions.py")
    ok &= run(sys.executable, "src/tools/status/render_md.py", json_path, f"{prefix}-{today}.tables.md")
    if not ok:
        print(f"STATUS FAILED -> {json_path}", file=sys.stderr)
        return 1
    print(f"OK -> {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
