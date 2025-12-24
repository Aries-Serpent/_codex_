"""
Dynamic Detector: Status Reporting (v1.4.0)

Identifies status reporting and audit capabilities including:
- Status update modules
- Audit reporting scripts
- Progress tracking systems

Codex-specific status reporting infrastructure.
"""

from __future__ import annotations



def detect(file_index: dict) -> dict:
    """
    Detect status reporting capability.

    Args:
        file_index: Context index with file metadata

    Returns:
        Detection result with id, evidence, patterns, and metadata
    """
    files = file_index.get("files", [])
    evidence: set[str] = set()
    found: set[str] = set()
    required = ["status", "report", "audit"]

    # Patterns to detect status reporting
    status_patterns = ["status", "codex_status"]
    report_patterns = ["report", "audit", "summary"]

    for meta in files:
        path = meta["path"]
        lower_path = path.lower()

        # Check for status modules
        if any(pattern in lower_path for pattern in status_patterns):
            evidence.add(path)
            found.add("status")

        # Check for reporting infrastructure
        if any(pattern in lower_path for pattern in report_patterns):
            evidence.add(path)
            found.add("report")

        # Specific file patterns
        if "audit" in lower_path:
            evidence.add(path)
            found.add("audit")

        # Check for status update scripts
        if "codex_status" in lower_path or "_status" in lower_path:
            evidence.add(path)
            found.add("status")

    return {
        "id": "status-reporting",
        "evidence_files": sorted(evidence),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "meta": {"layer": "operations", "priority": "medium", "category": "monitoring"},
    }
