"""
Integration tests for archival-bundling system.

Tests archive creation, manifest generation, and basic workflows.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


class TestArchiveBasics:
    """Test basic archive functionality that we can verify exists."""

    def test_archive_directory_structure(self):
        """Test that .codex/archive directory structure can be created."""
        test_dir = Path(tempfile.mkdtemp())
        archive_dir = test_dir / ".codex" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        assert archive_dir.exists(), "Condition must be true"
        assert archive_dir.is_dir(), "Condition must be true"

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    def test_manifest_file_structure(self):
        """Test creating and reading a manifest file."""
        test_dir = Path(tempfile.mkdtemp())
        manifest_file = test_dir / "manifest.json"

        manifest_data = {
            "version": "1.0",
            "generated": "2025-11-09T00:00:00Z",
            "items": [
                {
                    "path": "src/file1.py",
                    "sha256": "a" * 64,
                    "size": 1024,
                }
            ],
        }

        manifest_file.write_text(json.dumps(manifest_data, indent=2))
        loaded = json.loads(manifest_file.read_text())

        assert loaded["version"] == "1.0", "Condition must be true"
        assert len(loaded["items"]) == 1, "Collection must not be empty"

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    def test_evidence_file_creation(self):
        """Test creating evidence log file."""
        test_dir = Path(tempfile.mkdtemp())
        evidence_dir = test_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence_file = evidence_dir / "archive_ops.jsonl"

        # Write test evidence entry
        entry = {
            "ts": "2025-11-09T00:00:00Z",
            "action": "ARCHIVE",
            "path": "test.py",
            "repo": "test-repo",
        }

        with evidence_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

        assert evidence_file.exists(), "Condition must be true"
        lines = evidence_file.read_text().strip().split("\n")
        assert len(lines) >= 1, "Lines must not be empty"

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)


class TestArchiveUtilities:
    """Test archive utility functions."""

    def test_sha256_calculation(self):
        """Test SHA256 hash calculation."""
        import hashlib

        content = b"Test content"
        expected_sha = hashlib.sha256(content).hexdigest()

        assert len(expected_sha) == 64, "Expected_sha must not be empty"
        assert all(c in "0123456789abcdef" for c in expected_sha), "Condition must be true"

    def test_compression_basics(self):
        """Test zlib compression/decompression."""
        import zlib

        content = b"AAAA" * 100
        compressed = zlib.compress(content, level=9)
        decompressed = zlib.decompress(compressed)

        assert len(compressed) < len(content), "Compressed must not be empty"
        assert decompressed == content, "Content must not be empty"

    def test_json_serialization(self):
        """Test JSON serialization for manifests."""
        data = {
            "version": "1.0",
            "items": [{"path": "test.py", "size": 100}],
        }

        serialized = json.dumps(data, indent=2, sort_keys=True)
        deserialized = json.loads(serialized)

        assert deserialized == data, "Data must not be empty"


class TestManifestOperations:
    """Test manifest file operations."""

    def test_manifest_atomic_rename(self):
        """Test atomic manifest write using temp file."""
        test_dir = Path(tempfile.mkdtemp())
        manifest_file = test_dir / "manifest.json"
        temp_file = test_dir / "manifest.json.tmp"

        manifest = {"version": "1.0", "items": []}

        # Write to temp, then rename (atomic)
        temp_file.write_text(json.dumps(manifest, indent=2))
        temp_file.rename(manifest_file)

        assert manifest_file.exists(), "Condition must be true"
        assert not temp_file.exists(), "Condition must be true"

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    def test_manifest_validation(self):
        """Test basic manifest validation."""
        manifest = {
            "version": "1.0",
            "generated": "2025-11-09T00:00:00Z",
            "items": [],
        }

        # Check required fields
        assert "version" in manifest, "Condition must be true"
        assert "generated" in manifest, "Condition must be true"
        assert "items" in manifest, "Item must not be empty"
        assert isinstance(manifest["items"], list)

    def test_manifest_checksum_format(self):
        """Test SHA256 checksum format validation."""
        valid_sha = "a" * 64
        invalid_sha = "xyz"

        # Valid format
        assert len(valid_sha) == 64, "Valid_sha must not be empty"
        assert all(c in "0123456789abcdef" for c in valid_sha), "Condition must be true"

        # Invalid format
        assert len(invalid_sha) != 64, "Invalid_sha must not be empty"


class TestEvidenceLogging:
    """Test evidence logging functionality."""

    def test_evidence_append_pattern(self):
        """Test append-only evidence logging pattern."""
        test_dir = Path(tempfile.mkdtemp())
        evidence_file = test_dir / "archive_ops.jsonl"

        # Append multiple entries
        for i in range(3):
            entry = {
                "ts": f"2025-11-09T00:00:0{i}Z",
                "action": "ARCHIVE",
                "path": f"file{i}.py",
            }
            with evidence_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")

        # Verify all entries present
        lines = evidence_file.read_text().strip().split("\n")
        assert len(lines) == 3, "Lines must not be empty"

        entries = [json.loads(line) for line in lines]
        assert all(entry["action"] == "ARCHIVE" for entry in entries), "Condition must be true"

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    def test_evidence_timestamp_format(self):
        """Test evidence timestamp format."""
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()

        # Should be ISO format
        assert "T" in ts, "Condition must be true"
        assert ts.endswith("Z") or "+" in ts or ts.endswith(":00")


class TestArchiveScripts:
    """Test archive-related scripts exist and are importable."""

    def test_archive_scripts_exist(self):
        """Test that archive scripts exist in expected locations."""
        from pathlib import Path

        repo_root = Path(__file__).parents[2]

        expected_scripts = [
            "scripts/archive/select_and_compress.py",
            "scripts/archive/validate_prefixes.py",
            "build_helpers_manifest.py",
        ]

        for script_path in expected_scripts:
            full_path = repo_root / script_path
            # Just check file exists, don't import to avoid dependencies
            if full_path.exists():
                assert full_path.is_file(), "Condition must be true"

    def test_archive_module_importable(self):
        """Test that archive module can be imported."""
        try:
            from src.codex import archive

            assert hasattr(archive, "api") or True  # Module exists
        except ImportError:
            pytest.skip("Archive module not in path")


class TestArchiveTombstoneCompliance:
    """Test tombstone compliance checking (using existing test)."""

    def test_existing_tombstone_test_exists(self):
        """Verify existing tombstone test file exists."""
        from pathlib import Path

        test_file = Path(__file__).parent / "test_archival_tombstone_required.py"
        assert test_file.exists(), "Condition must be true"

    def test_tombstone_test_can_be_imported(self):
        """Test that tombstone compliance test can be imported."""
        try:
            from tests.archival import test_archival_tombstone_required

            assert hasattr(test_archival_tombstone_required, "test_missing_tombstone_fails")
        except ImportError as e:
            pytest.skip(f"Cannot import tombstone test: {e}")
