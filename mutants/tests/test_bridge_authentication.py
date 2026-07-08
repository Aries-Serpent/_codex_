"""
Test suite for bridge authentication and audit trail features (PS-02).

Tests the security enhancements added in PS-02:
- Authentication token validation
- Security audit trail logging
- Constant-time token comparison (timing attack prevention)
"""

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from bridge_manager import (
    BridgeManager,
    BridgeMode,
    ContextMessage,
)


class TestBridgeAuthentication:
    """Test suite for bridge authentication features."""

    def test_auth_token_from_environment(self):
        """Test that auth token is loaded from CODEX_BRIDGE_TOKEN environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set auth token
            os.environ["CODEX_BRIDGE_TOKEN"] = "test_token_12345"

            try:
                bridge = BridgeManager(
                    bridge_dir=Path(tmpdir) / "auth_test",
                    mode=BridgeMode.NAMED_PIPE,
                    require_auth=True,
                )

                assert bridge.auth_token == "test_token_12345", "auth_token is not valid"
                assert bridge.require_auth is True, "require_auth is not valid"

                bridge.cleanup()
            finally:
                del os.environ["CODEX_BRIDGE_TOKEN"]

    def test_auth_disabled_when_token_missing(self):
        """Test that authentication is disabled when CODEX_BRIDGE_TOKEN is not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Ensure token is not set
            if "CODEX_BRIDGE_TOKEN" in os.environ:
                del os.environ["CODEX_BRIDGE_TOKEN"]

            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "no_auth_test",
                mode=BridgeMode.NAMED_PIPE,
                require_auth=True,  # Request auth
            )

            # Auth should be disabled since token is missing
            assert bridge.require_auth is False, "require_auth is not valid"

            bridge.cleanup()

    def test_message_with_valid_token_accepted(self):
        """Test that messages with valid auth tokens are accepted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CODEX_BRIDGE_TOKEN"] = "secure_token_xyz"

            try:
                bridge = BridgeManager(
                    bridge_dir=Path(tmpdir) / "valid_token_test",
                    mode=BridgeMode.NAMED_PIPE,
                    require_auth=True,
                )

                message = ContextMessage(
                    timestamp=datetime.now(UTC).isoformat(),
                    source="test_client",
                    message_type="test_message",
                    context={"data": "test"},
                    auth_token="secure_token_xyz",
                )

                # Should pass authentication
                assert bridge._verify_auth_token(message) is True, "Condition must be true"

                bridge.cleanup()
            finally:
                del os.environ["CODEX_BRIDGE_TOKEN"]

    def test_message_with_invalid_token_rejected(self):
        """Test that messages with invalid auth tokens are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CODEX_BRIDGE_TOKEN"] = "correct_token"

            try:
                bridge = BridgeManager(
                    bridge_dir=Path(tmpdir) / "invalid_token_test",
                    mode=BridgeMode.NAMED_PIPE,
                    require_auth=True,
                )

                message = ContextMessage(
                    timestamp=datetime.now(UTC).isoformat(),
                    source="malicious_client",
                    message_type="test_message",
                    context={"data": "test"},
                    auth_token="wrong_token",  # Wrong token
                )

                # Should fail authentication
                assert bridge._verify_auth_token(message) is False, "Condition must be true"

                bridge.cleanup()
            finally:
                del os.environ["CODEX_BRIDGE_TOKEN"]

    def test_message_without_token_rejected(self):
        """Test that messages without auth tokens are rejected when auth is required."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CODEX_BRIDGE_TOKEN"] = "required_token"

            try:
                bridge = BridgeManager(
                    bridge_dir=Path(tmpdir) / "no_token_test",
                    mode=BridgeMode.NAMED_PIPE,
                    require_auth=True,
                )

                message = ContextMessage(
                    timestamp=datetime.now(UTC).isoformat(),
                    source="unauthorized_client",
                    message_type="test_message",
                    context={"data": "test"},
                    auth_token=None,  # No token
                )

                # Should fail authentication
                assert bridge._verify_auth_token(message) is False, "Condition must be true"

                bridge.cleanup()
            finally:
                del os.environ["CODEX_BRIDGE_TOKEN"]

    def test_auth_bypass_when_disabled(self):
        """Test that authentication is bypassed when require_auth is False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "auth_disabled_test",
                mode=BridgeMode.NAMED_PIPE,
                require_auth=False,  # Auth disabled
            )

            message = ContextMessage(
                timestamp=datetime.now(UTC).isoformat(),
                source="any_client",
                message_type="test_message",
                context={"data": "test"},
                auth_token=None,  # No token needed
            )

            # Should pass even without token
            assert bridge._verify_auth_token(message) is True, "Condition must be true"

            bridge.cleanup()


class TestBridgeAuditTrail:
    """Test suite for bridge audit trail logging."""

    def test_audit_file_created(self):
        """Test that audit log file is created with secure permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "audit_test",
                mode=BridgeMode.NAMED_PIPE,
                owner_only=True,
            )

            # Audit file should exist
            assert bridge.audit_file.exists(), "Condition must be true"

            # Check permissions (0o600 = owner only rw)
            audit_stat = bridge.audit_file.stat()
            audit_mode = audit_stat.st_mode & 0o777
            assert audit_mode == 0o600, f"Expected 0o600, got {oct(audit_mode)}"

            bridge.cleanup()

    def test_audit_log_records_init(self):
        """Test that bridge initialization is logged to audit trail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "init_audit_test",
                mode=BridgeMode.NAMED_PIPE,
            )

            # Read audit log
            with open(bridge.audit_file, "r") as f:
                lines = f.readlines()

            # Should have at least one entry (BRIDGE_INIT)
            assert len(lines) >= 1, "Lines must not be empty"

            # Parse first entry
            init_entry = json.loads(lines[0])
            assert init_entry["event"] == "BRIDGE_INIT", "Condition must be true"
            assert "mode" in init_entry["details"], "Condition must be true"
            assert init_entry["details"]["mode"] == "named_pipe", "Condition must be true"

            bridge.cleanup()

    def test_audit_log_records_auth_success(self):
        """Test that successful authentication is logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CODEX_BRIDGE_TOKEN"] = "audit_test_token"

            try:
                bridge = BridgeManager(
                    bridge_dir=Path(tmpdir) / "auth_success_audit",
                    mode=BridgeMode.NAMED_PIPE,
                    require_auth=True,
                )

                message = ContextMessage(
                    timestamp=datetime.now(UTC).isoformat(),
                    source="test_client",
                    message_type="test_message",
                    context={"data": "test"},
                    auth_token="audit_test_token",
                )

                # Verify token (triggers audit log)
                bridge._verify_auth_token(message)

                # Read audit log
                with open(bridge.audit_file, "r") as f:
                    lines = f.readlines()

                # Find AUTH_SUCCESS entry
                auth_entries = []
                for line in lines:
                    entry = json.loads(line)
                    if entry["event"] == "AUTH_SUCCESS":
                        auth_entries.append(entry)

                assert len(auth_entries) >= 1, "Auth_entries must not be empty"
                assert auth_entries[0]["details"]["source"] == "test_client", "Condition must be true"

                bridge.cleanup()
            finally:
                del os.environ["CODEX_BRIDGE_TOKEN"]

    def test_audit_log_records_auth_failure(self):
        """Test that failed authentication is logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CODEX_BRIDGE_TOKEN"] = "correct_token"

            try:
                bridge = BridgeManager(
                    bridge_dir=Path(tmpdir) / "auth_failure_audit",
                    mode=BridgeMode.NAMED_PIPE,
                    require_auth=True,
                )

                message = ContextMessage(
                    timestamp=datetime.now(UTC).isoformat(),
                    source="malicious_client",
                    message_type="test_message",
                    context={"data": "test"},
                    auth_token="wrong_token",
                )

                # Verify token (should fail and log)
                bridge._verify_auth_token(message)

                # Read audit log
                with open(bridge.audit_file, "r") as f:
                    lines = f.readlines()

                # Find AUTH_FAILURE entry
                failure_entries = []
                for line in lines:
                    entry = json.loads(line)
                    if entry["event"] == "AUTH_FAILURE":
                        failure_entries.append(entry)

                assert len(failure_entries) >= 1, "Failure_entries must not be empty"
                assert failure_entries[0]["details"]["reason"] == "invalid_token", "Condition must be true"
                assert failure_entries[0]["details"]["source"] == "malicious_client", "Condition must be true"

                bridge.cleanup()
            finally:
                del os.environ["CODEX_BRIDGE_TOKEN"]

    def test_audit_log_records_cleanup(self):
        """Test that bridge cleanup is logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "cleanup_audit",
                mode=BridgeMode.NAMED_PIPE,
            )

            audit_file_path = bridge.audit_file

            # Cleanup (should log)
            bridge.cleanup()

            # Read audit log
            with open(audit_file_path, "r") as f:
                lines = f.readlines()

            # Find BRIDGE_CLEANUP entry
            cleanup_entries = []
            for line in lines:
                entry = json.loads(line)
                if entry["event"] == "BRIDGE_CLEANUP":
                    cleanup_entries.append(entry)

            assert len(cleanup_entries) >= 1, "Cleanup_entries must not be empty"

    def test_audit_log_includes_pid_and_uid(self):
        """Test that audit log entries include process ID and user ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "pid_uid_audit",
                mode=BridgeMode.NAMED_PIPE,
            )

            # Read audit log
            with open(bridge.audit_file, "r") as f:
                lines = f.readlines()

            # Parse first entry
            entry = json.loads(lines[0])
            assert "pid" in entry, "Condition must be true"
            assert "uid" in entry, "Condition must be true"
            assert entry["pid"] == os.getpid(), "Condition must be true"
            assert entry["uid"] == os.getuid(), "Condition must be true"

            bridge.cleanup()


class TestTimingAttackPrevention:
    """Test suite for timing attack prevention in authentication."""

    def test_constant_time_token_comparison(self):
        """Test that token comparison uses constant-time algorithm."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CODEX_BRIDGE_TOKEN"] = "secret_token_12345"

            try:
                bridge = BridgeManager(
                    bridge_dir=Path(tmpdir) / "timing_test",
                    mode=BridgeMode.NAMED_PIPE,
                    require_auth=True,
                )

                # Create messages with different tokens
                valid_message = ContextMessage(
                    timestamp=datetime.now(UTC).isoformat(),
                    source="test",
                    message_type="test",
                    context={},
                    auth_token="secret_token_12345",  # Correct
                )

                invalid_message = ContextMessage(
                    timestamp=datetime.now(UTC).isoformat(),
                    source="test",
                    message_type="test",
                    context={},
                    auth_token="aaaaaaaaaaaaaaaaa",  # Wrong
                )

                # Both should execute without revealing timing information
                # (We can't easily test timing directly, but we verify both execute)
                result1 = bridge._verify_auth_token(valid_message)
                result2 = bridge._verify_auth_token(invalid_message)

                assert result1 is True, "Result must not be empty"
                assert result2 is False, "Result must not be empty"

                bridge.cleanup()
            finally:
                del os.environ["CODEX_BRIDGE_TOKEN"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
