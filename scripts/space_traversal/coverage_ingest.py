#!/usr/bin/env python
"""
Coverage XML Ingestion (P4)

Reads coverage.xml (Cobertura or lcov-like parsed into coverage.xml) and produces
coverage_stats.json:
- For each file: lines_covered, lines_total
- Aggregate mapping from capability evidence to coverage percent if file matches
- Intended to refine tests component (use max(existing_tests_ratio, coverage_percent))

Environment:
  COVERAGE_XML_PATH=coverage.xml (default)
"""
from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

COVERAGE_XML = Path(os.getenv("COVERAGE_XML_PATH", "coverage.xml"))
OUT = Path("audit_artifacts/coverage_map.json")
RAW = Path("audit_artifacts/capabilities_raw.json")


def parse_coverage(root: Path):
    if not root.exists():
        return {}
    try:
        tree = ET.parse(str(root))
    except Exception as e:
        print(f"[ERR] Failed to parse coverage XML: {e}", file=sys.stderr)
        return {}

    data = {}
    # Cobertura style: <class filename="..."><lines>...</lines>
    for cls in tree.findall(".//class"):
        fname = cls.attrib.get("filename")
        if not fname:
            continue
        lines = cls.findall(".//line")
        total = 0
        covered = 0
        for ln in lines:
            total += 1
            if ln.attrib.get("hits", "0") != "0":
                covered += 1
        if total > 0:
            data[fname] = {"covered": covered, "total": total, "percent": covered / total}
    return data


def map_to_capabilities(cov_map, capabilities):
    result = []
    for cap in capabilities:
        ev = cap.get("evidence_files", [])
        matched = [cov_map[f] for f in ev if f in cov_map]
        if matched:
            covered = sum(m["covered"] for m in matched)
            total = sum(m["total"] for m in matched)
            percent = covered / total if total else 0.0
        else:
            covered = total = 0
            percent = 0.0
        result.append({"id": cap["id"], "coverage_percent": round(percent, 4)})
    return result


def main():
    if not RAW.exists():
        print("[WARN] capabilities_raw.json absent; run earlier stages.", file=sys.stderr)
        return 2

    caps = json.loads(RAW.read_text())["capabilities"]
    cov_map = parse_coverage(COVERAGE_XML)
    mapping = map_to_capabilities(cov_map, caps)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"capabilities": mapping}, indent=2), encoding="utf-8")
    print(f"[INFO] Coverage stats written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
