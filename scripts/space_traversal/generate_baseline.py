#!/usr/bin/env python3
"""
Generate baseline file from decoded Phase-A snapshot input.
"""
from __future__ import annotations
import argparse
import base64
import gzip
import json
import os
import sys

DEFAULT_MAX_BYTES = 200 * 1024 * 1024

def decode_b64_gz_bytes(b64_bytes: bytes) -> bytes:
    decoded = base64.b64decode(b64_bytes)
    return gzip.decompress(decoded)

def load_from_local(path: str, max_bytes: int):
    with open(path, "rb") as fh:
        b64 = fh.read()
    if len(b64) > max_bytes:
        raise RuntimeError("input exceeds max_bytes")
    decoded_bytes = decode_b64_gz_bytes(b64)
    return json.loads(decoded_bytes)

def write_baseline(baseline_path: str, data):
    d = os.path.dirname(baseline_path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

def main(argv=None):
    p = argparse.ArgumentParser(description="Generate baseline from base64+gz Phase-A snapshot")
    p.add_argument("--input", help="local b64+gz path", required=True)
    p.add_argument("--baseline-path", help="output baseline path (file)", required=True)
    p.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = p.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2

    try:
        decoded = load_from_local(args.input, args.max_bytes)
    except Exception as exc:
        print(f"Decode error: {exc}", file=sys.stderr)
        return 3

    if isinstance(decoded, dict) and "capabilities_scored" in decoded:
        baseline = decoded["capabilities_scored"]
    else:
        baseline = decoded

    try:
        write_baseline(args.baseline_path, baseline)
    except Exception as exc:
        print(f"Write baseline error: {exc}", file=sys.stderr)
        return 4

    print(f"Wrote baseline to: {args.baseline_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
