"""
Tests for codex.ast.smells module.

This module contains tests for the code smell detection engine.
"""

import pytest
import ast
from pathlib import Path


class TestSmellSeverity:
    """Tests for SmellSeverity enum."""

    def test_info_value(self):
        """Test INFO severity value."""
        from codex.ast.smells import SmellSeverity
        
        assert SmellSeverity.INFO.value == "info"

    def test_warning_value(self):
        """Test WARNING severity value."""
        from codex.ast.smells import SmellSeverity
        
        assert SmellSeverity.WARNING.value == "warning"

    def test_error_value(self):
        """Test ERROR severity value."""
        from codex.ast.smells import SmellSeverity
        
        assert SmellSeverity.ERROR.value == "error"

    def test_critical_value(self):
        """Test CRITICAL severity value."""
        from codex.ast.smells import SmellSeverity
        
        assert SmellSeverity.CRITICAL.value == "critical"


class TestSmellCategory:
    """Tests for SmellCategory enum."""

    def test_complexity_value(self):
        """Test COMPLEXITY category value."""
        from codex.ast.smells import SmellCategory
        
        assert SmellCategory.COMPLEXITY.value == "complexity"

    def test_naming_value(self):
        """Test NAMING category value."""
        from codex.ast.smells import SmellCategory
        
        assert SmellCategory.NAMING.value == "naming"

    def test_structure_value(self):
        """Test STRUCTURE category value."""
        from codex.ast.smells import SmellCategory
        
        assert SmellCategory.STRUCTURE.value == "structure"

    def test_security_value(self):
        """Test SECURITY category value."""
        from codex.ast.smells import SmellCategory
        
        assert SmellCategory.SECURITY.value == "security"


class TestCodeSmell:
    """Tests for CodeSmell dataclass."""

    def test_basic_creation(self):
        """Test CodeSmell basic creation."""
        from codex.ast.smells import CodeSmell, SmellSeverity, SmellCategory
        
        smell = CodeSmell(
            rule_id="RULE001",
            message="Function too complex",
            severity=SmellSeverity.WARNING,
            category=SmellCategory.COMPLEXITY,
            file_path=Path("test.py"),
            line_start=10,
            line_end=50
        )
        
        assert smell.rule_id == "RULE001"
        assert smell.message == "Function too complex"
        assert smell.severity == SmellSeverity.WARNING
        assert smell.category == SmellCategory.COMPLEXITY
        assert smell.line_start == 10
        assert smell.line_end == 50
        assert smell.suggestion is None
        assert smell.metadata == {}

    def test_with_suggestion(self):
        """Test CodeSmell with suggestion."""
        from codex.ast.smells import CodeSmell, SmellSeverity, SmellCategory
        
        smell = CodeSmell(
            rule_id="RULE002",
            message="Variable name too short",
            severity=SmellSeverity.INFO,
            category=SmellCategory.NAMING,
            file_path=Path("module.py"),
            line_start=5,
            line_end=5,
            suggestion="Use a more descriptive name"
        )
        
        assert smell.suggestion == "Use a more descriptive name"

    def test_to_dict(self):
        """Test to_dict serialization."""
        from codex.ast.smells import CodeSmell, SmellSeverity, SmellCategory
        
        smell = CodeSmell(
            rule_id="RULE003",
            message="Duplicate code detected",
            severity=SmellSeverity.ERROR,
            category=SmellCategory.DUPLICATION,
            file_path=Path("src/main.py"),
            line_start=100,
            line_end=150,
            suggestion="Extract to common function",
            metadata={"similarity": 0.95}
        )
        
        result = smell.to_dict()
        
        assert result["rule_id"] == "RULE003"
        assert result["message"] == "Duplicate code detected"
        assert result["severity"] == "error"
        assert result["category"] == "duplication"
        assert result["file"] == "src/main.py"
        assert result["line_start"] == 100
        assert result["line_end"] == 150
        assert result["suggestion"] == "Extract to common function"
        assert result["metadata"]["similarity"] == 0.95


class TestSmellRule:
    """Tests for SmellRule dataclass."""

    def test_basic_creation(self):
        """Test SmellRule basic creation."""
        from codex.ast.smells import SmellRule, SmellSeverity, SmellCategory
        
        def dummy_detector(tree, path):
            return []
        
        rule = SmellRule(
            rule_id="COMPLEX001",
            name="High Complexity",
            description="Detects functions with high cyclomatic complexity",
            severity=SmellSeverity.WARNING,
            category=SmellCategory.COMPLEXITY,
            detector=dummy_detector
        )
        
        assert rule.rule_id == "COMPLEX001"
        assert rule.name == "High Complexity"
        assert rule.enabled is True
        assert callable(rule.detector)

    def test_disabled_rule(self):
        """Test SmellRule when disabled."""
        from codex.ast.smells import SmellRule, SmellSeverity, SmellCategory
        
        rule = SmellRule(
            rule_id="RULE999",
            name="Disabled Rule",
            description="This rule is disabled",
            severity=SmellSeverity.INFO,
            category=SmellCategory.STRUCTURE,
            detector=lambda t, p: [],
            enabled=False
        )
        
        assert rule.enabled is False


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.ast.smells import logger
        
        assert logger is not None
        assert logger.name == "codex.ast.smells"
