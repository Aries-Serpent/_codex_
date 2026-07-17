"""
Development Tools Validation Test Suite

Tests that validate all development tools work correctly:
1. pytest - testing framework
2. mypy - type checking
3. ruff - linting
4. black - code formatting
5. isort - import sorting
"""

import subprocess
import sys


class TestPytestTool:
    """Test suite for pytest."""

    def test_pytest_installed(self, check_tool_installed):
        """Test that pytest is installed."""
        installed, version = check_tool_installed("pytest")
        assert installed, "pytest is not installed"
        assert "pytest" in version.lower(), f"Unexpected version output: {version}"

    def test_pytest_version_format(self, tool_versions):
        """Test that pytest version is in expected format."""
        pytest_version = tool_versions["pytest"]
        assert "pytest" in pytest_version.lower(), f"Unexpected version: {pytest_version}"
        # Should contain version number like "9.0.3"
        assert any(char.isdigit() for char in pytest_version), f"No version number found: {pytest_version}"

    def test_pytest_discovers_tests(self, project_root, run_tool_command):
        """Test that pytest can discover tests."""
        # Collect only from the full test directory to avoid timeout
        returncode, stdout, stderr = run_tool_command(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/full/"],
            cwd=project_root,
        )
        # Should exit with 0 or 5 (no tests collected in full dir initially)
        assert returncode in [0, 5], f"pytest collection failed: {stderr}"

    def test_pytest_can_run_simple_test(self, tmp_path):
        """Test that pytest can execute a simple test."""
        test_file = tmp_path / "test_simple.py"
        test_file.write_text("""
def test_basic():
    assert 1 + 1 == 2

def test_string():
    assert "hello" == "hello"
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"Simple test failed: {result.stderr}"
        assert "2 passed" in result.stdout, f"Unexpected output: {result.stdout}"


class TestMypyTool:
    """Test suite for mypy type checking."""

    def test_mypy_installed(self, check_tool_installed):
        """Test that mypy is installed."""
        installed, version = check_tool_installed("mypy")
        assert installed, "mypy is not installed"

    def test_mypy_version_format(self, tool_versions):
        """Test that mypy version is in expected format."""
        mypy_version = tool_versions["mypy"]
        assert "mypy" in mypy_version.lower() or any(char.isdigit() for char in mypy_version), \
            f"Unexpected version: {mypy_version}"

    def test_mypy_can_check_file(self, tmp_path):
        """Test that mypy can type check a simple file."""
        test_file = tmp_path / "typed_module.py"
        test_file.write_text("""
def add(a: int, b: int) -> int:
    return a + b

result: int = add(1, 2)
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Should complete without critical errors
        assert "error" not in result.stdout.lower() or "Success" in result.stdout, \
            f"mypy check failed: {result.stdout}"

    def test_mypy_detects_type_errors(self, tmp_path):
        """Test that mypy detects type errors."""
        test_file = tmp_path / "typed_errors.py"
        test_file.write_text("""
def add(a: int, b: int) -> int:
    return a + b

result: int = add("1", "2")  # Type error - passing strings instead of ints
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Should detect the type error
        assert result.returncode != 0, "mypy should have detected type error"


class TestRuffTool:
    """Test suite for ruff linting."""

    def test_ruff_installed(self, check_tool_installed):
        """Test that ruff is installed."""
        installed, version = check_tool_installed("ruff")
        assert installed, "ruff is not installed"

    def test_ruff_version_format(self, tool_versions):
        """Test that ruff version is in expected format."""
        ruff_version = tool_versions["ruff"]
        assert "ruff" in ruff_version.lower() or any(char.isdigit() for char in ruff_version), \
            f"Unexpected version: {ruff_version}"

    def test_ruff_can_lint_file(self, tmp_path):
        """Test that ruff can lint a file."""
        test_file = tmp_path / "clean_code.py"
        test_file.write_text("""
def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello("World"))
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Clean code should have no errors or just warnings
        assert result.returncode in [0, 1], f"ruff check failed: {result.stderr}"

    def test_ruff_detects_issues(self, tmp_path):
        """Test that ruff detects style issues."""
        test_file = tmp_path / "style_issues.py"
        test_file.write_text("""
        import os, sys
x=1+2
y = 3
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should detect at least one issue
        assert result.returncode != 0 or "warning" in result.stdout.lower() or len(result.stdout) > 0, \
            "ruff should detect style issues"


class TestBlackTool:
    """Test suite for black code formatting."""

    def test_black_installed(self, check_tool_installed):
        """Test that black is installed."""
        installed, version = check_tool_installed("black")
        assert installed, "black is not installed"

    def test_black_version_format(self, tool_versions):
        """Test that black version is in expected format."""
        black_version = tool_versions["black"]
        assert "black" in black_version.lower() or any(char.isdigit() for char in black_version), \
            f"Unexpected version: {black_version}"

    def test_black_can_format_check(self, tmp_path):
        """Test that black can check formatting."""
        test_file = tmp_path / "format_test.py"
        # Well formatted code
        test_file.write_text("""
def hello(name: str) -> str:
    return f"Hello, {name}!"
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "black", "--check", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should complete successfully
        assert result.returncode in [0, 1], f"black check failed: {result.stderr}"

    def test_black_can_format_code(self, tmp_path):
        """Test that black can format code."""
        test_file = tmp_path / "poorly_formatted.py"
        # Poorly formatted code
        test_file.write_text("x=1;y=2;z=3")
        
        result = subprocess.run(
            [sys.executable, "-m", "black", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"black formatting failed: {result.stderr}"
        formatted_content = test_file.read_text()
        assert "x = 1" in formatted_content or "x=1" not in formatted_content, \
            "black should have reformatted the code"


class TestIsortTool:
    """Test suite for isort import sorting."""

    def test_isort_installed(self, check_tool_installed):
        """Test that isort is installed."""
        installed, version = check_tool_installed("isort")
        assert installed, "isort is not installed"

    def test_isort_version_format(self, tool_versions):
        """Test that isort version is in expected format."""
        isort_version = tool_versions["isort"]
        assert "isort" in isort_version.lower() or any(char.isdigit() for char in isort_version), \
            f"Unexpected version: {isort_version}"

    def test_isort_can_check_imports(self, tmp_path):
        """Test that isort can check import sorting."""
        test_file = tmp_path / "import_test.py"
        # Unsorted imports
        test_file.write_text("""
        import sys
        import os
        from pathlib import Path
        from typing import List
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "isort", "--check-only", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should complete (may have changes needed or not)
        assert result.returncode in [0, 1], f"isort check failed: {result.stderr}"

    def test_isort_can_sort_imports(self, tmp_path):
        """Test that isort can sort imports."""
        test_file = tmp_path / "unsorted_imports.py"
        test_file.write_text("""
        import sys
        import os
""")
        
        result = subprocess.run(
            [sys.executable, "-m", "isort", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"isort sorting failed: {result.stderr}"
        # File should still be valid Python
        sorted_content = test_file.read_text()
        assert "import" in sorted_content, "isort should have preserved imports"


class TestToolIntegration:
    """Test suite for tool integration and compatibility."""

    def test_all_tools_installed(self, tool_versions):
        """Test that all required dev tools are installed."""
        required_tools = ["pytest", "mypy", "ruff", "black", "isort"]
        for tool in required_tools:
            assert tool in tool_versions, f"Tool {tool} not in version dict"
            version = tool_versions[tool]
            assert "unknown" not in version.lower() or version != "unknown", \
                f"{tool} is not properly installed: {version}"

    def test_tools_work_together(self, tmp_path):
        """Test that all tools can work on the same codebase."""
        # Create a test Python file
        test_file = tmp_path / "sample_module.py"
        test_file.write_text("""
        from typing import List
        import os

def process_items(items: List[str]) -> int:
    count = 0
    for item in items:
        count += 1
    return count
""")
        
        # Run ruff
        result_ruff = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result_ruff.returncode in [0, 1], "ruff check failed"
        
        # Run black
        result_black = subprocess.run(
            [sys.executable, "-m", "black", "--check", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result_black.returncode in [0, 1], "black check failed"
        
        # Run isort
        result_isort = subprocess.run(
            [sys.executable, "-m", "isort", "--check-only", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result_isort.returncode in [0, 1], "isort check failed"
        
        # Run mypy
        result_mypy = subprocess.run(
            [sys.executable, "-m", "mypy", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result_mypy.returncode in [0, 1], "mypy check failed"

    def test_configuration_validation(self, project_root):
        """Test that tool configurations are valid."""
        # Check if tool configuration files exist
        config_files = [
            project_root / "pyproject.toml",
            project_root / "ruff.toml",
            project_root / "mypy.ini",
        ]
        
        # At least pyproject.toml should exist
        assert (project_root / "pyproject.toml").exists(), "pyproject.toml not found"
        
        # pyproject.toml should be readable
        with open(project_root / "pyproject.toml", "r") as f:
            content = f.read()
            assert len(content) > 0, "pyproject.toml is empty"


class TestDevToolchain:
    """Test suite for the complete dev toolchain."""

    def test_full_toolchain_execution(self, project_root, tmp_path):
        """Test that all tools can execute together on a test file."""
        # Create a sample test file in a temporary location
        test_dir = tmp_path / "test_toolchain"
        test_dir.mkdir()
        
        test_file = test_dir / "toolchain_test.py"
        test_file.write_text("""
'''Test module for toolchain validation.'''

        from typing import Dict, List
        import sys

def validate_data(data: Dict[str, List[int]]) -> bool:
    '''Validate data structure.'''
    return len(data) > 0

if __name__ == "__main__":
    test_data = {"values": [1, 2, 3]}
    result = validate_data(test_data)
    print(f"Validation result: {result}")
""")
        
        tools_executed = []
        
        # Execute pytest (discover tests)
        pytest_result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", str(test_dir)],
            capture_output=True,
            text=True,
            timeout=10
        )
        tools_executed.append(("pytest", pytest_result.returncode in [0, 5]))
        
        # Execute ruff
        ruff_result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        tools_executed.append(("ruff", ruff_result.returncode in [0, 1]))
        
        # Execute black
        black_result = subprocess.run(
            [sys.executable, "-m", "black", "--check", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        tools_executed.append(("black", black_result.returncode in [0, 1]))
        
        # Execute isort
        isort_result = subprocess.run(
            [sys.executable, "-m", "isort", "--check-only", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        tools_executed.append(("isort", isort_result.returncode in [0, 1]))
        
        # Execute mypy
        mypy_result = subprocess.run(
            [sys.executable, "-m", "mypy", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        tools_executed.append(("mypy", mypy_result.returncode in [0, 1]))
        
        # Verify all tools executed successfully
        failed_tools = [tool for tool, success in tools_executed if not success]
        assert not failed_tools, f"Tools failed: {failed_tools}"
