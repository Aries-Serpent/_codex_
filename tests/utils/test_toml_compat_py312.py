"""
Test TOML compatibility layer for Python 3.12.

Verifies tomllib is used on Python 3.11+ and fallback works correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


class TestTomlCompatibility:
    """Test TOML loading compatibility."""

    @pytest.mark.skipif(sys.version_info < (3, 11), reason="tomllib requires 3.11+")
    def test_uses_tomllib_on_py311_plus(self):
        """Verify tomllib is imported on Python 3.11+."""
        try:
            import tomllib
            assert tomllib.__name__ == 'tomllib'
        except ImportError:
            pytest.fail("tomllib should be available on Python 3.11+")

    @pytest.mark.skipif(sys.version_info < (3, 11), reason="tomllib requires 3.11+")
    def test_toml_compat_uses_tomllib(self):
        """Verify codex uses tomllib on Python 3.11+."""
        try:
            from codex_ml.utils import toml_compat
            # Check if it imported the _toml module (tomllib or tomli)
            assert hasattr(toml_compat, '_toml')
        except ImportError:
            pytest.skip("toml_compat module not available")

    def test_loads_valid_toml(self, tmp_path):
        """Test TOML loading with Python 3.12."""
        # Create sample TOML file
        toml_file = tmp_path / "test.toml"
        toml_content = """
[project]
name = "test-project"
version = "1.0.0"

[project.dependencies]
numpy = ">=1.26"
torch = ">=2.0"

[tool.pytest]
testpaths = ["tests"]
"""
        toml_file.write_text(toml_content)

        # Load with tomllib (Python 3.11+) or tomli
        data: dict = {}
        try:
            import tomllib
            with open(toml_file, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            try:
                import tomli
                with open(toml_file, "rb") as f:
                    data = tomli.load(f)
            except ImportError:
                pytest.skip("Neither tomllib nor tomli available")

        assert data["project"]["name"] == "test-project"
        assert data["project"]["version"] == "1.0.0"
        assert "numpy" in data["project"]["dependencies"]

    def test_handles_binary_mode(self, tmp_path):
        """
        Verify binary mode requirement for tomllib.

        tomllib requires files to be opened in binary mode,
        unlike some other TOML parsers.
        """
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"')

        try:
            import tomllib
        except ImportError:
            pytest.skip("tomllib not available")
        else:
            with open(toml_file, "rb") as f:
                data = tomllib.load(f)
            assert data["section"]["key"] == "value"

            # Text mode should raise TypeError
            with pytest.raises(TypeError), open(toml_file, "r") as f:
                tomllib.load(f)

    def test_complex_toml_structure(self, tmp_path):
        """Test loading complex TOML structures."""
        toml_file = tmp_path / "complex.toml"
        toml_content = """
[build-system]
requires = ["setuptools>=65", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "codex-ml"
version = "0.1.0"
dependencies = [
    "numpy>=1.26,<3",
    "torch>=2.0,<3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
]
test = [
    "pytest>=7.4",
    "hypothesis>=6.100",
]

[[project.authors]]
name = "Test Author"
email = "test@example.com"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --strict-markers"
"""
        toml_file.write_text(toml_content)

        data: dict = {}
        try:
            import tomllib
            with open(toml_file, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            try:
                import tomli
                with open(toml_file, "rb") as f:
                    data = tomli.load(f)
            except ImportError:
                pytest.skip("Neither tomllib nor tomli available")

        assert data["project"]["name"] == "codex-ml"
        assert len(data["project"]["dependencies"]) == 2
        assert "dev" in data["project"]["optional-dependencies"]
        assert "test" in data["project"]["optional-dependencies"]
        assert data["project"]["authors"][0]["name"] == "Test Author"
        assert data["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


class TestPyprojectTomlParsing:
    """Test parsing actual pyproject.toml file."""

    def test_parse_repository_pyproject(self):
        """Test parsing the repository's pyproject.toml."""
        repo_root = Path(__file__).parent.parent.parent
        pyproject_path = repo_root / "pyproject.toml"

        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")

        data: dict = {}
        try:
            import tomllib
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            try:
                import tomli
                with open(pyproject_path, "rb") as f:
                    data = tomli.load(f)
            except ImportError:
                pytest.skip("Neither tomllib nor tomli available")

        # Verify expected structure
        assert "project" in data
        assert "name" in data["project"]
        assert "dependencies" in data["project"]

        # Check Python version requirement
        if "requires-python" in data["project"]:
            # Repository supports Python >=3.10, validate the requirement
            requires_python = data["project"]["requires-python"]
            # Use packaging library for robust version parsing if available
            try:
                from packaging.specifiers import SpecifierSet
                spec = SpecifierSet(requires_python)
                # Verify that 3.10, 3.11, or 3.12 are in the valid range
                assert any(f"3.{minor}" in spec for minor in range(10, 13)), \
                    f"Expected Python 3.10-3.12 support, got: {requires_python}"
            except ImportError:
                # Fallback to string matching if packaging is not available
                assert any(v in requires_python for v in ["3.10", "3.11", "3.12", ">=3.10"]), \
                    f"Expected Python 3.10+ support, got: {requires_python}"

    def test_dependency_extraction(self):
        """Test extracting dependencies from pyproject.toml."""
        repo_root = Path(__file__).parent.parent.parent
        pyproject_path = repo_root / "pyproject.toml"

        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")

        data: dict = {}
        try:
            import tomllib
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            try:
                import tomli
                with open(pyproject_path, "rb") as f:
                    data = tomli.load(f)
            except ImportError:
                pytest.skip("Neither tomllib nor tomli available")

        deps = data.get("project", {}).get("dependencies", [])
        assert isinstance(deps, list)
        assert len(deps) > 0

        # Check for known dependencies
        dep_names = [d.split("[")[0].split(">=")[0].split("==")[0].split("<")[0] for d in deps]
        assert any("torch" in name.lower() for name in dep_names)


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ specific tests")
class TestPython312TomlFeatures:
    """Test Python 3.12-specific TOML features."""

    def test_tomllib_load_performance(self, tmp_path):
        """
        Test tomllib performance in Python 3.12.

        Python 3.12 has optimized tomllib implementation.
        """
        import time

        # Create a moderately sized TOML file
        toml_file = tmp_path / "large.toml"
        sections = []
        for i in range(100):
            sections.append(f"""
[section_{i}]
key1 = "value1"
key2 = "value2"
key3 = 123
key4 = true
""")
        toml_file.write_text("\n".join(sections))

        try:
            import tomllib
        except ImportError:
            pytest.skip("tomllib not available")
        else:
            start = time.time()
            with open(toml_file, "rb") as f:
                data = tomllib.load(f)
            elapsed = time.time() - start

            assert len(data) == 100
            assert elapsed < 1.0  # Should be fast

    def test_unicode_handling(self, tmp_path):
        """Test Unicode handling in TOML files."""
        toml_file = tmp_path / "unicode.toml"
        toml_content = """
[project]
name = "测试项目"
description = "Test with émojis 🚀 and ümlauts"
author = "José García"
"""
        toml_file.write_text(toml_content, encoding="utf-8")

        data: dict = {}
        try:
            import tomllib
            with open(toml_file, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            pytest.skip("tomllib not available")

        assert data["project"]["name"] == "测试项目"
        assert "🚀" in data["project"]["description"]
        assert data["project"]["author"] == "José García"


class TestTomlErrorHandling:
    """Test TOML error handling."""

    def test_invalid_toml_syntax(self, tmp_path):
        """Test handling of invalid TOML syntax."""
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("this is not valid TOML syntax [[")

        try:
            import tomllib
            with pytest.raises(tomllib.TOMLDecodeError), open(toml_file, "rb") as f:
                tomllib.load(f)
        except ImportError:
            try:
                import tomli
                with pytest.raises(tomli.TOMLDecodeError):
                    with open(toml_file, "rb") as f:
                        tomli.load(f)
            except ImportError:
                pytest.skip("Neither tomllib nor tomli available")

    def test_missing_file(self):
        """Test handling of missing TOML file."""
        try:
            import tomllib
            with pytest.raises(FileNotFoundError), open("nonexistent.toml", "rb") as f:
                tomllib.load(f)
        except ImportError:
            pytest.skip("tomllib not available")
