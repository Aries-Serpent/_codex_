"""
Tests for codex.ast.smells module.

This module contains tests for the code smell detection engine.
"""

from pathlib import Path


class TestSmellSeverity:
    """Tests for SmellSeverity enum."""

    def test_info_value(self):
        """Test INFO severity value."""
        from codex.ast.smells import SmellSeverity

        assert SmellSeverity.INFO.value == "info", "Value must be initialized"

    def test_warning_value(self):
        """Test WARNING severity value."""
        from codex.ast.smells import SmellSeverity

        assert SmellSeverity.WARNING.value == "warning", "Value must be initialized"

    def test_error_value(self):
        """Test ERROR severity value."""
        from codex.ast.smells import SmellSeverity

        assert SmellSeverity.ERROR.value == "error", "Value must be initialized"

    def test_critical_value(self):
        """Test CRITICAL severity value."""
        from codex.ast.smells import SmellSeverity

        assert SmellSeverity.CRITICAL.value == "critical", "Value must be initialized"


class TestSmellCategory:
    """Tests for SmellCategory enum."""

    def test_complexity_value(self):
        """Test COMPLEXITY category value."""
        from codex.ast.smells import SmellCategory

        assert SmellCategory.COMPLEXITY.value == "complexity", "Value must be initialized"

    def test_naming_value(self):
        """Test NAMING category value."""
        from codex.ast.smells import SmellCategory

        assert SmellCategory.NAMING.value == "naming", "Value must be initialized"

    def test_structure_value(self):
        """Test STRUCTURE category value."""
        from codex.ast.smells import SmellCategory

        assert SmellCategory.STRUCTURE.value == "structure", "Value must be initialized"

    def test_security_value(self):
        """Test SECURITY category value."""
        from codex.ast.smells import SmellCategory

        assert SmellCategory.SECURITY.value == "security", "Value must be initialized"


class TestCodeSmell:
    """Tests for CodeSmell dataclass."""

    def test_basic_creation(self):
        """Test CodeSmell basic creation."""
        from codex.ast.smells import CodeSmell, SmellCategory, SmellSeverity

        smell = CodeSmell(
            rule_id="RULE001",
            message="Function too complex",
            severity=SmellSeverity.WARNING,
            category=SmellCategory.COMPLEXITY,
            file_path=Path("test.py"),
            line_start=10,
            line_end=50,
        )

        assert smell.rule_id == "RULE001", "rule_id is not valid"
        assert smell.message == "Function too complex", "message is not valid"
        assert smell.severity == SmellSeverity.WARNING, "severity is not valid"
        assert smell.category == SmellCategory.COMPLEXITY, "category is not valid"
        assert smell.line_start == 10, "line_start is not valid"
        assert smell.line_end == 50, "line_end is not valid"
        assert smell.suggestion is None, "suggestion is not valid"
        assert smell.metadata == {}, "Data must not be empty"

    def test_with_suggestion(self):
        """Test CodeSmell with suggestion."""
        from codex.ast.smells import CodeSmell, SmellCategory, SmellSeverity

        smell = CodeSmell(
            rule_id="RULE002",
            message="Variable name too short",
            severity=SmellSeverity.INFO,
            category=SmellCategory.NAMING,
            file_path=Path("module.py"),
            line_start=5,
            line_end=5,
            suggestion="Use a more descriptive name",
        )

        assert smell.suggestion == "Use a more descriptive name", "suggestion is not valid"

    def test_to_dict(self):
        """Test to_dict serialization."""
        from codex.ast.smells import CodeSmell, SmellCategory, SmellSeverity

        smell = CodeSmell(
            rule_id="RULE003",
            message="Duplicate code detected",
            severity=SmellSeverity.ERROR,
            category=SmellCategory.DUPLICATION,
            file_path=Path("src/main.py"),
            line_start=100,
            line_end=150,
            suggestion="Extract to common function",
            metadata={"similarity": 0.95},
        )

        result = smell.to_dict()

        assert result["rule_id"] == "RULE003", "Result must not be empty"
        assert result["message"] == "Duplicate code detected", "Result must not be empty"
        assert result["severity"] == "error", "Result must not be empty"
        assert result["category"] == "duplication", "Result must not be empty"
        assert result["file"] == "src/main.py", "Result must not be empty"
        assert result["line_start"] == 100, "Result must not be empty"
        assert result["line_end"] == 150, "Result must not be empty"
        assert result["suggestion"] == "Extract to common function", "Result must not be empty"
        assert result["metadata"]["similarity"] == 0.95, "Result must not be empty"


class TestSmellRule:
    """Tests for SmellRule dataclass."""

    def test_basic_creation(self):
        """Test SmellRule basic creation."""
        from codex.ast.smells import SmellCategory, SmellRule, SmellSeverity

        def dummy_detector(tree, path):
            return []

        rule = SmellRule(
            rule_id="COMPLEX001",
            name="High Complexity",
            description="Detects functions with high cyclomatic complexity",
            severity=SmellSeverity.WARNING,
            category=SmellCategory.COMPLEXITY,
            detector=dummy_detector,
        )

        assert rule.rule_id == "COMPLEX001", "rule_id is not valid"
        assert rule.name == "High Complexity", "name is not valid"
        assert rule.enabled is True, "enabled is not valid"
        assert callable(rule.detector), "Condition must be true"

    def test_disabled_rule(self):
        """Test SmellRule when disabled."""
        from codex.ast.smells import SmellCategory, SmellRule, SmellSeverity

        rule = SmellRule(
            rule_id="RULE999",
            name="Disabled Rule",
            description="This rule is disabled",
            severity=SmellSeverity.INFO,
            category=SmellCategory.STRUCTURE,
            detector=lambda t, p: [],
            enabled=False,
        )

        assert rule.enabled is False, "enabled is not valid"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.ast.smells import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.ast.smells", "name is not valid"
