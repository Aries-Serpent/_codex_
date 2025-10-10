import shutil
import subprocess
from pathlib import Path

import pytest

MYPY = shutil.which("mypy")
BASELINE_PATH = Path(".mypy-baseline.txt")


def _load_baseline(path: Path) -> set[str]:
    if not path.exists():
        return set()
    entries: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.add(stripped)
    return entries


def _parse_mypy_output(output: str) -> set[str]:
    issues: set[str] = set()
    for line in output.splitlines():
        stripped = line.strip()
        if stripped and ": error:" in stripped:
            issues.add(stripped)
    return issues


@pytest.mark.skipif(MYPY is None, reason="mypy not installed")
def test_mypy_strict_passes() -> None:
    result = subprocess.run(
        ["mypy", "src", "--strict", "--show-error-codes"],
        capture_output=True,
        text=True,
    )
    baseline = _load_baseline(BASELINE_PATH)
    current = _parse_mypy_output(result.stdout + result.stderr)
    new_violations = current - baseline
    assert not new_violations, f"New mypy violations: {sorted(new_violations)}"
