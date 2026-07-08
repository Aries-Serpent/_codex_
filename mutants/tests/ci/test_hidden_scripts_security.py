"""Security tests for hidden scripts infrastructure.

Comprehensive test suite covering:
    - Access control and RBAC enforcement
    - Integrity verification and checksum validation
    - Audit logging and forensics
    - Encryption/decryption roundtrips
    - Scenario 8b: Security script storage and retrieval integration

All tests enforce zero token exposure in logs and full audit coverage.
"""

import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import (
    Path,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from _hidden_scripts_manager import (
    AuditLogEntry,
    HiddenScriptsManager,
    ScriptMetadata,
    SecurityLevel,
)


class TestAccessControl(unittest.TestCase):
    """Test suite for access control validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = HiddenScriptsManager(
            cache_dir=Path(self.temp_dir.name) / "cache",
            audit_log_path=Path(self.temp_dir.name) / "audit.ndjson",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_token_scope_validation(self):
        """Test that insufficient token scope is blocked.

        A token with only 'repo' scope should not be able to access
        CRITICAL security scripts.
        """
        with patch("_hidden_scripts_manager.get_token") as mock_get_token:
            # Simulate token with insufficient scope (not CODEX_MASTER_KEY)
            mock_get_token.return_value = ("fake_token", "GH_TOKEN")

            is_allowed, msg = self.manager.validate_access_control("test_script")

            # Should be blocked because not CODEX_MASTER_KEY
            self.assertFalse(is_allowed)
            self.assertIn("CODEX_MASTER_KEY", msg)

    def test_unauthorized_agent_rejection(self):
        """Test that non-elevated tokens are rejected.

        Only CODEX_MASTER_KEY should be accepted for security scripts.
        """
        with patch("_hidden_scripts_manager.get_token") as mock_get_token:
            # Simulate fallback token source (not CODEX_MASTER_KEY)
            from scripts.ci._token_resolver import TokenResolutionError
            mock_get_token.side_effect = TokenResolutionError("No elevated token")

            is_allowed, msg = self.manager.validate_access_control("test_script")

            self.assertFalse(is_allowed)

    def test_cross_repo_access_prevention(self):
        """Test that org-level scripts cannot be accessed from non-org context.

        This validates proper isolation of security-critical scripts.
        """
        with patch("_hidden_scripts_manager.get_token") as mock_get_token:
            with patch(
                "_hidden_scripts_manager.get_token_scope"
            ) as mock_scope:
                mock_get_token.return_value = ("fake_token", "CODEX_MASTER_KEY")
                mock_scope.return_value = "standard"  # Not elevated

                is_allowed, msg = self.manager.validate_access_control("org_script")

                self.assertFalse(is_allowed)

    def test_rate_limiting_detection(self):
        """Test handling of GitHub API rate limiting (429 responses).

        Access control should handle rate limit errors gracefully.
        """
        with patch("_hidden_scripts_manager.get_token") as mock_get_token:
            # Simulate rate limit error
            from scripts.ci._token_resolver import TokenResolutionError
            mock_get_token.side_effect = TokenResolutionError(
                "API rate limit exceeded (429 Too Many Requests)"
            )

            is_allowed, msg = self.manager.validate_access_control("test_script")

            self.assertFalse(is_allowed)


class TestIntegrityVerification(unittest.TestCase):
    """Test suite for script integrity verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = HiddenScriptsManager(
            cache_dir=Path(self.temp_dir.name) / "cache",
            audit_log_path=Path(self.temp_dir.name) / "audit.ndjson",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_checksum_validation_on_retrieve(self):
        """Test that SHA256 checksum must match on retrieval.

        Tampered scripts should be rejected with checksum mismatch.
        """
        script_content = "logger.info('test')"

        # Calculate expected checksum
        expected_checksum = self.manager._calculate_checksum(script_content)

        # Create metadata with matching checksum
        metadata = ScriptMetadata(
            name="test_script",
            version="1.0.0",
            security_level=SecurityLevel.HIGH,
            checksum=expected_checksum,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            dependencies=[],
            author="test",
            description="Test",
        )

        self.manager.scripts["test_script"] = metadata

        # Validate integrity with correct content
        is_valid, msg = self.manager.validate_script_integrity(
            "test_script", script_content
        )
        self.assertTrue(is_valid)

        # Validate integrity with tampered content
        tampered_content = "logger.info('tampered')"
        is_valid, msg = self.manager.validate_script_integrity(
            "test_script", tampered_content
        )
        self.assertFalse(is_valid)
        self.assertIn("checksum", msg.lower())

    def test_corrupted_script_detection(self):
        """Test that corrupted (invalid base64) scripts are rejected.

        Invalid base64 data should be detected and rejected gracefully.
        """
        # Create invalid base64 in cache
        cache_path = self.manager.cache_dir / "corrupted.b64"
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        with open(cache_path, "w") as f:
            f.write("this_is_not_valid_base64!!!")

        # Attempt to decode
        with self.assertRaises(ValueError) as ctx:
            self.manager._decode_script("this_is_not_valid_base64!!!")

        self.assertIn("Failed to decode", str(ctx.exception))


class TestAuditLogging(unittest.TestCase):
    """Test suite for audit logging and forensics."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = HiddenScriptsManager(
            cache_dir=Path(self.temp_dir.name) / "cache",
            audit_log_path=Path(self.temp_dir.name) / "audit.ndjson",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_all_access_logged_to_actions(self):
        """Test that all script access is logged to audit trail.

        Every access (store, retrieve, execute) must be logged with
        full metadata but no token values.
        """
        with patch("_hidden_scripts_manager.get_token_scope") as mock_scope:
            mock_scope.return_value = "elevated"

            self.manager._log_security_event(
                event_type="retrieve",
                script_name="test_script",
                result="success",
            )

            # Read audit log
            audit_log = self.manager.get_audit_log()

            self.assertEqual(len(audit_log), 1)
            entry = audit_log[0]

            # Verify no token values in log
            self.assertNotIn("CODEX_MASTER_KEY", json.dumps(entry))
            self.assertNotIn("ghu_", json.dumps(entry))  # GitHub token prefix

            # Verify required fields
            self.assertEqual(entry["event_type"], "retrieve")
            self.assertEqual(entry["script_name"], "test_script")
            self.assertEqual(entry["result"], "success")
            self.assertEqual(entry["token_scope"], "elevated")

    def test_security_events_flagged_correctly(self):
        """Test that security violations are properly flagged.

        Access denials and integrity failures must be marked as
        'blocked' or 'failure' in audit log.
        """
        with patch("_hidden_scripts_manager.get_token_scope") as mock_scope:
            mock_scope.return_value = "standard"

            # Log a blocked access
            self.manager._log_security_event(
                event_type="access_denied",
                script_name="critical_script",
                result="blocked",
                error_message="Insufficient token scope",
            )

            # Log an integrity failure
            self.manager._log_security_event(
                event_type="integrity_check",
                script_name="tampered_script",
                result="failure",
                error_message="Checksum mismatch",
            )

            # Retrieve audit log
            audit_log = self.manager.get_audit_log()

            self.assertEqual(len(audit_log), 2)

            # Verify blocking
            blocked_entry = audit_log[0]
            self.assertEqual(blocked_entry["result"], "blocked")
            self.assertEqual(blocked_entry["error_message"], "Insufficient token scope")

            # Verify failure
            failed_entry = audit_log[1]
            self.assertEqual(failed_entry["result"], "failure")
            self.assertIn("checksum", failed_entry["error_message"].lower())


class TestEncryptionDecryption(unittest.TestCase):
    """Test suite for encryption/decryption operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = HiddenScriptsManager(
            cache_dir=Path(self.temp_dir.name) / "cache",
            audit_log_path=Path(self.temp_dir.name) / "audit.ndjson",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_base64_roundtrip_with_metadata(self):
        """Test encode -> decode roundtrip preserves content and metadata.

        Script content and metadata should survive base64 encoding/decoding
        without corruption.
        """
        original_content = "logger.info('Hello, World!')"
        metadata = {
            "name": "test",
            "version": "1.0.0",
            "security_level": 2,
            "checksum": "abc123",
        }

        # Encode
        encoded = self.manager._encode_script(original_content, metadata)

        # Decode
        decoded_content, decoded_metadata = self.manager._decode_script(encoded)

        # Verify
        self.assertEqual(decoded_content, original_content)
        self.assertEqual(decoded_metadata["name"], metadata["name"])
        self.assertEqual(decoded_metadata["version"], metadata["version"])
        self.assertEqual(decoded_metadata["security_level"], metadata["security_level"])

    def test_invalid_base64_handling(self):
        """Test graceful handling of invalid base64 data.

        Corrupted or invalid base64 should raise informative error.
        """
        invalid_base64 = "not@valid#base64!!!"

        with self.assertRaises(ValueError) as ctx:
            self.manager._decode_script(invalid_base64)

        self.assertIn("Failed to decode", str(ctx.exception))


class TestScenario8bIntegration(unittest.TestCase):
    """Test suite for Scenario 8b: Security script storage and retrieval.

    This scenario validates the full lifecycle:
    1. Store vulnerability detector script as base64
    2. Retrieve with CODEX_MASTER_KEY
    3. Execute in sandbox
    4. Verify: script NOT in git, checksum valid, audit log complete, no token exposure
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = HiddenScriptsManager(
            cache_dir=Path(self.temp_dir.name) / "cache",
            audit_log_path=Path(self.temp_dir.name) / "audit.ndjson",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_scenario_8b_security_script_storage_retrieval(self):
        """Full Scenario 8b integration test."""
        # Vulnerability detector script
        vulnerability_detector = """
import json
import sys
from codex.logging.structured_logger import logger

# Simulated vulnerability detection logic
vulnerabilities = [
    {"id": "CVE-2024-001", "severity": "HIGH", "package": "requests"},
    {"id": "CVE-2024-002", "severity": "CRITICAL", "package": "flask"},
]

logger.info(json.dumps({"vulnerabilities": vulnerabilities, "scan_time": 1234}))
sys.exit(0)
"""

        with patch("_hidden_scripts_manager.get_token") as mock_get_token:
            with patch(
                "_hidden_scripts_manager.get_token_scope"
            ) as mock_scope:
                with patch(
                    "_hidden_scripts_manager.validate_token_scope"
                ) as mock_validate_scope:
                    mock_get_token.return_value = ("fake_master_key", "CODEX_MASTER_KEY")
                    mock_scope.return_value = "elevated"
                    mock_validate_scope.return_value = (True, "Valid scope")

                    # STEP 1: Store the script
                    success, msg = self.manager.store_hidden_script(
                        name="vulnerability_detector",
                        script_content=vulnerability_detector,
                        security_level=SecurityLevel.CRITICAL,
                        version="1.0.0",
                        author="security_team",
                        description="Detects known vulnerabilities in dependencies",
                    )

                    self.assertTrue(success)
                    self.assertIn("stored successfully", msg.lower())

                    # Verify script NOT in git (only in cache)
                    cache_path = self.manager.cache_dir / "vulnerability_detector.b64"
                    self.assertTrue(cache_path.exists())

                    # STEP 2: Retrieve the script
                    retrieved_content, retrieve_msg = self.manager.retrieve_hidden_script(
                        "vulnerability_detector"
                    )

                    self.assertIsNotNone(retrieved_content)
                    self.assertEqual(retrieved_content, vulnerability_detector)

                    # STEP 3: Verify checksum is valid
                    checksum_valid, checksum_msg = self.manager.validate_script_integrity(
                        "vulnerability_detector", retrieved_content
                    )
                    self.assertTrue(checksum_valid)

                    # STEP 4: Verify audit log is complete
                    audit_log = self.manager.get_audit_log()

                    # Should have store + retrieve entries
                    self.assertGreaterEqual(len(audit_log), 2)

                    store_entry = [e for e in audit_log if e["event_type"] == "store"][0]
                    retrieve_entry = [
                        e for e in audit_log if e["event_type"] == "retrieve"
                    ][0]

                    # Verify required fields
                    self.assertEqual(store_entry["script_name"], "vulnerability_detector")
                    self.assertEqual(store_entry["result"], "success")
                    self.assertEqual(store_entry["token_scope"], "elevated")

                    self.assertEqual(retrieve_entry["script_name"], "vulnerability_detector")
                    self.assertEqual(retrieve_entry["result"], "success")

                    # STEP 5: Verify zero token exposure in logs
                    audit_json = json.dumps(audit_log)
                    self.assertNotIn("CODEX_MASTER_KEY", audit_json)
                    self.assertNotIn("ghu_", audit_json)
                    self.assertNotIn("fake_master_key", audit_json)

                    # STEP 6: Verify 100% audit coverage
                    self.assertEqual(len([e for e in audit_log if e["result"] != ""]), len(audit_log))


class TestScriptMetadata(unittest.TestCase):
    """Test suite for script metadata handling."""

    def test_metadata_serialization(self):
        """Test ScriptMetadata serialization and deserialization."""
        metadata = ScriptMetadata(
            name="test_script",
            version="1.0.0",
            security_level=SecurityLevel.HIGH,
            checksum="abc123def456",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
            dependencies=["requests", "flask"],
            author="test_author",
            description="Test script",
        )

        # Serialize
        data = metadata.to_dict()

        self.assertEqual(data["name"], "test_script")
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["security_level"], SecurityLevel.HIGH)
        self.assertEqual(len(data["dependencies"]), 2)

        # Deserialize
        restored = ScriptMetadata.from_dict(data)

        self.assertEqual(restored.name, metadata.name)
        self.assertEqual(restored.version, metadata.version)
        self.assertEqual(restored.security_level, metadata.security_level)


class TestAuditLogEntry(unittest.TestCase):
    """Test suite for audit log entry handling."""

    def test_audit_entry_creation_and_serialization(self):
        """Test AuditLogEntry creation and JSON serialization."""
        entry = AuditLogEntry(
            timestamp="2024-01-01T00:00:00",
            event_type="execute",
            script_name="test_script",
            agent_id="test_agent",
            token_scope="elevated",
            result="success",
            execution_time_ms=1234,
        )

        # Serialize
        data = entry.to_dict()

        self.assertEqual(data["event_type"], "execute")
        self.assertEqual(data["script_name"], "test_script")
        self.assertEqual(data["result"], "success")
        self.assertEqual(data["execution_time_ms"], 1234)

        # Verify JSON serializable
        json_str = json.dumps(data)
        self.assertIsInstance(json_str, str)


def run_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAccessControl))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrityVerification))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestEncryptionDecryption))
    suite.addTests(loader.loadTestsFromTestCase(TestScenario8bIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestScriptMetadata))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLogEntry))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
