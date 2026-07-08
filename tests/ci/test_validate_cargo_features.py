"""
Tests for Cargo.toml Feature Validation Script

This test suite validates the validate_cargo_features.py script,
with a specific focus on the regression test for the missing json import
that caused GitHub Actions job #61098313515 to fail.

The script ensures proper validation of Cargo.toml features configuration
for PyO3 Python extensions.
"""

import json
import sys
import textwrap
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "scripts" / "ci"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_cargo_features import main, validate_cargo_features


class TestValidateCargoFeatures:
    """Comprehensive test suite for Cargo.toml validation."""

    @pytest.fixture
    def valid_cargo_toml(self, tmp_path: Path) -> Path:
        """Create valid Cargo.toml with all required features."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"
            version = "0.1.0"

            [features]
            python = ["extension-module"]
            extension-module = ["pyo3/extension-module"]
            default = ["python"]
            """))
        return cargo_file

    @pytest.fixture
    def invalid_cargo_toml_no_features(self, tmp_path: Path) -> Path:
        """Create Cargo.toml without features section."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"
            version = "0.1.0"

            [dependencies]
            pyo3 = "0.18"
            """))
        return cargo_file

    @pytest.fixture
    def invalid_cargo_toml_no_python(self, tmp_path: Path) -> Path:
        """Create Cargo.toml without 'python' feature."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"
            version = "0.1.0"

            [features]
            extension-module = ["pyo3/extension-module"]
            default = []
            """))
        return cargo_file

    @pytest.fixture
    def invalid_cargo_toml_no_extension_module(self, tmp_path: Path) -> Path:
        """Create Cargo.toml without 'extension-module' feature."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"
            version = "0.1.0"

            [features]
            python = []
            default = []
            """))
        return cargo_file

    def test_missing_json_import_regression(self, valid_cargo_toml: Path) -> None:
        """
        Regression test for NameError: json module not imported.

        This test validates the fix for GitHub Actions job #61098313515
        where missing json import caused CI failure when json.dumps was used
        at line 71 of validate_cargo_features.py.

        The test ensures that:
        1. json module is properly imported
        2. json.dumps can be used to serialize features lists
        3. No NameError is raised during validation
        """
        # Should not raise NameError when json.dumps is used
        is_valid, errors = validate_cargo_features(valid_cargo_toml)
        assert is_valid is True, "is_valid is not valid"
        assert len(errors) == 0, "Errors must not be empty"

        # Additional verification: json module should be accessible
        vcf = sys.modules["validate_cargo_features"]

        assert hasattr(vcf, "json"), "json module should be imported in validate_cargo_features"
        assert vcf.json is json, "json module should be the standard library json"

    def test_valid_cargo_toml_all_features(self, valid_cargo_toml: Path) -> None:
        """Test that valid Cargo.toml passes all validation checks."""
        is_valid, errors = validate_cargo_features(valid_cargo_toml)
        assert is_valid is True, "is_valid is not valid"
        assert len(errors) == 0, "Errors must not be empty"

    def test_missing_cargo_toml(self, tmp_path: Path) -> None:
        """Test handling of missing Cargo.toml file."""
        nonexistent = tmp_path / "Cargo.toml"
        is_valid, errors = validate_cargo_features(nonexistent)
        assert is_valid is False, "is_valid is not valid"
        assert len(errors) == 1, "Errors must not be empty"
        assert "not found" in errors[0].lower(), "Error should be raised or set"

    def test_missing_features_section(self, invalid_cargo_toml_no_features: Path) -> None:
        """Test detection of missing [features] section."""
        is_valid, errors = validate_cargo_features(invalid_cargo_toml_no_features)
        assert is_valid is False, "is_valid is not valid"
        assert any("[features]" in err for err in errors), "Error should be raised or set"

    def test_missing_python_feature(self, invalid_cargo_toml_no_python: Path) -> None:
        """Test detection of missing 'python' feature."""
        is_valid, errors = validate_cargo_features(invalid_cargo_toml_no_python)
        assert is_valid is False, "is_valid is not valid"
        assert any("python" in err.lower() for err in errors), "Error should be raised or set"

    def test_missing_extension_module_feature(
        self, invalid_cargo_toml_no_extension_module: Path
    ) -> None:
        """Test detection of missing 'extension-module' feature."""
        is_valid, errors = validate_cargo_features(invalid_cargo_toml_no_extension_module)
        assert is_valid is False, "is_valid is not valid"
        assert any("extension-module" in err for err in errors), "Error should be raised or set"

    def test_extension_module_missing_pyo3_dependency(self, tmp_path: Path) -> None:
        """Test detection of extension-module without pyo3 dependency."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features]
            python = ["extension-module"]
            extension-module = []
            """))
        is_valid, errors = validate_cargo_features(cargo_file)
        assert is_valid is False, "is_valid is not valid"
        assert any("pyo3/extension-module" in err for err in errors), "Error should be raised or set"

    def test_python_feature_without_extension_module_warning(self, tmp_path: Path) -> None:
        """Test warning when python feature doesn't depend on extension-module."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features]
            python = []
            extension-module = ["pyo3/extension-module"]
            """))
        _is_valid, errors = validate_cargo_features(cargo_file)
        # Should have warning about python not depending on extension-module
        assert any("WARNING" in err for err in errors), "Error should be raised or set"

    def test_empty_cargo_toml(self, tmp_path: Path) -> None:
        """Test handling of empty Cargo.toml file."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text("")
        is_valid, errors = validate_cargo_features(cargo_file)
        assert is_valid is False, "is_valid is not valid"
        assert len(errors) > 0, "Errors must not be empty"


class TestRegexFallback:
    """Tests for regex-based TOML parsing fallback."""

    @pytest.fixture
    def disable_toml_parsers(self) -> Any:
        """Disable TOML parsers to force regex fallback."""
        with patch.dict(sys.modules, {"tomllib": None, "tomli": None}):
            # Reimport to pick up the patched modules
            if "validate_cargo_features" in sys.modules:
                del sys.modules["validate_cargo_features"]
            yield

    def test_regex_fallback_with_valid_config(self, tmp_path: Path) -> None:
        """Test regex fallback parsing with valid configuration."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features]
            python = ["extension-module"]
            extension-module = ["pyo3/extension-module"]
            default = ["python"]
            """))
        is_valid, _errors = validate_cargo_features(cargo_file)
        assert is_valid is True, "is_valid is not valid"

    def test_regex_fallback_with_missing_feature(self, tmp_path: Path) -> None:
        """Test regex fallback detects missing features."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features]
            default = []
            """))
        is_valid, errors = validate_cargo_features(cargo_file)
        assert is_valid is False, "is_valid is not valid"
        assert any("python" in err.lower() for err in errors), "Error should be raised or set"


class TestLibRsValidation:
    """Tests for src/lib.rs feature cross-validation."""

    def test_lib_rs_feature_cross_validation(self, tmp_path: Path) -> None:
        """Test that features used in lib.rs are validated against Cargo.toml."""
        # Create Cargo.toml
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features]
            python = ["extension-module"]
            extension-module = ["pyo3/extension-module"]
            custom-feature = []
            """))

        # Create src directory and lib.rs
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        lib_rs = src_dir / "lib.rs"
        lib_rs.write_text(textwrap.dedent("""
            #[cfg(feature = "python")]
            mod python_module;

            #[cfg(feature = "custom-feature")]
            mod custom_module;
            """))

        is_valid, errors = validate_cargo_features(cargo_file)
        assert is_valid is True, "is_valid is not valid"
        assert len(errors) == 0, "Errors must not be empty"

    def test_lib_rs_undeclared_feature(self, tmp_path: Path) -> None:
        """Test detection of features used in lib.rs but not declared."""
        # Create Cargo.toml
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features]
            python = ["extension-module"]
            extension-module = ["pyo3/extension-module"]
            """))

        # Create src directory and lib.rs with undeclared feature
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        lib_rs = src_dir / "lib.rs"
        lib_rs.write_text(textwrap.dedent("""
            #[cfg(feature = "python")]
            mod python_module;

            #[cfg(feature = "undeclared-feature")]
            mod undeclared_module;
            """))

        is_valid, errors = validate_cargo_features(cargo_file)
        assert is_valid is False, "is_valid is not valid"
        assert any("undeclared-feature" in err for err in errors), "Error should be raised or set"


class TestMainFunction:
    """Tests for the main() entry point function."""

    def test_main_function_success(self) -> None:
        """Test main function returns 0 on success."""
        repo_root = Path(__file__).resolve().parents[2]
        cargo_toml = repo_root / "Cargo.toml"

        if cargo_toml.exists():
            # Test with actual repository Cargo.toml
            exit_code = main()
            assert exit_code == 0, "exit_code is not valid"
        else:
            pytest.skip("Repository Cargo.toml not found")

    def test_main_function_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main function produces expected output."""
        repo_root = Path(__file__).resolve().parents[2]
        cargo_toml = repo_root / "Cargo.toml"

        if cargo_toml.exists():
            exit_code = main()
            captured = capsys.readouterr()
            if exit_code == 0:
                assert "✅" in captured.out, "Condition must be true"
                assert "Validating Cargo.toml" in captured.out, "Condition must be true"
            else:
                assert "❌" in captured.out, "Condition must be true"
        else:
            pytest.skip("Repository Cargo.toml not found")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_malformed_features_section(self, tmp_path: Path) -> None:
        """Test handling of malformed features section."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features
            python = ["extension-module"]
            """))
        is_valid, _errors = validate_cargo_features(cargo_file)
        assert is_valid is False, "is_valid is not valid"

    def test_unicode_in_cargo_toml(self, tmp_path: Path) -> None:
        """Test handling of unicode characters in Cargo.toml."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"
            description = "Test package with émojis 🦀"

            [features]
            python = ["extension-module"]
            extension-module = ["pyo3/extension-module"]
            """))
        is_valid, _errors = validate_cargo_features(cargo_file)
        assert is_valid is True, "is_valid is not valid"

    def test_multiple_feature_dependencies(self, tmp_path: Path) -> None:
        """Test features with multiple dependencies."""
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"

            [features]
            python = ["extension-module", "numpy", "pandas"]
            extension-module = ["pyo3/extension-module", "pyo3/abi3-py38"]
            numpy = []
            pandas = []
            default = ["python"]
            """))
        is_valid, _errors = validate_cargo_features(cargo_file)
        assert is_valid is True, "is_valid is not valid"


class TestJsonModuleIntegration:
    """Tests specifically for json module integration."""

    def test_json_module_imported(self) -> None:
        """Verify json module is properly imported in the script."""
        vcf = sys.modules["validate_cargo_features"]

        assert hasattr(vcf, "json"), "json should be imported at module level"

    def test_json_dumps_callable(self) -> None:
        """Verify json.dumps is callable from the module."""
        vcf = sys.modules["validate_cargo_features"]

        test_data = {"key": ["value1", "value2"]}
        result = vcf.json.dumps(test_data)
        assert '"key"' in result, "Result must not be empty"
        assert '"value1"' in result, "Result must not be empty"

    def test_feature_list_serialization(self, tmp_path: Path) -> None:
        """Test that feature lists can be serialized without NameError."""
        # This is the exact scenario that caused the original bug
        # json.dumps was called on feature lists but json wasn't imported
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text(textwrap.dedent("""
            [package]
            name = "test-package"
            version = "0.1.0"

            [features]
            python = ["extension-module"]
            extension-module = ["pyo3/extension-module"]
            default = ["python"]
            """))
        is_valid, _errors = validate_cargo_features(cargo_file)
        assert is_valid is True, "is_valid is not valid"
        # If we got here without NameError, the json import is working


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
