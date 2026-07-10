"""
Fixtures and utilities for dev tools validation tests.

This module provides fixtures for testing development tools:
- pytest
- mypy
- ruff
- black
- isort
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def source_files(project_root: Path) -> List[Path]:
    """Get all Python source files in the project."""
    src_dir = project_root / "src"
    return list(src_dir.glob("**/*.py")) if src_dir.exists() else []


@pytest.fixture(scope="session")
def test_files(project_root: Path) -> List[Path]:
    """Get all test files in the project."""
    tests_dir = project_root / "tests"
    return list(tests_dir.glob("**/*.py")) if tests_dir.exists() else []


@pytest.fixture(scope="session")
def all_python_files(project_root: Path) -> List[Path]:
    """Get all Python files (src + tests)."""
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"
    
    files = []
    if src_dir.exists():
        files.extend(src_dir.glob("**/*.py"))
    if tests_dir.exists():
        files.extend(tests_dir.glob("**/*.py"))
    return files


@pytest.fixture
def run_tool_command():
    """Fixture to run a tool command and capture output."""
    def _run(
        cmd: List[str],
        cwd: Path = None,
        check: bool = False
    ) -> Tuple[int, str, str]:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 60 seconds"
        except Exception as e:
            return -1, "", str(e)
    
    return _run


@pytest.fixture
def tool_versions() -> Dict[str, str]:
    """Get versions of installed dev tools."""
    versions = {}
    
    tools = ["pytest", "mypy", "ruff", "black", "isort"]
    
    for tool in tools:
        try:
            result = subprocess.run(
                [sys.executable, "-m", tool, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                versions[tool] = result.stdout.strip()
            else:
                versions[tool] = "unknown (error)"
        except subprocess.TimeoutExpired:
            versions[tool] = "unknown (timeout)"
        except Exception as e:
            versions[tool] = f"unknown ({type(e).__name__})"
    
    return versions


@pytest.fixture
def check_tool_installed():
    """Check if a tool is installed and working."""
    def _check(tool_name: str, module_name: str = None) -> Tuple[bool, str]:
        """Check if a tool is installed. Returns (installed, version_string)."""
        if module_name is None:
            module_name = tool_name
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", module_name, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            # Some tools use -h to show version
            result = subprocess.run(
                [sys.executable, "-m", module_name, "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0, "installed"
        except Exception:
            return False, ""
    
    return _check
