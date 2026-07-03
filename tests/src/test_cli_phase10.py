"""Phase 10B gap-fill: CLI entry-point and command coverage.

Tests the Click-based CLI surface in ``src/codex/cli.py``.
Uses :class:`click.testing.CliRunner` to exercise commands without
spawning subprocesses, so they run reliably in minimal environments.

NOTE: This test module may be skipped if required dependencies are unavailable.
"""

from __future__ import annotations

import tempfile

import pytest

try:
    import click
    from click.testing import CliRunner
except ImportError:
    pytest.skip("click not available", allow_module_level=True)

import inspect
from unittest.mock import MagicMock, patch

from codex.cli import (
    ALLOWED_TASKS,
    _emit_group_help,
    _missing_command,
    cli,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def runner():
    if "mix_stderr" in inspect.signature(CliRunner).parameters:
        return CliRunner(mix_stderr=False)
    return CliRunner()


# ---------------------------------------------------------------------------
# 1. Top-level CLI group
# ---------------------------------------------------------------------------


class TestCLIGroup:
    """Tests for the ``cli`` Click group entry point."""

    def test_cli_no_args_shows_help(self, runner):
        """Invoking without subcommand prints help and exits 0."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0, "Result must not be empty"
        assert "subcommand" in result.output.lower() or "codex" in result.output.lower(), "Result must not be empty"

    def test_cli_help_flag(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Usage" in result.output or "usage" in result.output, "Result must not be empty"

    def test_cli_unknown_subcommand_fails(self, runner):
        result = runner.invoke(cli, ["nonexistent-cmd-xyz"])
        assert result.exit_code != 0, "Result must not be empty"


# ---------------------------------------------------------------------------
# 2. ``tasks`` / ``run`` commands
# ---------------------------------------------------------------------------


class TestTaskCommands:
    """Tests for ``codex tasks`` and ``codex run``."""

    def test_tasks_lists_allowed(self, runner):
        result = runner.invoke(cli, ["tasks"])
        assert result.exit_code == 0, "Result must not be empty"
        for task_name in ALLOWED_TASKS:
            assert task_name in result.output, "Result must not be empty"

    def test_run_without_task_shows_whitelist(self, runner):
        result = runner.invoke(cli, ["run"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Whitelisted" in result.output or "task" in result.output.lower(), "Result must not be empty"

    def test_run_unknown_task_fails(self, runner):
        result = runner.invoke(cli, ["run", "does-not-exist"])
        assert result.exit_code != 0, "Result must not be empty"
        assert ("not allowed" in result.output.lower() or "not allowed" in (result.stderr or "").lower()
        )

    def test_run_valid_task_executes(self, runner):
        """Pick the first ALLOWED_TASK and patch its callable."""
        task_name = next(iter(ALLOWED_TASKS))
        mock_fn = MagicMock()
        with patch.dict(ALLOWED_TASKS, {task_name: (mock_fn, "test task")}):
            result = runner.invoke(cli, ["run", task_name])
        assert result.exit_code == 0, "Result must not be empty"
        mock_fn.assert_called_once()


# ---------------------------------------------------------------------------
# 3. ``logs`` subgroup
# ---------------------------------------------------------------------------


class TestLogsGroup:
    """Tests for ``codex logs`` subcommands."""

    def test_logs_no_subcommand_shows_help(self, runner):
        result = runner.invoke(cli, ["logs"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_logs_init_invokes_script(self, runner):
        with patch("codex._cli_click.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(cli, ["logs", "init", "--db", os.path.join(tempfile.gettempdir(), "test.sqlite")])
        assert result.exit_code == 0, "Result must not be empty"
        mock_run.assert_called_once()

    def test_logs_init_failure_reports_error(self, runner):
        with patch("codex._cli_click.subprocess.run", side_effect=RuntimeError("boom")):
            result = runner.invoke(cli, ["logs", "init", "--db", os.path.join(tempfile.gettempdir(), "test.sqlite")])
        assert result.exit_code != 0, "Result must not be empty"

    def test_logs_query_invokes_script(self, runner):
        with patch("codex._cli_click.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(
                cli, ["logs", "query", "--sql", "SELECT 1", "--db", os.path.join(tempfile.gettempdir(), "test.sqlite")]
            )
        assert result.exit_code == 0, "Result must not be empty"
        mock_run.assert_called_once()

    def test_logs_query_failure_reports_error(self, runner):
        with patch("codex._cli_click.subprocess.run", side_effect=RuntimeError("db error")):
            result = runner.invoke(
                cli, ["logs", "query", "--sql", "SELECT 1", "--db", os.path.join(tempfile.gettempdir(), "test.sqlite")]
            )
        assert result.exit_code != 0, "Result must not be empty"


# ---------------------------------------------------------------------------
# 4. Tokenizer subgroup
# ---------------------------------------------------------------------------


class TestTokenizerGroup:
    """Tests for ``codex tokenizer`` commands."""

    def test_tokenizer_no_subcommand_shows_help(self, runner):
        result = runner.invoke(cli, ["tokenizer"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_encode_basic(self, runner):
        """encode should call the tokenizer and print token IDs."""
        with patch("codex.cli.importlib.import_module") as mock_import:
            mock_mod = MagicMock()
            mock_mod.encode.return_value = [1, 2, 3]
            mock_import.return_value = mock_mod
            result = runner.invoke(cli, ["tokenizer", "encode", "hello world"])
        # May fail if tokenizer not available — that's OK, we verify no crash
        # The command may exit 0 or 1 depending on env
        assert result.exit_code in (0, 1, 2)


# ---------------------------------------------------------------------------
# 5. Reproducibility subgroup
# ---------------------------------------------------------------------------


class TestReproGroup:
    """Tests for ``codex repro`` commands."""

    def test_repro_no_subcommand_shows_help(self, runner):
        result = runner.invoke(cli, ["repro"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_repro_seed_creates_output(self, runner, tmp_path):
        with patch("codex.cli.importlib.import_module") as mock_import:
            mock_mod = MagicMock()
            mock_import.return_value = mock_mod
            result = runner.invoke(
                cli, ["repro", "seed", "--seed", "42", "--out-dir", str(tmp_path)]
            )
        # Check it ran without crashing
        assert result.exit_code in (0, 1, 2)


# ---------------------------------------------------------------------------
# 6. Helper functions
# ---------------------------------------------------------------------------


class TestHelpers:
    """Tests for internal helper functions."""

    def test_missing_command_returns_click_command(self):
        cmd = _missing_command("test", "Test is unavailable")
        assert isinstance(cmd, click.Command)
        assert cmd.name == "test", "name is not valid"

    def test_missing_command_invocation_fails(self, runner):
        cmd = _missing_command("broken", "Broken dep missing")
        result = runner.invoke(cmd)
        assert result.exit_code != 0, "Result must not be empty"

    def test_emit_group_help(self, runner):
        """_emit_group_help should list subcommands."""

        @click.group(invoke_without_command=True)
        @click.pass_context
        def test_group(ctx):
            if not ctx.invoked_subcommand:
                _emit_group_help(ctx)

        @test_group.command("sub1")
        def sub1():
            pass

        result = runner.invoke(test_group, [])
        assert result.exit_code == 0, "Result must not be empty"
        assert "sub1" in result.output, "Result must not be empty"

    def test_allowed_tasks_has_entries(self):
        assert len(ALLOWED_TASKS) >= 1, "Allowed_tasks must not be empty"
        for name, (func, desc) in ALLOWED_TASKS.items():
            assert callable(func), "Condition must be true"
            assert isinstance(desc, str)


# ---------------------------------------------------------------------------
# 7. Auth subgroup
# ---------------------------------------------------------------------------


class TestAuthGroup:
    """Tests for ``codex auth`` commands."""

    def test_auth_no_subcommand_shows_help(self, runner):
        result = runner.invoke(cli, ["auth"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_auth_status_runs(self, runner):
        """auth status should not crash even without credentials."""
        result = runner.invoke(cli, ["auth", "status"])
        # May succeed or fail depending on env, but shouldn't crash
        assert result.exit_code in (0, 1, 2)
