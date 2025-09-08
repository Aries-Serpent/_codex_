#!/usr/bin/env python3
"""Pre-commit hook to block large generated files in .codex directory.

Refuses to commit any file under .codex/ exceeding 200 KB. Intended to
prevent accidentally committing huge markdown or database files.
"""
import os
import sys

MAX_SIZE = 200_000  # 200 KB threshold


def main(argv: list[str]) -> int:
    bad = []
    for path in argv:
        if path.startswith(".codex/") and os.path.isfile(path):
            size = os.path.getsize(path)
            if size > MAX_SIZE:
                bad.append((path, size))

    if bad:
        print("Refusing to commit large generated files in .codex/:")
        for p, sz in bad:
            print(f" - {p} ({sz} bytes > {MAX_SIZE})")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
