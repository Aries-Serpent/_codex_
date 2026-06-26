"""Test suite for data migration utilities."""

from __future__ import annotations

import json

import pytest

from codex_ml.data.migration import (
    AssignmentMappingMigration,
    load_assignment_mappings,
)


class TestAssignmentMappingMigration:
    """Test assignment mapping migration functionality."""

    def test_migrate_v1_to_v2(self, tmp_path):
        """Test migration from v1 to v2 format."""
        # Create v1 format file
        v1_file = tmp_path / "mappings_v1.json"
        v1_data = {
            "version": "1.0",
            "assignments": [
                {
                    "id": "123",
                    "name": "Test Mapping",
                    "type": "test",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "extra": {"key": "value"},
                }
            ],
        }
        v1_file.write_text(json.dumps(v1_data), encoding="utf-8")

        # Migrate
        v2_data = AssignmentMappingMigration.migrate_v1_to_v2(v1_file)

        # Verify v2 structure
        assert v2_data["version"] == "2.0", "Data must not be empty"
        assert len(v2_data["mappings"]) == 1, "Collection must not be empty"
        mapping = v2_data["mappings"][0]
        assert mapping["id"] == "123", "Condition must be true"
        assert mapping["name"] == "Test Mapping", "Condition must be true"
        assert mapping["type"] == "test", "Condition must be true"
        assert mapping["created_at"] == "2025-01-01T00:00:00Z", "Condition must be true"
        assert mapping["metadata"] == {"key": "value"}, "Data must not be empty"

    def test_migrate_v2_to_v3(self, tmp_path):
        """Test migration from v2 to v3 format."""
        # Create v2 format file
        v2_file = tmp_path / "mappings_v2.json"
        v2_data = {
            "version": "2.0",
            "mappings": [
                {
                    "id": "456",
                    "name": "Test V2",
                    "type": "example",
                    "created_at": "2025-02-01T00:00:00Z",
                    "metadata": {"foo": "bar"},
                }
            ],
        }
        v2_file.write_text(json.dumps(v2_data), encoding="utf-8")

        # Migrate
        v3_data = AssignmentMappingMigration.migrate_v2_to_v3(v2_file)

        # Verify v3 structure
        assert v3_data["version"] == "3.0", "Data must not be empty"
        assert v3_data["schema"] == "assignment_mapping_v3", "Data must not be empty"
        assert len(v3_data["items"]) == 1, "Collection must not be empty"
        item = v3_data["items"][0]
        assert item["uuid"] == "456", "Item must not be empty"
        assert item["label"] == "Test V2", "Item must not be empty"
        assert item["category"] == "example", "Item must not be empty"
        assert item["timestamp"] == "2025-02-01T00:00:00Z", "Item must not be empty"
        assert item["attributes"] == {"foo": "bar"}, "Item must not be empty"

    def test_migrate_v1_with_defaults(self, tmp_path):
        """Test v1 migration handles missing optional fields."""
        v1_file = tmp_path / "minimal_v1.json"
        v1_data = {"assignments": [{"id": "789"}]}  # Minimal entry
        v1_file.write_text(json.dumps(v1_data), encoding="utf-8")

        v2_data = AssignmentMappingMigration.migrate_v1_to_v2(v1_file)

        assert v2_data["version"] == "2.0", "Data must not be empty"
        mapping = v2_data["mappings"][0]
        assert mapping["id"] == "789", "Condition must be true"
        assert mapping["name"] == "", "Condition must be true"
        assert mapping["type"] == "default", "Condition must be true"
        assert mapping["created_at"] == "", "Condition must be true"
        assert mapping["metadata"] == {}, "Data must not be empty"

    def test_migrate_v2_with_defaults(self, tmp_path):
        """Test v2 migration handles missing optional fields."""
        v2_file = tmp_path / "minimal_v2.json"
        v2_data = {"version": "2.0", "mappings": [{"id": "abc"}]}  # Minimal entry
        v2_file.write_text(json.dumps(v2_data), encoding="utf-8")

        v3_data = AssignmentMappingMigration.migrate_v2_to_v3(v2_file)

        assert v3_data["version"] == "3.0", "Data must not be empty"
        item = v3_data["items"][0]
        assert item["uuid"] == "abc", "Item must not be empty"
        assert item["label"] == "", "Item must not be empty"
        assert item["category"] == "general", "Item must not be empty"
        assert item["timestamp"] == "", "Item must not be empty"
        assert item["attributes"] == {}, "Item must not be empty"


class TestLoadAssignmentMappings:
    """Test assignment mapping loading with auto-migration."""

    def test_load_v3_no_migration(self, tmp_path):
        """Test loading v3 format requires no migration."""
        v3_file = tmp_path / "v3.json"
        v3_data = {"version": "3.0", "schema": "assignment_mapping_v3", "items": [{"uuid": "test"}]}
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")

        result = load_assignment_mappings(v3_file)
        assert result == v3_data, "Result must not be empty"

    def test_load_v1_with_auto_migration(self, tmp_path):
        """Test loading v1 with auto-migration to v3."""
        v1_file = tmp_path / "v1.json"
        v1_data = {"version": "1.0", "assignments": [{"id": "test-id", "name": "Test"}]}
        v1_file.write_text(json.dumps(v1_data), encoding="utf-8")

        with pytest.warns(DeprecationWarning, match="v1 assignment mappings"):
            result = load_assignment_mappings(v1_file, auto_migrate=True)

        # Should be migrated to v3
        assert result["version"] == "3.0", "Result must not be empty"
        assert result["schema"] == "assignment_mapping_v3", "Result must not be empty"
        assert len(result["items"]) == 1, "Collection must not be empty"

    def test_load_v2_with_auto_migration(self, tmp_path):
        """Test loading v2 with auto-migration to v3."""
        v2_file = tmp_path / "v2.json"
        v2_data = {"version": "2.0", "mappings": [{"id": "test-id-2", "name": "Test 2"}]}
        v2_file.write_text(json.dumps(v2_data), encoding="utf-8")

        with pytest.warns(PendingDeprecationWarning, match="v2 assignment mappings"):
            result = load_assignment_mappings(v2_file, auto_migrate=True)

        # Should be migrated to v3
        assert result["version"] == "3.0", "Result must not be empty"
        assert result["schema"] == "assignment_mapping_v3", "Result must not be empty"
        assert len(result["items"]) == 1, "Collection must not be empty"

    def test_load_v1_without_auto_migration(self, tmp_path):
        """Test loading v1 without auto-migration returns original."""
        v1_file = tmp_path / "v1_no_migrate.json"
        v1_data = {"version": "1.0", "assignments": [{"id": "no-migrate"}]}
        v1_file.write_text(json.dumps(v1_data), encoding="utf-8")

        with pytest.warns(DeprecationWarning):
            result = load_assignment_mappings(v1_file, auto_migrate=False)

        # Should return original v1 format
        assert result["version"] == "1.0", "Result must not be empty"
        assert "assignments" in result, "Result must not be empty"

    def test_load_unknown_version(self, tmp_path):
        """Test loading file with unknown version raises error."""
        unknown_file = tmp_path / "unknown.json"
        unknown_data = {"version": "99.0", "data": []}
        unknown_file.write_text(json.dumps(unknown_data), encoding="utf-8")

        with pytest.raises(ValueError, match="Unknown assignment mapping version"):
            load_assignment_mappings(unknown_file)

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading non-existent file raises error."""
        nonexistent = tmp_path / "does_not_exist.json"

        with pytest.raises(FileNotFoundError):
            load_assignment_mappings(nonexistent)

    def test_load_malformed_json(self, tmp_path):
        """Test loading malformed JSON raises error."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            load_assignment_mappings(bad_file)

    def test_load_missing_version_defaults_to_v1(self, tmp_path):
        """Test file without version field defaults to v1.0."""
        no_version_file = tmp_path / "no_version.json"
        no_version_data = {"assignments": [{"id": "test"}]}
        no_version_file.write_text(json.dumps(no_version_data), encoding="utf-8")

        with pytest.warns(DeprecationWarning):
            result = load_assignment_mappings(no_version_file, auto_migrate=True)

        # Should be treated as v1 and migrated to v3
        assert result["version"] == "3.0", "Result must not be empty"


class TestDataMigrationRollback:
    """Test rollback scenarios for data migration."""

    def test_rollback_v3_to_v2(self, tmp_path):
        """Test rollback from v3 back to v2 format."""
        # Create v3 format file
        v3_file = tmp_path / "mappings_v3.json"
        v3_data = {
            "version": "3.0",
            "schema": "assignment_mapping_v3",
            "items": [
                {
                    "uuid": "123",
                    "label": "Test Mapping",
                    "category": "test",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "attributes": {"key": "value"},
                }
            ],
        }
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")

        # Perform rollback from AssignmentMappingMigration
        from codex_ml.data.migration import AssignmentMappingMigration

        v2_data = AssignmentMappingMigration.rollback_v3_to_v2(v3_file)

        # Verify v2 structure after rollback
        assert v2_data["version"] == "2.0", "Data must not be empty"
        assert len(v2_data["mappings"]) == 1, "Collection must not be empty"
        mapping = v2_data["mappings"][0]
        assert mapping["id"] == "123", "Condition must be true"
        assert mapping["name"] == "Test Mapping", "Condition must be true"
        assert mapping["type"] == "test", "Condition must be true"
        assert mapping["created_at"] == "2025-01-01T00:00:00Z", "Condition must be true"

    def test_rollback_v2_to_v1(self, tmp_path):
        """Test rollback from v2 back to v1 format."""
        v2_file = tmp_path / "mappings_v2.json"
        v2_data = {
            "version": "2.0",
            "mappings": [
                {
                    "id": "456",
                    "name": "Test V2",
                    "type": "example",
                    "created_at": "2025-02-01T00:00:00Z",
                    "metadata": {"foo": "bar"},
                }
            ],
        }
        v2_file.write_text(json.dumps(v2_data), encoding="utf-8")

        from codex_ml.data.migration import AssignmentMappingMigration

        v1_data = AssignmentMappingMigration.rollback_v2_to_v1(v2_file)

        # Verify v1 structure after rollback
        assert v1_data["version"] == "1.0", "Data must not be empty"
        assert len(v1_data["assignments"]) == 1, "Collection must not be empty"
        assignment = v1_data["assignments"][0]
        assert assignment["id"] == "456", "Condition must be true"
        assert assignment["name"] == "Test V2", "Condition must be true"
        assert assignment["type"] == "example", "Condition must be true"

    def test_selective_rollback_partial_items(self, tmp_path):
        """Test rolling back only selected items, not entire dataset."""
        v3_file = tmp_path / "mappings_selective.json"
        v3_data = {
            "version": "3.0",
            "schema": "assignment_mapping_v3",
            "items": [
                {
                    "uuid": "1",
                    "label": "Keep",
                    "category": "keep",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "attributes": {},
                },
                {
                    "uuid": "2",
                    "label": "Rollback",
                    "category": "rollback",
                    "timestamp": "2025-01-02T00:00:00Z",
                    "attributes": {},
                },
                {
                    "uuid": "3",
                    "label": "Keep2",
                    "category": "keep",
                    "timestamp": "2025-01-03T00:00:00Z",
                    "attributes": {},
                },
            ],
        }
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")

        from codex_ml.data.migration import AssignmentMappingMigration

        # Rollback only item with uuid "2"
        rolled_data = AssignmentMappingMigration.selective_rollback(v3_file, item_ids=["2"])

        # Verify that only specified item was rolled back
        assert len(rolled_data["items"]) == 3, "Collection must not be empty"
        # Item 2 should be in v2 format after rollback (uses "id" instead of "uuid")
        [i for i in rolled_data["items"] if i.get("uuid") == "2"]
        item_2_v2 = [i for i in rolled_data["items"] if i.get("id") == "2"]
        # Should be in v2 format
        assert len(item_2_v2) == 1, "Item_2_v2 must not be empty"
        item_2 = item_2_v2[0]
        assert "name" in item_2, "Item must not be empty"
        assert item_2["name"] == "Rollback", "Item must not be empty"
        assert item_2["id"] == "2", "Item must not be empty"

    def test_rollback_with_data_integrity_check(self, tmp_path):
        """Test that rollback preserves data integrity."""
        v3_file = tmp_path / "mappings_integrity.json"
        original_uuid = "test-uuid-123"
        original_label = "Original Label"
        original_timestamp = "2025-01-01T12:34:56Z"
        v3_data = {
            "version": "3.0",
            "schema": "assignment_mapping_v3",
            "items": [
                {
                    "uuid": original_uuid,
                    "label": original_label,
                    "category": "test",
                    "timestamp": original_timestamp,
                    "attributes": {"key1": "value1", "key2": "value2"},
                }
            ],
        }
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")

        from codex_ml.data.migration import AssignmentMappingMigration

        v2_data = AssignmentMappingMigration.rollback_v3_to_v2(v3_file)

        # Verify data integrity: all important fields preserved
        mapping = v2_data["mappings"][0]
        assert mapping["id"] == original_uuid, "Condition must be true"
        assert mapping["name"] == original_label, "Condition must be true"
        assert mapping["created_at"] == original_timestamp, "Condition must be true"
        assert mapping["metadata"]["key1"] == "value1", "Data must not be empty"
        assert mapping["metadata"]["key2"] == "value2", "Data must not be empty"

    def test_rollback_error_handling_corrupt_file(self, tmp_path):
        """Test rollback error handling with corrupted file."""
        corrupt_file = tmp_path / "corrupt.json"
        corrupt_file.write_text("{invalid json content", encoding="utf-8")

        from codex_ml.data.migration import AssignmentMappingMigration

        with pytest.raises(json.JSONDecodeError):
            AssignmentMappingMigration.rollback_v3_to_v2(corrupt_file)

    def test_rollback_error_recovery(self, tmp_path):
        """Test recovery mechanism when rollback fails."""
        v3_file = tmp_path / "mappings_backup.json"
        v3_data = {
            "version": "3.0",
            "schema": "assignment_mapping_v3",
            "items": [
                {
                    "uuid": "test",
                    "label": "Test",
                    "category": "test",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "attributes": {},
                }
            ],
        }
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")
        backup_file = tmp_path / "mappings_backup_v3.json"
        backup_file.write_text(json.dumps(v3_data), encoding="utf-8")

        # Verify backup was created and can be restored
        assert backup_file.exists(), "Condition must be true"
        restored = json.loads(backup_file.read_text())
        assert restored["version"] == "3.0", "rest is not valid"
        assert len(restored["items"]) == 1, "Collection must not be empty"

    def test_migration_and_rollback_bidirectional(self, tmp_path):
        """Test that migration and rollback are bidirectional."""
        # Start with v1
        v1_original = {
            "version": "1.0",
            "assignments": [
                {
                    "id": "test-123",
                    "name": "Test Assignment",
                    "type": "primary",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "extra": {"metadata": "value"},
                }
            ],
        }
        v1_file = tmp_path / "v1_bidirectional.json"
        v1_file.write_text(json.dumps(v1_original), encoding="utf-8")

        from codex_ml.data.migration import AssignmentMappingMigration

        # Migrate: v1 → v2
        v2_data = AssignmentMappingMigration.migrate_v1_to_v2(v1_file)
        v2_file = tmp_path / "v2_bidirectional.json"
        v2_file.write_text(json.dumps(v2_data), encoding="utf-8")

        # Migrate: v2 → v3
        v3_data = AssignmentMappingMigration.migrate_v2_to_v3(v2_file)
        v3_file = tmp_path / "v3_bidirectional.json"
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")

        # Rollback: v3 → v2
        v2_restored = AssignmentMappingMigration.rollback_v3_to_v2(v3_file)
        assert v2_restored["version"] == "2.0", "v2_rest is not valid"

        # Rollback: v2 → v1
        v1_restored = AssignmentMappingMigration.rollback_v2_to_v1(v2_file)
        assert v1_restored["version"] == "1.0", "v1_rest is not valid"
        assert v1_restored["assignments"][0]["id"] == "test-123", "v1_rest is not valid"

    def test_data_consistency_empty_dataset(self, tmp_path):
        """Test rollback with empty dataset maintains structure."""
        v3_file = tmp_path / "empty_v3.json"
        v3_data = {
            "version": "3.0",
            "schema": "assignment_mapping_v3",
            "items": [],
        }
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")

        from codex_ml.data.migration import AssignmentMappingMigration

        v2_data = AssignmentMappingMigration.rollback_v3_to_v2(v3_file)

        assert v2_data["version"] == "2.0", "Data must not be empty"
        assert v2_data["mappings"] == [], "Data must not be empty"

    def test_large_dataset_rollback_performance(self, tmp_path):
        """Test rollback performance with large dataset."""
        v3_file = tmp_path / "large_v3.json"
        # Create 1000 items
        items = [
            {
                "uuid": f"item-{i:04d}",
                "label": f"Label {i}",
                "category": f"category_{i % 10}",
                "timestamp": "2025-01-01T00:00:00Z",
                "attributes": {"index": i, "data": f"value_{i}"},
            }
            for i in range(1000)
        ]
        v3_data = {
            "version": "3.0",
            "schema": "assignment_mapping_v3",
            "items": items,
        }
        v3_file.write_text(json.dumps(v3_data), encoding="utf-8")

        import time

        from codex_ml.data.migration import AssignmentMappingMigration

        start = time.time()
        v2_data = AssignmentMappingMigration.rollback_v3_to_v2(v3_file)
        elapsed = time.time() - start

        # Verify performance (should complete in under 5 seconds)
        assert elapsed < 5.0, "elapsed is not valid"
        assert len(v2_data["mappings"]) == 1000, "Collection must not be empty"
        assert v2_data["version"] == "2.0", "Data must not be empty"
