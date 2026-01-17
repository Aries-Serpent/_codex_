"""
Tests for codex.archive.standardization module.

This module contains tests for SLSA L3 standardization layer.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestStandardizationMetadata:
    """Tests for StandardizationMetadata dataclass."""

    def test_default_values(self):
        """Test StandardizationMetadata default values."""
        from codex.archive.standardization import StandardizationMetadata
        
        metadata = StandardizationMetadata()
        
        assert metadata.schema_version == "2.0"
        assert metadata.slsa_level == "L3"
        assert metadata.signature is None
        assert metadata.certificate_chain is None
        assert metadata.issuer is None
        assert metadata.signed_at is None
        assert metadata.in_toto_attestation_id is None
        assert metadata.merkle_proof is None

    def test_custom_values(self):
        """Test StandardizationMetadata with custom values."""
        from codex.archive.standardization import StandardizationMetadata
        
        metadata = StandardizationMetadata(
            schema_version="3.0",
            slsa_level="L4",
            signature="sig_abc123",
            issuer="sigstore.dev"
        )
        
        assert metadata.schema_version == "3.0"
        assert metadata.slsa_level == "L4"
        assert metadata.signature == "sig_abc123"
        assert metadata.issuer == "sigstore.dev"

    def test_to_dict(self):
        """Test to_dict method omits None values."""
        from codex.archive.standardization import StandardizationMetadata
        
        metadata = StandardizationMetadata(
            signature="sig_123",
            issuer="test_issuer"
        )
        
        result = metadata.to_dict()
        
        assert result["schema_version"] == "2.0"
        assert result["slsa_level"] == "L3"
        assert result["signature"] == "sig_123"
        assert result["issuer"] == "test_issuer"
        # None values should be omitted
        assert "certificate_chain" not in result
        assert "signed_at" not in result


class TestStandardizationManager:
    """Tests for StandardizationManager class."""

    @patch('codex.archive.standardization.SignstoreClient')
    @patch('codex.archive.standardization.EvidenceSchemaValidator')
    @patch.dict('os.environ', {'CODEX_ENABLE_SIGNING': 'false'})
    def test_init_signing_disabled(self, MockValidator, MockClient):
        """Test initialization with signing disabled."""
        from codex.archive.standardization import StandardizationManager
        
        manager = StandardizationManager(enable_signing=False)
        
        assert manager.enable_signing is False
        assert manager.sigstore_client is None

    @patch('codex.archive.standardization.SignstoreClient')
    @patch('codex.archive.standardization.EvidenceSchemaValidator')
    def test_init_verify_only(self, MockValidator, MockClient):
        """Test initialization in verify-only mode."""
        from codex.archive.standardization import StandardizationManager
        
        MockClient.return_value = MagicMock()
        
        manager = StandardizationManager(verify_only=True)
        
        assert manager.enable_signing is True

    @patch('codex.archive.standardization.SignstoreClient')
    @patch('codex.archive.standardization.EvidenceSchemaValidator')
    def test_has_schema_validator(self, MockValidator, MockClient):
        """Test manager has schema validator."""
        from codex.archive.standardization import StandardizationManager
        
        MockValidator.return_value = MagicMock()
        
        manager = StandardizationManager(enable_signing=False)
        
        assert manager.schema_validator is not None


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_standardization_version(self):
        """Test STANDARDIZATION_VERSION constant."""
        from codex.archive.standardization import STANDARDIZATION_VERSION
        
        assert STANDARDIZATION_VERSION == "2.0"

    def test_slsa_level(self):
        """Test SLSA_LEVEL constant."""
        from codex.archive.standardization import SLSA_LEVEL
        
        assert SLSA_LEVEL == "L3"

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.standardization import logger
        
        assert logger is not None
        assert logger.name == "codex.archive.standardization"
