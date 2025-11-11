#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime, timezone


def run(*args):
    try:
        subprocess.check_call(list(args))
    except Exception as e:
        print(f"[warn] {e}", file=sys.stderr)

def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prefix = "reports/daily/_codex_status_update"
    json_path = f"{prefix}-{today}.json"
    # generate
    run("python","tools/status/generate_status_update.py","--emit-md")
    # validate
    run("python","tools/status/validate_status_update.py", json_path)
    # auto-discover capabilities
    run("python","tools/status/capability_autodiscovery.py")
    # harvest questions
    run("python","tools/docs/harvest_open_questions.py")
    # render nicer MD
    run("python","tools/status/render_md.py", json_path, f"{prefix}-{today}.tables.md")
    print(f"OK -> {json_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
