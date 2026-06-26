"""
Test Codex CLI Core Module

Comprehensive unit tests for the main CLI functionality in src/codex/cli.py
"""

from __future__ import annotations

from pathlib import Path

import click
import pytest
from click.testing import CliRunner


def _get_cli_module():
    """Helper to get the Click CLI module from sys.modules."""
    import sys

    return sys.modules.get("codex._cli_click")


@pytest.fixture
def cli_module():
    """Pytest fixture providing access to the Click CLI module."""
    module = _get_cli_module()
    if module is None:
        pytest.skip("Click CLI module not loaded")
    return module


class TestCLIImports:
    """Tests for CLI module imports."""

    def test_import_cli(self) -> None:
        from codex.cli import cli

        assert cli is not None, "cli must be initialized"

    def test_import_logs_group(self) -> None:
        from codex.cli import logs

        assert logs is not None, "logs must be initialized"

    def test_import_tokenizer_group(self) -> None:
        from codex.cli import tokenizer_group

        assert tokenizer_group is not None, "tokenizer_group must be initialized"

    def test_import_repro_group(self) -> None:
        from codex.cli import repro_group

        assert repro_group is not None, "repro_group must be initialized"

    def test_import_allowed_tasks(self, cli_module) -> None:
        ALLOWED_TASKS = getattr(cli_module, "ALLOWED_TASKS", None)
        assert isinstance(ALLOWED_TASKS, dict)

    def test_import_tools_dir(self, cli_module) -> None:
        TOOLS_DIR = getattr(cli_module, "TOOLS_DIR", None)
        assert isinstance(TOOLS_DIR, Path)


class TestAllowedTasks:
    """Tests for ALLOWED_TASKS dictionary."""

    def test_contains_ingest(self, cli_module) -> None:
        ALLOWED_TASKS = getattr(cli_module, "ALLOWED_TASKS", None)
        assert "ingest" in ALLOWED_TASKS, "Condition must be true"

    def test_contains_ci(self, cli_module) -> None:
        ALLOWED_TASKS = getattr(cli_module, "ALLOWED_TASKS", None)
        assert "ci" in ALLOWED_TASKS, "Condition must be true"

    def test_contains_pool_fix(self, cli_module) -> None:
        ALLOWED_TASKS = getattr(cli_module, "ALLOWED_TASKS", None)
        assert "pool-fix" in ALLOWED_TASKS, "Condition must be true"

    def test_task_has_callable_and_description(self, cli_module) -> None:
        ALLOWED_TASKS = getattr(cli_module, "ALLOWED_TASKS", None)
        for name, (func, desc) in ALLOWED_TASKS.items():
            assert callable(func), f"{name} function is not callable"
            assert isinstance(desc, str), f"{name} description is not a string"


class TestCLIHelp:
    """Tests for CLI help output."""

    def test_cli_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Codex CLI" in result.output, "Result must not be empty"

    def test_logs_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["logs", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tasks_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["tasks", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_run_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["run", "--help"])
        assert result.exit_code == 0, "Result must not be empty"


class TestTasksCommand:
    """Tests for 'tasks' command."""

    def test_list_tasks(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["tasks"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Whitelisted maintenance tasks" in result.output, "Result must not be empty"

    def test_tasks_lists_ingest(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["tasks"])
        assert "ingest" in result.output, "Result must not be empty"

    def test_tasks_lists_ci(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["tasks"])
        assert "ci" in result.output, "Result must not be empty"


class TestRunCommand:
    """Tests for 'run' command."""

    def test_run_without_task_shows_whitelist(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["run"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Whitelisted maintenance tasks" in result.output, "Result must not be empty"

    def test_run_invalid_task_fails(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["run", "invalid_task"])
        assert result.exit_code != 0, "Result must not be empty"
        assert "not allowed" in result.output.lower(), "Result must not be empty"


class TestLogsGroup:
    """Tests for 'logs' command group."""

    def test_logs_init_command_exists(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["logs", "init", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_logs_ingest_command_exists(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["logs", "ingest", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_logs_query_command_exists(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["logs", "query", "--help"])
        assert result.exit_code == 0, "Result must not be empty"


class TestTokenizerGroup:
    """Tests for 'tokenizer' command group."""

    def test_tokenizer_encode_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["tokenizer", "encode", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_decode_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["tokenizer", "decode", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_stats_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["tokenizer", "stats", "--help"])
        assert result.exit_code == 0, "Result must not be empty"


class TestReproGroup:
    """Tests for 'repro' command group."""

    def test_repro_seed_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["repro", "seed", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--seed" in result.output, "Result must not be empty"

    def test_repro_env_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["repro", "env", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_repro_system_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["repro", "system", "--help"])
        assert result.exit_code == 0, "Result must not be empty"


class TestSessionLoggerCommand:
    """Tests for 'session-logger' command."""

    def test_session_logger_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["session-logger", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--role" in result.output, "Result must not be empty"
        assert "--message" in result.output, "Result must not be empty"


class TestViewerCommand:
    """Tests for 'viewer' command."""

    def test_viewer_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["viewer", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--session-id" in result.output, "Result must not be empty"
        assert "--format" in result.output, "Result must not be empty"


class TestQueryLogsCommand:
    """Tests for 'query-logs' command."""

    def test_query_logs_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["query-logs", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--search" in result.output, "Result must not be empty"
        assert "--role" in result.output, "Result must not be empty"


class TestValidateEnvCommand:
    """Tests for 'validate-env' command."""

    def test_validate_env_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["validate-env", "--help"])
        assert result.exit_code == 0, "Result must not be empty"


class TestInitDbCommand:
    """Tests for 'init-db' command."""

    def test_init_db_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["init-db", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--db-path" in result.output, "Result must not be empty"


class TestExportEnvCommand:
    """Tests for 'export-env' command."""

    def test_export_env_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["export-env", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--format" in result.output, "Result must not be empty"
        assert "--output" in result.output, "Result must not be empty"


class TestListSessionsCommand:
    """Tests for 'list-sessions' command."""

    def test_list_sessions_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["list-sessions", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--limit" in result.output, "Result must not be empty"
        assert "--format" in result.output, "Result must not be empty"


class TestCleanLogsCommand:
    """Tests for 'clean-logs' command."""

    def test_clean_logs_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["clean-logs", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--older-than" in result.output, "Result must not be empty"
        assert "--dry-run" in result.output, "Result must not be empty"
        assert "--yes" in result.output, "Result must not be empty"


class TestDuplicationGroup:
    """Tests for 'duplication' command group."""

    def test_duplication_check_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["duplication", "check", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--min-lines" in result.output, "Result must not be empty"
        assert "--threshold" in result.output, "Result must not be empty"

    def test_duplication_report_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["duplication", "report", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--output" in result.output, "Result must not be empty"

    def test_duplication_compare_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["duplication", "compare", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--baseline" in result.output, "Result must not be empty"


class TestTrainCommand:
    """Tests for 'train' command."""

    def test_train_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["train", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--engine" in result.output, "Result must not be empty"


class TestResumeCommand:
    """Tests for 'resume' command."""

    def test_resume_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["resume", "--help"])
        assert result.exit_code == 0, "Result must not be empty"


class TestMissingCommand:
    """Tests for _missing_command function."""

    def test_missing_command_creation(self, cli_module) -> None:
        _missing_command = getattr(cli_module, "_missing_command", None)
        if _missing_command:
            cmd = _missing_command("test", "Test message", "Test help")
            assert isinstance(cmd, click.Command)
            assert cmd.name == "test", "name is not valid"
        else:
            pytest.skip("_missing_command not available")


class TestEmitGroupHelp:
    """Tests for _emit_group_help function."""

    def test_emit_group_help_exists(self, cli_module) -> None:
        _emit_group_help = getattr(cli_module, "_emit_group_help", None)
        assert callable(_emit_group_help), "Condition must be true"


class TestRegisterClickCommand:
    """Tests for _register_click_command function."""

    def test_register_click_command_exists(self, cli_module) -> None:
        _register_click_command = getattr(cli_module, "_register_click_command", None)
        assert callable(_register_click_command), "Condition must be true"


class TestRegisterTyperApp:
    """Tests for _register_typer_app function."""

    def test_register_typer_app_exists(self, cli_module) -> None:
        _register_typer_app = getattr(cli_module, "_register_typer_app", None)
        assert callable(_register_typer_app), "Condition must be true"


class TestCLIWithoutSubcommand:
    """Tests for CLI invoked without subcommand."""

    def test_cli_without_subcommand_shows_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Available subcommands" in result.output, "Result must not be empty"


class TestWorkflowScanCommand:
    """Tests for 'workflow-scan' command."""

    def test_workflow_scan_help(self) -> None:
        from codex.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["workflow-scan", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "--workflows-dir" in result.output or "-d" in result.output, "Result must not be empty"


class TestPrintTaskWhitelist:
    """Tests for _print_task_whitelist function."""

    def test_print_task_whitelist_exists(self, cli_module) -> None:
        _print_task_whitelist = getattr(cli_module, "_print_task_whitelist", None)
        assert callable(_print_task_whitelist), "Condition must be true"


class TestRunIngest:
    """Tests for _run_ingest function."""

    def test_run_ingest_exists(self, cli_module) -> None:
        _run_ingest = getattr(cli_module, "_run_ingest", None)
        assert callable(_run_ingest), "Condition must be true"


class TestRunCi:
    """Tests for _run_ci function."""

    def test_run_ci_exists(self, cli_module) -> None:
        _run_ci = getattr(cli_module, "_run_ci", None)
        assert callable(_run_ci), "Condition must be true"


class TestFixPool:
    """Tests for _fix_pool function."""

    def test_fix_pool_exists(self) -> None:
        from codex.cli import _fix_pool

        assert callable(_fix_pool), "Condition must be true"

    def test_fix_pool_with_none(self) -> None:
        from codex.cli import _fix_pool

        # Should not raise
        _fix_pool(None)
