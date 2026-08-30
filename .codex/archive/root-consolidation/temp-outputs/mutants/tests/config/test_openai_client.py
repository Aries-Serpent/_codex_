"""
Tests for OpenAI Client Configuration.

Tests the CodexOpenAIClient class including:
- Model selection logic
- Cost estimation
- Audit logging
- Usage summary

Author: Copilot Agent
Generated: 2025-12-24
"""

from __future__ import annotations

import os
from unittest.mock import patch

# pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
import pytest


class TestCodexOpenAIClient:
    """Test suite for CodexOpenAIClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance for testing."""
        from src.config.openai_client import CodexOpenAIClient

        # Ensure dry-run mode for testing
        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GITHUB_CODEX": ""}):
            return CodexOpenAIClient()

    @pytest.fixture
    def client_with_key(self):
        """Create a client with a mock API key."""
        from src.config.openai_client import CodexOpenAIClient

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-fake-key-for-unit-testing-only"}):
            return CodexOpenAIClient()

    def test_client_initialization_dry_run(self, client):
        """Test client initializes in dry-run mode without API key."""
        assert client._dry_run is True, "_dry_run is not valid"
        assert len(client.models) > 0, "Collection must not be empty"

    def test_client_initialization_with_key(self, client_with_key):
        """Test client initializes properly with API key."""
        assert client_with_key._dry_run is False, "_dry_run is not valid"
        assert client_with_key.api_key is not None, "api_key must be initialized"

    def test_available_models_count(self, client):
        """Test that expected models are available."""
        # Should have at least 10 models configured
        assert len(client.models) >= 10, "Collection must not be empty"

        # Check for key models
        expected_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "o1-mini"]
        for model in expected_models:
            assert model in client.models, f"Missing expected model: {model}"

    def test_select_model_default(self, client):
        """Test default model selection."""
        model = client.select_model()
        assert model in client.models, "Condition must be true"

    def test_select_model_reasoning(self, client):
        """Test model selection with reasoning requirement."""
        model = client.select_model(requires_reasoning=True)
        config = client.models[model]
        assert config.reasoning is True, "reasoning is not valid"

    def test_select_model_low_cost(self, client):
        """Test model selection with low cost tier."""
        model = client.select_model(max_cost="low")
        config = client.models[model]
        assert config.cost_tier == "low", "cost_tier is not valid"

    def test_select_model_preferred(self, client):
        """Test preferred model selection."""
        preferred = "gpt-4o-mini"
        model = client.select_model(preferred_model=preferred)
        assert model == preferred, "model is not valid"

    def test_select_model_invalid_preferred(self, client):
        """Test that invalid preferred model falls back to auto-selection."""
        model = client.select_model(preferred_model="nonexistent-model")
        assert model in client.models, "Condition must be true"

    def test_select_model_min_context(self, client):
        """Test model selection with minimum context requirement."""
        model = client.select_model(min_context=100000)
        config = client.models[model]
        assert config.context_length >= 100000, "context_length must be positive"

    def test_estimate_cost(self, client):
        """Test cost estimation."""
        usage = {"prompt_tokens": 1000, "completion_tokens": 500}
        cost = client.estimate_cost("gpt-4o", usage)

        # Cost should be positive and reasonable
        assert cost > 0, "cost must be greater than zero"
        assert cost < 1.0, "cost is not valid"

    def test_estimate_cost_unknown_model(self, client):
        """Test cost estimation for unknown model returns 0."""
        usage = {"prompt_tokens": 1000, "completion_tokens": 500}
        cost = client.estimate_cost("unknown-model", usage)
        assert cost == 0.0, "cost is not valid"

    def test_log_execution(self, client):
        """Test execution logging."""
        initial_count = len(client.audit_log)

        client.log_execution(
            task_id="test-123",
            model="gpt-4o",
            tokens_used=100,
            duration_ms=500,
            estimated_cost=0.01,
            success=True,
        )

        assert len(client.audit_log) == initial_count + 1, "Collection must not be empty"
        assert client.audit_log[-1].task_id == "test-123", "task_id is not valid"
        assert client.audit_log[-1].success is True, "success is not valid"

    def test_log_execution_max_entries(self, client):
        """Test that audit log is bounded."""
        from src.config.openai_client import MAX_AUDIT_LOG_SIZE

        # Fill beyond max
        for i in range(MAX_AUDIT_LOG_SIZE + 100):
            client.log_execution(
                task_id=f"test-{i}",
                model="gpt-4o",
                tokens_used=10,
                duration_ms=50,
                estimated_cost=0.001,
                success=True,
            )

        assert len(client.audit_log) <= MAX_AUDIT_LOG_SIZE, "Collection must not be empty"

    def test_get_usage_summary_empty(self, client):
        """Test usage summary with no logs."""
        summary = client.get_usage_summary()

        assert summary["total_requests"] == 0, "Condition must be true"
        assert summary["total_tokens"] == 0, "Condition must be true"
        assert summary["total_cost"] == 0.0, "Condition must be true"

    def test_get_usage_summary_with_logs(self, client):
        """Test usage summary with logged executions."""
        # Log some executions
        client.log_execution(
            task_id="test-1",
            model="gpt-4o",
            tokens_used=100,
            duration_ms=500,
            estimated_cost=0.01,
            success=True,
        )
        client.log_execution(
            task_id="test-2",
            model="gpt-4o-mini",
            tokens_used=50,
            duration_ms=250,
            estimated_cost=0.005,
            success=True,
        )
        client.log_execution(
            task_id="test-3",
            model="gpt-4o",
            tokens_used=200,
            duration_ms=1000,
            estimated_cost=0.02,
            success=False,
        )

        summary = client.get_usage_summary()

        assert summary["total_requests"] == 3, "Condition must be true"
        assert summary["successful_requests"] == 2, "Condition must be true"
        assert summary["total_tokens"] == 350, "Condition must be true"
        assert summary["total_cost"] == pytest.approx(0.035), "Condition must be true"
        assert set(summary["models_used"]) == {"gpt-4o", "gpt-4o-mini"}

    def test_build_system_prompt(self, client):
        """Test system prompt generation."""
        prompt = client.build_system_prompt(task_type="code_review")

        assert "autonomous AI agent" in prompt, "Condition must be true"
        assert "Aries-Serpent" in prompt, "Condition must be true"
        assert "code_review" in prompt, "Condition must be true"

    def test_model_config_properties(self, client):
        """Test ModelConfig has expected properties."""
        config = client.models["gpt-4o"]

        assert hasattr(config, "context_length")
        assert hasattr(config, "reasoning")
        assert hasattr(config, "cost_tier")
        assert hasattr(config, "input_cost_per_1k")
        assert hasattr(config, "output_cost_per_1k")


class TestModelSelection:
    """Test model selection edge cases."""

    @pytest.fixture
    def client(self):
        """Create a client instance for testing."""
        from src.config.openai_client import CodexOpenAIClient

        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GITHUB_CODEX": ""}):
            return CodexOpenAIClient()

    def test_reasoning_with_cost_constraint(self, client):
        """Test selecting reasoning model with cost constraint."""
        model = client.select_model(requires_reasoning=True, max_cost="medium")
        config = client.models[model]

        assert config.reasoning is True, "reasoning is not valid"
        assert config.cost_tier in ["low", "medium"]

    def test_fallback_to_gpt4o_mini(self, client):
        """Test fallback when no model matches constraints."""
        # Request impossible constraints
        model = client.select_model(
            requires_reasoning=True,
            max_cost="low",  # No reasoning models are low cost
        )

        # Should fall back to gpt-4o-mini
        assert model == "gpt-4o-mini", "model is not valid"


class TestExecutionResult:
    """Test ExecutionResult dataclass."""

    def test_execution_result_creation(self):
        """Test creating ExecutionResult."""
        from src.config.openai_client import ExecutionResult

        result = ExecutionResult(
            success=True,
            model="gpt-4o",
            response="Test response",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
            duration_ms=500,
            estimated_cost=0.01,
        )

        assert result.success is True, "Result must not be empty"
        assert result.model == "gpt-4o", "Result must not be empty"
        assert result.response == "Test response", "Response must not be empty"
        assert result.error is None, "Result must not be empty"

    def test_execution_result_failure(self):
        """Test creating failed ExecutionResult."""
        from src.config.openai_client import ExecutionResult

        result = ExecutionResult(
            success=False,
            model="gpt-4o",
            error="API rate limit exceeded",
        )

        assert result.success is False, "Result must not be empty"
        assert result.error == "API rate limit exceeded", "Result must not be empty"
        assert result.response is None, "Response must not be empty"


class TestAPIKeyValidation:
    """Test API key validation."""

    def test_validate_api_key_valid(self):
        """Test validation of valid API key format."""
        from src.config.openai_client import _validate_api_key

        # Valid format: sk- followed by 32+ alphanumeric chars
        assert _validate_api_key("sk-test-fake-key-for-unit-testing-only") is True, "Condition must be true"
        assert _validate_api_key("sk-abcdefghijklmnopqrstuvwxyzABCDEF") is True, "Condition must be true"

    def test_validate_api_key_invalid(self):
        """Test validation of invalid API key formats."""
        from src.config.openai_client import _validate_api_key

        assert _validate_api_key("") is False, "Condition must be true"
        assert _validate_api_key(None) is False, "Condition must be true"
        assert _validate_api_key("invalid-key") is False, "Condition must be true"
        assert _validate_api_key("sk-short") is False, "Condition must be true"
        assert _validate_api_key("pk-12345678901234567890123456789012") is False, "Condition must be true"

    def test_validate_api_key_too_long(self):
        """Test validation rejects excessively long keys."""
        from src.config.openai_client import MAX_API_KEY_LENGTH, _validate_api_key

        long_key = "sk-" + "a" * (MAX_API_KEY_LENGTH + 1)
        assert _validate_api_key(long_key) is False, "Condition must be true"
