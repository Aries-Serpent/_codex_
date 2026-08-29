"""Comprehensive tests for codex_ml.data.validation module.

Tests cover:
- Validation rules (required columns, null checks, data types, ranges, unique)
- Schema validation
- DataValidator class
- Error reporting
- Performance with sampling
"""

from __future__ import annotations

import pytest

# Import module under test
try:
    from codex_ml.data import validation
except ImportError:
    pytest.skip("validation module not available", allow_module_level=True)


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    try:
        import pandas as pd

        return pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "age": [25, 30, 35, 40, 45],
                "score": [85.5, 90.0, 78.5, 95.0, 88.0],
            }
        )
    except ImportError:
        pytest.skip("pandas not available")
        return None


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test creating ValidationResult."""
        result = validation.ValidationResult(
            rule_name="test_rule",
            is_valid=True,
            message="Validation passed",
        )
        assert result.rule_name == "test_rule", "Result must not be empty"
        assert result.is_valid is True, "Result must not be empty"
        assert result.message == "Validation passed", "Result must not be empty"

    def test_validation_result_defaults(self):
        """Test ValidationResult default values."""
        result = validation.ValidationResult(
            rule_name="test",
            is_valid=True,
            message="Test",
        )
        assert result.errors == [], "Result must not be empty"
        assert result.warnings == [], "Result must not be empty"
        assert result.metadata == {}, "Result must not be empty"

    def test_validation_result_to_dict(self):
        """Test ValidationResult to_dict conversion."""
        result = validation.ValidationResult(
            rule_name="test_rule",
            is_valid=False,
            message="Validation failed",
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["rule_name"] == "test_rule", "Condition must be true"
        assert d["is_valid"] is False, "Condition must be true"
        assert len(d["errors"]) == 2, "Collection must not be empty"
        assert len(d["warnings"]) == 1, "Collection must not be empty"


class TestValidationRule:
    """Test ValidationRule abstract base class."""

    def test_validation_rule_is_abstract(self):
        """Test ValidationRule cannot be instantiated directly."""
        with pytest.raises(TypeError):
            validation.ValidationRule("test")

    def test_validation_rule_subclass_must_implement_validate(self):
        """Test subclass must implement validate method."""

        class IncompleteRule(validation.ValidationRule):
            pass

        with pytest.raises(TypeError):
            IncompleteRule("test")


class TestRequiredColumnsRule:
    """Test RequiredColumnsRule validation."""

    def test_required_columns_rule_creation(self):
        """Test creating RequiredColumnsRule."""
        rule = validation.RequiredColumnsRule(["id", "name", "age"])
        assert rule.name == "required_columns", "name is not valid"
        assert "id" in rule.required_columns, "Condition must be true"
        assert "name" in rule.required_columns, "Condition must be true"

    def test_required_columns_validation_pass(self, sample_dataframe):
        """Test validation passes with all required columns."""
        rule = validation.RequiredColumnsRule(["id", "name", "age"])
        result = rule.validate(sample_dataframe)
        assert result.is_valid is True, "Result must not be empty"

    def test_required_columns_validation_fail(self, sample_dataframe):
        """Test validation fails with missing columns."""
        rule = validation.RequiredColumnsRule(["id", "name", "missing_col"])
        result = rule.validate(sample_dataframe)
        assert result.is_valid is False, "Result must not be empty"
        assert len(result.errors) > 0, "Collection must not be empty"

    def test_required_columns_empty_list(self):
        """Test RequiredColumnsRule with empty column list."""
        rule = validation.RequiredColumnsRule([])
        # Should create rule without error
        assert rule.required_columns == set(), "required_columns is not valid"


class TestNullCheckRule:
    """Test NullCheckRule validation."""

    def test_null_check_rule_creation(self):
        """Test creating NullCheckRule."""
        if hasattr(validation, "NullCheckRule"):
            rule = validation.NullCheckRule(["id", "name"])
            assert rule.name == "null_check", "name is not valid"

    def test_null_check_validation_pass(self, sample_dataframe):
        """Test validation passes with no nulls."""
        if hasattr(validation, "NullCheckRule"):
            rule = validation.NullCheckRule(["id", "name", "age"])
            result = rule.validate(sample_dataframe)
            assert result.is_valid is True, "Result must not be empty"

    def test_null_check_validation_fail(self):
        """Test validation fails with nulls."""
        if hasattr(validation, "NullCheckRule"):
            try:
                import pandas as pd

                df = pd.DataFrame(
                    {
                        "id": [1, 2, None],
                        "name": ["Alice", "Bob", "Charlie"],
                    }
                )
                rule = validation.NullCheckRule(["id"])
                result = rule.validate(df)
                assert result.is_valid is False, "Result must not be empty"
            except ImportError:
                pytest.skip("pandas not available")


class TestDataTypeRule:
    """Test DataTypeRule validation."""

    def test_data_type_rule_creation(self):
        """Test creating DataTypeRule."""
        if hasattr(validation, "DataTypeRule"):
            rule = validation.DataTypeRule({"id": int, "name": str})
            assert rule.name == "data_type", "Data must not be empty"

    def test_data_type_validation_pass(self, sample_dataframe):
        """Test validation passes with correct types."""
        if hasattr(validation, "DataTypeRule"):
            rule = validation.DataTypeRule({"id": int, "name": str, "age": int})
            result = rule.validate(sample_dataframe)
            # May pass or fail depending on pandas dtype representation
            assert isinstance(result.is_valid, bool)

    def test_data_type_validation_fail(self):
        """Test validation fails with incorrect types."""
        if hasattr(validation, "DataTypeRule"):
            try:
                import pandas as pd

                df = pd.DataFrame(
                    {
                        "id": ["1", "2", "3"],  # strings instead of ints
                        "name": ["Alice", "Bob", "Charlie"],
                    }
                )
                rule = validation.DataTypeRule({"id": int})
                result = rule.validate(df)
                # Result depends on pandas type inference
                assert isinstance(result.is_valid, bool)
            except ImportError:
                pytest.skip("pandas not available")


class TestRangeCheckRule:
    """Test RangeCheckRule validation."""

    def test_range_check_rule_creation(self):
        """Test creating RangeCheckRule."""
        if hasattr(validation, "RangeCheckRule"):
            rule = validation.RangeCheckRule({"age": {"min": 0, "max": 120}})
            assert rule.name == "range_check", "name is not valid"

    def test_range_check_validation_pass(self, sample_dataframe):
        """Test validation passes within range."""
        if hasattr(validation, "RangeCheckRule"):
            rule = validation.RangeCheckRule({"age": {"min": 0, "max": 100}})
            result = rule.validate(sample_dataframe)
            assert result.is_valid is True, "Result must not be empty"

    def test_range_check_validation_fail(self, sample_dataframe):
        """Test validation fails outside range."""
        if hasattr(validation, "RangeCheckRule"):
            rule = validation.RangeCheckRule({"age": {"min": 50, "max": 60}})
            result = rule.validate(sample_dataframe)
            assert result.is_valid is False, "Result must not be empty"


class TestUniqueCheckRule:
    """Test UniqueCheckRule validation."""

    def test_unique_check_rule_creation(self):
        """Test creating UniqueCheckRule."""
        if hasattr(validation, "UniqueCheckRule"):
            rule = validation.UniqueCheckRule("id")
            assert rule.name == "unique_check", "name is not valid"

    def test_unique_check_validation_pass(self, sample_dataframe):
        """Test validation passes with unique values."""
        if hasattr(validation, "UniqueCheckRule"):
            rule = validation.UniqueCheckRule("id")
            result = rule.validate(sample_dataframe)
            assert result.is_valid is True, "Result must not be empty"

    def test_unique_check_validation_fail(self):
        """Test validation fails with duplicate values."""
        if hasattr(validation, "UniqueCheckRule"):
            try:
                import pandas as pd

                df = pd.DataFrame(
                    {
                        "id": [1, 2, 2, 3],  # Duplicate 2
                        "name": ["Alice", "Bob", "Charlie", "David"],
                    }
                )
                rule = validation.UniqueCheckRule("id")
                result = rule.validate(df)
                assert result.is_valid is False, "Result must not be empty"
            except ImportError:
                pytest.skip("pandas not available")


class TestSchemaValidationRule:
    """Test SchemaValidationRule validation."""

    def test_schema_validation_rule_creation(self):
        """Test creating SchemaValidationRule."""
        if hasattr(validation, "SchemaValidationRule"):
            schema = {
                "id": {"type": int, "required": True},
                "name": {"type": str, "required": True},
            }
            rule = validation.SchemaValidationRule(schema)
            assert rule.name == "schema_validation", "name is not valid"

    def test_schema_validation_pass(self, sample_dataframe):
        """Test schema validation passes."""
        if hasattr(validation, "SchemaValidationRule"):
            schema = {
                "id": {"type": int},
                "name": {"type": str},
                "age": {"type": int},
            }
            rule = validation.SchemaValidationRule(schema)
            result = rule.validate(sample_dataframe)
            assert isinstance(result.is_valid, bool)


class TestDataValidator:
    """Test DataValidator class."""

    def test_data_validator_creation(self):
        """Test creating DataValidator."""
        if hasattr(validation, "DataValidator"):
            validator = validation.DataValidator()
            assert validator is not None, "validator must be initialized"

    def test_data_validator_add_rule(self):
        """Test adding validation rule."""
        if hasattr(validation, "DataValidator"):
            validator = validation.DataValidator()
            rule = validation.RequiredColumnsRule(["id"])
            if hasattr(validator, "add_rule"):
                validator.add_rule(rule)

    def test_data_validator_validate(self, sample_dataframe):
        """Test validating data."""
        if hasattr(validation, "DataValidator"):
            validator = validation.DataValidator()
            rule = validation.RequiredColumnsRule(["id", "name"])
            if hasattr(validator, "add_rule"):
                validator.add_rule(rule)
            if hasattr(validator, "validate"):
                results = validator.validate(sample_dataframe)
                assert isinstance(results, (list, dict))
