#!/usr/bin/env python3
"""
Produce a stable manifest JSON for a given output directory.
"""
from __future__ import annotations
import argparse
import json
import os
import re

TIMESTAMP_RE = re.compile(r"_(?:20\d{6}_\d{6}|\d{8}_\d{6})")

def normalize_name(name: str) -> str:
    return TIMESTAMP_RE.sub("_TIMESTAMP", name)

def manifest_for_dir(dirpath: str):
    entries = []
    for root, _, files in os.walk(dirpath):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), dirpath)
            entries.append(normalize_name(rel))
    return entries

def main(argv=None):
    p = argparse.ArgumentParser(description="Produce stable manifest for directory")
    p.add_argument("--dir", required=True, help="directory to manifest")
    p.add_argument("--out", required=True, help="output json manifest")
    args = p.parse_args(argv)

    entries = manifest_for_dir(args.dir)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2)
    print(f"Wrote manifest to {args.out}")

if __name__ == "__main__":
    main()
