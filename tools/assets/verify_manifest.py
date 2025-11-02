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
    ok = True
    for entry in manifest.get("items", []):
        path = Path(entry.get("path", ""))
        expected = entry.get("sha256")
        if not path.exists():
            print(f"MISSING: {path}")
            ok = False
            continue
        actual = sha256(path)
        if actual != expected:
            print(f"MISMATCH: {path} expected={expected} actual={actual}")
            ok = False
    return 0 if ok else 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
