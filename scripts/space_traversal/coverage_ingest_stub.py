#!/usr/bin/env python3
"""
Coverage Ingest Stub

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/space_traversal/coverage_ingest_stub.py [options]
    
    Examples:
    $ python scripts/space_traversal/coverage_ingest_stub.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

# Lightweight coverage ingest stub for tests.

import argparse
import json
import os
import sys
from defusedxml import ElementTree as ET
from pathlib import Path
from typing import Any

__all__ = ["parse_cobertura", "parse_simple_coverage", "write_stub_report", "main"]


def parse_cobertura(xml_path: str) -> dict[str, Any]:
    """
    Parse Cobertura XML and return line-level coverage details per file.
    """
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


def parse_simple_coverage(xml_path: Path) -> dict[str, Any]:
    """
    Parse Cobertura XML and return summary coverage stats (covered/total) per file.
    """
    tree = ET.parse(xml_path)
    data: dict[str, Any] = {}
    for cls in tree.findall(".//class"):
        filename = cls.attrib.get("filename", "")
        lines = cls.findall(".//line")
        covered = sum(1 for line in lines if line.attrib.get("hits", "0") != "0")
        total = len(lines)
        data[filename] = {"covered": covered, "total": total}
    return data


def write_stub_report(xml_path: Path, destination: Path) -> Path:
    """
    Write a stub coverage report from cobertura to destination JSON file.
    """
    coverage = parse_simple_coverage(xml_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"coverage": coverage}, indent=2), encoding="utf-8")
    return destination


def main(argv=None):
    """
    CLI entrypoint for converting cobertura XML to JSON coverage mapping.
    Supports both detailed line coverage (parse_cobertura) and stub report.
    """
    p = argparse.ArgumentParser(description="Coverage ingest stub")
    p.add_argument("--input", required=True, help="coverage XML input")
    p.add_argument("--out", required=True, help="JSON output path")
    p.add_argument("--summary", action="store_true", help="Output summary (covered/total) per file")
    args = p.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 2

    input_path = Path(args.input)
    out_path = Path(args.out)
    out_dir = out_path.parent
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    if args.summary:
        # Write stub report (summary)
        write_stub_report(input_path, out_path)
    else:
        # Write full verbose coverage
        cov = parse_cobertura(args.input)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(cov, fh, indent=2)

    print(f"Wrote coverage mapping to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
