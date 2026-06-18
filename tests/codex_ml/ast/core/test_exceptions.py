"""
Comprehensive tests for codex_ml.ast.core.exceptions module.

Tests cover exception hierarchy with 60+ test cases covering
exception creation, properties, string representations, and integration.
"""

import pytest

from codex_ml.ast.core.exceptions import (
    AnalysisError,
    ASTError,
    ConfigurationError,
    CycleDetectedError,
    ParseError,
    StorageError,
)

# ============================================================================
# ASTError Tests (Base Exception)
# ============================================================================


class TestASTErrorBasic:
    """Test ASTError basic functionality."""

    def test_ast_error_creation_message_only(self):
        """Test creating ASTError with message only."""
        error = ASTError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}

    def test_ast_error_creation_with_details(self):
        """Test creating ASTError with message and details."""
        details = {"code": "E001", "line": 10}
        error = ASTError("Test error", details=details)
        assert error.message == "Test error"
        assert error.details == details

    def test_ast_error_inheritance(self):
        """Test ASTError is an Exception."""
        error = ASTError("Test")
        assert isinstance(error, Exception)

    def test_ast_error_details_default_empty(self):
        """Test ASTError details defaults to empty dict."""
        error = ASTError("Test error")
        assert error.details == {}

    def test_ast_error_string_conversion(self):
        """Test ASTError string conversion."""
        error = ASTError("Error message")
        assert repr(error) is not None
        assert "Error message" in str(error)


# ============================================================================
# ParseError Tests
# ============================================================================


class TestParseErrorBasic:
    """Test ParseError basic functionality."""

    def test_parse_error_creation_message_only(self):
        """Test creating ParseError with message only."""
        error = ParseError("Syntax error")
        assert error.message == "Syntax error"
        assert error.file_path is None
        assert error.line is None
        assert error.column is None

    def test_parse_error_creation_with_location(self):
        """Test creating ParseError with location information."""
        error = ParseError(
            "Invalid syntax",
            file_path="test.py",
            line=10,
            column=5,
        )
        assert error.message == "Invalid syntax"
        assert error.file_path == "test.py"
        assert error.line == 10
        assert error.column == 5

    def test_parse_error_string_with_location(self):
        """Test ParseError string representation with location."""
        error = ParseError(
            "Invalid syntax",
            file_path="test.py",
            line=10,
            column=5,
        )
        error_str = str(error)
        assert "test.py" in error_str
        assert "10" in error_str
        assert "5" in error_str
        assert "Invalid syntax" in error_str

    def test_parse_error_string_file_only(self):
        """Test ParseError string with file only."""
        error = ParseError("Error", file_path="test.py")
        error_str = str(error)
        assert "test.py:" in error_str

    def test_parse_error_string_file_and_line(self):
        """Test ParseError string with file and line."""
        error = ParseError("Error", file_path="test.py", line=10)
        error_str = str(error)
        assert "test.py:10" in error_str

    def test_parse_error_string_without_location(self):
        """Test ParseError string without location."""
        error = ParseError("Error message")
        error_str = str(error)
        assert error_str == "Error message"

    def test_parse_error_partial_location(self):
        """Test ParseError with partial location information."""
        error = ParseError("Error", file_path="test.py", line=5)
        error_str = str(error)
        assert "test.py:5" in error_str

    def test_parse_error_inheritance(self):
        """Test ParseError inherits from ASTError."""
        error = ParseError("Test")
        assert isinstance(error, ASTError)
        assert isinstance(error, Exception)


# ============================================================================
# AnalysisError Tests
# ============================================================================


class TestAnalysisErrorBasic:
    """Test AnalysisError basic functionality."""

    def test_analysis_error_creation_message_only(self):
        """Test creating AnalysisError with message only."""
        error = AnalysisError("Analysis failed")
        assert error.message == "Analysis failed"
        assert error.analyzer_type is None

    def test_analysis_error_creation_with_analyzer(self):
        """Test creating AnalysisError with analyzer type."""
        error = AnalysisError(
            "Complexity analysis failed",
            analyzer_type="complexity_analyzer",
        )
        assert error.message == "Complexity analysis failed"
        assert error.analyzer_type == "complexity_analyzer"

    def test_analysis_error_inheritance(self):
        """Test AnalysisError inherits from ASTError."""
        error = AnalysisError("Test")
        assert isinstance(error, ASTError)

    def test_analysis_error_analyzer_type_none(self):
        """Test AnalysisError analyzer_type can be None."""
        error = AnalysisError("Error", analyzer_type=None)
        assert error.analyzer_type is None

    def test_analysis_error_with_empty_analyzer(self):
        """Test AnalysisError with empty analyzer type."""
        error = AnalysisError("Error", analyzer_type="")
        assert error.analyzer_type == ""


# ============================================================================
# StorageError Tests
# ============================================================================


class TestStorageErrorBasic:
    """Test StorageError basic functionality."""

    def test_storage_error_creation_message_only(self):
        """Test creating StorageError with message only."""
        error = StorageError("File not found")
        assert error.message == "File not found"
        assert error.operation is None

    def test_storage_error_creation_with_operation(self):
        """Test creating StorageError with operation."""
        error = StorageError(
            "Failed to write file",
            operation="write",
        )
        assert error.message == "Failed to write file"
        assert error.operation == "write"

    def test_storage_error_inheritance(self):
        """Test StorageError inherits from ASTError."""
        error = StorageError("Test")
        assert isinstance(error, ASTError)

    def test_storage_error_operation_variants(self):
        """Test StorageError with different operations."""
        operations = ["read", "write", "delete", "update"]
        for op in operations:
            error = StorageError("Failed", operation=op)
            assert error.operation == op


# ============================================================================
# ConfigurationError Tests
# ============================================================================


class TestConfigurationErrorBasic:
    """Test ConfigurationError basic functionality."""

    def test_configuration_error_creation_message_only(self):
        """Test creating ConfigurationError with message only."""
        error = ConfigurationError("Invalid config")
        assert error.message == "Invalid config"
        assert error.key is None

    def test_configuration_error_creation_with_key(self):
        """Test creating ConfigurationError with key."""
        error = ConfigurationError(
            "Invalid value for parser_backend",
            key="parser_backend",
        )
        assert error.message == "Invalid value for parser_backend"
        assert error.key == "parser_backend"

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from ASTError."""
        error = ConfigurationError("Test")
        assert isinstance(error, ASTError)

    def test_configuration_error_with_config_key(self):
        """Test ConfigurationError with configuration key."""
        error = ConfigurationError(
            "Missing required key",
            key="database_path",
        )
        assert error.key == "database_path"


# ============================================================================
# CycleDetectedError Tests
# ============================================================================


class TestCycleDetectedErrorBasic:
    """Test CycleDetectedError basic functionality."""

    def test_cycle_detected_error_default_message(self):
        """Test creating CycleDetectedError with default message."""
        error = CycleDetectedError()
        assert error.message == "Circular dependency detected"
        assert error.cycle == []

    def test_cycle_detected_error_custom_message(self):
        """Test creating CycleDetectedError with custom message."""
        error = CycleDetectedError("Graph has cycles")
        assert error.message == "Graph has cycles"

    def test_cycle_detected_error_with_cycle(self):
        """Test creating CycleDetectedError with cycle information."""
        cycle = ["A", "B", "C", "A"]
        error = CycleDetectedError(cycle=cycle)
        assert error.cycle == cycle

    def test_cycle_detected_error_cycle_default_empty(self):
        """Test cycle defaults to empty list."""
        error = CycleDetectedError()
        assert error.cycle == []

    def test_cycle_detected_error_inheritance(self):
        """Test CycleDetectedError inherits from ASTError."""
        error = CycleDetectedError()
        assert isinstance(error, ASTError)

    def test_cycle_detected_error_with_message_and_cycle(self):
        """Test CycleDetectedError with both message and cycle."""
        cycle = [1, 2, 3, 1]
        error = CycleDetectedError("Cycle found", cycle=cycle)
        assert error.message == "Cycle found"
        assert error.cycle == cycle


# ============================================================================
# Exception Raising and Catching
# ============================================================================


class TestExceptionRaisingAndCatching:
    """Test raising and catching exceptions."""

    def test_raise_and_catch_ast_error(self):
        """Test raising and catching ASTError."""
        with pytest.raises(ASTError):
            raise ASTError("Test error")

    def test_raise_and_catch_parse_error(self):
        """Test raising and catching ParseError."""
        with pytest.raises(ParseError):
            raise ParseError("Parse failed", file_path="test.py", line=10)

    def test_catch_parse_error_as_ast_error(self):
        """Test catching ParseError as ASTError."""
        with pytest.raises(ASTError):
            raise ParseError("Parse failed")

    def test_raise_analysis_error(self):
        """Test raising AnalysisError."""
        with pytest.raises(AnalysisError):
            raise AnalysisError("Analysis failed", analyzer_type="tester")

    def test_catch_analysis_error_as_ast_error(self):
        """Test catching AnalysisError as ASTError."""
        with pytest.raises(ASTError):
            raise AnalysisError("Analysis failed")

    def test_raise_storage_error(self):
        """Test raising StorageError."""
        with pytest.raises(StorageError):
            raise StorageError("Storage failed", operation="write")

    def test_catch_storage_error_as_ast_error(self):
        """Test catching StorageError as ASTError."""
        with pytest.raises(ASTError):
            raise StorageError("Storage failed")

    def test_raise_configuration_error(self):
        """Test raising ConfigurationError."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config invalid", key="timeout")

    def test_catch_configuration_error_as_ast_error(self):
        """Test catching ConfigurationError as ASTError."""
        with pytest.raises(ASTError):
            raise ConfigurationError("Config invalid")

    def test_raise_cycle_detected_error(self):
        """Test raising CycleDetectedError."""
        with pytest.raises(CycleDetectedError):
            raise CycleDetectedError(cycle=["A", "B", "A"])

    def test_catch_cycle_detected_error_as_ast_error(self):
        """Test catching CycleDetectedError as ASTError."""
        with pytest.raises(ASTError):
            raise CycleDetectedError()


# ============================================================================
# Exception Properties and Details
# ============================================================================


class TestExceptionProperties:
    """Test exception properties."""

    def test_ast_error_message_property(self):
        """Test ASTError message property."""
        error = ASTError("Test message")
        assert hasattr(error, "message")
        assert error.message == "Test message"

    def test_ast_error_details_property(self):
        """Test ASTError details property."""
        details = {"key": "value"}
        error = ASTError("Test", details=details)
        assert hasattr(error, "details")
        assert error.details == details

    def test_parse_error_all_properties(self):
        """Test ParseError has all expected properties."""
        error = ParseError("Error", file_path="test.py", line=5, column=2)
        assert hasattr(error, "message")
        assert hasattr(error, "file_path")
        assert hasattr(error, "line")
        assert hasattr(error, "column")

    def test_analysis_error_analyzer_property(self):
        """Test AnalysisError analyzer_type property."""
        error = AnalysisError("Error", analyzer_type="test_analyzer")
        assert hasattr(error, "analyzer_type")
        assert error.analyzer_type == "test_analyzer"

    def test_storage_error_operation_property(self):
        """Test StorageError operation property."""
        error = StorageError("Error", operation="write")
        assert hasattr(error, "operation")
        assert error.operation == "write"

    def test_configuration_error_key_property(self):
        """Test ConfigurationError key property."""
        error = ConfigurationError("Error", key="timeout")
        assert hasattr(error, "key")
        assert error.key == "timeout"

    def test_cycle_detected_error_cycle_property(self):
        """Test CycleDetectedError cycle property."""
        cycle = ["A", "B", "C"]
        error = CycleDetectedError(cycle=cycle)
        assert hasattr(error, "cycle")
        assert error.cycle == cycle


# ============================================================================
# Exception String Representations
# ============================================================================


class TestExceptionStringRepresentations:
    """Test exception string representations."""

    def test_ast_error_str(self):
        """Test ASTError string representation."""
        error = ASTError("Test error")
        str_repr = str(error)
        assert "Test error" in str_repr

    def test_parse_error_str_detailed(self):
        """Test ParseError provides detailed location info."""
        error = ParseError("Syntax error", file_path="module.py", line=42, column=10)
        str_repr = str(error)
        assert "module.py" in str_repr
        assert "42" in str_repr
        assert "10" in str_repr

    def test_analysis_error_str(self):
        """Test AnalysisError string representation."""
        error = AnalysisError("Failed to analyze")
        str_repr = str(error)
        assert "Failed to analyze" in str_repr

    def test_storage_error_str(self):
        """Test StorageError string representation."""
        error = StorageError("Cannot read file")
        str_repr = str(error)
        assert "Cannot read file" in str_repr

    def test_configuration_error_str(self):
        """Test ConfigurationError string representation."""
        error = ConfigurationError("Invalid timeout value")
        str_repr = str(error)
        assert "Invalid timeout value" in str_repr

    def test_cycle_detected_error_str(self):
        """Test CycleDetectedError string representation."""
        error = CycleDetectedError()
        str_repr = str(error)
        assert "Circular dependency" in str_repr


# ============================================================================
# Complex Exception Scenarios
# ============================================================================


class TestComplexExceptionScenarios:
    """Test complex exception scenarios."""

    def test_exception_chaining(self):
        """Test exception chaining."""
        original_error = ValueError("Original error")
        ast_error = ASTError("AST error", details={"original": str(original_error)})
        assert "original" in ast_error.details

    def test_multiple_exception_types_same_operation(self):
        """Test multiple exception types in same operation."""
        errors = [
            ParseError("Parse failed", file_path="file1.py"),
            AnalysisError("Analysis failed", analyzer_type="analyzer1"),
            StorageError("Storage failed", operation="write"),
        ]
        assert len(errors) == 3
        for error in errors:
            assert isinstance(error, ASTError)

    def test_exception_details_with_structured_data(self):
        """Test exception with structured details."""
        details = {
            "file": "test.py",
            "line": 10,
            "column": 5,
            "context": {"severity": "high", "category": "syntax"},
        }
        error = ASTError("Complex error", details=details)
        assert error.details["context"]["severity"] == "high"

    def test_parse_error_complex_path(self):
        """Test ParseError with complex file path."""
        error = ParseError(
            "Parse failed",
            file_path="src/module/submodule/file.py",
            line=100,
            column=50,
        )
        error_str = str(error)
        assert "src/module/submodule/file.py" in error_str

    def test_cycle_detected_with_complex_cycle(self):
        """Test CycleDetectedError with complex cycle."""
        cycle = ["module_a", "module_b", "module_c", "module_d", "module_a"]
        error = CycleDetectedError("Complex cycle", cycle=cycle)
        assert len(error.cycle) == 5
        assert error.cycle[0] == error.cycle[-1]
