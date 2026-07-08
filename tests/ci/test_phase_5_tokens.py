from typing import Dict

# from scripts.ci._token_resolver import get_token
# This module implements 8 core test scenarios validating the entire token
#         Validates:
#         - Token resolution is fast (< 10ms per call)
#         - No performance regression
# Test Scenarios:
# 1. CODEX_MASTER_KEY available (primary token)
# 2. CODEX_BACKUP_KEY available (fallback 1)
# 3. GH_TOKEN available (fallback 2)
# 4. GITHUB_TOKEN available (fallback 3)
# 5. Elevated deny (required token missing - security)
# 6. Scope validation (scope detection)
# 7. Audit logging without token exposure (security)
# 8. Base64 Python-to-Variable round-trip (integration)
#         - Token resolution is fast (< 10ms per call)
#         - No performance regression
# from __future__ import annotations
# from scripts.ci._token_resolver import get_token
# import logging
# from scripts.ci._token_resolver import (
# import uuid
# # Import the token resolver module
# from typing import Any, Dict, Optional, Tuple
# from scripts.ci._token_resolver import (
# import pytest
# # Import the token resolver module
# 
# # Import the token resolver module
# from scripts.ci._token_resolver import (
# 
#     CANONICAL_HIERARCHY,
#     TOKEN_SCOPES,
#     TokenResolutionError,
#     get_auth_header,
#     get_token,
#     get_token_scope,
#     get_token_source,
#     log_token_usage,
#     validate_token,
#     validate_token_scope,
# )


# ============================================================================
# SCENARIO 1: CODEX_MASTER_KEY AVAILABLE (PRIMARY TOKEN)
# ============================================================================


class TestScenario1MasterKeyNormal:
    """Scenario 1: CODEX_MASTER_KEY Available (Normal Operation).

    Tests the primary token resolution path when CODEX_MASTER_KEY is available.
    This is the normal, expected operating condition.
    """

    def test_scenario_1_master_key_normal(
        self, env_with_master_key: Dict[str, str], token_log_capture: Any
    ) -> None:
        """Test normal operation with CODEX_MASTER_KEY available.

        Validates:
        - Token is retrieved from CODEX_MASTER_KEY (highest priority)
        - Token source is correctly identified
        - Scope is elevated
        - Authorization header is properly formatted
        - All required scopes are available
        - Token never exposed in logs
        """
        master_key = get_token(required_elevated=True)[0]
        assert isinstance(master_key, str) and len(master_key) > 0, "master_key must be a non-empty string"

        # Test 1: get_token retrieves the correct token
        token, source = get_token(required_elevated=False)
        assert token == master_key, "Token mismatch"
        assert source == "CODEX_MASTER_KEY", "Source mismatch"

        # Test 2: get_token_source returns correct source
        source = get_token_source()
        assert source == "CODEX_MASTER_KEY", "get_token_source failed"

        # Test 3: get_token_scope returns elevated
        scope = get_token_scope(token)
        assert scope == "elevated", f"Expected 'elevated', got '{scope}'"

        # Test 4: get_auth_header is properly formatted
        auth_header = get_auth_header(token)
        assert auth_header.startswith("Authorization: token "), "Header format wrong"
        assert master_key in auth_header, "Token not in header"

        # Test 5: validate_token_scope with elevated scopes
        is_valid, msg = validate_token_scope(
            token, ["repo", "workflow", "actions:write"]
        )
        assert is_valid is True, f"Scope validation failed: {msg}"
        assert "CODEX_MASTER_KEY" in msg, "Source not mentioned"

        # Test 6: Verify logging doesn't expose token
        with token_log_capture as capture:
            log_token_usage("Testing scenario 1", required_elevated=False)
            capture.assert_token_not_exposed(master_key)
            assert "CODEX_MASTER_KEY" in capture.text, "Source not logged"


# ============================================================================
# SCENARIO 2: CODEX_BACKUP_KEY AVAILABLE (FALLBACK 1)
# ============================================================================


class TestScenario2BackupKeyFallback:
    """Scenario 2: CODEX_BACKUP_KEY Available (Fallback 1).

    Tests fallback to CODEX_BACKUP_KEY when CODEX_MASTER_KEY is unavailable.
    """

    def test_scenario_2_backup_key_fallback(
        self, env_with_backup_key: Dict[str, str], token_log_capture: Any
    ) -> None:
        """Test fallback to CODEX_BACKUP_KEY when master is unavailable.

        Validates:
        - Token falls back to CODEX_BACKUP_KEY (when master unavailable)
        - Token source is correctly identified as CODEX_BACKUP_KEY
        - Scope is standard (not elevated)
        - Authorization header works with backup key
        - Backup key has repo + workflow scopes
        - Token never exposed in logs
        """
        backup_key = get_token(required_elevated=True)[0]
        assert isinstance(backup_key, str) and len(backup_key) > 0, "backup_key must be a non-empty string"

        # Verify CODEX_MASTER_KEY is not set
        assert get_token(required_elevated=True)[0] is None, "Master key should be unset"

        # Test 1: get_token retrieves backup key
        token, source = get_token(required_elevated=False)
        assert token == backup_key, "Token mismatch"
        assert source == "CODEX_BACKUP_KEY", f"Expected CODEX_BACKUP_KEY, got {source}"

        # Test 2: get_token_source returns correct source
        source = get_token_source()
        assert source == "CODEX_BACKUP_KEY", "get_token_source failed"

        # Test 3: get_token_scope returns standard (not elevated)
        scope = get_token_scope(token)
        assert scope == "standard", f"Expected 'standard', got '{scope}'"

        # Test 4: Authorization header works
        auth_header = get_auth_header(token)
        assert backup_key in auth_header, "Backup key not in header"

        # Test 5: Backup key has expected scopes
        with token_log_capture as capture:
            is_valid, msg = validate_token_scope(token, ["repo", "workflow"])
            assert is_valid is True, f"Scope validation failed: {msg}"

        # Test 6: Verify token not exposed
        capture.assert_token_not_exposed(backup_key)


# ============================================================================
# SCENARIO 3: GH_TOKEN AVAILABLE (FALLBACK 2)
# ============================================================================


class TestScenario3GHTokenFallback:
    """Scenario 3: GH_TOKEN Available (Fallback 2).

    Tests fallback to GH_TOKEN when CODEX_* keys are unavailable.
    """

    def test_scenario_3_gh_token_fallback(
        self, env_with_gh_token: Dict[str, str], token_log_capture: Any
    ) -> None:
        """Test fallback to GH_TOKEN.

        Validates:
        - Token falls back to GH_TOKEN (when CODEX_* unavailable)
        - Token source is correctly identified as GH_TOKEN
        - Scope is standard
        - GH_TOKEN has repo scope
        - Token never exposed in logs
        """
        gh_token = get_token(required_elevated=False)[0]
        assert isinstance(gh_token, str) and len(gh_token) > 0, "gh_token must be a non-empty string"

        # Verify CODEX_* keys are not set
        assert get_token(required_elevated=True)[0] is None, "Master key should be unset"
        assert get_token(required_elevated=True)[0] is None, "Backup key should be unset"

        # Test 1: get_token retrieves GH_TOKEN
        token, source = get_token(required_elevated=False)
        assert token == gh_token, "Token mismatch"
        assert source == "GH_TOKEN", f"Expected GH_TOKEN, got {source}"

        # Test 2: get_token_source returns correct source
        source = get_token_source()
        assert source == "GH_TOKEN", "get_token_source failed"

        # Test 3: get_token_scope returns standard
        scope = get_token_scope(token)
        assert scope == "standard", f"Expected 'standard', got '{scope}'"

        # Test 4: Authorization header works
        auth_header = get_auth_header(token)
        assert gh_token in auth_header, "GH_TOKEN not in header"

        # Test 5: GH_TOKEN has repo scope
        with token_log_capture as capture:
            is_valid, msg = validate_token_scope(token, ["repo"])
            assert is_valid is True, f"Scope validation failed: {msg}"

        # Test 6: Verify token not exposed
        capture.assert_token_not_exposed(gh_token)


# ============================================================================
# SCENARIO 4: GITHUB_TOKEN AVAILABLE (FALLBACK 3)
# ============================================================================


class TestScenario4GitHubTokenFallback:
    """Scenario 4: GITHUB_TOKEN Available (Fallback 3).

    Tests fallback to GITHUB_TOKEN when all other tokens are unavailable.
    """

    def test_scenario_4_github_token_fallback(
        self, env_with_github_token: Dict[str, str], token_log_capture: Any
    ) -> None:
        """Test fallback to GITHUB_TOKEN (lowest priority).

        Validates:
        - Token falls back to GITHUB_TOKEN (when all others unavailable)
        - Token source is correctly identified as GITHUB_TOKEN
        - Scope is fallback
        - GITHUB_TOKEN has repo scope
        - Token never exposed in logs
        """
        github_token = os.environ.get("GITHUB_TOKEN")
        assert isinstance(github_token, str) and len(github_token) > 0, "github_token must be a non-empty string"

        # Verify all other tokens are unset
        for var in ["CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN"]:
            assert os.environ.get(var) is None, f"{var} should be unset"

        # Test 1: get_token retrieves GITHUB_TOKEN
        token, source = get_token(required_elevated=False)
        assert token == github_token, "Token mismatch"
        assert source == "GITHUB_TOKEN", f"Expected GITHUB_TOKEN, got {source}"

        # Test 2: get_token_source returns correct source
        source = get_token_source()
        assert source == "GITHUB_TOKEN", "get_token_source failed"

        # Test 3: get_token_scope returns fallback
        scope = get_token_scope(token)
        assert scope == "fallback", f"Expected 'fallback', got '{scope}'"

        # Test 4: Authorization header works
        auth_header = get_auth_header(token)
        assert github_token in auth_header, "GITHUB_TOKEN not in header"

        # Test 5: GITHUB_TOKEN has repo scope
        with token_log_capture as capture:
            is_valid, msg = validate_token_scope(token, ["repo"])
            assert is_valid is True, f"Scope validation failed: {msg}"

        # Test 6: Verify token not exposed
        capture.assert_token_not_exposed(github_token)


# ============================================================================
# SCENARIO 5: ELEVATED DENY (SECURITY)
# ============================================================================


class TestScenario5ElevatedDeny:
    """Scenario 5: Elevated Operations Denied (Security).

    Tests that operations requiring elevated scopes are correctly denied
    when only fallback tokens are available.
    """

    def test_scenario_5_elevated_deny_gh_token(
        self, env_with_gh_token: Dict[str, str]
    ) -> None:
        """Test that elevated operations are denied with GH_TOKEN.

        Validates:
        - get_token(required_elevated=True) fails with GH_TOKEN
        - Correct error message is provided
        - get_token(required_elevated=True) succeeds with appropriate token
        """
        gh_token = get_token(required_elevated=False)[0]
        assert isinstance(gh_token, str) and len(gh_token) > 0, "gh_token must be a non-empty string"

        # Test 1: get_token(required_elevated=True) should fail
        with pytest.raises(
            TokenResolutionError, match="No elevated token available"
        ) as exc_info:
            get_token(required_elevated=True)

        error_msg = str(exc_info.value)
        assert "CODEX_MASTER_KEY" in error_msg, "Should mention CODEX_MASTER_KEY"
        assert "CODEX_BACKUP_KEY" in error_msg, "Should mention CODEX_BACKUP_KEY"

    def test_scenario_5_elevated_deny_github_token(
        self, env_with_github_token: Dict[str, str]
    ) -> None:
        """Test that elevated operations are denied with GITHUB_TOKEN.

        Validates:
        - get_token(required_elevated=True) fails with GITHUB_TOKEN
        - Only CODEX_* keys are acceptable for elevated operations
        """
        github_token = os.environ.get("GITHUB_TOKEN")
        assert isinstance(github_token, str) and len(github_token) > 0, "github_token must be a non-empty string"

        # Test: get_token(required_elevated=True) should fail
        with pytest.raises(TokenResolutionError):
            get_token(required_elevated=True)

    def test_scenario_5_elevated_allow_backup_key(
        self, env_with_backup_key: Dict[str, str]
    ) -> None:
        """Test that elevated operations are ALLOWED with CODEX_BACKUP_KEY.

        Validates:
        - get_token(required_elevated=True) succeeds with CODEX_BACKUP_KEY
        - Elevated operations can use backup key
        """
        backup_key = get_token(required_elevated=True)[0]
        assert isinstance(backup_key, str) and len(backup_key) > 0, "backup_key must be a non-empty string"

        # Test: get_token(required_elevated=True) should succeed
        token, source = get_token(required_elevated=True)
        assert token == backup_key, "Token mismatch"
        assert source == "CODEX_BACKUP_KEY", "Source mismatch"


# ============================================================================
# SCENARIO 6: SCOPE VALIDATION
# ============================================================================


class TestScenario6ScopeValidation:
    """Scenario 6: Scope Validation.

    Tests that token scopes are correctly detected and validated.
    """

    def test_scenario_6_master_key_scopes(
        self, env_with_master_key: Dict[str, str]
    ) -> None:
        """Test CODEX_MASTER_KEY has all required scopes.

        Validates:
        - CODEX_MASTER_KEY has repo + workflow + actions:write + security_events
        - scope_validation passes for all master key scopes
        """
        master_key = get_token(required_elevated=True)[0]
        assert isinstance(master_key, str) and len(master_key) > 0, "master_key must be a non-empty string"

        # Test all master key scopes
        required_scopes = [
            "repo",
            "workflow",
            "actions:write",
            "security_events",
        ]
        is_valid, msg = validate_token_scope(master_key, required_scopes)
        assert is_valid is True, f"Master key scope validation failed: {msg}"

    def test_scenario_6_backup_key_scopes(
        self, env_with_backup_key: Dict[str, str]
    ) -> None:
        """Test CODEX_BACKUP_KEY has repo + workflow scopes.

        Validates:
        - CODEX_BACKUP_KEY has repo + workflow
        - CODEX_BACKUP_KEY missing actions:write and security_events
        """
        backup_key = get_token(required_elevated=True)[0]
        assert isinstance(backup_key, str) and len(backup_key) > 0, "backup_key must be a non-empty string"

        # Test backup key has repo + workflow
        is_valid, msg = validate_token_scope(backup_key, ["repo", "workflow"])
        assert is_valid is True, f"Backup key scope validation failed: {msg}"

        # Test backup key missing security_events
        is_valid, msg = validate_token_scope(backup_key, ["security_events"])
        assert (
            is_valid is False
        ), "Backup key should not have security_events scope"
        assert "security_events" in msg, "Error should mention missing scope"

    def test_scenario_6_gh_token_scopes(
        self, env_with_gh_token: Dict[str, str]
    ) -> None:
        """Test GH_TOKEN has repo scope only.

        Validates:
        - GH_TOKEN has repo scope
        - GH_TOKEN missing workflow and actions:write
        """
        gh_token = get_token(required_elevated=False)[0]
        assert isinstance(gh_token, str) and len(gh_token) > 0, "gh_token must be a non-empty string"

        # Test GH_TOKEN has repo
        is_valid, msg = validate_token_scope(gh_token, ["repo"])
        assert is_valid is True, f"GH_TOKEN scope validation failed: {msg}"

        # Test GH_TOKEN missing workflow
        is_valid, msg = validate_token_scope(gh_token, ["workflow"])
        assert is_valid is False, "GH_TOKEN should not have workflow scope"


# ============================================================================
# SCENARIO 7: AUDIT LOGGING WITHOUT TOKEN EXPOSURE
# ============================================================================


class TestScenario7AuditLogging:
    """Scenario 7: Audit Logging Without Token Exposure (Security).

    Tests that token usage is logged for auditing but never exposes token values.
    """

    def test_scenario_7_audit_logging_master_key(
        self, env_with_master_key: Dict[str, str], token_log_capture: Any
    ) -> None:
        """Test audit logging with CODEX_MASTER_KEY.

        Validates:
        - log_token_usage logs the token context
        - Token source is logged (CODEX_MASTER_KEY)
        - Token scope is logged (elevated)
        - Actual token value is never exposed
        - Context message is preserved
        """
        master_key = get_token(required_elevated=True)[0]
        assert isinstance(master_key, str) and len(master_key) > 0, "master_key must be a non-empty string"

        with token_log_capture as capture:
            log_token_usage("Testing elevated operation", required_elevated=False)

            log_text = capture.text
            # Verify token source is logged
            assert "CODEX_MASTER_KEY" in log_text, "Source not logged"
            # Verify scope is logged
            assert "elevated" in log_text, "Scope not logged"
            # Verify context is logged
            assert "Testing elevated operation" in log_text, "Context not logged"
            # Verify token NOT exposed
            assert master_key not in log_text, "Token exposed in logs!"

    def test_scenario_7_audit_logging_backup_key(
        self, env_with_backup_key: Dict[str, str], token_log_capture: Any
    ) -> None:
        """Test audit logging with CODEX_BACKUP_KEY.

        Validates:
        - Token source is logged (CODEX_BACKUP_KEY)
        - Scope is logged (standard)
        - Token value is not exposed
        """
        backup_key = get_token(required_elevated=True)[0]
        assert isinstance(backup_key, str) and len(backup_key) > 0, "backup_key must be a non-empty string"

        with token_log_capture as capture:
            log_token_usage("Backup key test", required_elevated=False)

            log_text = capture.text
            assert "CODEX_BACKUP_KEY" in log_text, "Source not logged"
            assert backup_key not in log_text, "Token exposed in logs!"

    def test_scenario_7_audit_logging_no_token_raises(
        self, env_no_tokens: Dict[str, str], token_log_capture: Any
    ) -> None:
        """Test audit logging fails gracefully when no token available.

        Validates:
        - log_token_usage raises TokenResolutionError appropriately
        - Error is logged
        """
        with pytest.raises(TokenResolutionError):
            with token_log_capture as capture:
                log_token_usage("Should fail", required_elevated=False)

                # Verify error was logged
                assert "Token resolution failed" in capture.text


# ============================================================================
# SCENARIO 8: BASE64 PYTHON-TO-VARIABLE ROUND-TRIP (NEW)
# ============================================================================


class TestScenario8Base64RoundTrip:
    """Scenario 8: Base64 Python-to-Variable Round-Trip (Integration).

    Tests the NEW integration scenario: encode Python file to base64,
    write to GitHub variable, retrieve, decode, and validate integrity.
    """

    def test_scenario_8_base64_roundtrip_with_master_key(
        self,
        env_with_master_key: Dict[str, str],
        mock_github_api: Any,
        token_factory: Any,
        sample_python_file: str,
        token_log_capture: Any,
    ) -> None:
        """Test base64 round-trip with CODEX_MASTER_KEY.

        Validates:
        - Python file can be base64 encoded
        - Encoded content can be written via GitHub API (mocked)
        - Encoded content can be retrieved via GitHub API (mocked)
        - Decoded content matches original
        - Token never exposed in logs
        - Cleanup removes test variable
        """
        master_key = get_token(required_elevated=True)[0]
        assert isinstance(master_key, str) and len(master_key) > 0, "master_key must be a non-empty string"

        # Step 1: Encode Python content
        original_content = sample_python_file
        encoded_content = token_factory.create_base64_content(original_content)
        assert len(encoded_content) > 0, "Encoded content is empty"
        assert encoded_content != original_content, "Encoding failed"

        # Step 2: Write variable with CODEX_MASTER_KEY
        with token_log_capture as capture:
            token, source = get_token(required_elevated=True)
            assert source == "CODEX_MASTER_KEY", "Should use CODEX_MASTER_KEY"

            var_name = f"TEST_PYTHON_B64_{uuid.uuid4().hex[:8]}"
            success, msg = mock_github_api.create_variable(
                var_name, encoded_content, token
            )
            assert success is True, f"Variable creation failed: {msg}"

            # Step 3: Retrieve variable with CODEX_MASTER_KEY
            retrieved_encoded, found = mock_github_api.get_variable(var_name, token)
            assert found is True, f"Variable not found: {var_name}"
            assert retrieved_encoded == encoded_content, "Retrieved value != encoded value"

            # Step 4: Decode and validate
            decoded_content = token_factory.decode_base64_content(retrieved_encoded)
            assert (
                decoded_content == original_content
            ), "Decoded content != original content"

            # Step 5: Cleanup
            success, msg = mock_github_api.delete_variable(var_name, token)
            assert success is True, f"Variable deletion failed: {msg}"

            # Step 6: Verify cleanup
            retrieved_again, found = mock_github_api.get_variable(var_name, token)
            assert found is False, "Variable should be deleted"

            # Step 7: Verify token never exposed
            capture.assert_token_not_exposed(master_key)

    def test_scenario_8_base64_roundtrip_with_backup_key(
        self,
        env_with_backup_key: Dict[str, str],
        mock_github_api: Any,
        token_factory: Any,
        sample_python_file: str,
    ) -> None:
        """Test base64 round-trip with CODEX_BACKUP_KEY.

        Validates:
        - Backup key also succeeds with elevated operations
        - Round-trip works with backup key
        """
        backup_key = get_token(required_elevated=True)[0]
        assert isinstance(backup_key, str) and len(backup_key) > 0, "backup_key must be a non-empty string"

        # Encode, write, retrieve, decode
        original_content = sample_python_file
        encoded_content = token_factory.create_base64_content(original_content)

        token, source = get_token(required_elevated=True)
        assert source == "CODEX_BACKUP_KEY", "Should use CODEX_BACKUP_KEY"

        var_name = f"TEST_PYTHON_B64_{uuid.uuid4().hex[:8]}"
        success, msg = mock_github_api.create_variable(var_name, encoded_content, token)
        assert success is True, f"Variable creation failed: {msg}"

        retrieved_encoded, found = mock_github_api.get_variable(var_name, token)
        assert found is True, "Variable not found"

        decoded_content = token_factory.decode_base64_content(retrieved_encoded)
        assert decoded_content == original_content, "Round-trip failed"

        # Cleanup
        mock_github_api.delete_variable(var_name, token)

    def test_scenario_8_base64_roundtrip_error_no_elevated_token(
        self,
        env_with_gh_token: Dict[str, str],
        mock_github_api: Any,
        token_factory: Any,
        sample_python_file: str,
    ) -> None:
        """Test base64 round-trip fails without elevated token.

        Validates:
        - Scenario 8 requires elevated token (CODEX_MASTER_KEY or CODEX_BACKUP_KEY)
        - GH_TOKEN cannot be used for elevated operations
        """
        # Should fail to get elevated token
        with pytest.raises(TokenResolutionError):
            get_token(required_elevated=True)

    def test_scenario_8_base64_decode_error(
        self,
        env_with_master_key: Dict[str, str],
        token_factory: Any,
    ) -> None:
        """Test base64 decode error handling.

        Validates:
        - Invalid base64 raises error
        - Error is handled gracefully
        """
        # Invalid base64 (not properly encoded)
        invalid_b64 = "not_valid_base64!!!"

        with pytest.raises(Exception):  # base64 decode error
            token_factory.decode_base64_content(invalid_b64)


# ============================================================================
# TEST SUITE METADATA AND INTEGRATION
# ============================================================================


class TestPhase5TokenIntegration:
    """Integration tests validating all scenarios work together."""

    def test_phase5_token_hierarchy_ordering(
        self,
        isolated_env: Dict[str, str],
        token_factory: Any,
    ) -> None:
        """Test token hierarchy ordering is correct.

        Validates:
        - CANONICAL_HIERARCHY is [MASTER, BACKUP, GH, GITHUB]
        - Priority order is enforced
        """
        master = token_factory.create_token("master")
        backup = token_factory.create_token("backup")

        get_token(required_elevated=True)[0] = master
        get_token(required_elevated=True)[0] = backup

        token, source = get_token(required_elevated=False)
        assert token == master, "Master key should have priority"
        assert source == "CODEX_MASTER_KEY", "Source should be master"

        # Remove master, backup should be next
        os.environ.pop("CODEX_MASTER_KEY")
        token, source = get_token(required_elevated=False)
        assert token == backup, "Backup key should be next in priority"
        assert source == "CODEX_BACKUP_KEY", "Source should be backup"

    def test_phase5_all_scenarios_isolation(
        self,
        isolated_env: Dict[str, str],
    ) -> None:
        """Test that each scenario is properly isolated.

        Validates:
        - Environment is clean between tests
        - No token leakage between scenarios
        """
        # Verify environment is clean
        for var in CANONICAL_HIERARCHY:
            assert os.environ.get(var) is None, f"{var} should not be set"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPhase5Performance:
    """Performance tests for token operations."""

    def test_phase5_token_resolution_performance(
        self,
        env_with_master_key: Dict[str, str],
    ) -> None:
        """Test token resolution performance.

        Validates:
        - Token resolution is fast (< 10ms per call)
        - No performance regression
        """
        start = time.time()
        for _ in range(100):
            get_token(required_elevated=False)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        avg_time = elapsed / 100
        assert avg_time < 10, f"Token resolution too slow: {avg_time}ms per call"

    def test_phase5_scope_validation_performance(
        self,
        env_with_master_key: Dict[str, str],
    ) -> None:
        """Test scope validation performance.

        Validates:
        - Scope validation is fast (< 5ms per call)
        """
        token, _ = get_token(required_elevated=False)

        start = time.time()
        for _ in range(100):
            validate_token_scope(token, ["repo", "workflow"])
        elapsed = (time.time() - start) * 1000  # Convert to ms

        avg_time = elapsed / 100
        assert avg_time < 5, f"Scope validation too slow: {avg_time}ms per call"


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "TestScenario1MasterKeyNormal",
    "TestScenario2BackupKeyFallback",
    "TestScenario3GHTokenFallback",
    "TestScenario4GitHubTokenFallback",
    "TestScenario5ElevatedDeny",
    "TestScenario6ScopeValidation",
    "TestScenario7AuditLogging",
    "TestScenario8Base64RoundTrip",
    "TestPhase5TokenIntegration",
    "TestPhase5Performance",
]
