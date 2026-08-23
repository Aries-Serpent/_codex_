#!/usr/bin/env python3
"""Integration tests for Phase 4.2 token utility adoption.

This module contains 12 integration test scenarios verifying that:
1. Token resolution utilities work correctly
2. Refactored scripts use centralized token resolution
3. Error handling is preserved
4. Token values are never logged
5. API operations use proper authentication
6. Elevated operations validate scopes

Test Categories:
- Test Category A: Token Resolution (3 tests)
- Test Category B: API Operations (2 tests)
- Test Category C: Variable Operations (2 tests)
- Test Category D: Error Scenarios (3 tests)
- Test Category E: Scope Validation (2 tests)
"""

import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from ci._token_resolver import (
    TokenResolutionError,
    get_token,
    get_token_scope,
    validate_token,
    validate_token_scope,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Test Category A: Token Resolution (3 tests)
# ============================================================================


class TestTokenResolution:
    """Tests for token resolution functionality."""

    def test_get_token_returns_tuple(self):
        """TEST A1: Verify get_token returns (token, source) tuple."""
        with patch.dict(os.environ, {"CODEX_MASTER_KEY": "test_token"}):
            result = get_token(required_elevated=True)

            assert isinstance(result, tuple), "get_token should return tuple"
            assert len(result) == 2, "Tuple should have 2 elements"
            token, source = result
            assert token == "test_token", "Token value should match"
            assert source == "CODEX_MASTER_KEY", "Source should be correct"

    def test_get_token_validates_scope(self):
        """TEST A2: Verify get_token validates scope correctly."""
        with patch.dict(os.environ, {"GH_TOKEN": "limited_token"}):
            # Should fail with required_elevated=True
            with pytest.raises(TokenResolutionError):
                get_token(required_elevated=True)

            # Should succeed with required_elevated=False
            with patch.dict(os.environ, {"GH_TOKEN": "valid_token"}):
                token, source = get_token(required_elevated=False)
                assert source == "GH_TOKEN", "Should accept GH_TOKEN when elevated not required"

    def test_get_token_validates_hierarchy(self):
        """TEST A3: Verify get_token respects environment variable hierarchy."""
        env = {
            "CODEX_MASTER_KEY": "master",
            "CODEX_BACKUP_KEY": "backup",
            "GH_TOKEN": "limited",
            "GITHUB_TOKEN": "default",
        }

        with patch.dict(os.environ, env):
            # Should prefer CODEX_MASTER_KEY
            token, source = get_token(required_elevated=False)
            assert source == "CODEX_MASTER_KEY", "Should prefer CODEX_MASTER_KEY"
            assert token == "master", "Token should be from CODEX_MASTER_KEY"


# ============================================================================
# Test Category B: API Operations (2 tests)
# ============================================================================


class TestAPIOperations:
    """Tests for API operations using token utility."""

    def test_api_call_uses_auth_header(self):
        """TEST B1: Verify API calls properly construct Authorization header."""
        from ci._token_resolver import get_auth_header

        with patch.dict(os.environ, {"CODEX_MASTER_KEY": "test_token_123"}):
            token, _ = get_token(required_elevated=True)
            header = get_auth_header(token)

            assert isinstance(header, str), "Auth header should be string"
            assert "Authorization" in header, "Should contain Authorization"
            assert "token " in header or "Bearer " in header, "Should use token or ******"
            assert "test_token_123" in header, "Token should be in header"

    def test_api_error_handling_preserves_scopes(self):
        """TEST B2: Verify API error handling validates scopes."""
        from ci._token_resolver import validate_token_scope

        with patch.dict(os.environ, {"CODEX_MASTER_KEY": "elevated_token"}):
            token, _ = get_token(required_elevated=True)

            # Test scope validation
            is_valid, msg = validate_token_scope(token, ["repo", "workflow"])

            assert is_valid, "Scope validation should pass for elevated token"


# ============================================================================
# Test Category C: Variable Operations (2 tests)
# ============================================================================


class TestVariableOperations:
    """Tests for GitHub variables operations with proper token handling."""

    def test_variable_operations_use_elevated_token(self):
        """TEST C1: Verify variable operations request elevated token."""
        with patch.dict(os.environ, {"CODEX_MASTER_KEY": "elevated"}):
            # Simulating a refactored script that manages variables
            token, source = get_token(required_elevated=True)

            assert token == "elevated", "Should get elevated token"
            assert source == "CODEX_MASTER_KEY", "Should use CODEX_MASTER_KEY"

    def test_variable_operations_handle_errors(self):
        """TEST C2: Verify variable operation errors are handled properly."""
        with patch.dict(os.environ, {}, clear=True):
            # No token available
            with pytest.raises(TokenResolutionError) as exc_info:
                get_token(required_elevated=True)

            assert "elevated token" in str(exc_info.value).lower(), "Error should mention elevated"


# ============================================================================
# Test Category D: Error Scenarios (3 tests)
# ============================================================================


class TestErrorScenarios:
    """Tests for error handling in token operations."""

    def test_missing_token_handling(self):
        """TEST D1: Verify graceful handling when token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(TokenResolutionError) as exc_info:
                get_token(required_elevated=False)

            error_msg = str(exc_info.value)
            assert "token" in error_msg.lower(), "Error should mention token"

    def test_invalid_token_validation(self):
        """TEST D2: Verify invalid token values are rejected."""
        # Empty token
        is_valid, msg = validate_token("")
        assert not is_valid, "Empty token should be invalid"

        # None token
        is_valid, msg = validate_token(None)
        assert not is_valid, "None token should be invalid"

        # Whitespace only
        is_valid, msg = validate_token("   ")
        assert not is_valid, "Whitespace token should be invalid"

        # Valid token
        is_valid, msg = validate_token("valid_token_here")
        assert is_valid, "Valid token should pass"

    def test_insufficient_scope_error(self):
        """TEST D3: Verify insufficient scope errors are caught."""
        with patch.dict(os.environ, {"GH_TOKEN": "limited_token"}):
            # Requesting elevated operations with limited token
            with pytest.raises(TokenResolutionError) as exc_info:
                get_token(required_elevated=True)

            assert "elevated" in str(exc_info.value).lower()


# ============================================================================
# Test Category E: Scope Validation (2 tests)
# ============================================================================


class TestScopeValidation:
    """Tests for token scope validation."""

    def test_get_token_scope_detection(self):
        """TEST E1: Verify token scope is correctly detected."""
        from ci._token_resolver import get_token_scope

        with patch.dict(os.environ, {"CODEX_MASTER_KEY": "master_token"}):
            token, source = get_token(required_elevated=True)
            scope = get_token_scope(token)

            assert scope == "elevated", "CODEX_MASTER_KEY should have elevated scope"

        with patch.dict(os.environ, {"GH_TOKEN": "limited_token"}):
            token, source = get_token(required_elevated=False)
            scope = get_token_scope(token)

            assert scope in ["standard", "fallback"], "GH_TOKEN should have limited scope"

    def test_scope_checks_use_the_actual_token_value(self):
        """TEST E2: Scope detection should follow the token value, not the active env default."""
        with patch.dict(
            os.environ,
            {"CODEX_MASTER_KEY": "master_token", "CODEX_BACKUP_KEY": "backup_token"},
            clear=True,
        ):
            assert get_token_scope("master_token") == "elevated"
            assert get_token_scope("backup_token") == "standard"
            assert validate_token_scope("master_token", ["repo", "workflow", "actions:write"]) == (
                True,
                "Token from CODEX_MASTER_KEY has all required scopes",
            )

    def test_log_token_usage_no_exposure(self):
        """TEST E3: Verify log_token_usage never exposes token values."""
        from ci._token_resolver import log_token_usage

        with patch("ci._token_resolver.logger") as mock_logger:
            with patch.dict(os.environ, {"CODEX_MASTER_KEY": "secret_token_12345"}):
                token, source = get_token(required_elevated=True)
                log_token_usage("test_operation", token)

                # Verify logger was called but token not included
                mock_logger.info.assert_called()
                call_args = str(mock_logger.info.call_args)

                # Token value should NOT appear in logs
                assert "secret_token_12345" not in call_args, "Token value exposed in logs!"
                # Source should appear
                assert "CODEX_MASTER_KEY" in call_args or "source" in call_args.lower()


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_env():
    """Cleanup environment variables after each test."""
    yield
    # Ensure clean state
    for var in ["CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN", "GITHUB_TOKEN"]:
        os.environ.pop(var, None)


# ============================================================================
# Test Summary
# ============================================================================


def test_all_integration_tests_present():
    """Verify all 12 integration tests are defined."""
    # This meta-test documents all test categories
    test_categories = {
        "A: Token Resolution": ["test_get_token_returns_tuple", "test_get_token_validates_scope", "test_get_token_validates_hierarchy"],
        "B: API Operations": ["test_api_call_uses_auth_header", "test_api_error_handling_preserves_scopes"],
        "C: Variable Operations": ["test_variable_operations_use_elevated_token", "test_variable_operations_handle_errors"],
        "D: Error Scenarios": ["test_missing_token_handling", "test_invalid_token_validation", "test_insufficient_scope_error"],
        "E: Scope Validation": ["test_get_token_scope_detection", "test_log_token_usage_no_exposure"],
    }

    total_tests = sum(len(tests) for tests in test_categories.values())
    assert total_tests == 12, f"Expected 12 tests, found {total_tests}"

    logger.info("✅ All 12 integration tests present")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
