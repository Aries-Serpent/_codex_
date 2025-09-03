#!/usr/bin/env python3
"""Pre-commit hook to block large generated files in .codex directory.

Refuses to commit any file under .codex/ exceeding 200 KB. Intended to
prevent accidentally committing huge markdown or database files.
"""
import os
import sys

MAX_SIZE = 200_000  # 200 KB threshold

bad = []
for path in sys.argv[1:]:
    if path.startswith(".codex/") and os.path.isfile(path):
        size = os.path.getsize(path)
        if size > MAX_SIZE:
            bad.append((path, size))

if bad:
    print("Refusing to commit large generated files in .codex/:")
    for p, sz in bad:
        print(f" - {p} ({sz} bytes > {MAX_SIZE})")
    sys.exit(1)

sys.exit(0)
