#!/usr/bin/env python3
"""
Coverage Ingest

Purpose:
    Main execution script

Usage:
    python scripts/space_traversal/coverage_ingest.py [options]

    Examples:
    $ python scripts/space_traversal/coverage_ingest.py --help

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


import json
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from defusedxml import ElementTree as ET
except ImportError:  # pragma: no cover - CI may not have defusedxml
    import warnings
    warnings.warn(
        "defusedxml not installed; falling back to stdlib XML parser. "
        "Only parse trusted XML (e.g. CI coverage reports).",
        stacklevel=2,
    )
    from xml.etree import (
        ElementTree as ET,  # nosec B314 — coverage XML is CI-generated, not untrusted input
    )

ROOT = Path(__file__).resolve().parents[2]

# Shared constant from audit_runner.py for consistency
# Max bytes to read from files to avoid memory issues
MAX_READ_BYTES = 200_000


def parse_coverage_xml_to_map(
    xml_path: Path, root: Optional[Path] = None
) -> dict[str, dict[str, Any]]:
    """
    Parse coverage XML file to map format.

    Supports Cobertura and coverage.py XML formats.
    Returns dict mapping file paths to coverage data:
    {
        "path/to/file.py": {
            "percent": 0.85,
            "covered_lines": [1, 2, 3, ...],
            "total_lines": 100
        }
    }

    Args:
        xml_path: Path to coverage XML file
        root: Repository root path (defaults to ROOT)

    Returns:
        Coverage map dictionary
    """
    if root is None:
        root = ROOT

    if not xml_path.exists():
        return {}

    try:
        tree = ET.parse(xml_path)  # nosec B314 — CI-generated coverage XML, not untrusted input
    except ET.ParseError as e:
        print(f"Failed parsing coverage xml: {e}", file=sys.stderr)
        return {}

    xml_root = tree.getroot()
    cov = {}

    # Try Cobertura format first (class elements)
    for cls in xml_root.findall(".//class"):
        filename = cls.get("filename")
        lines = []
        for ln in cls.findall(".//line"):
            num = ln.get("number")
            hits = ln.get("hits")
            if num is not None and hits is not None and int(hits) > 0:
                lines.append(int(num))
        if filename:
            cov[filename] = {"covered_lines": sorted(set(lines))}

    # Try coverage.py format (package/classes structure)
    if not cov:
        for pkg in xml_root.findall(".//package"):
            for cls in pkg.findall("classes/class"):
                filename = cls.get("filename")
                if not filename:
                    # Sometimes the name attribute contains the path
                    filename = cls.get("name", "").replace(".", "/") + ".py"
                lines = []
                for ln in cls.findall("lines/line"):
                    num = ln.get("number")
                    hits = ln.get("hits")
                    if num is not None and hits is not None and int(hits) > 0:
                        lines.append(int(num))
                if filename:
                    cov[filename] = {"covered_lines": sorted(set(lines))}

    # Calculate percentages and total lines
    for f, data in cov.items():
        try:
            full_path = root / f
            if full_path.exists() and full_path.stat().st_size < MAX_READ_BYTES:
                with open(full_path, encoding="utf-8", errors="ignore") as file:
                    total_lines = sum(1 for _ in file)
                data["total_lines"] = total_lines
                covered_count = len(data["covered_lines"])
                data["percent"] = round(covered_count / max(1, total_lines), 6)
            else:
                # File too large or missing, estimate from covered lines
                covered_count = len(data["covered_lines"])
                max_line = max(data["covered_lines"]) if data["covered_lines"] else 1
                data["total_lines"] = max_line
                data["percent"] = round(covered_count / max(1, max_line), 6)
        except Exception:
            data["total_lines"] = len(data.get("covered_lines", []))
            data["percent"] = 0.0

    # Return a deterministically ordered mapping for stable downstream manifests
    return {path: cov[path] for path in sorted(cov)}


def discover_and_parse_coverage(
    cfg: dict[str, Any], artifacts_dir: Path
) -> Optional[dict[str, dict[str, Any]]]:
    """
    Discover and parse coverage XML files based on configuration.

    Auto-discovers coverage.xml or uses patterns from cfg["scoring"]["coverage"]["xml_patterns"].
    Only runs when coverage is enabled in config.

    Args:
        cfg: Workflow configuration dictionary
        artifacts_dir: Directory to write coverage_map.json

    Returns:
        Coverage map dictionary, or None if coverage is disabled/not found
    """
    # Check if coverage is enabled
    scoring = cfg.get("scoring", {})
    coverage_cfg = scoring.get("coverage", {})

    if not coverage_cfg or not coverage_cfg.get("enabled", False):
        return None

    # Get patterns from config, default to common locations
    xml_patterns = coverage_cfg.get(
        "xml_patterns", ["coverage.xml", ".coverage.xml", "**/coverage.xml", "htmlcov/coverage.xml"]
    )

    # Find coverage XML files
    xml_files: list[Path] = []
    for pattern in xml_patterns:
        pattern_path = Path(pattern)
        if pattern_path.is_absolute():
            if pattern_path.exists():
                xml_files.append(pattern_path)
        else:
            # Search from ROOT
            if "**" in pattern:
                xml_files.extend(ROOT.glob(pattern))
            else:
                candidate = ROOT / pattern
                if candidate.exists():
                    xml_files.append(candidate)

    if not xml_files:
        print("No coverage XML files found", file=sys.stderr)
        return None

    # Use the first (most recent) coverage file found, breaking ties deterministically
    xml_files = sorted(xml_files, key=lambda p: (p.stat().st_mtime, p.as_posix()), reverse=True)
    xml_path = xml_files[0]
    print(f"Parsing coverage from: {xml_path}")

    # Parse and save
    cov_map = parse_coverage_xml_to_map(xml_path, ROOT)

    if cov_map:
        out_path = artifacts_dir / "coverage_map.json"
        write_coverage_map(out_path, cov_map)
        print(f"Wrote coverage map to {out_path}")

    return cov_map


def parse_coverage_xml(xml_path: Path):
    """Legacy function for backward compatibility."""
    return parse_coverage_xml_to_map(xml_path, ROOT)


def write_coverage_map(out_path: Path, cov_map: dict):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cov_map, indent=2, sort_keys=True), encoding="utf-8")


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
