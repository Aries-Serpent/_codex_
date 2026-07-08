"""
Tests for secure token scope verification (PS-05).

Tests the safe token verification without any token decoding or logging.
"""

import os
from unittest.mock import Mock, patch

import pytest

from scripts.security.verify_token_scope import (  # pragma: allowlist secret
    TokenScopeVerifier,
    verify_github_token,
)


class TestTokenScopeVerifier:
    """Test suite for TokenScopeVerifier."""

    def test_initialization_with_token(self):
        """Test verifier initializes with provided token."""
        verifier = TokenScopeVerifier(token="test_token")
        assert verifier.token == "test_token", "token is not valid"
        assert verifier.verification_results is None, "Result must not be empty"

    def test_initialization_from_github_token_env(self):
        """Test verifier loads token from GITHUB_TOKEN environment variable."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            verifier = TokenScopeVerifier()
            assert verifier.token == "env_token", "token is not valid"

    def test_initialization_from_gh_token_env(self):
        """Test verifier loads token from GH_TOKEN as fallback."""
        with patch.dict(os.environ, {"GH_TOKEN": "gh_env_token"}, clear=True):
            verifier = TokenScopeVerifier()
            assert verifier.token == "gh_env_token", "token is not valid"

    def test_initialization_prefers_github_token(self):
        """Test GITHUB_TOKEN takes precedence over GH_TOKEN."""
        with patch.dict(
            os.environ, {"GITHUB_TOKEN": "primary_token", "GH_TOKEN": "fallback_token"}
        ):
            verifier = TokenScopeVerifier()
            assert verifier.token == "primary_token", "token is not valid"

    @patch("scripts.security.verify_token_scope.get_token")
    def test_initialization_without_token(self, mock_get_token):
        """Test verifier handles missing token gracefully."""
        # Mock get_token to return None when no token is available
        mock_get_token.return_value = (None,)
        with patch.dict(os.environ, {}, clear=True):
            verifier = TokenScopeVerifier()
            assert verifier.token is None, "token is not valid"

    @patch("scripts.security.verify_token_scope.requests")
    def test_verify_scopes_with_valid_token(self, mock_requests):
        """Test scope verification with valid token."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo, workflow, read:org",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        results = verifier.verify_scopes()

        assert results["status"] == "valid", "Result must not be empty"
        assert results["http_status"] == 200, "Result must not be empty"
        assert "repo" in results["scopes"], "Result must not be empty"
        assert "workflow" in results["scopes"], "Result must not be empty"
        assert "read:org" in results["scopes"], "Result must not be empty"
        assert results["rate_limit_remaining"] == 5000, "Result must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_verify_scopes_with_all_required_scopes(self, mock_requests):
        """Test verification passes with all required scopes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo, workflow, write:packages, read:org",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        results = verifier.verify_scopes()

        assert results["required_scopes_met"] is True, "Result must not be empty"
        assert len(results["missing_required_scopes"]) == 0, "Collection must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_verify_scopes_with_missing_required_scopes(self, mock_requests):
        """Test verification detects missing required scopes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo, read:org",  # Missing: workflow, write:packages
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        results = verifier.verify_scopes()

        assert results["required_scopes_met"] is False, "Result must not be empty"
        assert "workflow" in results["missing_required_scopes"], "Result must not be empty"
        assert "write:packages" in results["missing_required_scopes"], "Result must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_verify_scopes_with_invalid_token(self, mock_requests):
        """Test verification handles invalid token."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {
            "x-oauth-scopes": "",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "0",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="invalid_token")
        results = verifier.verify_scopes()

        assert results["status"] == "invalid", "Result must not be empty"
        assert results["http_status"] == 401, "Result must not be empty"

    @patch("scripts.security.verify_token_scope.get_token")
    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.security.verify_token_scope.os.getenv", return_value=None)
    def test_verify_scopes_without_token(self, _mock_getenv, mock_get_token):
        """Test verification fails gracefully without token."""
        # Mock get_token to return None when no token is available
        mock_get_token.return_value = (None,)
        verifier = TokenScopeVerifier(token=None)
        assert verifier.token is None, "Token should be None when no token or env var is available"
        results = verifier.verify_scopes()

        assert results["status"] == "error", "Result must not be empty"
        assert "No token available" in results["error"], "Result must not be empty"

    @patch("scripts.security.verify_token_scope.REQUESTS_AVAILABLE", False)
    def test_verify_scopes_without_requests_library(self):
        """Test verification handles missing requests library."""
        verifier = TokenScopeVerifier(token="test_token")
        results = verifier.verify_scopes()

        assert results["status"] == "error", "Result must not be empty"
        assert "requests library not available" in results["error"], "Result must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_verify_scopes_with_network_error(self, mock_requests):
        """Test verification handles network errors."""
        import requests as real_requests

        mock_requests.RequestException = real_requests.RequestException
        mock_requests.get.side_effect = real_requests.RequestException("Network error")

        verifier = TokenScopeVerifier(token="test_token")
        results = verifier.verify_scopes()

        assert results["status"] == "error", "Result must not be empty"
        assert "API request failed" in results["error"], "Result must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_check_scope_with_granted_scope(self, mock_requests):
        """Test check_scope returns True for granted scope."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo, workflow",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        verifier.verify_scopes()

        assert verifier.check_scope("repo") is True, "Condition must be true"
        assert verifier.check_scope("workflow") is True, "Condition must be true"

    @patch("scripts.security.verify_token_scope.requests")
    def test_check_scope_with_missing_scope(self, mock_requests):
        """Test check_scope returns False for missing scope."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        verifier.verify_scopes()

        assert verifier.check_scope("workflow") is False, "Condition must be true"

    def test_check_scope_without_verification(self):
        """Test check_scope returns False if verification not run."""
        verifier = TokenScopeVerifier(token="test_token")
        assert verifier.check_scope("repo") is False, "Condition must be true"

    @patch("scripts.security.verify_token_scope.requests")
    def test_print_report_with_valid_results(self, mock_requests, capsys):
        """Test print_report generates readable output."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo, workflow, read:org",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        verifier.verify_scopes()
        verifier.print_report()

        captured = capsys.readouterr()
        assert "GitHub Token Scope Verification Report" in captured.out, "Condition must be true"
        assert "Status: VALID" in captured.out, "Condition must be true"
        # Note: For security, scope names are not displayed in output
        assert "Granted Scopes:" in captured.out, "Condition must be true"

    def test_print_report_without_verification(self, capsys):
        """Test print_report handles no verification results."""
        verifier = TokenScopeVerifier(token="test_token")
        verifier.print_report()

        captured = capsys.readouterr()
        assert "No verification results available" in captured.out, "Result must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_verify_github_token_convenience_function(self, mock_requests):
        """Test convenience function works correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            results = verify_github_token()

            assert results["status"] == "valid", "Result must not be empty"
            assert "repo" in results["scopes"], "Result must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_verify_scopes_includes_timestamp(self, mock_requests):
        """Test verification results include UTC timestamp."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        results = verifier.verify_scopes()

        assert "timestamp" in results, "Result must not be empty"
        assert "T" in results["timestamp"], "Result must not be empty"

    @patch("scripts.security.verify_token_scope.requests")
    def test_token_never_logged_in_verification(self, mock_requests):
        """Test that token value is never exposed in logs or output."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        secret_token = "ghp_SECRETTOKEN123456789"  # pragma: allowlist secret
        verifier = TokenScopeVerifier(token=secret_token)
        results = verifier.verify_scopes()

        # Verify token is not in results
        results_str = str(results)
        assert secret_token not in results_str, "Result must not be empty"
        assert "ghp_" not in results_str, "Result must not be empty"


class TestSecurityPrinciples:
    """Test suite verifying security principles."""

    @patch("scripts.security.verify_token_scope.requests")
    def test_no_token_decoding(self, mock_requests):
        """Verify token is NEVER decoded, only used in Authorization header."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        verifier.verify_scopes()

        # Verify requests.get was called with proper headers
        call_args = mock_requests.get.call_args
        headers = call_args[1]["headers"]
        assert "Authorization" in headers, "Condition must be true"
        # Token is used but not decoded
        assert headers["Authorization"].startswith("token "), "Condition must be true"

    def test_environment_variable_usage(self):
        """Verify tokens are loaded from environment variables."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_test_token"}):
            verifier = TokenScopeVerifier()
            # Token loaded from environment, not hardcoded
            assert verifier.token == "env_test_token", "token is not valid"

    @patch("scripts.security.verify_token_scope.requests")
    def test_api_based_verification(self, mock_requests):
        """Verify verification uses API, not token decoding."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-oauth-scopes": "repo",
            "x-ratelimit-remaining": "5000",
            "x-ratelimit-reset": "1234567890",
        }
        mock_requests.get.return_value = mock_response

        verifier = TokenScopeVerifier(token="test_token")
        results = verifier.verify_scopes()

        # Scopes extracted from API response header, not token decoding
        assert "scopes" in results, "Result must not be empty"
        assert results["scopes"] == ["repo"], "Result must not be empty"

        # Verify API was called
        assert mock_requests.get.called, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
