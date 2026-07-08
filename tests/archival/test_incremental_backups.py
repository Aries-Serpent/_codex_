"""
Tests for incremental archival backups.

Tests differential backups, timestamp-based incremental updates,
change detection, and backup chain management.
"""

from __future__ import annotations

import hashlib
import tarfile
import time
from datetime import UTC, datetime, timedelta

import pytest

from .security_utils import safe_extract_tarfile


class TestIncrementalBackups:
    """Test incremental backup functionality"""

    def test_full_backup_creation(self, tmp_path):
        """Test creating initial full backup"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create initial files
        (source_dir / "file1.txt").write_text("initial content 1")
        (source_dir / "file2.txt").write_text("initial content 2")

        # Create full backup
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        full_backup = backup_dir / "full_backup.tar.gz"
        with tarfile.open(full_backup, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        assert full_backup.exists(), "Condition must be true"

        # Record backup metadata
        metadata = {
            "type": "full",
            "timestamp": datetime.now(UTC).isoformat(),
            "file_count": len(list(source_dir.iterdir())),
        }

        assert metadata["type"] == "full", "Data must not be empty"
        assert metadata["file_count"] == 2, "Data must not be empty"

    def test_incremental_backup_changed_files(self, tmp_path):
        """Test incremental backup of only changed files"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Initial files
        file1 = source_dir / "file1.txt"
        file2 = source_dir / "file2.txt"
        file1.write_text("original 1")
        file2.write_text("original 2")

        # Record initial state
        initial_state = {
            "file1.txt": hashlib.sha256(file1.read_bytes()).hexdigest(),
            "file2.txt": hashlib.sha256(file2.read_bytes()).hexdigest(),
        }

        # Modify one file
        time.sleep(0.01)  # Ensure timestamp difference
        file1.write_text("modified 1")

        # Detect changes
        changed_files = []
        for filename, old_checksum in initial_state.items():
            file_path = source_dir / filename
            new_checksum = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if old_checksum != new_checksum:
                changed_files.append(filename)

        assert len(changed_files) == 1, "Changed_files must not be empty"
        assert "file1.txt" in changed_files, "Condition must be true"

    def test_differential_backup_strategy(self, tmp_path):
        """Test differential backup (changes since last full backup)"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Full backup
        (source_dir / "file1.txt").write_text("data 1")
        (source_dir / "file2.txt").write_text("data 2")

        full_backup = backup_dir / "full.tar.gz"
        full_backup_files = set()

        with tarfile.open(full_backup, "w:gz") as tar:
            for file_path in source_dir.iterdir():
                tar.add(file_path, arcname=file_path.name)
                full_backup_files.add(file_path.name)

        # Add new file (differential change)
        (source_dir / "file3.txt").write_text("data 3")

        # Differential backup (only new/changed files)
        diff_backup = backup_dir / "diff.tar.gz"
        with tarfile.open(diff_backup, "w:gz") as tar:
            for file_path in source_dir.iterdir():
                if file_path.name not in full_backup_files:
                    tar.add(file_path, arcname=file_path.name)

        # Verify differential contains only new file
        with tarfile.open(diff_backup, "r:gz") as tar:
            members = tar.getmembers()
            assert len(members) == 1, "Members must not be empty"
            assert members[0].name == "file3.txt", "name is not valid"

    def test_timestamp_based_incremental(self, tmp_path):
        """Test incremental backup based on modification timestamps"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create files
        old_file = source_dir / "old.txt"
        old_file.write_text("old content")

        # Record cutoff time
        cutoff_time = time.time()
        time.sleep(0.1)

        # Create new file after cutoff
        new_file = source_dir / "new.txt"
        new_file.write_text("new content")

        # Find files modified after cutoff
        modified_files = []
        for file_path in source_dir.iterdir():
            if file_path.stat().st_mtime > cutoff_time:
                modified_files.append(file_path.name)

        assert "new.txt" in modified_files, "Condition must be true"
        assert "old.txt" not in modified_files, "Condition must be true"

    def test_backup_chain_metadata(self, tmp_path):
        """Test maintaining backup chain metadata"""
        backup_chain = []

        # Full backup entry
        backup_chain.append(
            {
                "id": "backup_001",
                "type": "full",
                "timestamp": datetime.now(UTC).isoformat(),
                "parent": None,
                "file_count": 10,
            }
        )

        # Incremental backup entries
        backup_chain.append(
            {
                "id": "backup_002",
                "type": "incremental",
                "timestamp": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
                "parent": "backup_001",
                "file_count": 3,
            }
        )

        backup_chain.append(
            {
                "id": "backup_003",
                "type": "incremental",
                "timestamp": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
                "parent": "backup_002",
                "file_count": 2,
            }
        )

        # Verify chain
        assert len(backup_chain) == 3, "Backup_chain must not be empty"
        assert backup_chain[0]["type"] == "full", "Condition must be true"
        assert backup_chain[1]["parent"] == "backup_001", "Condition must be true"
        assert backup_chain[2]["parent"] == "backup_002", "Condition must be true"

    def test_restore_from_backup_chain(self, tmp_path):
        """Test restoring from a chain of incremental backups"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Full backup
        (source_dir / "file1.txt").write_text("v1")
        full_backup = backup_dir / "full.tar.gz"
        with tarfile.open(full_backup, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        # Incremental 1: add file2
        (source_dir / "file2.txt").write_text("v1")
        inc1_backup = backup_dir / "inc1.tar.gz"
        with tarfile.open(inc1_backup, "w:gz") as tar:
            tar.add(source_dir / "file2.txt", arcname="file2.txt")

        # Restore process (full + incremental)
        restore_dir = tmp_path / "restore"
        restore_dir.mkdir()

        # Extract full backup
        safe_extract_tarfile(full_backup, restore_dir)

        # Extract incremental
        safe_extract_tarfile(inc1_backup, restore_dir)

        # Verify both files present
        assert (restore_dir / "file1.txt").exists(), "Condition must be true"
        assert (restore_dir / "file2.txt").exists(), "Condition must be true"


class TestChangeDetection:
    """Test change detection for incremental backups"""

    def test_detect_new_files(self, tmp_path):
        """Test detecting newly added files"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Initial files
        initial_files = {"file1.txt", "file2.txt"}
        for filename in initial_files:
            (source_dir / filename).write_text("content")

        # Add new file
        (source_dir / "file3.txt").write_text("new content")

        # Detect new files
        current_files = {f.name for f in source_dir.iterdir()}
        new_files = current_files - initial_files

        assert new_files == {"file3.txt"}, "new_files is not valid"

    def test_detect_deleted_files(self, tmp_path):
        """Test detecting deleted files"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Initial files
        initial_files = {"file1.txt", "file2.txt", "file3.txt"}
        for filename in initial_files:
            (source_dir / filename).write_text("content")

        # Delete one file
        (source_dir / "file2.txt").unlink()

        # Detect deletions
        current_files = {f.name for f in source_dir.iterdir()}
        deleted_files = initial_files - current_files

        assert deleted_files == {"file2.txt"}, "deleted_files is not valid"

    def test_detect_modified_files_by_checksum(self, tmp_path):
        """Test detecting modified files using checksums"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create files and record checksums
        file1 = source_dir / "file1.txt"
        file2 = source_dir / "file2.txt"
        file1.write_text("original 1")
        file2.write_text("original 2")

        checksums = {
            "file1.txt": hashlib.sha256(file1.read_bytes()).hexdigest(),
            "file2.txt": hashlib.sha256(file2.read_bytes()).hexdigest(),
        }

        # Modify file1
        file1.write_text("modified 1")

        # Detect modifications
        modified_files = []
        for filename, old_checksum in checksums.items():
            file_path = source_dir / filename
            new_checksum = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if old_checksum != new_checksum:
                modified_files.append(filename)

        assert modified_files == ["file1.txt"], "modified_files is not valid"

    def test_detect_modified_files_by_size(self, tmp_path):
        """Test detecting modified files using size"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create files and record sizes
        file1 = source_dir / "file1.txt"
        file2 = source_dir / "file2.txt"
        file1.write_text("short")
        file2.write_text("medium content")

        sizes = {
            "file1.txt": file1.stat().st_size,
            "file2.txt": file2.stat().st_size,
        }

        # Modify file1 (change size)
        file1.write_text("much longer content now")

        # Detect size changes
        size_changed = []
        for filename, old_size in sizes.items():
            file_path = source_dir / filename
            if file_path.stat().st_size != old_size:
                size_changed.append(filename)

        assert size_changed == ["file1.txt"], "size_changed is not valid"

    def test_change_summary_report(self, tmp_path):
        """Test generating change summary for backup"""
        # Simulate change detection
        changes = {
            "added": ["new_file1.txt", "new_file2.txt"],
            "modified": ["existing_file.txt"],
            "deleted": ["old_file.txt"],
        }

        # Create change summary
        summary = {
            "timestamp": datetime.now(UTC).isoformat(),
            "changes": changes,
            "total_changes": sum(len(v) for v in changes.values()),
        }

        assert summary["total_changes"] == 4, "Condition must be true"
        assert len(summary["changes"]["added"]) == 2, "Collection must not be empty"


class TestBackupVerification:
    """Test verification of incremental backups"""

    def test_verify_backup_integrity(self, tmp_path):
        """Test verifying backup integrity using manifest"""
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        # Create backup with manifest
        (backup_dir / "file1.txt").write_text("content 1")
        (backup_dir / "file2.txt").write_text("content 2")

        # Create manifest
        manifest = {"files": []}
        for file_path in backup_dir.glob("*.txt"):
            manifest["files"].append(
                {
                    "path": file_path.name,
                    "sha256": hashlib.sha256(file_path.read_bytes()).hexdigest(),
                    "size": file_path.stat().st_size,
                }
            )

        # Verify all files against manifest
        all_valid = True
        for file_entry in manifest["files"]:
            file_path = backup_dir / file_entry["path"]
            actual_checksum = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if actual_checksum != file_entry["sha256"]:
                all_valid = False

        assert all_valid is True, "all_valid is not valid"

    def test_backup_restoration_test(self, tmp_path):
        """Test performing restoration test of backup"""
        # Create backup
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.txt").write_text("test data")

        backup_path = tmp_path / "backup.tar.gz"
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        # Test restoration
        restore_dir = tmp_path / "restore_test"
        restore_dir.mkdir()
        safe_extract_tarfile(backup_path, restore_dir)

        # Verify restoration
        restored_file = restore_dir / "test.txt"
        assert restored_file.exists(), "rest is not valid"
        assert restored_file.read_text() == "test data", "Data must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
