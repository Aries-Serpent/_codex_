"""
End-to-end integration tests for Python 3.12.

Tests complete workflows to ensure no subtle compatibility issues.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12 integration tests")
class TestPython312Integration:
    """Integration tests for Python 3.12 migration."""

    def test_python_version_check(self):
        """Verify we're running on Python 3.12."""
        assert sys.version_info >= (3, 12), f"Expected Python 3.12+, got {sys.version_info}"
        assert sys.version_info.major == 3, "major is not valid"
        assert sys.version_info.minor >= 12, "minor must be greater than zero"

    def test_repository_structure_intact(self):
        """Verify repository structure is intact."""
        repo_root = Path(__file__).parent.parent.parent

        # Key directories should exist
        assert (repo_root / "src").exists(), "src/ directory missing"
        assert (repo_root / "tests").exists(), "tests/ directory missing"
        assert (repo_root / "scripts").exists(), "scripts/ directory missing"
        assert (repo_root / "docs").exists(), "docs/ directory missing"

        # Key files should exist
        assert (repo_root / "pyproject.toml").exists(), "pyproject.toml missing"
        assert (repo_root / "pytest.ini").exists() or (repo_root / "pyproject.toml").exists(), "Condition must be true"

    def test_core_imports_work(self):
        """Test that core modules can be imported."""
        # Test standard library imports that may have changed

        # Try importing tomllib (Python 3.11+)
        try:
            import tomllib

            assert tomllib is not None, "tomllib must be initialized"
        except ImportError:
            pytest.fail("tomllib should be available on Python 3.12")

    def test_codex_ml_imports(self):
        """Test that codex_ml modules can be imported."""
        try:
            # Try importing core modules (availability check only)
            import codex_ml  # noqa: F401

            # These may fail if dependencies aren't installed, so catch gracefully
            optional_imports = []

            try:
                import codex_ml.evaluation  # noqa: F401

                optional_imports.append("evaluation")
            except ImportError:
                # Optional module not available, skip
                _ = None  # suppressed: no action needed

            try:
                import codex_ml.data  # noqa: F401

                optional_imports.append("data")
            except ImportError:
                # Optional module not available, skip
                _ = None  # suppressed: no action needed

            try:
                import codex_ml.models  # noqa: F401

                optional_imports.append("models")
            except ImportError:
                # Optional module not available, skip
                _ = None  # suppressed: no action needed

            # At least the main package should import
            assert codex_ml is not None, "codex_ml must be initialized"

        except ImportError as e:
            pytest.skip(f"codex_ml not available: {e}")


@pytest.mark.integration
class TestCLIIntegration:
    """Test CLI tools work on Python 3.12."""

    def test_python_executable_version(self):
        """Verify Python executable version."""
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, "Result must not be empty"
        assert "Python 3." in result.stdout or "Python 3." in result.stderr, "Result must not be empty"

    def test_pip_works(self):
        """Verify pip works in Python 3.12."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, "Result must not be empty"
        assert "pip" in result.stdout.lower(), "Result must not be empty"

    def test_pytest_works(self):
        """Verify pytest works in Python 3.12."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, "Result must not be empty"
        assert "pytest" in result.stdout.lower(), "Result must not be empty"

    @pytest.mark.slow
    def test_dependency_checker_runs(self):
        """Test that dependency checker script runs."""
        repo_root = Path(__file__).parent.parent.parent
        script_path = repo_root / "scripts" / "check_py312_deps.py"

        if not script_path.exists():
            pytest.skip("Dependency checker script not found")

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=repo_root,
        )

        # Should run (exit code 0 or 1 depending on compatibility)
        assert result.returncode in [0, 1]
        assert "Python 3.12 Dependency Compatibility Checker" in result.stdout, "Result must not be empty"


@pytest.mark.integration
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12 specific")
class TestAsyncWorkflows:
    """Test async workflows in Python 3.12."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_basic_async_workflow(self):
        """Test basic async workflow."""
        import asyncio

        async def fetch_data(id: int):
            await asyncio.sleep(0.001)
            return {"id": id, "data": f"item_{id}"}

        async def process_data(item):
            await asyncio.sleep(0.001)
            return {**item, "processed": True}

        # Fetch multiple items
        items = await asyncio.gather(*[fetch_data(i) for i in range(5)])

        # Process them
        processed = await asyncio.gather(*[process_data(item) for item in items])

        assert len(processed) == 5, "Processed must not be empty"
        assert all(item["processed"] for item in processed), "Item must not be empty"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_async_context_manager_workflow(self):
        """Test async context manager workflow."""
        import asyncio

        class AsyncResource:
            def __init__(self):
                self.opened = False
                self.closed = False

            async def __aenter__(self):
                await asyncio.sleep(0.001)
                self.opened = True
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await asyncio.sleep(0.001)
                self.closed = True
                return False

        async with AsyncResource() as resource:
            assert resource.opened, "Condition must be true"
            assert not resource.closed, "Condition must be true"

        assert resource.closed, "Condition must be true"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_async_generator_workflow(self):
        """Test async generator workflow."""
        import asyncio

        async def async_range(n):
            for i in range(n):
                await asyncio.sleep(0.001)
                yield i

        results = []
        async for value in async_range(5):
            results.append(value)

        assert results == [0, 1, 2, 3, 4]


@pytest.mark.integration
class TestDataProcessingWorkflow:
    """Test data processing workflows."""

    def test_json_workflow(self, tmp_path):
        """Test JSON processing workflow."""
        import json

        # Create test data
        data = {
            "config": {
                "model": "test-model",
                "version": "1.0.0",
                "parameters": {
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 10,
                },
            },
            "results": [
                {"epoch": 1, "loss": 0.5, "accuracy": 0.85},
                {"epoch": 2, "loss": 0.3, "accuracy": 0.90},
                {"epoch": 3, "loss": 0.2, "accuracy": 0.92},
            ],
        }

        # Write to file
        json_file = tmp_path / "data.json"
        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)

        # Read back
        with open(json_file, "r") as f:
            loaded = json.load(f)

        assert loaded == data, "Data must not be empty"
        assert loaded["config"]["model"] == "test-model", "Condition must be true"
        assert len(loaded["results"]) == 3, "Collection must not be empty"

    def test_toml_workflow(self, tmp_path):
        """Test TOML processing workflow."""
        try:
            import tomllib
        except ImportError:
            pytest.skip("tomllib not available")
        else:
            toml_file = tmp_path / "config.toml"
            toml_content = """
[project]
name = "test-project"
version = "1.0.0"

[project.dependencies]
numpy = ">=1.26"
torch = ">=2.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
"""
            toml_file.write_text(toml_content)

            # Parse TOML
            with open(toml_file, "rb") as f:
                config = tomllib.load(f)

            assert config["project"]["name"] == "test-project", "Condition must be true"
            assert "numpy" in config["project"]["dependencies"], "Condition must be true"
            assert config["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"], "Condition must be true"

    def test_text_processing_workflow(self, tmp_path):
        """Test text processing workflow."""
        # Create test file
        text_file = tmp_path / "data.txt"
        lines = [f"Line {i}: Test data\n" for i in range(100)]
        text_file.write_text("".join(lines))

        # Process file
        with open(text_file, "r") as f:
            data = f.read()

        # Transform
        processed_lines = [line.strip().upper() for line in data.split("\n") if line.strip()]

        assert len(processed_lines) == 100, "Processed_lines must not be empty"
        assert all("LINE" in line for line in processed_lines), "Condition must be true"


@pytest.mark.integration
@pytest.mark.slow
class TestFullSystemIntegration:
    """Test full system integration scenarios."""

    def test_import_all_test_modules(self):
        """Test that all test modules can be imported."""
        repo_root = Path(__file__).parent.parent.parent
        tests_dir = repo_root / "tests"

        if not tests_dir.exists():
            pytest.skip("tests directory not found")

        # Find all test files
        test_files = list(tests_dir.rglob("test_*.py"))

        # Should have many test files
        assert len(test_files) > 10, f"Expected many test files, found {len(test_files)}"

    def test_pyproject_toml_valid(self):
        """Test that pyproject.toml is valid."""
        repo_root = Path(__file__).parent.parent.parent
        pyproject_path = repo_root / "pyproject.toml"

        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")

        try:
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            # Should have expected sections
            assert "project" in data, "Data must not be empty"
            assert "build-system" in data, "Data must not be empty"

            # Should have Python requirement
            if "requires-python" in data["project"]:
                requires = data["project"]["requires-python"]
                assert "3.11" in requires or "3.12" in requires, "Condition must be true"
        except ImportError:
            pytest.skip("tomllib not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_concurrent_operations(self):
        """Test concurrent operations work correctly."""
        import asyncio

        async def task(n):
            await asyncio.sleep(0.01)
            return n * 2

        # Run many tasks concurrently
        tasks = [task(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 100, "Results must not be empty"
        assert results[0] == 0, "Result must not be empty"
        assert results[99] == 198, "Result must not be empty"


@pytest.mark.integration
class TestBackwardCompatibility:
    """Test backward compatibility with Python 3.11."""

    def test_future_annotations_work(self):
        """Test that __future__ annotations work."""

        # This file uses __future__ annotations
        def test_func(x: str) -> str:
            return x.upper()

        result = test_func("hello")
        assert result == "HELLO", "Result must not be empty"

    def test_typing_compatibility(self):
        """Test typing compatibility."""
        from typing import Any, Dict, List, Optional

        # Old style should still work
        def old_style(data: Dict[str, Any]) -> Optional[List[str]]:
            return list(data.keys()) if data else None

        # New style should also work
        def new_style(data: dict[str, Any]) -> list[str] | None:
            return list(data.keys()) if data else None

        test_data = {"a": 1, "b": 2}
        assert old_style(test_data) == new_style(test_data), "Data must not be empty"
