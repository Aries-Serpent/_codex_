#!/usr/bin/env python3
# .github/scripts/ci_parse_coverage.py
# Read coverage.xml and print percentage as e.g. 92.34
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("USAGE: ci_parse_coverage.py <coverage-xml-path>", file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"ERROR: coverage xml not found at {p}", file=sys.stderr)
        sys.exit(3)
    try:
        tree = ET.parse(p)
        root = tree.getroot()
        # coverage.py xml format has root <coverage> with attribute 'line-rate'
        line_rate = root.attrib.get("line-rate")
        if line_rate:
            percent = float(line_rate) * 100.0
            print(f"{percent:.2f}")
            return
        # fallback: try to compute from counters if present
        # search for counters elements typical in other coverage tools
        totals = root.findall(".//<output too long - dropped 28 lines from the middle>")
        # try to find attributes lines-covered and lines-valid in any top-level element
        for elem in root.iter():
            lc = elem.attrib.get("lines-covered")
            lv = elem.attrib.get("lines-valid")
            if lc and lv:
                percent = (float(lc) / float(lv)) * 100.0
                print(f"{percent:.2f}")
                return
        # final fallback: try counters attr 'covered' and 'total' on <coverage> or <metrics>
        for elem in root.iter():
            covered = elem.attrib.get("covered")
            total = elem.attrib.get("total")
            if covered and total:
                percent = (float(covered) / float(total)) * 100.0
                print(f"{percent:.2f}")
                return
        print("ERROR: could not determine coverage percent from xml", file=sys.stderr)
        sys.exit(4)
    except ET.ParseError as e:
        print(f"ERROR: failed to parse coverage xml: {e}", file=sys.stderr)
        sys.exit(5)

if __name__ == "__main__":
    main()
