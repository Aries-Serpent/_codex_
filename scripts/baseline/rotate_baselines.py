#!/usr/bin/env python3
import shutil
import sys
from pathlib import Path


def main(retain: int = 5):
    # Validate positive integer
    if retain <= 0:
        print(f"[ERR] retain must be positive integer, got {retain}", file=sys.stderr)
        sys.exit(1)

    base = Path("audit_artifacts/baselines")
    if not base.exists():
        print("[INFO] no baselines to rotate")
        return

    entries = sorted([p for p in base.iterdir() if p.is_dir()])
    if len(entries) <= retain:
        print(f"[INFO] within retain window ({len(entries)}/{retain})")
        return

    to_delete = entries[:-retain]
    for d in to_delete:
        try:
            shutil.rmtree(d)
            print(f"[INFO] removed baseline: {d}")
        except OSError as e:
            print(f"[WARN] failed to remove {d}: {e}", file=sys.stderr)


if __name__ == "__main__":
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except ValueError:
        print(f"[ERR] invalid retain argument: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    main(n)
