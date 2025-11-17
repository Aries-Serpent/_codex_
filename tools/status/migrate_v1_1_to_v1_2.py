#!/usr/bin/env python3
"""
Offline, idempotent migration from v1.1 -> v1.2.
Adds/adjusts metadata.template_version and preserves all content.
"""
import argparse
import json
import pathlib
import sys


def migrate(obj: dict) -> dict:
    out = json.loads(json.dumps(obj))  # deep copy
    md = out.setdefault("metadata", {})
    md["template_version"] = "v1.2"
    # ensure tokenization sub-doc exists (additive; safe defaults)
    tok = out.setdefault("tokenization", {})
    tok.setdefault("summary", "")
    tok.setdefault("settings", "")
    tok.setdefault("caching_parity", "")
    tok.setdefault("offline_considerations", "")
    tok.setdefault("recommendations", "")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_json", type=pathlib.Path)
    ap.add_argument("output_json", type=pathlib.Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    src = json.loads(args.input_json.read_text(encoding="utf-8"))
    migrated = migrate(src)
    if args.dry_run:
        print(json.dumps(migrated, indent=2))
        return 0
    args.output_json.write_text(json.dumps(migrated, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
