#!/usr/bin/env python3
"""
.github/scripts/ci_parse_coverage.py
Purpose: Parse a coverage XML and print a numeric coverage percentage (0.00 - 100.00).
This parser is tolerant of several coverage XML variants:
 - coverage.py style: <coverage line-rate="0.92345" ...>
 - some variants use percent (e.g., line-rate="92.345" or percentage="92.34")
 - variants that provide lines-covered / lines-valid attributes
 - variants that use covered / total attributes

Special handling for "70 - 100" variant:
 If a numeric root attribute is >= 70 we assume it's already a percentage value (70..100).
 If it's <= 1.0 we assume it's a 0..1 fraction and multiply by 100.
 For intermediate values between 1 and 70 (rare), the script will attempt sensible interpretation:
  - if value >= 70 treat as percentage
  - if value <= 1 multiply by 100
  - otherwise treat value as percentage (conservative).

Usage:
  python .github/scripts/ci_parse_coverage.py <path/to/coverage.xml>

Outputs:
  Writes "NN.NN" to stdout on success (two-decimal percent).
  On failure prints an ERROR message to stderr and exits with non-zero.
"""
from __future__ import annotations

import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _as_float(s: str) -> float | None:
    try:
        s = s.strip()
        if s.endswith("%"):
            s = s[:-1]
        return float(s)
    except Exception:
        return None


def interpret_value_as_percent(val: float) -> float:
    """
    Interpret a numeric value from XML as a percentage 0..100.
    Rules:
      - if val <= 1.0 -> it's a fraction -> val * 100
      - if val >= 70.0 -> already percent -> val
      - otherwise -> treat as percent (conservative)
    """
    if val <= 1.0:
        return val * 100.0
    if val >= 70.0:
        return val
    # Fallback: treat as percentage (e.g., 92 -> 92)
    return val


def parse_coverage_xml(path: Path) -> float:
    if not path.exists():
        raise FileNotFoundError(f"coverage xml not found at {path}")
    tree = ET.parse(path)
    root = tree.getroot()

    # 1) Common: root attribute 'line-rate' (coverage.py)
    lr = root.attrib.get("line-rate") or root.attrib.get("line_rate") or root.attrib.get("lineRate")
    if lr:
        v = _as_float(lr)
        if v is None:
            raise ValueError(f"cannot parse line-rate value '{lr}'")
        percent = interpret_value_as_percent(v)
        return percent

    # 2) Some variants provide 'percentage' or 'percent' attribute on root or <coverage> node
    pct = root.attrib.get("percentage") or root.attrib.get("percent")
    if pct:
        v = _as_float(pct)
        if v is None:
            raise ValueError(f"cannot parse percentage value '{pct}'")
        return interpret_value_as_percent(v)

    # 3) Search elements for lines-covered / lines-valid (integer counts)
    for elem in root.iter():
        lc = elem.attrib.get("lines-covered") or elem.attrib.get("lines_covered")
        lv = (
            elem.attrib.get("lines-valid")
            or elem.attrib.get("lines_valid")
            or elem.attrib.get("lines")
        )
        if lc and lv:
            try:
                lc_f = float(lc)
                lv_f = float(lv)
                if lv_f == 0:
                    raise ZeroDivisionError("lines-valid is zero")
                return (lc_f / lv_f) * 100.0
            except Exception as e:
                raise ValueError(f"failed computing percent from lines-covered/lines-valid: {e}")

    # 4) Search for covered / total counters (some tools)
    for elem in root.iter():
        covered = elem.attrib.get("covered")
        total = elem.attrib.get("total")
        if covered and total:
            try:
                cov = float(covered)
                tot = float(total)
                if tot == 0:
                    raise ZeroDivisionError("total is zero")
                return (cov / tot) * 100.0
            except Exception as e:
                raise ValueError(f"failed computing percent from covered/total: {e}")

    # 5) Some report <metrics statements with attributes e.g. statements, coveredstatements etc.
    # Try to compute any ratio we can find
    for elem in root.iter():
        # try common patterns
        for a_num, a_den in (
            ("coveredstatements", "statements"),
            ("covered_lines", "lines"),
            ("covered_lines", "total_lines"),
        ):
            n = elem.attrib.get(a_num)
            d = elem.attrib.get(a_den)
            if n and d:
                try:
                    n_f = float(n)
                    d_f = float(d)
                    if d_f == 0:
                        continue
                    return (n_f / d_f) * 100.0
                except Exception:
                    continue

    raise ValueError("could not determine coverage percent from xml")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("USAGE: ci_parse_coverage.py <coverage-xml-path>", file=sys.stderr)
        return 2
    p = Path(argv[1])
    try:
        pct = parse_coverage_xml(p)
        # Clamp to 0..100 and format with two decimals
        if math.isfinite(pct):
            pct = max(0.0, min(100.0, pct))
            print(f"{pct:.2f}")
            return 0
        else:
            print("ERROR: parsed non-finite coverage value", file=sys.stderr)
            return 6
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    except ET.ParseError as e:
        print(f"ERROR: failed to parse coverage xml as XML: {e}", file=sys.stderr)
        return 4
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 5
    except Exception as e:
        print(f"ERROR: unexpected error: {e}", file=sys.stderr)
        return 8


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
