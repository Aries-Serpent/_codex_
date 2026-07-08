"""
Tests for codex.analyze.static.analyzer module.

This module contains tests for the static analyzer.
"""


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
            file_path="test.py",
        )

        assert issue.rule == "E501", "rule is not valid"
        assert issue.severity == "warning", "severity is not valid"
        assert issue.line == 10, "line is not valid"
        assert issue.column == 80, "column is not valid"
        assert issue.message == "Line too long", "message is not valid"
        assert issue.file_path == "test.py", "file_path is not valid"


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
            file_path="module.py",
        )

        assert issue.tool == "bandit", "tool is not valid"
        assert issue.rule_id == "B101", "rule_id is not valid"
        assert issue.severity == "high", "severity is not valid"
        assert issue.line == 15, "line is not valid"


class TestComplexityMetrics:
    """Tests for ComplexityMetrics dataclass."""

    def test_basic_creation(self):
        """Test ComplexityMetrics basic creation."""
        from codex.analyze.static.analyzer import ComplexityMetrics

        metrics = ComplexityMetrics(cyclomatic=5.0, cognitive=3.0)

        assert metrics.cyclomatic == 5.0, "cyclomatic is not valid"
        assert metrics.cognitive == 3.0, "cognitive is not valid"
        assert metrics.halstead_difficulty is None, "halstead_difficulty is not valid"

    def test_with_halstead(self):
        """Test ComplexityMetrics with Halstead difficulty."""
        from codex.analyze.static.analyzer import ComplexityMetrics

        metrics = ComplexityMetrics(cyclomatic=10.0, cognitive=8.0, halstead_difficulty=15.5)

        assert metrics.halstead_difficulty == 15.5, "halstead_difficulty is not valid"


class TestFileAnalysis:
    """Tests for FileAnalysis dataclass."""

    def test_basic_creation(self):
        """Test FileAnalysis basic creation."""
        from codex.analyze.static.analyzer import ComplexityMetrics, FileAnalysis

        complexity = ComplexityMetrics(cyclomatic=3.0, cognitive=2.0)

        analysis = FileAnalysis(
            path="src/module.py",
            loc=100,
            sloc=80,
            complexity=complexity,
            imports=["os", "sys"],
            exports=["main"],
            lint_issues=[],
            security_issues=[],
        )

        assert analysis.path == "src/module.py", "path is not valid"
        assert analysis.loc == 100, "loc is not valid"
        assert analysis.sloc == 80, "sloc is not valid"
        assert len(analysis.imports) == 2, "Collection must not be empty"


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_max_file_size(self):
        """Test MAX_FILE_SIZE_KB constant."""
        from codex.analyze.static.analyzer import MAX_FILE_SIZE_KB

        assert MAX_FILE_SIZE_KB > 0, "MAX_FILE_SIZE_KB must be greater than zero"
        assert MAX_FILE_SIZE_KB == 1024, "MAX_FILE_SIZE_KB is not valid"

    def test_max_files(self):
        """Test MAX_FILES_TO_ANALYZE constant."""
        from codex.analyze.static.analyzer import MAX_FILES_TO_ANALYZE

        assert MAX_FILES_TO_ANALYZE > 0, "MAX_FILES_TO_ANALYZE must be greater than zero"
        assert MAX_FILES_TO_ANALYZE == 1000, "MAX_FILES_TO_ANALYZE is not valid"

    def test_trusted_dirs(self):
        """Test TRUSTED_TOOL_DIRS constant."""
        from codex.analyze.static.analyzer import DEFAULT_TRUSTED_DIRS

        assert isinstance(DEFAULT_TRUSTED_DIRS, list)
        assert "/usr/bin" in DEFAULT_TRUSTED_DIRS, "Condition must be true"

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.analyze.static.analyzer import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.analyze.static.analyzer", "name is not valid"
