# src/codex/archive/evidence_schema.py
"""
Evidence Record Schema Versioning and Validation

Supports parallel v1 (legacy) and v2 (standardized) schemas
with automatic migration capabilities.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    HAS_JSONSCHEMA = False


class EvidenceSchemaValidator:
    """Validates evidence records against versioned schemas."""

    def __init__(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "schemas")
        self.schema_dir = Path(schema_dir)
        self.schemas: dict[str, Any] = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def validate(self, record: dict[str, Any], version: str = "2.0") -> bool:
        """
        Validate evidence record against schema version.

        Args:
            record: Evidence record to validate
            version: Schema version ("1.0" or "2.0")

        Returns:
            True if valid; raises jsonschema.ValidationError if invalid

        Raises:
            ValueError: If version not supported
            jsonschema.ValidationError: If record doesn't match schema
        """
        if not HAS_JSONSCHEMA:
            # Skip validation if jsonschema not available
            return True

        if version not in self.schemas:
            raise ValueError(f"Unsupported schema version: {version}")

        schema = self.schemas[version]
        jsonschema.validate(instance=record, schema=schema)
        return True

    def auto_detect_version(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def migrate_to_v2(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "schemaVersion": "2.0",
            "standardizationMetadata": {
                "schema_version": "2.0",
                "slsa_level": "L3",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def migrate_record(
        self,
        record: dict[str, Any],
        from_version: Optional[str] = None,
        to_version: str = "2.0",
    ) -> dict[str, Any]:
        """
        Migrate record between schema versions.

        Args:
            record: Record to migrate
            from_version: Source version (auto-detected if None)
            to_version: Target version (default 2.0)

        Returns:
            Migrated record
        """
        if from_version is None:
            from_version = self.auto_detect_version(record)

        if from_version == "1.0" and to_version == "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")
