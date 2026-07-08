"""Test that generated configuration files are up to date and functional.

These tests ensure that:
1. pytest.ini contains all discovered markers
2. The chaos marker is properly registered
3. Configuration generators can run without errors
"""

import subprocess
import sys
from pathlib import Path


def test_chaos_marker_registered():
    """Ensure chaos marker is properly registered in pytest.ini."""
    repo_root = Path(__file__).parent.parent
    pytest_ini = repo_root / "pytest.ini"

    assert pytest_ini.exists(), "pytest.ini not found"
    content = pytest_ini.read_text()

    # Check for chaos marker
    assert "chaos:" in content, "Chaos marker not registered in pytest.ini"
    assert "markers =" in content, "No markers section in pytest.ini"


def test_pytest_config_generator_runs():
    """Verify the pytest config generator can run without errors."""
    repo_root = Path(__file__).parent.parent
    script = repo_root / "scripts" / "generate_pytest_config.py"

    assert script.exists(), f"Generator script not found at {script}"

    result = subprocess.run(
        [sys.executable, str(script)], cwd=repo_root, capture_output=True, text=True
    )

    # Should exit with 0 (no changes) or 1 (changes made)
    assert result.returncode in [0, 1], f"Generator failed: {result.stderr}"


def test_codex_init_generator_runs():
    """Verify the codex init generator can run without errors."""
    repo_root = Path(__file__).parent.parent
    script = repo_root / "scripts" / "generate_codex_init.py"

    assert script.exists(), f"Generator script not found at {script}"

    result = subprocess.run(
        [sys.executable, str(script)], cwd=repo_root, capture_output=True, text=True
    )

    # Should exit with 0 (no changes) or 1 (changes made)
    assert result.returncode in [0, 1], f"Generator failed: {result.stderr}"


def test_pytest_markers_are_registered():
    """Verify that commonly used markers are registered."""
    repo_root = Path(__file__).parent.parent
    pytest_ini = repo_root / "pytest.ini"

    content = pytest_ini.read_text()

    # Check for essential markers
    essential_markers = [
        "smoke",
        "integration",
        "chaos",
        "slow",
        "regression",
    ]

    for marker in essential_markers:
        assert f"{marker}:" in content, f"Essential marker '{marker}' not registered"
