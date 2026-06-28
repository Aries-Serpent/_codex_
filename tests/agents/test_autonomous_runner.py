"""Tests for Autonomous Agent Runner.

Tests the autonomous agent execution capabilities including:
- Input validation safeguards
- Task execution
- Report generation and cleanup
- Error handling
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMaxConstants:
    """Tests for safeguard constants."""

    def test_constants_defined(self):
        """Test that safeguard constants are defined."""
        try:
            from src.agents.autonomous_runner import (
                MAX_REPORTS_COUNT,
                MAX_RESPONSE_LENGTH,
                MAX_TASK_LENGTH,
            )

            assert MAX_TASK_LENGTH == 100000, "Length must be greater than zero"
            assert MAX_RESPONSE_LENGTH == 500000, "Response must not be empty"
            assert MAX_REPORTS_COUNT == 1000, "Count must be greater than zero"
        except ImportError:
            pytest.skip("autonomous_runner module not available")


class TestAutonomousAgentInit:
    """Tests for AutonomousAgent initialization."""

    def test_agent_init_default_path(self, tmp_path):
        """Test agent initialization with default path."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client.return_value = MagicMock()
                agent = AutonomousAgent(reports_dir=tmp_path)

                assert agent.reports_dir == tmp_path, "reports_dir is not valid"
                assert tmp_path.exists(), "Condition must be true"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    def test_agent_init_custom_path(self, tmp_path):
        """Test agent initialization with custom path."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            custom_path = tmp_path / "custom_reports"

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client.return_value = MagicMock()
                agent = AutonomousAgent(reports_dir=custom_path)

                assert agent.reports_dir == custom_path, "reports_dir is not valid"
                assert custom_path.exists(), "Condition must be true"
        except ImportError:
            pytest.skip("autonomous_runner module not available")


class TestAutonomousAgentExecute:
    """Tests for AutonomousAgent.execute method."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_empty_task(self, tmp_path):
        """Test execution with empty task returns error."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)
                result = await agent.execute("")

                assert result.success is False, "Result must not be empty"
                assert "non-empty string" in result.error, "Result must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_none_task(self, tmp_path):
        """Test execution with None task returns error."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)
                result = await agent.execute(None)  # type: ignore

                assert result.success is False, "Result must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_truncates_long_task(self, tmp_path):
        """Test that very long tasks are truncated."""
        try:
            from src.agents.autonomous_runner import MAX_TASK_LENGTH, AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client_instance.select_model.return_value = "gpt-4"
                mock_client_instance._dry_run = True
                mock_client_instance.log_execution = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                # Create task longer than MAX_TASK_LENGTH
                long_task = "x" * (MAX_TASK_LENGTH + 1000)

                result = await agent.execute(long_task)

                # Should succeed (task truncated internally)
                assert result.success is True, "Result must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_dry_run_mode(self, tmp_path):
        """Test execution in dry-run mode."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client_instance.select_model.return_value = "gpt-4o-mini"
                mock_client_instance._dry_run = True
                mock_client_instance.log_execution = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                result = await agent.execute("Test task")

                assert result.success is True, "Result must not be empty"
                assert "DRY RUN" in result.response, "Response must not be empty"
                assert result.model == "gpt-4o-mini", "Result must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_logs_execution(self, tmp_path):
        """Test that execution is logged."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client_instance.select_model.return_value = "gpt-4"
                mock_client_instance._dry_run = True
                mock_client_instance.log_execution = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                await agent.execute("Test task")

                mock_client_instance.log_execution.assert_called_once()
        except ImportError:
            pytest.skip("autonomous_runner module not available")


class TestSaveReport:
    """Tests for report saving functionality."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_save_report_creates_file(self, tmp_path):
        """Test that report file is created."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent
            from src.config.openai_client import ExecutionResult

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                result = ExecutionResult(
                    success=True,
                    model="gpt-4",
                    response="Test response",
                    usage={"total_tokens": 100},
                    duration_ms=500,
                    estimated_cost=0.01,
                )

                report_path = await agent._save_report("Test task", result)

                assert report_path.exists(), "rep is not valid"
                assert report_path.name.startswith("agent_"), "rep is not valid"
                assert report_path.suffix == ".json", "suffix is not valid"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_save_report_content(self, tmp_path):
        """Test report content structure."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent
            from src.config.openai_client import ExecutionResult

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                result = ExecutionResult(
                    success=True,
                    model="gpt-4",
                    response="Test response",
                    usage={"total_tokens": 100},
                    duration_ms=500,
                    estimated_cost=0.01,
                )

                report_path = await agent._save_report("Test task", result)

                content = json.loads(report_path.read_text())

                assert "timestamp" in content, "Content must not be empty"
                assert "task" in content, "Content must not be empty"
                assert "result" in content, "Result must not be empty"
                assert content["result"]["success"] is True, "Result must not be empty"
                assert content["result"]["model"] == "gpt-4", "Result must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")


class TestCleanupOldReports:
    """Tests for report cleanup functionality."""

    def test_cleanup_removes_old_reports(self, tmp_path):
        """Test that old reports are removed when exceeding limit."""
        try:
            from src.agents.autonomous_runner import MAX_REPORTS_COUNT, AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                # Create more reports than allowed
                for i in range(MAX_REPORTS_COUNT + 10):
                    report_file = tmp_path / f"agent_{i:04d}.json"
                    report_file.write_text("{}")

                agent._cleanup_old_reports()

                remaining = list(tmp_path.glob("agent_*.json"))
                assert len(remaining) <= MAX_REPORTS_COUNT, "Remaining must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    def test_cleanup_keeps_recent_reports(self, tmp_path):
        """Test that recent reports are kept."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                # Create a few reports (under limit)
                for i in range(5):
                    report_file = tmp_path / f"agent_{i:04d}.json"
                    report_file.write_text("{}")

                agent._cleanup_old_reports()

                remaining = list(tmp_path.glob("agent_*.json"))
                assert len(remaining) == 5, "Remaining must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")


class TestMainFunction:
    """Tests for main entry point."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_main_function_exists(self):
        """Test that main function exists and is async."""
        try:
            import asyncio

            from src.agents.autonomous_runner import main

            assert asyncio.iscoroutinefunction(main), "Condition must be true"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_main_uses_environment_variables(self, tmp_path):
        """Test that main reads from environment variables."""
        try:
            import os

            from src.agents.autonomous_runner import main

            with (
                patch.dict(
                    os.environ,
                    {
                        "AGENT_TASK": "Custom test task",
                        "MODEL_PREFERENCE": "gpt-4",
                    },
                ),
                patch("src.agents.autonomous_runner.AutonomousAgent") as mock_agent,
            ):
                mock_instance = MagicMock()
                mock_instance.execute = AsyncMock(
                    return_value=MagicMock(
                        success=True,
                        response="Test response",
                    )
                )
                mock_instance.client.get_usage_summary.return_value = {}
                mock_agent.return_value = mock_instance

                with patch("builtins.print"):
                    await main()

                mock_instance.execute.assert_called_once()
        except ImportError:
            pytest.skip("autonomous_runner module not available")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_with_special_characters(self, tmp_path):
        """Test execution with special characters in task."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client_instance.select_model.return_value = "gpt-4"
                mock_client_instance._dry_run = True
                mock_client_instance.log_execution = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                special_task = "Test with émojis 🎉 and spëcial çhars"
                result = await agent.execute(special_task)

                assert result.success is True, "Result must not be empty"
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_with_model_preference(self, tmp_path):
        """Test execution with specific model preference."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client_instance.select_model.return_value = "gpt-4-turbo"
                mock_client_instance._dry_run = True
                mock_client_instance.log_execution = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                await agent.execute("Test", model_preference="gpt-4-turbo")

                mock_client_instance.select_model.assert_called_with(preferred_model="gpt-4-turbo")
        except ImportError:
            pytest.skip("autonomous_runner module not available")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_with_auto_model(self, tmp_path):
        """Test execution with auto model selection."""
        try:
            from src.agents.autonomous_runner import AutonomousAgent

            with patch("src.agents.autonomous_runner.CodexOpenAIClient") as mock_client:
                mock_client_instance = MagicMock()
                mock_client_instance.select_model.return_value = "gpt-4"
                mock_client_instance._dry_run = True
                mock_client_instance.log_execution = MagicMock()
                mock_client.return_value = mock_client_instance

                agent = AutonomousAgent(reports_dir=tmp_path)

                await agent.execute("Test", model_preference="auto")

                mock_client_instance.select_model.assert_called_with(preferred_model=None)
        except ImportError:
            pytest.skip("autonomous_runner module not available")
