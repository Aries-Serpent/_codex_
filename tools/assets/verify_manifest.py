"""Verify asset checksums listed in ``assets/manifest.json``."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

MANIFEST_PATH = Path("assets/manifest.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not MANIFEST_PATH.exists():
        print(f"Manifest not found: {MANIFEST_PATH}")
        return 1
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest.get("files", {})
    if not files:
        print("ERROR: Manifest contains no files to verify")
        return 1
    ok = True
    for path_str, expected in files.items():
        path = Path(path_str)
        if not path.exists():
            print(f"MISSING: {path}")
            ok = False
            continue
        try:
            actual = sha256(path)
        except Exception as e:
            print(f"ERROR reading {path}: {e}")
            ok = False
            continue
        if actual != expected:
            print(f"MISMATCH: {path} expected={expected} actual={actual}")
            ok = False
    return 0 if ok else 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
