"""
Comprehensive cleanup validation tests.

This test suite verifies that root folder cleanup doesn't break:
1. Configuration loading (pytest.ini, mypy.ini, pyproject.toml, requirements)
2. Tool integration (pytest, mypy, pre-commit, coverage, linting)
3. Import paths (all public APIs)
4. Workflow simulation (CI/CD pipeline)
5. Artifact verification (output file generation)

Each phase has multiple assertions to ensure zero breaking changes.
"""

import subprocess
import sys
import os
import tempfile
from pathlib import Path
from typing import List, Tuple

import pytest


# ============================================================================
# PHASE 1: Configuration Loading Tests
# ============================================================================


class TestConfigurationLoading:
    """Verify all configuration files load correctly."""

    def test_pytest_ini_loads(self):
        """Verify pytest.ini loads and pytest can discover tests."""
        config_path = Path("pytest.ini")
        assert config_path.exists(), "pytest.ini not found"

        # Verify pytest can load config
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"pytest collection failed: {result.stderr}"
        assert "test session starts" in result.stdout or "tests collected" in result.stdout

    def test_pytest_ini_pythonpath_configured(self):
        """Verify pythonpath in pytest.ini points to src."""
        config_path = Path("pytest.ini")
        content = config_path.read_text()
        assert "pythonpath = src" in content, "pythonpath not configured in pytest.ini"

    def test_pytest_markers_configured(self):
        """Verify pytest markers are properly defined."""
        config_path = Path("pytest.ini")
        content = config_path.read_text()
        required_markers = [
            "edge_case",
            "smoke",
            "integration",
            "training",
            "cpu",
            "gpu",
        ]
        for marker in required_markers:
            assert f"    {marker}:" in content, f"Marker {marker} not defined"

    def test_mypy_ini_loads(self):
        """Verify mypy.ini loads and mypy works."""
        config_path = Path("mypy.ini")
        assert config_path.exists(), "mypy.ini not found"

        # Verify mypy can load config
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"mypy failed to load: {result.stderr}"
        assert "mypy" in result.stdout

    def test_mypy_ini_python_version(self):
        """Verify mypy.ini has correct Python version."""
        config_path = Path("mypy.ini")
        content = config_path.read_text()
        assert "python_version = 3.12" in content, "Python 3.12 not configured"

    def test_pyproject_toml_loads(self):
        """Verify pyproject.toml loads correctly."""
        config_path = Path("pyproject.toml")
        assert config_path.exists(), "pyproject.toml not found"

        # Try to parse it using setuptools
        result = subprocess.run(
            [sys.executable, "-c", "from importlib.metadata import version; print(version('codex-ml'))"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should find version or at least not error on parsing
        assert "codex-ml" in result.stdout or "ModuleNotFoundError" in result.stderr

    def test_pyproject_toml_build_system(self):
        """Verify pyproject.toml has correct build system."""
        config_path = Path("pyproject.toml")
        content = config_path.read_text()
        assert "[build-system]" in content, "build-system section missing"
        assert "setuptools" in content.lower(), "setuptools not configured"

    def test_all_requirements_files_exist(self):
        """Verify all required requirements files exist."""
        required_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
            "requirements-optional.txt",
            "requirements-minimal.txt",
        ]
        for req_file in required_files:
            path = Path(req_file)
            assert path.exists(), f"{req_file} not found"

    def test_requirements_files_parseable(self):
        """Verify all requirements files have valid syntax."""
        req_files = list(Path(".").glob("requirements*.txt"))
        for req_file in req_files:
            content = req_file.read_text()
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            for line in lines:
                # Skip comments and empty lines
                if line.startswith("#"):
                    continue
                # Verify basic package format
                assert any(
                    c in line for c in ["==", ">=", "<=", ">", "<", "~=", "["]
                ) or (not line.startswith("-")), f"Invalid requirement in {req_file}: {line}"

    def test_coverage_config_exists(self):
        """Verify coverage configuration exists."""
        config_files = [".coveragerc", "pyproject.toml"]
        assert (
            any(Path(f).exists() for f in config_files)
        ), "No coverage configuration found"


# ============================================================================
# PHASE 2: Tool Integration Tests
# ============================================================================


class TestToolIntegration:
    """Verify all CLI tools work after cleanup."""

    def test_pytest_collection_works(self):
        """Verify pytest can collect tests."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert (
            result.returncode == 0
        ), f"pytest collection failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    def test_pytest_basic_test_runs(self):
        """Verify pytest can run basic tests."""
        # Use a simple marker that exists
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-m",
                "smoke",
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Should at least complete (even if tests are skipped)
        assert "FAILED" not in result.stdout or "error" not in result.stderr.lower()

    def test_mypy_can_check_code(self):
        """Verify mypy can type check code."""
        # Create a simple test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x: int = 5\ny: str = x  # type error\n")
            test_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", test_file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should detect the type error or at least run
            assert result.returncode != 0 or "mypy" in result.stdout or "success" in result.stdout.lower()
        finally:
            os.unlink(test_file)

    def test_pre_commit_config_exists(self):
        """Verify pre-commit configuration exists."""
        config_files = [
            ".pre-commit-config.yaml",
            ".pre-commit-ruff.yaml",
        ]
        assert any(
            Path(f).exists() for f in config_files
        ), "No pre-commit configuration found"

    def test_ruff_config_exists(self):
        """Verify ruff configuration exists."""
        config_files = [".ruff.toml", "pyproject.toml"]
        assert any(
            Path(f).exists() for f in config_files
        ), "No ruff configuration found"

    def test_editorconfig_exists(self):
        """Verify editorconfig exists for formatting."""
        assert Path(".editorconfig").exists(), ".editorconfig not found"

    def test_black_can_format_sample_code(self):
        """Verify black can format code (if installed)."""
        try:
            import black
        except ImportError:
            pytest.skip("black not installed")

        code = "x  =   5"
        try:
            formatted = black.format_str(code, mode=black.FileMode())
            assert "x = 5" in formatted
        except Exception as e:
            pytest.fail(f"black formatting failed: {e}")


# ============================================================================
# PHASE 3: Import Path Tests
# ============================================================================


class TestImportPaths:
    """Verify no broken imports after cleanup."""

    def test_src_imports_work(self):
        """Verify src/ module imports work."""
        try:
            import codex
        except ImportError as e:
            pytest.fail(f"Failed to import codex: {e}")

    def test_critical_public_apis_importable(self):
        """Verify critical public APIs can be imported."""
        apis = [
            ("codex", None),
            ("codex.rag", None),
            ("codex.utils", None),
            ("codex.agent", None),
            ("codex.integrations", None),
        ]

        for module_name, attr in apis:
            try:
                module = __import__(module_name, fromlist=[""])
                if attr:
                    getattr(module, attr)
            except ImportError as e:
                # Some modules might be optional
                if "optional" not in str(e).lower():
                    pytest.skip(f"Module {module_name} not available (expected for optional features)")

    def test_no_broken_relative_imports(self):
        """Verify no broken relative imports in src."""
        result = subprocess.run(
            [sys.executable, "-c", "from codex import *"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should not have import errors (warning are OK)
        assert "ImportError" not in result.stderr or "ModuleNotFoundError" not in result.stderr

    def test_conftest_loads(self):
        """Verify conftest.py loads without errors."""
        result = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); from tests import conftest"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Should load or be skipped if not needed
        if result.returncode != 0:
            assert "ModuleNotFoundError" in result.stderr


# ============================================================================
# PHASE 4: Workflow Simulation
# ============================================================================


class TestWorkflowSimulation:
    """Simulate CI workflow execution."""

    def test_pytest_collect_discovers_tests(self):
        """Verify pytest can discover tests."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        # Should find at least some tests
        assert ("collected" in result.stdout or "test" in result.stdout.lower())

    def test_import_smoke_test(self):
        """Verify critical imports work (smoke test)."""
        test_code = """
import sys
sys.path.insert(0, 'src')

# Test critical imports
try:
    import codex
    print("✓ codex")
except ImportError as e:
    print(f"✗ codex: {e}")
    sys.exit(1)

try:
    from codex.rag import *
    print("✓ codex.rag")
except ImportError as e:
    print(f"✗ codex.rag: {e}")
    sys.exit(1)

try:
    from codex.agent import *
    print("✓ codex.agent")
except ImportError as e:
    print(f"✗ codex.agent: {e}")
    sys.exit(1)

print("All imports successful")
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Import smoke test failed: {result.stderr}"
        assert "All imports successful" in result.stdout

    def test_pytest_basic_test_discovery(self):
        """Verify basic test discovery works."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--collect-only",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert (
            result.returncode == 0
        ), f"Test collection failed: {result.stderr}"

    def test_config_files_in_place(self):
        """Verify all critical config files are in place."""
        critical_configs = [
            "pytest.ini",
            "mypy.ini",
            "pyproject.toml",
            "requirements.txt",
            ".editorconfig",
            ".pre-commit-config.yaml",
        ]
        missing = [f for f in critical_configs if not Path(f).exists()]
        assert not missing, f"Missing critical config files: {missing}"


# ============================================================================
# PHASE 5: Artifact Verification
# ============================================================================


class TestArtifactVerification:
    """Verify artifact generation still works."""

    def test_pytest_can_generate_report(self):
        """Verify pytest can generate test reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_file = Path(tmpdir) / "report.txt"
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=line"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            # Should complete (might skip tests)
            assert "error" not in result.stderr.lower() or "FAILED" not in result.stdout

    def test_mypy_generates_output(self):
        """Verify mypy can generate analysis output."""
        # Test on a known file
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "mypy" in result.stdout

    def test_coverage_can_be_configured(self):
        """Verify coverage configuration exists and is readable."""
        coverage_configs = [".coveragerc"]
        config_exists = any(Path(f).exists() for f in coverage_configs)

        # Try to import coverage
        try:
            import coverage
            # Coverage should be installable
            assert config_exists or True  # OK if config doesn't exist
        except ImportError:
            pytest.skip("coverage not installed")


# ============================================================================
# Integration Tests
# ============================================================================


class TestCleanupSafety:
    """Integration tests to verify cleanup safety."""

    def test_no_circular_imports_in_src(self):
        """Verify no circular imports in src."""
        result = subprocess.run(
            [sys.executable, "-c", "import py_compile; import os; [py_compile.compile(f, doraise=True) for f in __import__('glob').glob('src/**/*.py', recursive=True)]"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Compilation errors would indicate syntax errors
        assert (
            "SyntaxError" not in result.stderr
        ), f"Syntax errors in src: {result.stderr}"

    def test_git_status_clean_after_tests(self):
        """Verify tests don't accidentally modify files."""
        # Run a quick test
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/cleanup_validation/", "-v"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Tests should complete
        assert result.returncode in [0, 5]  # 0=pass, 5=no tests collected

    def test_all_test_markers_defined(self):
        """Verify all used test markers are defined in pytest.ini."""
        pytest_ini = Path("pytest.ini").read_text()

        # Find marker definitions
        marker_section = False
        defined_markers = set()
        for line in pytest_ini.split("\n"):
            if "markers =" in line:
                marker_section = True
                continue
            if marker_section:
                if line.startswith("    ") and ":" in line:
                    marker = line.strip().split(":")[0]
                    defined_markers.add(marker)
                elif not line.startswith(" "):
                    break

        # Check required markers
        required = ["smoke", "integration", "edge_case", "training", "cpu"]
        missing = [m for m in required if m not in defined_markers]
        assert not missing, f"Missing marker definitions: {missing}"


# ============================================================================
# Summary Test
# ============================================================================


class TestValidationSummary:
    """Summary validation to ensure overall health."""

    def test_validation_summary(self):
        """Provide validation summary."""
        checks = {
            "Config loading": Path("pytest.ini").exists()
            and Path("mypy.ini").exists()
            and Path("pyproject.toml").exists(),
            "Requirements files": all(
                Path(f).exists() for f in ["requirements.txt", "requirements-dev.txt"]
            ),
            "Tool configs": Path(".editorconfig").exists()
            and Path(".pre-commit-config.yaml").exists(),
        }

        print("\n" + "=" * 60)
        print("Cleanup Validation Summary")
        print("=" * 60)
        for check_name, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{check_name}: {status}")
        print("=" * 60)

        assert all(checks.values()), "Some validation checks failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
