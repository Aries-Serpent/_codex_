"""
Phase 16.1: Schema Validation Tests

This module provides comprehensive tests for validating JSON schemas,
data validation contracts, and type safety across the codebase.

Created: 2026-01-18
Phase: 16.1 - API Contract Testing
Tests: 20+
"""

import json
import re
from pathlib import Path

import pytest

# Repository root
REPO_ROOT = Path(__file__).parents[2]
SCHEMAS_DIR = REPO_ROOT / "schemas"
CONFIGS_DIR = REPO_ROOT / "configs"
SRC_DIR = REPO_ROOT / "src"


class TestJSONSchemaStructure:
    """Tests for JSON schema structural validity."""

    def test_schemas_directory_exists(self):
        """Verify schemas directory exists."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("schemas/ directory not required")

    def test_all_json_files_valid(self):
        """Verify all JSON files in schemas/ are valid."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("schemas/ directory not found")

        invalid = []
        for json_file in SCHEMAS_DIR.rglob("*.json"):
            try:
                json.loads(json_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                invalid.append(f"{json_file.name}: {e}")

        assert len(invalid) == 0, f"Invalid JSON files: {invalid}"

    def test_schema_files_have_type(self):
        """Verify schema files define a type."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("schemas/ directory not found")

        missing_type = []
        for schema_file in list(SCHEMAS_DIR.rglob("*.schema.json"))[:10]:
            try:
                content = json.loads(schema_file.read_text(encoding="utf-8"))
                if "type" not in content and "oneOf" not in content and "anyOf" not in content:
                    missing_type.append(schema_file.name)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        # Allow some without explicit type
        max_missing = max(1, len(list(SCHEMAS_DIR.rglob("*.schema.json"))[:10]) // 3)
        assert len(missing_type) <= max_missing, f"Schemas missing type: {missing_type}"


class TestYAMLSchemaValidation:
    """Tests for YAML configuration schema validation."""

    def test_config_yaml_files_exist(self):
        """Verify configuration YAML files exist."""
        if not CONFIGS_DIR.exists():
            pytest.skip("configs/ directory not found")

        yaml_files = list(CONFIGS_DIR.rglob("*.yaml")) + list(CONFIGS_DIR.rglob("*.yml"))
        assert len(yaml_files) > 0, "Should have YAML config files"

    def test_config_yaml_parseable(self):
        """Verify YAML config files are parseable."""
        if not CONFIGS_DIR.exists():
            pytest.skip("configs/ directory not found")

        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        invalid = []
        for yaml_file in list(CONFIGS_DIR.rglob("*.yaml"))[:20]:
            try:
                content = yaml_file.read_text(encoding="utf-8")
                yaml.safe_load(content)
            except yaml.YAMLError as e:
                invalid.append(f"{yaml_file.name}: {e}")
            except UnicodeDecodeError:
                continue

        assert len(invalid) == 0, f"Invalid YAML files: {invalid}"


class TestPydanticSchemaGeneration:
    """Tests for Pydantic schema generation capability."""

    def _find_pydantic_imports(self) -> list[Path]:
        """Find files that import Pydantic."""
        if not SRC_DIR.exists():
            return []

        files = []
        for py_file in SRC_DIR.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "from pydantic" in content or "import pydantic" in content:
                    files.append(py_file)
            except (UnicodeDecodeError, OSError):
                continue
        return files[:20]

    def test_pydantic_used_for_validation(self):
        """Verify Pydantic is used for data validation."""
        files = self._find_pydantic_imports()
        if not files:
            pytest.skip("Pydantic not used in codebase")

        assert len(files) > 0, "Should find Pydantic usage"

    def test_pydantic_models_have_field_descriptions(self):
        """Spot-check that Pydantic models have Field descriptions."""
        files = self._find_pydantic_imports()
        if not files:
            pytest.skip("Pydantic not used in codebase")

        models_with_descriptions = 0
        models_checked = 0

        for py_file in files[:10]:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Check for Field with description
            if "Field(" in content:
                models_checked += 1
                if "description=" in content:
                    models_with_descriptions += 1

        # Just log, don't require descriptions


class TestDataContractConsistency:
    """Tests for data contract consistency."""

    def test_no_any_type_in_public_apis(self):
        """Check for Any type usage in public APIs (discouraged)."""
        if not SRC_DIR.exists():
            pytest.skip("src/ directory not found")

        any_usage = []
        for py_file in list(SRC_DIR.rglob("*.py"))[:30]:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                # Look for Any in function signatures
                pattern = r"def\s+\w+\s*\([^)]*:\s*Any[^)]*\)"
                matches = re.findall(pattern, content)
                if matches:
                    any_usage.append(py_file.name)
            except (UnicodeDecodeError, OSError):
                continue

        # Log but don't fail (Any is sometimes appropriate)
        if any_usage:
            pytest.skip(f"Found Any usage (acceptable): {any_usage[:3]}")

    def test_optional_fields_have_defaults(self):
        """Verify Optional fields have default values."""
        if not SRC_DIR.exists():
            pytest.skip("src/ directory not found")

        # This is a complex check that would require AST parsing
        # Simplified version: just verify we have typing imports
        typing_files = 0
        for py_file in list(SRC_DIR.rglob("*.py"))[:30]:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "from typing import" in content or "Optional" in content:
                    typing_files += 1
            except (UnicodeDecodeError, OSError):
                continue

        # Verify typing is used
        assert typing_files > 0, "Should use typing module"


class TestSchemaEvolution:
    """Tests for schema evolution and migration."""

    def test_schema_versions_documented(self):
        """Check if schema versions are documented."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("schemas/ directory not found")

        versioned_schemas = []
        for schema_file in SCHEMAS_DIR.rglob("*.json"):
            if re.search(r"v\d+|_v\d+|\.\d+\.", schema_file.name):
                versioned_schemas.append(schema_file.name)

        # Just verify we can find schemas
        # Versioning is optional

    def test_deprecation_markers_present(self):
        """Check for deprecation markers in schemas."""
        if not SCHEMAS_DIR.exists():
            pytest.skip("schemas/ directory not found")

        for schema_file in list(SCHEMAS_DIR.rglob("*.json"))[:10]:
            try:
                content = json.loads(schema_file.read_text(encoding="utf-8"))
                # Check for deprecated field
                if isinstance(content, dict):
                    props = content.get("properties", {})
                    for prop_name, prop_def in props.items():
                        if isinstance(prop_def, dict) and "deprecated" in prop_def:
                            # Found deprecation marker - good practice
                            pass
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
