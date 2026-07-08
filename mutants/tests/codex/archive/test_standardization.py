"""
Tests for codex.archive.standardization module.

This module contains tests for SLSA L3 standardization layer.
"""

from unittest.mock import MagicMock, patch


class TestStandardizationMetadata:
    """Tests for StandardizationMetadata dataclass."""

    def test_default_values(self):
        """Test StandardizationMetadata default values."""
        from codex.archive.standardization import StandardizationMetadata

        metadata = StandardizationMetadata()

        assert metadata.schema_version == "2.0", "Data must not be empty"
        assert metadata.slsa_level == "L3", "Data must not be empty"
        assert metadata.signature is None, "Data must not be empty"
        assert metadata.certificate_chain is None, "Data must not be empty"
        assert metadata.issuer is None, "Data must not be empty"
        assert metadata.signed_at is None, "Data must not be empty"
        assert metadata.in_toto_attestation_id is None, "Data must not be empty"
        assert metadata.merkle_proof is None, "Data must not be empty"

    def test_custom_values(self):
        """Test StandardizationMetadata with custom values."""
        from codex.archive.standardization import StandardizationMetadata

        metadata = StandardizationMetadata(
            schema_version="3.0", slsa_level="L4", signature="sig_abc123", issuer="sigstore.dev"
        )

        assert metadata.schema_version == "3.0", "Data must not be empty"
        assert metadata.slsa_level == "L4", "Data must not be empty"
        assert metadata.signature == "sig_abc123", "Data must not be empty"
        assert metadata.issuer == "sigstore.dev", "Data must not be empty"

    def test_to_dict(self):
        """Test to_dict method omits None values."""
        from codex.archive.standardization import StandardizationMetadata

        metadata = StandardizationMetadata(signature="sig_123", issuer="test_issuer")

        result = metadata.to_dict()

        assert result["schema_version"] == "2.0", "Result must not be empty"
        assert result["slsa_level"] == "L3", "Result must not be empty"
        assert result["signature"] == "sig_123", "Result must not be empty"
        assert result["issuer"] == "test_issuer", "Result must not be empty"
        # None values should be omitted
        assert "certificate_chain" not in result, "Result must not be empty"
        assert "signed_at" not in result, "Result must not be empty"


class TestStandardizationManager:
    """Tests for StandardizationManager class."""

    @patch("codex.archive.standardization.SignstoreClient")
    @patch("codex.archive.standardization.EvidenceSchemaValidator")
    @patch.dict("os.environ", {"CODEX_ENABLE_SIGNING": "false"})
    def test_init_signing_disabled(self, MockValidator, MockClient):
        """Test initialization with signing disabled."""
        from codex.archive.standardization import StandardizationManager

        manager = StandardizationManager(enable_signing=False)

        assert manager.enable_signing is False, "enable_signing is not valid"
        assert manager.sigstore_client is None, "sigstore_client is not valid"

    @patch("codex.archive.standardization.SignstoreClient")
    @patch("codex.archive.standardization.EvidenceSchemaValidator")
    def test_init_verify_only(self, MockValidator, MockClient):
        """Test initialization in verify-only mode."""
        from codex.archive.standardization import StandardizationManager

        MockClient.return_value = MagicMock()

        manager = StandardizationManager(verify_only=True)

        assert manager.enable_signing is True, "enable_signing is not valid"

    @patch("codex.archive.standardization.SignstoreClient")
    @patch("codex.archive.standardization.EvidenceSchemaValidator")
    def test_has_schema_validator(self, MockValidator, MockClient):
        """Test manager has schema validator."""
        from codex.archive.standardization import StandardizationManager

        MockValidator.return_value = MagicMock()

        manager = StandardizationManager(enable_signing=False)

        assert manager.schema_validator is not None, "schema_validator must be initialized"


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_standardization_version(self):
        """Test STANDARDIZATION_VERSION constant."""
        from codex.archive.standardization import STANDARDIZATION_VERSION

        assert STANDARDIZATION_VERSION == "2.0", "STANDARDIZATION_VERSION is not valid"

    def test_slsa_level(self):
        """Test SLSA_LEVEL constant."""
        from codex.archive.standardization import SLSA_LEVEL

        assert SLSA_LEVEL == "L3", "SLSA_LEVEL is not valid"

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.standardization import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.archive.standardization", "name is not valid"
