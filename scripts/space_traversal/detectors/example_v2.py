"""
Example V2

Purpose:
    [To be documented - Example V2]

Usage:
    python scripts/space_traversal/detectors/example_v2.py [options]
    
    Examples:
    $ python scripts/space_traversal/detectors/example_v2.py --help

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


def detect_v2(file_index: dict) -> dict:
    """
    Example detect_v2 demonstrating evidence ranges & confidence.
    Keep this side-effect free (only inspect file_index).
    """
    files = [f["path"] for f in file_index.get("files", []) if f.get("path", "").endswith(".py")]
    evidence = []
    for p in files:
        if "serve" in p.lower() or "checkpoint" in p.lower():
            evidence.append(
                {
                    "path": p,
                    "sha": None,
                    "ranges": [{"start_line": 1, "end_line": 40}],
                    "confidence": 0.9,
                    "excerpt": None,
                }
            )
    return {
        "id": "example-evidence-v2",
        "evidence": evidence,
        "found_patterns": ["serve", "checkpoint"],
        "required_patterns": ["serve"],
        "meta": {"detector_version": "v2", "source": "example_v2"},
    }
