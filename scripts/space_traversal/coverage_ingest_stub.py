#!/usr/bin/env python3
"""
Lightweight coverage ingest stub for tests.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

def parse_cobertura(xml_path: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    coverage = {}
    for cls in root.findall(".//class"):
        filename = cls.get("filename")
        lines = []
        for line in cls.findall(".//line"):
            num = int(line.get("number"))
            hits = int(line.get("hits", "0"))
            lines.append({"number": num, "hits": hits})
        coverage[filename] = {"lines": lines}
    return coverage

def main(argv=None):
    p = argparse.ArgumentParser(description="Coverage ingest stub")
    p.add_argument("--input", required=True, help="coverage XML input")
    p.add_argument("--out", required=True, help="json output path")
    args = p.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 2
    cov = parse_cobertura(args.input)
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(cov, fh, indent=2)
    print(f"Wrote coverage mapping to: {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
