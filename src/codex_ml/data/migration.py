"""Data migration utilities for assignment mappings."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any


class AssignmentMappingMigration:
    """Migrate legacy assignment mapping files to new format."""

    @staticmethod
    def migrate_v1_to_v2(v1_path: Path) -> dict[str, Any]:
        """Migrate v1 assignment mappings to v2 format.

        Args:
            v1_path: Path to v1 assignment mapping file

        Returns:
            dict containing v2 format assignment mappings
        """
        with open(v1_path, encoding="utf-8") as f:
            v1_data = json.load(f)

        # Transform v1 structure to v2
        v2_data: dict[str, Any] = {"version": "2.0", "mappings": []}

        for item in v1_data.get("assignments", []):
            v2_data["mappings"].append(
                {
                    "id": item["id"],
                    "name": item.get("name", ""),
                    "type": item.get("type", "default"),
                    # Add new v2 fields
                    "created_at": item.get("timestamp", ""),
                    "metadata": item.get("extra", {}),
                }
            )

        return v2_data

    @staticmethod
    def migrate_v2_to_v3(v2_path: Path) -> dict[str, Any]:
        """Migrate v2 assignment mappings to v3 format.

        Args:
            v2_path: Path to v2 assignment mapping file

        Returns:
            dict containing v3 format assignment mappings
        """
        with open(v2_path, encoding="utf-8") as f:
            v2_data = json.load(f)

        # Transform v2 structure to v3
        v3_data: dict[str, Any] = {
            "version": "3.0",
            "schema": "assignment_mapping_v3",
            "items": [],
        }

        for mapping in v2_data.get("mappings", []):
            v3_data["items"].append(
                {
                    "uuid": mapping["id"],
                    "label": mapping.get("name", ""),
                    "category": mapping.get("type", "general"),
                    "timestamp": mapping.get("created_at", ""),
                    "attributes": mapping.get("metadata", {}),
                }
            )

        return v3_data


def load_assignment_mappings(path: Path, auto_migrate: bool = True) -> dict[str, Any]:
    """Load assignment mappings with automatic migration support.

    Args:
        path: Path to assignment mapping file
        auto_migrate: If True, automatically migrate old formats

    Returns:
        Assignment mappings in current format (v3)

    Raises:
        ValueError: If version is unknown
        FileNotFoundError: If file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Assignment mapping file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    version = data.get("version", "1.0")

    if version == "1.0":
        warnings.warn(
            f"Loading v1 assignment mappings. Please migrate to v3. "
            f"Use: python -m codex_ml.data.migration migrate --input {path}",
            DeprecationWarning,
            stacklevel=2,
        )
        if auto_migrate:
            # Create temporary v2 file
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as tf:
                v2_data = AssignmentMappingMigration.migrate_v1_to_v2(path)
                json.dump(v2_data, tf)
                v2_path = Path(tf.name)

            try:
                return AssignmentMappingMigration.migrate_v2_to_v3(v2_path)
            finally:
                v2_path.unlink()
        return data

    if version == "2.0":
        warnings.warn(
            "Loading v2 assignment mappings. Consider migrating to v3.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        if auto_migrate:
            # Create temporary file for migration
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as tf:
                json.dump(data, tf)
                temp_path = Path(tf.name)

            try:
                return AssignmentMappingMigration.migrate_v2_to_v3(temp_path)
            finally:
                temp_path.unlink()
        return data

    if version == "3.0":
        return data

    raise ValueError(f"Unknown assignment mapping version: {version}")
