#!/usr/bin/env python3
"""
Coverage ingestion (Cobertura / coverage.py XML -> audit_artifacts/coverage_map.json)
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import sys

ROOT = Path(__file__).resolve().parents[2]

def parse_coverage_xml(xml_path: Path):
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        print(f"Failed parsing coverage xml: {e}", file=sys.stderr)
        sys.exit(2)
    root = tree.getroot()
    cov = {}
    for cls in root.findall(".//class"):
        filename = cls.get("filename")
        lines = []
        for ln in cls.findall(".//line"):
            num = ln.get("number")
            hits = ln.get("hits")
            if num is not None and hits is not None and int(hits) > 0:
                lines.append(int(num))
        if filename:
            cov[filename] = {"covered_lines": sorted(set(lines))}
    for f, data in cov.items():
        try:
            full_path = ROOT / f
            total_lines = sum(1 for _ in open(full_path, "r", encoding="utf-8", errors="ignore"))
            data["percent"] = len(data["covered_lines"]) / max(1, total_lines)
        except Exception:
            data["percent"] = 0.0
    return cov

def write_coverage_map(out_path: Path, cov_map: dict):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cov_map, indent=2), encoding="utf-8")

def main():
    if len(sys.argv) < 2:
        print("Usage: coverage_ingest.py <coverage_xml_path>", file=sys.stderr)
        sys.exit(2)
    xml_in = Path(sys.argv[1])
    if not xml_in.exists():
        print("Coverage xml not found", file=sys.stderr)
        sys.exit(2)
    cov_map = parse_coverage_xml(xml_in)
    out = Path.cwd() / "audit_artifacts" / "coverage_map.json"
    write_coverage_map(out, cov_map)
    print(f"Wrote coverage map to {out}")

if __name__ == "__main__":
    main()