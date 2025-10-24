#!/usr/bin/env python3
"""Validate 3.5% coverage gate enforcement across all test contexts.

This script ensures --cov-fail-under=3.5 is present in:
- README.md
- docs/governance/CONTRIBUTING.md
- config/pytest.ini
- config/Makefile
- noxfile.py
- .github/workflows/*.yml
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

COVERAGE_PATTERN = r"--cov-fail-under=3\.5"


def check_file(filepath: Path, pattern: str = COVERAGE_PATTERN) -> Tuple[bool, str]:
    """Check if file contains coverage gate pattern.

    Args:
        filepath: Path to file to check
        pattern: Regex pattern to search for (default: 3.5% coverage)

    Returns:
        (found, content_snippet) tuple
    """

    try:
        content = filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False, f"File not found: {filepath.as_posix()}"
    except OSError as exc:
        return False, f"Error reading {filepath.as_posix()}: {exc}"

    matches = list(re.finditer(pattern, content))
    if not matches:
        return False, ""
    snippet = matches[0].group(0)
    return True, snippet


def _gather_workflow_files(workflow_dir: Path) -> List[Path]:
    if not workflow_dir.exists():
        return []
    return sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))


def validate_coverage_gates() -> int:
    """Validate coverage gates in all required files.

    Returns:
        0 if all checks pass, 1 if any fail
    """

    files_to_check: List[Path] = [
        Path("README.md"),
        Path("docs/governance/CONTRIBUTING.md"),
        Path("config/pytest.ini"),
        Path("config/Makefile"),
        Path("noxfile.py"),
    ]

    workflow_dir = Path(".github/workflows")
    files_to_check.extend(_gather_workflow_files(workflow_dir))

    results: List[Dict[str, object]] = []
    failures: List[Path] = []

    for filepath in files_to_check:
        found, snippet = check_file(filepath)
        results.append(
            {
                "file": filepath.as_posix(),
                "found": found,
                "snippet": snippet,
            }
        )

        if found:
            print(f"✅ {filepath.as_posix()}: Coverage gate found ({snippet})")
        else:
            print(f"❌ {filepath.as_posix()}: Missing 3.5% coverage gate")
            failures.append(filepath)

    print("\n" + "=" * 60)
    print("Coverage Gate Validation Summary")
    print("=" * 60)
    print(f"Files checked: {len(results)}")
    print(f"✅ Passed: {len(results) - len(failures)}")
    print(f"❌ Failed: {len(failures)}")

    if failures:
        print("\nFailed files:")
        for missing in failures:
            print(f"  - {missing.as_posix()}")
        return 1

    print("\n✅ All coverage gates validated!")
    return 0


if __name__ == "__main__":
    sys.exit(validate_coverage_gates())
