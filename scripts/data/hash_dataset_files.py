#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compute sha256 for dataset files and update manifest")
    ap.add_argument("--manifest", default="data/manifest.json")
    args = ap.parse_args(argv)

    mpath = Path(args.manifest)
    data = json.loads(mpath.read_text(encoding="utf-8"))
    updated = 0
    for entry in data.get("checksums", []):
        p = Path(entry["path"])
        if p.exists():
            entry["sha256"] = sha256(p)
            updated += 1
    mpath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[OK] Updated {updated} checksum entries in {mpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
