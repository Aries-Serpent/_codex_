from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


def parse_simple_coverage(xml_path: Path) -> dict[str, Any]:
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
    coverage = parse_simple_coverage(xml_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"coverage": coverage}, indent=2), encoding="utf-8")
    return destination
