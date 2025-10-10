"""Dynamic detector for testing infrastructure capability.

Returns test evidence across the repository including pytest configs,
test files, fixtures, and test utilities.
"""
from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect testing infrastructure capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result
    """
    files = file_index.get("files", [])

    # Evidence collection
    test_files = []
    pytest_configs = []
    fixtures = []

    for f in files:
        path = f["path"]

        # Test files
        if path.startswith("tests/") and path.endswith(".py"):
            test_files.append(path)

        # Pytest configurations
        if any(name in path for name in ["pytest.ini", "pyproject.toml", "conftest.py"]):
            pytest_configs.append(path)

        # Test utilities and fixtures
        if "fixture" in path.lower() or "conftest" in path.lower():
            fixtures.append(path)

    # Pattern detection
    found_patterns = []
    required_patterns = ["pytest", "test_", "fixture", "marker"]

    evidence_files = sorted(set(test_files + pytest_configs + fixtures))

    # Simple pattern matching based on evidence
    if test_files:
        found_patterns.append("test_")
    if pytest_configs:
        found_patterns.append("pytest")
    if fixtures:
        found_patterns.append("fixture")
    if any("marker" in f for f in evidence_files):
        found_patterns.append("marker")

    return {
        "id": "testing-infrastructure",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "meta": {
            "test_count": len(test_files),
            "config_count": len(pytest_configs),
            "fixture_count": len(fixtures),
        },
    }
