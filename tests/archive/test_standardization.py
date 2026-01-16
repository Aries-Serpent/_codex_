"""
Test Standardization

Test module for standardization.
"""

# tests/archive/test_standardization.py
"""Tests for standardization layer."""

import pytest

from src.codex.archive.evidence_schema import EvidenceSchemaValidator
from src.codex.archive.standardization import (
    SLSA_LEVEL,
    STANDARDIZATION_VERSION,
    StandardizationManager,
    StandardizationMetadata,
)


class TestStandardizationMetadata:
    """Test StandardizationMetadata dataclass."""

    def test_creation(self):
        meta = StandardizationMetadata()
        assert meta.schema_version == "2.0"
        assert meta.slsa_level == "L3"

    def test_to_dict_omits_none(self):
        meta = StandardizationMetadata(
            schema_version="2.0",
            slsa_level="L3",
            signature=None,
        )
        d = meta.to_dict()
        assert "signature" not in d
        assert "schema_version" in d


class TestStandardizationManager:
    """Test StandardizationManager."""

    @pytest.fixture
    def manager(self):
        return StandardizationManager(enable_signing=False)

    @pytest.fixture
    def sample_record(self):
        return {
            "ts": "2025-11-02T19:44:00Z",
            "action": "ARCHIVE",
            "actor": "marc",
            "repo": "_codex_",
            "path": "src/legacy/test.py",
            "tombstone": "d3e8729-1234-5678-abcd-ef0123456789",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "size": 4096,
            "commit": "d3e87290abcdef1234567890",
        }

    def test_enhance_evidence_record(self, manager, sample_record):
        enhanced = manager.enhance_evidence_record(
            record=sample_record,
            actor="marc",
            sign_now=False,
        )

        assert enhanced["schemaVersion"] == "2.0"
        assert "standardizationMetadata" in enhanced
        assert enhanced["standardizationMetadata"]["slsa_level"] == "L3"

    def test_verify_standardization(self, manager, sample_record):
        enhanced = manager.enhance_evidence_record(
            record=sample_record,
            actor="marc",
            sign_now=False,
        )

        result = manager.verify_standardization(enhanced)
        assert result["valid"] is True
        assert result["schema_version"] == "2.0"

    def test_backward_compatibility_v1(self, manager, sample_record):
        """Test that v1 records still work."""
        result = manager.verify_standardization(sample_record)
        # v1 records should be valid even without standardization metadata
        assert result["schema_version"] == "1.0"

    def test_get_standardization_report(self, manager):
        """Test generating standardization report."""
        report = manager.get_standardization_report()

        assert report["standard_version"] == STANDARDIZATION_VERSION
        assert report["slsa_level"] == SLSA_LEVEL
        assert "1.0" in report["schema_versions_supported"]
        assert "2.0" in report["schema_versions_supported"]


class TestEvidenceSchemaValidator:
    """Test EvidenceSchemaValidator class."""

    @pytest.fixture
    def validator(self):
        # Use default (project root schemas dir)
        return EvidenceSchemaValidator()

    def test_auto_detect_version_v1(self, validator):
        """Test auto-detection of v1 record."""
        record = {"ts": "2025-11-02T19:44:00Z"}
        assert validator.auto_detect_version(record) == "1.0"

    def test_auto_detect_version_v2_explicit(self, validator):
        """Test auto-detection with explicit schemaVersion."""
        record = {"schemaVersion": "2.0"}
        assert validator.auto_detect_version(record) == "2.0"

    def test_auto_detect_version_v2_via_metadata(self, validator):
        """Test auto-detection via standardizationMetadata."""
        record = {"standardizationMetadata": {}}
        assert validator.auto_detect_version(record) == "2.0"

    def test_migrate_v1_to_v2(self, validator):
        """Test migrating v1 record to v2."""
        v1_record = {
            "ts": "2025-11-02T19:44:00Z",
            "action": "ARCHIVE",
            "actor": "marc",
            "tombstone": "d3e8729-1234-5678-abcd-ef0123456789",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }

        v2_record = validator.migrate_to_v2(v1_record)

        assert v2_record["schemaVersion"] == "2.0"
        assert "standardizationMetadata" in v2_record
        assert v2_record["standardizationMetadata"]["slsa_level"] == "L3"
