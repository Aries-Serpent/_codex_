#!/usr/bin/env python3
"""
Generate Pytest Config

Purpose:
    Test script for generate_pyconfig

Usage:
    python scripts/generate_pytest_config.py [options]

    Examples:
    $ python scripts/generate_pytest_config.py --help

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


import configparser
import re
import sys
from pathlib import Path

# Patterns for marker discovery
DECORATOR_PATTERN = re.compile(r'@pytest\.mark\.([a-zA-Z0-9_]+)')
MARKER_USAGE_PATTERN = re.compile(r'pytest\.mark\.([a-zA-Z0-9_]+)')
PYTESTMARK_PATTERN = re.compile(r'pytestmark\s*=\s*pytest\.mark\.([a-zA-Z0-9_]+)')

# Built-in pytest markers that should not be registered
BUILTIN_MARKERS = {
    'skip', 'skipif', 'xfail', 'parametrize', 'usefixtures',
    'filterwarnings', 'tryfirst', 'trylast', 'timeout'
}

# Known markers with descriptions
KNOWN_MARKERS = {
    "chaos": "Chaos engineering and fault injection tests",
    "slow": "Long-running tests",
    "integration": "Cross-component integration tests",
    "unit": "Unit test marker",
    "smoke": "Quick validation tests",
    "determinism": "Deterministic behavior tests",
    "gpu": "GPU specific tests",
    "cpu": "CPU specific tests",
    "eval": "Evaluation loop tests",
    "training": "Training pipeline tests",
    "regression": "Regression (bug fix) tests",
    "data": "Data layer tests",
    "recorded": "Integration tests that use recorded fixtures",
    "live": "Integration tests that call live providers (gated)",
    "not_live": "Tests that must run without live provider access",
    "timeout": "Tests with explicit timeout",
    "ml": "ML / tensor dependent",
    "ml_comprehensive": "Comprehensive ML tests for callback systems",
    "perf": "Performance snapshot tests",
    "asyncio": "Asynchronous test execution",
    "cpu_only": "Tests that require CPU-only execution",
    "performance": "Performance and benchmark tests",
    "security": "Security-focused tests",
}


def find_markers_in_file(filepath: Path) -> set[str]:
    """Find all pytest markers used in a Python file."""
    markers = set()
    try:
        content = filepath.read_text(errors='ignore')

        # Find decorator-style markers
        markers.update(DECORATOR_PATTERN.findall(content))

        # Find programmatic marker usage
        markers.update(MARKER_USAGE_PATTERN.findall(content))

        # Find pytestmark assignments
        markers.update(PYTESTMARK_PATTERN.findall(content))

    except Exception as e:
        print(f"⚠ Warning: Could not process {filepath}: {e}", file=sys.stderr)

    return markers


def scan_repository(root: Path) -> set[str]:
    """Scan repository for markers."""
    markers = set()

    # Scan all test files
    for pattern in ["test_*.py", "*_test.py"]:
        for py_file in root.rglob(pattern):
            # Skip virtual environments and build directories
            if any(part in py_file.parts for part in ['.venv', 'venv', 'build', 'dist', '__pycache__', '.tox']):
                continue

            file_markers = find_markers_in_file(py_file)
            if file_markers:
                markers.update(file_markers)

    # Filter out built-in pytest markers
    markers = markers - BUILTIN_MARKERS

    return markers


def read_existing_markers(pytest_ini_path: Path) -> dict[str, str]:
    """Read existing markers from pytest.ini."""
    if not pytest_ini_path.exists():
        return {}

    config = configparser.ConfigParser()
    config.read(pytest_ini_path)

    existing = {}
    if config.has_section('pytest') and config.has_option('pytest', 'markers'):
        markers_text = config.get('pytest', 'markers')
        for line in markers_text.split('\n'):
            line = line.strip()
            if ':' in line:
                marker_name, description = line.split(':', 1)
                existing[marker_name.strip()] = description.strip()

    return existing


def update_pytest_ini(pytest_ini_path: Path, discovered_markers: set[str]) -> bool:
    """Update pytest.ini with discovered markers, preserving existing content."""
    if not pytest_ini_path.exists():
        print(f"⚠ Error: {pytest_ini_path} does not exist")
        return False

    # Read existing markers
    existing_markers = read_existing_markers(pytest_ini_path)

    # Find new markers that need to be added
    new_markers = discovered_markers - set(existing_markers.keys())

    if not new_markers:
        print("✓ pytest.ini: All markers already registered")
        return False

    # Read the current content
    content = pytest_ini_path.read_text()
    lines = content.split('\n')

    # Find the markers section
    markers_start = -1
    markers_end = -1
    in_markers = False

    for i, line in enumerate(lines):
        if line.strip().startswith('markers ='):
            markers_start = i
            in_markers = True
        elif in_markers and line and not line[0].isspace():
            markers_end = i
            break
        elif in_markers and i == len(lines) - 1:
            markers_end = i + 1

    if markers_start == -1:
        print("⚠ Error: Could not find 'markers =' section in pytest.ini")
        return False

    # Insert new markers before the last marker line
    insert_pos = markers_end if markers_end > 0 else len(lines)

    new_marker_lines = []
    for marker in sorted(new_markers):
        description = KNOWN_MARKERS.get(marker, f"Auto-discovered marker: {marker}")
        new_marker_lines.append(f"    {marker}: {description}")

    # Insert the new lines
    lines[insert_pos:insert_pos] = new_marker_lines

    # Write back
    pytest_ini_path.write_text('\n'.join(lines))
    if not lines[-1].endswith('\n'):
        # Ensure file ends with newline
        with open(pytest_ini_path, 'a') as f:
            f.write('\n')

    print(f"✓ pytest.ini: Added {len(new_markers)} new marker(s):")
    for marker in sorted(new_markers):
        print(f"  - {marker}")

    return True


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent

    # Parse arguments
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])

    pytest_ini = repo_root / "pytest.ini"

    if not pytest_ini.exists():
        print(f"⚠ Error: pytest.ini not found at {pytest_ini}")
        return 1

    print("Scanning repository for pytest markers...")
    discovered_markers = scan_repository(repo_root)

    print(f"Found {len(discovered_markers)} unique marker(s) in use")

    if discovered_markers:
        changed = update_pytest_ini(pytest_ini, discovered_markers)
        return 0 if not changed else 1
    else:
        print("No markers found")
        return 0


if __name__ == "__main__":
    sys.exit(main())
