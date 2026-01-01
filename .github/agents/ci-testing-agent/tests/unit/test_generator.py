"""Unit tests for TestGenerator with mocked dependencies."""
import ast
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.generator import TestGenerator


class TestTestGenerator:
    """Test suite for TestGenerator class."""

    @pytest.fixture
    def tmp_workspace(self, tmp_path):
        """Create temporary workspace with structure."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        return tmp_path

    @pytest.fixture
    def generator(self, tmp_workspace):
        """Create TestGenerator instance."""
        return TestGenerator(workspace=tmp_workspace)

    def test_init(self, tmp_workspace):
        """Test TestGenerator initialization."""
        generator = TestGenerator(workspace=tmp_workspace)
        assert generator.workspace == tmp_workspace
        assert generator.src_dir == tmp_workspace / "src"

    def test_generate_success(self, generator, tmp_workspace):
        """Test successful test generation."""
        # Create mock module
        module_path = tmp_workspace / "src" / "test_module.py"
        module_path.write_text(
            """
def example_function(x, y):
    return x + y
"""
        )

        task = {"module": "test_module", "threshold": 85}

        result = generator.generate(task)

        assert result["status"] == "success"
        assert result["files_generated"] >= 0
        assert "test_files" in result
        assert result["module"] == "test_module"

    def test_generate_no_module(self, generator):
        """Test generation with no module specified."""
        task = {"threshold": 85}

        result = generator.generate(task)

        assert result["status"] == "error"
        assert "No target module" in result["error"]
        assert result["files_generated"] == 0

    def test_generate_module_not_found(self, generator):
        """Test generation with non-existent module."""
        task = {"module": "nonexistent_module", "threshold": 85}

        result = generator.generate(task)

        assert result["status"] == "error"
        assert "not found" in result["error"].lower()

    def test_extract_functions(self, generator, tmp_workspace):
        """Test function extraction from module."""
        # Create test module
        module_file = tmp_workspace / "src" / "sample.py"
        module_file.write_text(
            """
def public_function(a, b):
    return a + b

def _private_function():
    pass

def test_function():
    pass
"""
        )

        functions = generator._extract_functions(module_file)

        # Should only extract public_function (not private or test functions)
        func_names = [f["name"] for f in functions]
        assert "public_function" in func_names
        assert "_private_function" not in func_names
        assert "test_function" not in func_names

    def test_scaffold_test(self, generator):
        """Test test scaffold generation."""
        func = {
            "name": "example_function",
            "file": "src/module/code.py",
            "lineno": 10,
            "args": ["x", "y"],
        }

        test_code = generator._scaffold_test(func, "module")

        assert "def test_example_function_basic" in test_code
        assert "class TestExampleFunction" in test_code
        assert "import pytest" in test_code
        assert "pytest.skip" in test_code

    def test_has_test_coverage_no_tests(self, generator, tmp_workspace):
        """Test coverage check when no tests exist."""
        func = {"name": "example_function", "file": "src/module.py"}

        result = generator._has_test_coverage(func, "tests")

        assert result is False

    def test_has_test_coverage_with_tests(self, generator, tmp_workspace):
        """Test coverage check when tests exist."""
        # Create test directory with test
        test_dir = tmp_workspace / "tests"
        test_dir.mkdir()
        test_file = test_dir / "test_module.py"
        test_file.write_text("def test_example_function(): pass")

        func = {"name": "example_function", "file": "src/module.py"}

        result = generator._has_test_coverage(func, "tests")

        assert result is True

    def test_resolve_module_path_directory(self, generator, tmp_workspace):
        """Test resolving module name to directory path."""
        # Create module directory
        module_dir = tmp_workspace / "src" / "my_module"
        module_dir.mkdir(parents=True)

        path = generator._resolve_module_path("my_module")

        assert path == module_dir

    def test_resolve_module_path_file(self, generator, tmp_workspace):
        """Test resolving module name to file path."""
        # Create module file
        module_file = tmp_workspace / "src" / "my_module.py"
        module_file.write_text("# module")

        path = generator._resolve_module_path("my_module")

        assert path == module_file

    def test_determine_test_path(self, generator, tmp_workspace):
        """Test determining test file path."""
        func = {
            "name": "my_function",
            "file": "src/module/code.py",
            "lineno": 5,
        }

        test_path = generator._determine_test_path(func, "module", "tests")

        assert "tests" in str(test_path)
        assert "test_my_function_generated.py" in str(test_path)
