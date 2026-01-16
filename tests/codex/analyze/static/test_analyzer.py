"""
Tests for codex.analyze.static.analyzer module.

This module contains tests for the static analyzer.
"""

import pytest
from pathlib import Path


class TestLintIssue:
    """Tests for LintIssue dataclass."""

    def test_basic_creation(self):
        """Test LintIssue basic creation."""
        from codex.analyze.static.analyzer import LintIssue
        
        issue = LintIssue(
            rule="E501",
            severity="warning",
            line=10,
            column=80,
            message="Line too long",
            file_path="test.py"
        )
        
        assert issue.rule == "E501"
        assert issue.severity == "warning"
        assert issue.line == 10
        assert issue.column == 80
        assert issue.message == "Line too long"
        assert issue.file_path == "test.py"


class TestSecurityIssue:
    """Tests for SecurityIssue dataclass."""

    def test_basic_creation(self):
        """Test SecurityIssue basic creation."""
        from codex.analyze.static.analyzer import SecurityIssue
        
        issue = SecurityIssue(
            tool="bandit",
            rule_id="B101",
            severity="high",
            line=15,
            message="Use of assert detected",
            file_path="module.py"
        )
        
        assert issue.tool == "bandit"
        assert issue.rule_id == "B101"
        assert issue.severity == "high"
        assert issue.line == 15


class TestComplexityMetrics:
    """Tests for ComplexityMetrics dataclass."""

    def test_basic_creation(self):
        """Test ComplexityMetrics basic creation."""
        from codex.analyze.static.analyzer import ComplexityMetrics
        
        metrics = ComplexityMetrics(
            cyclomatic=5.0,
            cognitive=3.0
        )
        
        assert metrics.cyclomatic == 5.0
        assert metrics.cognitive == 3.0
        assert metrics.halstead_difficulty is None

    def test_with_halstead(self):
        """Test ComplexityMetrics with Halstead difficulty."""
        from codex.analyze.static.analyzer import ComplexityMetrics
        
        metrics = ComplexityMetrics(
            cyclomatic=10.0,
            cognitive=8.0,
            halstead_difficulty=15.5
        )
        
        assert metrics.halstead_difficulty == 15.5


class TestFileAnalysis:
    """Tests for FileAnalysis dataclass."""

    def test_basic_creation(self):
        """Test FileAnalysis basic creation."""
        from codex.analyze.static.analyzer import FileAnalysis, ComplexityMetrics
        
        complexity = ComplexityMetrics(cyclomatic=3.0, cognitive=2.0)
        
        analysis = FileAnalysis(
            path="src/module.py",
            loc=100,
            sloc=80,
            complexity=complexity,
            imports=["os", "sys"],
            exports=["main"],
            lint_issues=[],
            security_issues=[]
        )
        
        assert analysis.path == "src/module.py"
        assert analysis.loc == 100
        assert analysis.sloc == 80
        assert len(analysis.imports) == 2


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_max_file_size(self):
        """Test MAX_FILE_SIZE_KB constant."""
        from codex.analyze.static.analyzer import MAX_FILE_SIZE_KB
        
        assert MAX_FILE_SIZE_KB > 0
        assert MAX_FILE_SIZE_KB == 1024

    def test_max_files(self):
        """Test MAX_FILES_TO_ANALYZE constant."""
        from codex.analyze.static.analyzer import MAX_FILES_TO_ANALYZE
        
        assert MAX_FILES_TO_ANALYZE > 0
        assert MAX_FILES_TO_ANALYZE == 1000

    def test_trusted_dirs(self):
        """Test TRUSTED_TOOL_DIRS constant."""
        from codex.analyze.static.analyzer import DEFAULT_TRUSTED_DIRS
        
        assert isinstance(DEFAULT_TRUSTED_DIRS, list)
        assert "/usr/bin" in DEFAULT_TRUSTED_DIRS

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.analyze.static.analyzer import logger
        
        assert logger is not None
        assert logger.name == "codex.analyze.static.analyzer"
