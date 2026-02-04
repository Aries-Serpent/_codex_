# src/codex/archive/evidence_schema.py
"""
Evidence Record Schema Versioning and Validation

Supports parallel v1 (legacy) and v2 (standardized) schemas
with automatic migration capabilities.
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path
from typing import Any, Optional

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    HAS_JSONSCHEMA = False
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class EvidenceSchemaValidator:
    """Validates evidence records against versioned schemas."""

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_orig(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "schemas")
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_1(self, schema_dir: Optional[str] = None):
        if schema_dir is not None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "schemas")
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_2(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = None
            schema_dir = str(project_root / "schemas")
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_3(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(None).parent.parent.parent.parent
            schema_dir = str(project_root / "schemas")
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_4(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = None
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_5(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(None)
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_6(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root * "schemas")
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_7(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "XXschemasXX")
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_8(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "SCHEMAS")
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_9(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "schemas")
        self.schema_dir = None
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_10(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "schemas")
        self.schema_dir = Path(None)
        self.schemas = {}
        self._load_schemas()

    def xǁEvidenceSchemaValidatorǁ__init____mutmut_11(self, schema_dir: Optional[str] = None):
        if schema_dir is None:
            # Default to schemas dir relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            schema_dir = str(project_root / "schemas")
        self.schema_dir = Path(schema_dir)
        self.schemas = None
        self._load_schemas()
    
    xǁEvidenceSchemaValidatorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEvidenceSchemaValidatorǁ__init____mutmut_1': xǁEvidenceSchemaValidatorǁ__init____mutmut_1, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_2': xǁEvidenceSchemaValidatorǁ__init____mutmut_2, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_3': xǁEvidenceSchemaValidatorǁ__init____mutmut_3, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_4': xǁEvidenceSchemaValidatorǁ__init____mutmut_4, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_5': xǁEvidenceSchemaValidatorǁ__init____mutmut_5, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_6': xǁEvidenceSchemaValidatorǁ__init____mutmut_6, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_7': xǁEvidenceSchemaValidatorǁ__init____mutmut_7, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_8': xǁEvidenceSchemaValidatorǁ__init____mutmut_8, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_9': xǁEvidenceSchemaValidatorǁ__init____mutmut_9, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_10': xǁEvidenceSchemaValidatorǁ__init____mutmut_10, 
        'xǁEvidenceSchemaValidatorǁ__init____mutmut_11': xǁEvidenceSchemaValidatorǁ__init____mutmut_11
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁEvidenceSchemaValidatorǁ__init____mutmut_orig)
    xǁEvidenceSchemaValidatorǁ__init____mutmut_orig.__name__ = 'xǁEvidenceSchemaValidatorǁ__init__'

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_orig(self) -> None:
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

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_1(self) -> None:
        """Load all schema definitions."""
        schema_files = None

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_2(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "XX1.0XX": "archive_evidence_schema_v1.json",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_3(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "XXarchive_evidence_schema_v1.jsonXX",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_4(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "ARCHIVE_EVIDENCE_SCHEMA_V1.JSON",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_5(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "XX2.0XX": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_6(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "XXarchive_evidence_schema_v2.jsonXX",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_7(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "ARCHIVE_EVIDENCE_SCHEMA_V2.JSON",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_8(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = None
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_9(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir * filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_10(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(None) as f:
                    self.schemas[version] = json.load(f)

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_11(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = None

    def xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_12(self) -> None:
        """Load all schema definitions."""
        schema_files = {
            "1.0": "archive_evidence_schema_v1.json",
            "2.0": "archive_evidence_schema_v2.json",
        }

        for version, filename in schema_files.items():
            path = self.schema_dir / filename
            if path.exists():
                with open(path) as f:
                    self.schemas[version] = json.load(None)
    
    xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_1': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_1, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_2': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_2, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_3': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_3, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_4': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_4, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_5': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_5, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_6': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_6, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_7': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_7, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_8': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_8, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_9': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_9, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_10': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_10, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_11': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_11, 
        'xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_12': xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_12
    }
    
    def _load_schemas(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_orig"), object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_schemas.__signature__ = _mutmut_signature(xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_orig)
    xǁEvidenceSchemaValidatorǁ_load_schemas__mutmut_orig.__name__ = 'xǁEvidenceSchemaValidatorǁ_load_schemas'

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_orig(self, record: dict[str, Any], version: str = "2.0") -> bool:
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

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_1(self, record: dict[str, Any], version: str = "XX2.0XX") -> bool:
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

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_2(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
        if HAS_JSONSCHEMA:
            # Skip validation if jsonschema not available
            return True

        if version not in self.schemas:
            raise ValueError(f"Unsupported schema version: {version}")

        schema = self.schemas[version]
        jsonschema.validate(instance=record, schema=schema)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_3(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
            return False

        if version not in self.schemas:
            raise ValueError(f"Unsupported schema version: {version}")

        schema = self.schemas[version]
        jsonschema.validate(instance=record, schema=schema)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_4(self, record: dict[str, Any], version: str = "2.0") -> bool:
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

        if version in self.schemas:
            raise ValueError(f"Unsupported schema version: {version}")

        schema = self.schemas[version]
        jsonschema.validate(instance=record, schema=schema)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_5(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
            raise ValueError(None)

        schema = self.schemas[version]
        jsonschema.validate(instance=record, schema=schema)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_6(self, record: dict[str, Any], version: str = "2.0") -> bool:
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

        schema = None
        jsonschema.validate(instance=record, schema=schema)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_7(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
        jsonschema.validate(instance=None, schema=schema)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_8(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
        jsonschema.validate(instance=record, schema=None)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_9(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
        jsonschema.validate(schema=schema)
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_10(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
        jsonschema.validate(instance=record, )
        return True

    def xǁEvidenceSchemaValidatorǁvalidate__mutmut_11(self, record: dict[str, Any], version: str = "2.0") -> bool:
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
        return False
    
    xǁEvidenceSchemaValidatorǁvalidate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEvidenceSchemaValidatorǁvalidate__mutmut_1': xǁEvidenceSchemaValidatorǁvalidate__mutmut_1, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_2': xǁEvidenceSchemaValidatorǁvalidate__mutmut_2, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_3': xǁEvidenceSchemaValidatorǁvalidate__mutmut_3, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_4': xǁEvidenceSchemaValidatorǁvalidate__mutmut_4, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_5': xǁEvidenceSchemaValidatorǁvalidate__mutmut_5, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_6': xǁEvidenceSchemaValidatorǁvalidate__mutmut_6, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_7': xǁEvidenceSchemaValidatorǁvalidate__mutmut_7, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_8': xǁEvidenceSchemaValidatorǁvalidate__mutmut_8, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_9': xǁEvidenceSchemaValidatorǁvalidate__mutmut_9, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_10': xǁEvidenceSchemaValidatorǁvalidate__mutmut_10, 
        'xǁEvidenceSchemaValidatorǁvalidate__mutmut_11': xǁEvidenceSchemaValidatorǁvalidate__mutmut_11
    }
    
    def validate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁvalidate__mutmut_orig"), object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁvalidate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate.__signature__ = _mutmut_signature(xǁEvidenceSchemaValidatorǁvalidate__mutmut_orig)
    xǁEvidenceSchemaValidatorǁvalidate__mutmut_orig.__name__ = 'xǁEvidenceSchemaValidatorǁvalidate'

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_orig(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_1(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "XXschemaVersionXX" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_2(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaversion" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_3(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "SCHEMAVERSION" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_4(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" not in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_5(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["XXschemaVersionXX"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_6(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaversion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_7(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["SCHEMAVERSION"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_8(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "XXstandardizationMetadataXX" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_9(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "standardizationmetadata" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_10(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "STANDARDIZATIONMETADATA" in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_11(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" not in record:
            return "2.0"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_12(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "XX2.0XX"
        return "1.0"

    def xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_13(self, record: dict[str, Any]) -> str:
        """Auto-detect schema version of a record."""
        if "schemaVersion" in record:
            return record["schemaVersion"]
        if "standardizationMetadata" in record:
            return "2.0"
        return "XX1.0XX"
    
    xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_1': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_1, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_2': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_2, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_3': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_3, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_4': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_4, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_5': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_5, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_6': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_6, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_7': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_7, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_8': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_8, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_9': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_9, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_10': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_10, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_11': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_11, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_12': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_12, 
        'xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_13': xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_13
    }
    
    def auto_detect_version(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_orig"), object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_mutants"), args, kwargs, self)
        return result 
    
    auto_detect_version.__signature__ = _mutmut_signature(xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_orig)
    xǁEvidenceSchemaValidatorǁauto_detect_version__mutmut_orig.__name__ = 'xǁEvidenceSchemaValidatorǁauto_detect_version'

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_orig(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_1(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(None, version="1.0")

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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_2(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version=None)

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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_3(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(version="1.0")

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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_4(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, )

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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_5(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="XX1.0XX")

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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_6(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = None

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_7(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "XXschemaVersionXX": "2.0",
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_8(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "schemaversion": "2.0",
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_9(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "SCHEMAVERSION": "2.0",
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_10(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "schemaVersion": "XX2.0XX",
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_11(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "schemaVersion": "2.0",
            "XXstandardizationMetadataXX": {
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_12(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "schemaVersion": "2.0",
            "standardizationmetadata": {
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_13(self, v1_record: dict[str, Any]) -> dict[str, Any]:
        """
        Migrate v1 record to v2 format.

        Adds schemaVersion and standardizationMetadata fields.
        """
        if HAS_JSONSCHEMA:
            self.validate(v1_record, version="1.0")

        v2_record = {
            **v1_record,
            "schemaVersion": "2.0",
            "STANDARDIZATIONMETADATA": {
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

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_14(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "XXschema_versionXX": "2.0",
                "slsa_level": "L3",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_15(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "SCHEMA_VERSION": "2.0",
                "slsa_level": "L3",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_16(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "schema_version": "XX2.0XX",
                "slsa_level": "L3",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_17(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "XXslsa_levelXX": "L3",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_18(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "SLSA_LEVEL": "L3",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_19(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "slsa_level": "XXL3XX",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_20(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "slsa_level": "l3",
                "signature": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_21(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "XXsignatureXX": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_22(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "SIGNATURE": None,
                "issuer": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_23(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "XXissuerXX": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_24(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "ISSUER": None,
                "signed_at": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_25(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "XXsigned_atXX": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_26(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
                "SIGNED_AT": None,
            },
        }

        if HAS_JSONSCHEMA:
            self.validate(v2_record, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_27(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
            self.validate(None, version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_28(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
            self.validate(v2_record, version=None)
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_29(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
            self.validate(version="2.0")
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_30(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
            self.validate(v2_record, )
        return v2_record

    def xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_31(self, v1_record: dict[str, Any]) -> dict[str, Any]:
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
            self.validate(v2_record, version="XX2.0XX")
        return v2_record
    
    xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_1': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_1, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_2': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_2, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_3': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_3, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_4': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_4, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_5': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_5, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_6': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_6, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_7': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_7, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_8': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_8, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_9': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_9, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_10': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_10, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_11': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_11, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_12': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_12, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_13': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_13, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_14': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_14, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_15': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_15, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_16': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_16, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_17': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_17, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_18': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_18, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_19': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_19, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_20': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_20, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_21': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_21, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_22': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_22, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_23': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_23, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_24': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_24, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_25': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_25, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_26': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_26, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_27': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_27, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_28': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_28, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_29': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_29, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_30': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_30, 
        'xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_31': xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_31
    }
    
    def migrate_to_v2(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_orig"), object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_mutants"), args, kwargs, self)
        return result 
    
    migrate_to_v2.__signature__ = _mutmut_signature(xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_orig)
    xǁEvidenceSchemaValidatorǁmigrate_to_v2__mutmut_orig.__name__ = 'xǁEvidenceSchemaValidatorǁmigrate_to_v2'

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_orig(
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

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_1(
        self,
        record: dict[str, Any],
        from_version: Optional[str] = None,
        to_version: str = "XX2.0XX",
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

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_2(
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
        if from_version is not None:
            from_version = self.auto_detect_version(record)

        if from_version == "1.0" and to_version == "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_3(
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
            from_version = None

        if from_version == "1.0" and to_version == "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_4(
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
            from_version = self.auto_detect_version(None)

        if from_version == "1.0" and to_version == "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_5(
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

        if from_version == "1.0" or to_version == "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_6(
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

        if from_version != "1.0" and to_version == "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_7(
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

        if from_version == "XX1.0XX" and to_version == "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_8(
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

        if from_version == "1.0" and to_version != "2.0":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_9(
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

        if from_version == "1.0" and to_version == "XX2.0XX":
            return self.migrate_to_v2(record)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_10(
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
            return self.migrate_to_v2(None)

        if from_version == to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_11(
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

        if from_version != to_version:
            return record

        raise ValueError(f"Migration from {from_version} to {to_version} not supported")

    def xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_12(
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

        raise ValueError(None)
    
    xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_1': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_1, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_2': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_2, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_3': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_3, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_4': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_4, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_5': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_5, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_6': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_6, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_7': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_7, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_8': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_8, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_9': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_9, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_10': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_10, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_11': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_11, 
        'xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_12': xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_12
    }
    
    def migrate_record(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_orig"), object.__getattribute__(self, "xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_mutants"), args, kwargs, self)
        return result 
    
    migrate_record.__signature__ = _mutmut_signature(xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_orig)
    xǁEvidenceSchemaValidatorǁmigrate_record__mutmut_orig.__name__ = 'xǁEvidenceSchemaValidatorǁmigrate_record'
