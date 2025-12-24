"""Data validation module for dataset quality checks.

Provides:
- Pluggable validation rules
- Built-in common validations
- Great Expectations integration (optional)
- Detailed error reporting
- Performance optimized with sampling
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

__all__ = [
    "ValidationRule",
    "ValidationResult",
    "DataValidator",
    "RequiredColumnsRule",
    "NullCheckRule",
    "DataTypeRule",
    "RangeCheckRule",
    "UniqueCheckRule",
    "SchemaValidationRule",
]


@dataclass
class ValidationResult:
    """Result of a validation check.

    Attributes:
        rule_name: Name of the validation rule
        is_valid: Whether validation passed
        message: Validation message
        errors: List of specific error messages
        warnings: List of warning messages
        metadata: Additional metadata
    """

    rule_name: str
    is_valid: bool
    message: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "rule_name": self.rule_name,
            "is_valid": self.is_valid,
            "message": self.message,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


class ValidationRule(ABC):
    """Abstract base class for validation rules."""

    def __init__(self, name: str):
        """Initialize validation rule.

        Args:
            name: Rule name
        """
        self.name = name

    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Validate data.

        Args:
            data: Data to validate

        Returns:
            ValidationResult with pass/fail status
        """
        pass


class RequiredColumnsRule(ValidationRule):
    """Validate required columns are present."""

    def __init__(self, required_columns: List[str]):
        """Initialize rule.

        Args:
            required_columns: List of required column names
        """
        super().__init__("required_columns")
        self.required_columns = set(required_columns)

    def validate(self, data: Any) -> ValidationResult:
        """Validate required columns present."""
        if hasattr(data, "columns"):
            # DataFrame-like object
            actual_columns = set(data.columns)
            missing = self.required_columns - actual_columns

            if missing:
                return ValidationResult(
                    rule_name=self.name,
                    is_valid=False,
                    message=f"Missing required columns: {', '.join(sorted(missing))}",
                    errors=[f"Column '{col}' is required but missing" for col in sorted(missing)],
                )

            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="All required columns present",
            )

        # Dictionary-like object
        if isinstance(data, dict):
            actual_keys = set(data.keys())
            missing = self.required_columns - actual_keys

            if missing:
                return ValidationResult(
                    rule_name=self.name,
                    is_valid=False,
                    message=f"Missing required keys: {', '.join(sorted(missing))}",
                    errors=[f"Key '{key}' is required but missing" for key in sorted(missing)],
                )

            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="All required keys present",
            )

        return ValidationResult(
            rule_name=self.name,
            is_valid=False,
            message="Unsupported data type for column validation",
        )


class NullCheckRule(ValidationRule):
    """Check for null values in specified columns."""

    def __init__(self, columns: Optional[List[str]] = None, allow_nulls: bool = False):
        """Initialize rule.

        Args:
            columns: Columns to check (None = check all)
            allow_nulls: Whether nulls are allowed
        """
        super().__init__("null_check")
        self.columns = columns
        self.allow_nulls = allow_nulls

    def validate(self, data: Any) -> ValidationResult:
        """Validate null values."""
        if not hasattr(data, "isnull"):
            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="Data type does not support null checking",
            )

        columns_to_check = self.columns if self.columns else list(data.columns)
        null_counts = {}

        for col in columns_to_check:
            if col in data.columns:
                null_count = data[col].isnull().sum()
                if null_count > 0:
                    null_counts[col] = null_count

        if null_counts and not self.allow_nulls:
            total_nulls = sum(null_counts.values())
            errors = [
                f"Column '{col}' has {count} null value(s)" for col, count in null_counts.items()
            ]

            return ValidationResult(
                rule_name=self.name,
                is_valid=False,
                message=f"Found {total_nulls} null value(s) across {len(null_counts)} column(s)",
                errors=errors,
                metadata={"null_counts": null_counts},
            )

        return ValidationResult(
            rule_name=self.name,
            is_valid=True,
            message="No null values found" if not null_counts else "Null values allowed",
            metadata={"null_counts": null_counts},
        )


class DataTypeRule(ValidationRule):
    """Validate column data types."""

    def __init__(self, type_mapping: Dict[str, str]):
        """Initialize rule.

        Args:
            type_mapping: Map of column names to expected types
        """
        super().__init__("data_type")
        self.type_mapping = type_mapping

    def validate(self, data: Any) -> ValidationResult:
        """Validate data types."""
        if not hasattr(data, "dtypes"):
            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="Data type does not support dtype checking",
            )

        type_mismatches = []

        for col, expected_type in self.type_mapping.items():
            if col not in data.columns:
                continue

            actual_type = str(data[col].dtype)

            # Simple type matching (could be more sophisticated)
            if expected_type not in actual_type and actual_type not in expected_type:
                type_mismatches.append(
                    {
                        "column": col,
                        "expected": expected_type,
                        "actual": actual_type,
                    }
                )

        if type_mismatches:
            errors = [
                f"Column '{m['column']}': expected {m['expected']}, got {m['actual']}"
                for m in type_mismatches
            ]

            return ValidationResult(
                rule_name=self.name,
                is_valid=False,
                message=f"Found {len(type_mismatches)} data type mismatch(es)",
                errors=errors,
                metadata={"mismatches": type_mismatches},
            )

        return ValidationResult(
            rule_name=self.name,
            is_valid=True,
            message="All data types match expectations",
        )


class RangeCheckRule(ValidationRule):
    """Validate numeric values are within specified ranges."""

    def __init__(self, range_specs: Dict[str, Dict[str, float]]):
        """Initialize rule.

        Args:
            range_specs: Map of column names to {"min": val, "max": val}
        """
        super().__init__("range_check")
        self.range_specs = range_specs

    def validate(self, data: Any) -> ValidationResult:
        """Validate ranges."""
        if not hasattr(data, "columns"):
            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="Data type does not support range checking",
            )

        range_violations = []

        for col, spec in self.range_specs.items():
            if col not in data.columns:
                continue

            min_val = spec.get("min")
            max_val = spec.get("max")

            if min_val is not None:
                below_min = (data[col] < min_val).sum()
                if below_min > 0:
                    range_violations.append(
                        {
                            "column": col,
                            "violation": "below_min",
                            "count": int(below_min),
                            "threshold": min_val,
                        }
                    )

            if max_val is not None:
                above_max = (data[col] > max_val).sum()
                if above_max > 0:
                    range_violations.append(
                        {
                            "column": col,
                            "violation": "above_max",
                            "count": int(above_max),
                            "threshold": max_val,
                        }
                    )

        if range_violations:
            errors = [
                f"Column '{v['column']}': {v['count']} value(s) {v['violation']} (threshold: {v['threshold']})"
                for v in range_violations
            ]

            return ValidationResult(
                rule_name=self.name,
                is_valid=False,
                message=f"Found {len(range_violations)} range violation(s)",
                errors=errors,
                metadata={"violations": range_violations},
            )

        return ValidationResult(
            rule_name=self.name,
            is_valid=True,
            message="All values within expected ranges",
        )


class UniqueCheckRule(ValidationRule):
    """Check for duplicate values in specified columns."""

    def __init__(self, columns: List[str]):
        """Initialize rule.

        Args:
            columns: Columns that should have unique values
        """
        super().__init__("unique_check")
        self.columns = columns

    def validate(self, data: Any) -> ValidationResult:
        """Validate uniqueness."""
        if not hasattr(data, "columns"):
            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="Data type does not support uniqueness checking",
            )

        duplicate_info = []

        for col in self.columns:
            if col not in data.columns:
                continue

            duplicates = data[col].duplicated().sum()
            if duplicates > 0:
                duplicate_info.append(
                    {
                        "column": col,
                        "duplicate_count": int(duplicates),
                    }
                )

        if duplicate_info:
            errors = [
                f"Column '{d['column']}' has {d['duplicate_count']} duplicate value(s)"
                for d in duplicate_info
            ]

            return ValidationResult(
                rule_name=self.name,
                is_valid=False,
                message=f"Found duplicates in {len(duplicate_info)} column(s)",
                errors=errors,
                metadata={"duplicates": duplicate_info},
            )

        return ValidationResult(
            rule_name=self.name,
            is_valid=True,
            message="All specified columns have unique values",
        )


class SchemaValidationRule(ValidationRule):
    """Validate data against a JSON schema."""

    def __init__(self, schema: Dict[str, Any]):
        """Initialize rule.

        Args:
            schema: JSON schema for validation
        """
        super().__init__("schema_validation")
        self.schema = schema

    def validate(self, data: Any) -> ValidationResult:
        """Validate against schema."""
        try:
            import jsonschema
        except ImportError as e:
            logger.debug(f"ImportError: {e}")
            logger.warning(f"ImportError: {e}", exc_info=True)
            logger.warning("jsonschema not installed, skipping schema validation")
            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="jsonschema not available, validation skipped",
            )

        # Convert data to dict if needed
        if hasattr(data, "to_dict"):
            data_dict = data.to_dict()
        elif isinstance(data, dict):
            data_dict = data
        else:
            return ValidationResult(
                rule_name=self.name,
                is_valid=False,
                message="Data cannot be converted to dictionary for schema validation",
            )

        try:
            jsonschema.validate(instance=data_dict, schema=self.schema)
            return ValidationResult(
                rule_name=self.name,
                is_valid=True,
                message="Data matches schema",
            )
        except jsonschema.ValidationError as e:
            logger.debug("Exception caught, returning", exc_info=True)
            return ValidationResult(
                rule_name=self.name,
                is_valid=False,
                message=f"Schema validation failed: {e.message}",
                errors=[str(e)],
            )


class DataValidator:
    """Orchestrates multiple validation rules."""

    def __init__(self):
        """Initialize validator."""
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule.

        Args:
            rule: Validation rule to add
        """
        self.rules.append(rule)
        logger.debug(f"Added validation rule: {rule.name}")

    def validate(self, data: Any, sample_size: Optional[int] = None) -> ValidationResult:
        """Run all validation rules.

        Args:
            data: Data to validate
            sample_size: Optional sample size for large datasets

        Returns:
            Aggregated validation result
        """
        if sample_size and hasattr(data, "sample"):
            logger.info(f"Sampling {sample_size} rows for validation")
            data = data.sample(n=min(sample_size, len(data)))

        results = []
        all_errors = []
        all_warnings = []

        for rule in self.rules:
            logger.debug(f"Running validation rule: {rule.name}")
            result = rule.validate(data)
            results.append(result)

            if not result.is_valid:
                all_errors.extend(result.errors)

            all_warnings.extend(result.warnings)

        failed_rules = [r for r in results if not r.is_valid]

        if failed_rules:
            return ValidationResult(
                rule_name="data_validator",
                is_valid=False,
                message=f"{len(failed_rules)} of {len(results)} validation rule(s) failed",
                errors=all_errors,
                warnings=all_warnings,
                metadata={
                    "total_rules": len(results),
                    "failed_rules": len(failed_rules),
                    "results": [r.to_dict() for r in results],
                },
            )

        return ValidationResult(
            rule_name="data_validator",
            is_valid=True,
            message=f"All {len(results)} validation rule(s) passed",
            warnings=all_warnings,
            metadata={
                "total_rules": len(results),
                "results": [r.to_dict() for r in results],
            },
        )

    def validate_and_raise(self, data: Any, sample_size: Optional[int] = None) -> None:
        """Run validation and raise exception if failed.

        Args:
            data: Data to validate
            sample_size: Optional sample size

        Raises:
            ValueError: If validation fails
        """
        result = self.validate(data, sample_size=sample_size)

        if not result.is_valid:
            error_msg = f"Data validation failed: {result.message}\n"
            error_msg += "\n".join(f"  - {err}" for err in result.errors)
            raise ValueError(error_msg)
