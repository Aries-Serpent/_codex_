#!/usr/bin/env python3
"""
Validate docs/capabilities files for required structure.
"""
import json
from pathlib import Path
import re
import os

ROOT = Path(os.environ.get("CODEX_ROOT", Path(__file__).resolve().parents[3]))
CAPS_DIR = ROOT / "docs" / "capabilities"

# Required elements for a capability doc
REQUIRED_ELEMENTS = [
    "capability",  # Capability name/header
    "scope",  # Scope section
    "evidence",  # Evidence references
]

OPTIONAL_ELEMENTS = ["tests", "detectors", "scoring", "metrics", "examples"]

validation_results = []

if not CAPS_DIR.exists():
    print(f"ERROR: {CAPS_DIR} does not exist")
    exit(1)

cap_files = sorted(CAPS_DIR.glob("*.md"))
print(f"Validating {len(cap_files)} capability files...")

for cap_file in cap_files:
    result = {
        "filename": cap_file.name,
        "exists": True,
        "checks": {},
        "missing_items": [],
        "warnings": [],
    }

    try:
        content = cap_file.read_text(encoding="utf-8")
        content_lower = content.lower()

        # Check for required elements
        for elem in REQUIRED_ELEMENTS:
            present = elem in content_lower
            result["checks"][elem] = present
            if not present:
                result["missing_items"].append(elem)

        # Check for optional but recommended elements
        for elem in OPTIONAL_ELEMENTS:
            if elem in content_lower:
                result["checks"][elem] = True

        # Check file size (should have substantial content)
        if len(content) < 200:
            result["warnings"].append("File is very small (< 200 chars)")

        # Check for headers (markdown structure)
        if not re.search(r"^#+\s+", content, re.MULTILINE):
            result["warnings"].append("No markdown headers found")

    except Exception as e:
        result["checks"]["read_error"] = str(e)
        result["missing_items"].append(f"Error reading file: {e}")

    validation_results.append(result)

# Generate summary
total_files = len(validation_results)
files_with_issues = sum(1 for r in validation_results if r["missing_items"] or r["warnings"])
completeness = ((total_files - files_with_issues) / total_files * 100) if total_files > 0 else 0

output = {
    "validation_date": "2025-12-09",
    "total_files": total_files,
    "files_with_issues": files_with_issues,
    "completeness_percent": round(completeness, 2),
    "results": validation_results,
    "summary": {
        "total": total_files,
        "complete": total_files - files_with_issues,
        "incomplete": files_with_issues,
        "meets_threshold": completeness >= 90.0,
    },
}

output_path = ROOT / ".github/audit_artifacts_output/docs_capabilities_validation.json"
output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

print(f"\nValidation Summary:")
print(f"  Total files: {total_files}")
print(f"  Complete: {total_files - files_with_issues}")
print(f"  Incomplete: {files_with_issues}")
print(f"  Completeness: {completeness:.1f}%")
print(f"  Meets 90% threshold: {completeness >= 90.0}")
print(f"\nWrote validation results to {output_path}")

print(json.dumps(output, indent=2))
