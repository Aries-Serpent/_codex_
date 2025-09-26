import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_fences.py"
SAMPLE = ROOT / "tests" / "data" / "validate_fences_sample.md"


def test_sample_passes_in_warn_mode():
    """GIVEN a baseline sample; WHEN run in warn mode; THEN exit 0."""
    result = subprocess.run(
        [sys.executable, str(TOOL), "--warn-inner", str(SAMPLE)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_inner_collision_fails_in_strict_mode():
    """GIVEN a sample with an inner-run collision; WHEN strict; THEN nonzero exit."""
    result = subprocess.run(
        [sys.executable, str(TOOL), "--strict-inner", str(SAMPLE)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0, "strict mode should fail on inner collisions"
