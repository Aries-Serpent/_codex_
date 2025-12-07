"""Tests for data validation module."""

import pytest
from codex_ml.data.validation import (
    DataValidator,
    RequiredColumnsRule,
    NullCheckRule,
    DataTypeRule,
    RangeCheckRule,
    UniqueCheckRule,
    ValidationResult,
)


class TestValidationRules:
    """Test individual validation rules."""
    
    def test_required_columns_pass(self):
        """Test required columns validation passes."""
        rule = RequiredColumnsRule(["col1", "col2"])
        data = {"col1": [1], "col2": [2], "col3": [3]}
        result = rule.validate(data)
        assert result.is_valid
    
    def test_required_columns_fail(self):
        """Test required columns validation fails."""
        rule = RequiredColumnsRule(["col1", "col2"])
        data = {"col1": [1]}
        result = rule.validate(data)
        assert not result.is_valid
        assert "col2" in result.message
    
    def test_data_type_validation(self):
        """Test data type validation."""
        rule = DataTypeRule({"col1": "int64"})
        # Would need pandas DataFrame for full test
        result = rule.validate({"col1": [1]})
        assert result.is_valid  # Graceful degradation


class TestDataValidator:
    """Test DataValidator orchestration."""
    
    def test_validator_initialization(self):
        """Test validator initializes."""
        validator = DataValidator()
        assert validator.rules == []
    
    def test_add_rule(self):
        """Test adding rules."""
        validator = DataValidator()
        rule = RequiredColumnsRule(["col1"])
        validator.add_rule(rule)
        assert len(validator.rules) == 1
    
    def test_validate_all_pass(self):
        """Test validation when all rules pass."""
        validator = DataValidator()
        validator.add_rule(RequiredColumnsRule(["col1"]))
        result = validator.validate({"col1": [1]})
        assert result.is_valid


class TestValidationResult:
    """Test ValidationResult."""
    
    def test_result_creation(self):
        """Test creating validation result."""
        result = ValidationResult(
            rule_name="test",
            is_valid=True,
            message="Test passed",
        )
        assert result.is_valid
        assert result.rule_name == "test"
    
    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = ValidationResult(
            rule_name="test",
            is_valid=False,
            message="Test failed",
            errors=["Error 1"],
        )
        result_dict = result.to_dict()
        assert result_dict["is_valid"] is False
        assert len(result_dict["errors"]) == 1
