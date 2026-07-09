"""
Schema Validator Module for Docs Agent

Provides validation utilities for JSONL records against JSON Schema definitions.
Wraps jsonschema library with enhanced error reporting and cross-record validation.

Authority: Lane 3 Unified Documentation Agent
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema
    from jsonschema import Draft202012Validator, validate
    from jsonschema import ValidationError as JsonSchemaValidationError
except ImportError:
    raise ImportError("jsonschema module required. Install with: pip install jsonschema")

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Validation error details"""

    record_id: str
    record_type: str
    field: Optional[str]
    message: str
    severity: str  # "error" or "warning"


class SchemaValidator:
    """Validates JSONL records against JSON Schema definitions"""

    def __init__(self, schemas_dir: Optional[Path] = None):
        """Initialize with schemas directory

        Args:
            schemas_dir: Path to schemas directory (default: .codex/schemas)
        """
        if schemas_dir is None:
            schemas_dir = Path(".codex/schemas")

        self.schemas_dir = schemas_dir
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.validators: Dict[str, Draft202012Validator] = {}

        self._load_schemas()

    def _load_schemas(self):
        """Load all JSON Schema files from directory"""
        if not self.schemas_dir.exists():
            raise FileNotFoundError(f"Schemas directory not found: {self.schemas_dir}")

        schema_files = list(self.schemas_dir.glob("*.json"))
        if not schema_files:
            raise FileNotFoundError(f"No schema files in {self.schemas_dir}")

        for schema_file in schema_files:
            try:
                with open(schema_file, "r") as f:
                    schema = json.load(f)
                    record_type = schema_file.stem
                    self.schemas[record_type] = schema
                    self.validators[record_type] = Draft202012Validator(schema)
                    logger.debug(f"Loaded schema: {record_type}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {schema_file}: {e}")
                raise

        logger.info(f"Loaded {len(self.schemas)} schemas")

    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single record

        Args:
            record: JSON record to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Require id and type
        if "id" not in record:
            errors.append("Missing required field: id")
        if "type" not in record:
            errors.append("Missing required field: type")

        if errors:
            return False, errors

        record_type = record.get("type")
        if record_type not in self.schemas:
            errors.append(f"Unknown record type: {record_type}")
            return False, errors

        # Validate against schema
        try:
            self.validators[record_type].validate(record)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            return False, errors

        return True, []

    def validate_file(self, jsonl_file: Path) -> Dict[str, Any]:
        """Validate a JSONL file

        Args:
            jsonl_file: Path to JSONL file

        Returns:
            Dictionary with validation results
        """
        results: Dict[str, Any] = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "errors": [],
            "records_by_type": {},
        }

        with open(jsonl_file, "r") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                results["total_records"] += 1

                try:
                    record = json.loads(line)
                    is_valid, errors = self.validate_record(record)

                    record_type = record.get("type", "unknown")
                    record_id = record.get("id", "unknown")

                    if record_type not in results["records_by_type"]:
                        results["records_by_type"][record_type] = 0
                    results["records_by_type"][record_type] += 1

                    if is_valid:
                        results["valid_records"] += 1
                    else:
                        results["invalid_records"] += 1
                        for error in errors:
                            results["errors"].append(
                                {
                                    "line": line_no,
                                    "record_id": record_id,
                                    "record_type": record_type,
                                    "message": error,
                                }
                            )

                except json.JSONDecodeError as e:
                    results["invalid_records"] += 1
                    results["errors"].append({"line": line_no, "message": f"Invalid JSON: {e}"})

        results["accuracy_percent"] = (
            results["valid_records"] / results["total_records"] * 100
            if results["total_records"] > 0
            else 0
        )

        return results
