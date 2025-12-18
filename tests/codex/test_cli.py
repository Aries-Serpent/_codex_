"""
Tests for the Codex CLI module.

Tests cover:
- CLI commands and argument parsing
- PR operator functionality
- Integration with pipeline components
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestCLIBasics:
    """Tests for basic CLI functionality."""

    def test_cli_module_imports(self):
        """Test that CLI module can be imported."""
        from src.codex.cli import main
        assert callable(main)

    def test_cli_main_function_exists(self):
        """Test that main entry point exists."""
        from src.codex.cli.main import main
        assert callable(main)


class TestPROperator:
    """Tests for PR operator functionality."""

    def test_sanitize_branch_name(self):
        """Test branch name sanitization."""
        from src.codex.cli.pr_operator import _sanitize_branch_name
        
        assert _sanitize_branch_name("simple") == "simple"
        assert _sanitize_branch_name("with spaces") == "with-spaces"
        assert _sanitize_branch_name("special!@#chars") == "special-chars"
        assert _sanitize_branch_name("---multiple---dashes---") == "multiple-dashes"

    def test_sanitize_branch_name_length(self):
        """Test branch name length limiting."""
        from src.codex.cli.pr_operator import _sanitize_branch_name
        
        long_name = "a" * 200
        result = _sanitize_branch_name(long_name)
        
        assert len(result) <= 100

    def test_generate_pr_body(self):
        """Test PR body generation."""
        from src.codex.cli.pr_operator import _generate_pr_body
        
        body = _generate_pr_body(
            snapshot_id="test-123",
            intent_summary="Test script",
            confidence=0.85,
            tier_a_count=5,
            tier_b_count=2,
            tier_c_count=1,
            verification_result="pass",
            security_issues=0,
        )
        
        assert "test-123" in body
        assert "Test script" in body
        assert "85%" in body
        assert "✅" in body

    def test_generate_pr_body_with_failures(self):
        """Test PR body generation with failures."""
        from src.codex.cli.pr_operator import _generate_pr_body
        
        body = _generate_pr_body(
            snapshot_id="test-123",
            intent_summary="Test script",
            confidence=0.5,
            tier_a_count=0,
            tier_b_count=0,
            tier_c_count=0,
            verification_result="fail",
            security_issues=5,
        )
        
        assert "❌" in body

    def test_pr_config_defaults(self):
        """Test PRConfig default values."""
        from src.codex.cli.pr_operator import PRConfig
        
        config = PRConfig(owner="test", repo="repo")
        
        assert config.base_branch == "main"
        assert config.draft is True
        assert "copilot:automated" in config.labels

    def test_pr_content_creation(self):
        """Test PRContent creation."""
        from src.codex.cli.pr_operator import PRContent
        
        content = PRContent(
            title="Test PR",
            body="Test body",
            branch_name="test-branch",
            snapshot_id="snap-123",
        )
        
        assert content.title == "Test PR"
        assert content.snapshot_id == "snap-123"

    def test_pr_operator_generate_content(self):
        """Test PROperator.generate_pr_content."""
        from src.codex.cli.pr_operator import PROperator, PRConfig
        
        config = PRConfig(owner="test", repo="repo")
        operator = PROperator(config)
        
        content = operator.generate_pr_content(
            snapshot_id="snap-123",
            intent_summary="CLI tool for data processing",
            confidence=0.9,
            tier_a_count=3,
        )
        
        assert "snap-123" in content.branch_name
        assert "CLI tool" in content.title or "snap-123" in content.title
        assert content.snapshot_id == "snap-123"

    def test_pr_operator_save_content(self, tmp_path: Path):
        """Test saving PR content to files."""
        from src.codex.cli.pr_operator import PROperator, PRConfig, PRContent
        
        config = PRConfig(owner="test", repo="repo")
        operator = PROperator(config)
        
        content = PRContent(
            title="Test PR",
            body="Test body content",
            branch_name="test-branch",
            snapshot_id="snap-123",
        )
        
        output_dir = tmp_path / "pr-output"
        result = operator.save_pr_content(content, output_dir)
        
        assert result.exists()
        assert (output_dir / "pr-metadata.json").exists()

    def test_pr_result_success(self):
        """Test PRResult success state."""
        from src.codex.cli.pr_operator import PRResult
        
        result = PRResult(
            success=True,
            pr_number=123,
            pr_url="https://github.com/test/repo/pull/123",
        )
        
        assert result.success
        assert result.pr_number == 123
        assert "123" in result.pr_url

    def test_pr_result_failure(self):
        """Test PRResult failure state."""
        from src.codex.cli.pr_operator import PRResult
        
        result = PRResult(
            success=False,
            errors=["Authentication failed"],
        )
        
        assert not result.success
        assert "Authentication failed" in result.errors

    def test_pr_operator_without_github(self):
        """Test PROperator behavior without GitHub access."""
        from src.codex.cli.pr_operator import PROperator, PRConfig, PRContent
        
        with patch.dict("os.environ", {}, clear=True):
            config = PRConfig(owner="test", repo="repo")
            operator = PROperator(config)
            
            content = PRContent(
                title="Test",
                body="Body",
                branch_name="branch",
            )
            
            result = operator.create_pr(content)
            
            assert not result.success
            assert len(result.errors) > 0


class TestRuntimeComponents:
    """Tests for runtime analysis components."""

    def test_sandbox_config_defaults(self):
        """Test SandboxConfig default values."""
        from src.codex.analyze.runtime.sandbox import SandboxConfig
        
        config = SandboxConfig()
        
        assert config.timeout_seconds == 60
        assert config.memory_limit_mb == 512
        assert config.network_enabled is False

    def test_sandbox_config_custom(self):
        """Test SandboxConfig custom values."""
        from src.codex.analyze.runtime.sandbox import SandboxConfig
        
        config = SandboxConfig(
            timeout_seconds=30,
            memory_limit_mb=256,
            network_enabled=True,
        )
        
        assert config.timeout_seconds == 30
        assert config.memory_limit_mb == 256
        assert config.network_enabled is True

    def test_sandbox_manager_initialization(self):
        """Test SandboxManager initialization."""
        from src.codex.analyze.runtime.sandbox import SandboxManager, SandboxConfig
        
        config = SandboxConfig()
        manager = SandboxManager(config)
        
        assert manager.config == config

    def test_sandbox_manager_invalid_config(self):
        """Test SandboxManager with invalid config."""
        from src.codex.analyze.runtime.sandbox import SandboxManager, SandboxConfig
        
        config = SandboxConfig(timeout_seconds=-1)
        
        with pytest.raises(ValueError):
            SandboxManager(config)

    def test_sandbox_execute_simple_script(self, tmp_path: Path):
        """Test executing a simple script."""
        from src.codex.analyze.runtime.sandbox import SandboxManager
        
        script = tmp_path / "test.py"
        script.write_text("print('hello')\n", encoding="utf-8")
        
        manager = SandboxManager()
        result = manager.execute(script)
        
        assert result.exit_code == 0
        assert "hello" in result.stdout
        assert not result.timed_out

    def test_sandbox_execute_with_error(self, tmp_path: Path):
        """Test executing a script with error."""
        from src.codex.analyze.runtime.sandbox import SandboxManager
        
        script = tmp_path / "test.py"
        script.write_text("raise ValueError('test error')\n", encoding="utf-8")
        
        manager = SandboxManager()
        result = manager.execute(script)
        
        assert result.exit_code != 0
        assert "ValueError" in result.stderr or "error" in result.stderr.lower()

    def test_sandbox_execute_nonexistent(self, tmp_path: Path):
        """Test executing nonexistent script."""
        from src.codex.analyze.runtime.sandbox import SandboxManager
        
        manager = SandboxManager()
        
        with pytest.raises(FileNotFoundError):
            manager.execute(tmp_path / "nonexistent.py")

    def test_execution_result_to_dict(self, tmp_path: Path):
        """Test ExecutionResult serialization."""
        from src.codex.analyze.runtime.sandbox import SandboxManager
        
        script = tmp_path / "test.py"
        script.write_text("print('test')\n", encoding="utf-8")
        
        manager = SandboxManager()
        result = manager.execute(script)
        data = result.to_dict()
        
        assert "exit_code" in data
        assert "stdout_snapshot" in data
        assert "duration_ms" in data

    def test_runtime_tracer_initialization(self):
        """Test RuntimeTracer initialization."""
        from src.codex.analyze.runtime.tracer import RuntimeTracer
        
        tracer = RuntimeTracer("test-snapshot")
        
        assert tracer.snapshot_id == "test-snapshot"

    def test_runtime_tracer_find_entry_point(self, tmp_path: Path):
        """Test finding entry point."""
        from src.codex.analyze.runtime.tracer import RuntimeTracer
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("pass\n", encoding="utf-8")
        
        tracer = RuntimeTracer("test-snapshot")
        entry = tracer._find_entry_point(source_dir)
        
        assert entry == "main.py"

    def test_runtime_tracer_find_entry_point_fallback(self, tmp_path: Path):
        """Test entry point fallback to first .py file."""
        from src.codex.analyze.runtime.tracer import RuntimeTracer
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "custom.py").write_text("pass\n", encoding="utf-8")
        
        tracer = RuntimeTracer("test-snapshot")
        entry = tracer._find_entry_point(source_dir)
        
        assert entry == "custom.py"

    def test_runtime_report_to_dict(self):
        """Test RuntimeReport serialization."""
        from src.codex.analyze.runtime.tracer import RuntimeReport
        from datetime import datetime, timezone
        
        report = RuntimeReport(
            snapshot_id="test-123",
            timestamp=datetime.now(timezone.utc),
            sandbox_config={"timeout_seconds": 60},
            execution_results=[{"exit_code": 0}],
        )
        
        data = report.to_dict()
        
        assert data["snapshot_id"] == "test-123"
        assert "timestamp" in data
        assert len(data["execution_results"]) == 1

    def test_runtime_report_save(self, tmp_path: Path):
        """Test saving RuntimeReport to file."""
        from src.codex.analyze.runtime.tracer import RuntimeReport
        from datetime import datetime, timezone
        
        report = RuntimeReport(
            snapshot_id="test-123",
            timestamp=datetime.now(timezone.utc),
            sandbox_config={},
            execution_results=[],
        )
        
        output_path = tmp_path / "runtime-report.json"
        report.save(output_path)
        
        assert output_path.exists()
