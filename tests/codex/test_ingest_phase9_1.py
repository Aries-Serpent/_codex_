"""
Phase 9.1 - Comprehensive tests for codex.ingest.adapter module.

Tests cover:
- Snapshot creation from various sources
- File validation and security checks
- Archive extraction (ZIP/TAR)
- Git repository cloning
- Content hashing and provenance
- Size bounds enforcement
- Path traversal prevention
"""

from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codex.ingest.adapter import (
    MAX_FILE_SIZE_MB,
    MAX_FILES_COUNT,
    MAX_TOTAL_SIZE_MB,
    Snapshot,
    _check_size_bounds,
    _compute_content_hash,
    _extract_zip,
    _validate_path,
    ingest,
)


class TestSnapshot:
    """Test Snapshot dataclass functionality."""

    def test_snapshot_creation(self, tmp_path: Path) -> None:
        """Test basic snapshot creation."""
        from datetime import datetime, timezone

        snapshot = Snapshot(
            snapshot_id="20251217-abc123",
            source_path=os.path.join(tempfile.gettempdir(), "source"),
            snapshot_dir=tmp_path / "snap",
            content_hash="deadbeef",
            created_at=datetime.now(timezone.utc),
        )

        assert snapshot.snapshot_id == "20251217-abc123", "snapshot_id is not valid"
        assert snapshot.source_path == os.path.join(tempfile.gettempdir(), "source"), "source_path is not valid"
        assert snapshot.content_hash == "deadbeef", "Content must not be empty"

    def test_get_source_dir(self, tmp_path: Path) -> None:
        """Test get_source_dir returns correct path."""
        from datetime import datetime, timezone

        snapshot = Snapshot(
            snapshot_id="test",
            source_path=os.path.join(tempfile.gettempdir(), "test"),
            snapshot_dir=tmp_path,
            content_hash="hash",
            created_at=datetime.now(timezone.utc),
        )

        assert snapshot.get_source_dir() == tmp_path / "source", "Condition must be true"

    def test_get_artifact_path(self, tmp_path: Path) -> None:
        """Test get_artifact_path returns correct path."""
        from datetime import datetime, timezone

        snapshot = Snapshot(
            snapshot_id="test",
            source_path=os.path.join(tempfile.gettempdir(), "test"),
            snapshot_dir=tmp_path,
            content_hash="hash",
            created_at=datetime.now(timezone.utc),
        )

        artifact = snapshot.get_artifact_path("test.txt")
        assert artifact == tmp_path / "test.txt", "artifact is not valid"

    def test_to_dict(self, tmp_path: Path) -> None:
        """Test serialization to dictionary."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        snapshot = Snapshot(
            snapshot_id="test",
            source_path=os.path.join(tempfile.gettempdir(), "test"),
            snapshot_dir=tmp_path,
            content_hash="hash123",
            created_at=now,
            metadata={"key": "value"},
        )

        data = snapshot.to_dict()
        assert data["snapshot_id"] == "test", "Data must not be empty"
        assert data["source_path"] == os.path.join(tempfile.gettempdir(), "test"), "Data must not be empty"
        assert data["content_hash"] == "hash123", "Data must not be empty"
        assert data["metadata"] == {"key": "value"}, "Data must not be empty"
        assert data["created_at"] == now.isoformat(), "Data must not be empty"


class TestContentHashing:
    """Test content hashing functionality."""

    def test_hash_single_file(self, tmp_path: Path) -> None:
        """Test hashing a single file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        hash1 = _compute_content_hash(test_file)
        hash2 = _compute_content_hash(test_file)

        assert hash1 == hash2, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_hash_directory_deterministic(self, tmp_path: Path) -> None:
        """Test directory hashing is deterministic."""
        (tmp_path / "a.py").write_text("content_a")
        (tmp_path / "b.py").write_text("content_b")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "c.py").write_text("content_c")

        hash1 = _compute_content_hash(tmp_path)
        hash2 = _compute_content_hash(tmp_path)

        assert hash1 == hash2, "hash1 is not valid"

    def test_hash_empty_directory(self, tmp_path: Path) -> None:
        """Test hashing an empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        hash_val = _compute_content_hash(empty_dir)
        assert len(hash_val) == 64, "Hash_val must not be empty"


class TestPathValidation:
    """Test path validation and security checks."""

    def test_validate_simple_path(self, tmp_path: Path) -> None:
        """Test validation of simple path."""
        test_path = tmp_path / "test.txt"
        test_path.touch()

        _validate_path(test_path)  # Should not raise

    def test_validate_path_traversal_attack(self, tmp_path: Path) -> None:
        """Test path traversal detection."""
        base = tmp_path / "base"
        base.mkdir()

        # Try to escape via ../..
        malicious = base / ".." / ".." / "etc" / "passwd"

        with pytest.raises(ValueError, match="Path traversal"):
            _validate_path(malicious, base)

    def test_validate_path_with_base_dir(self, tmp_path: Path) -> None:
        """Test path validation with base directory containment."""
        base = tmp_path / "base"
        base.mkdir()
        safe_path = base / "safe.txt"
        safe_path.touch()

        _validate_path(safe_path, base)  # Should not raise

    def test_validate_nonexistent_path(self, tmp_path: Path) -> None:
        """Test validation of nonexistent path."""
        nonexistent = tmp_path / "does_not_exist"

        # Nonexistent paths can be validated (they just don't exist yet)
        # This should not raise unless there's a security issue
        try:
            _validate_path(nonexistent)
        except ValueError:
            _ = None  # May raise, depending on implementation


class TestSizeBounds:
    """Test size bounds checking."""

    def test_check_small_file(self, tmp_path: Path) -> None:
        """Test size check for small file passes."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("small content")

        _check_size_bounds(test_file)  # Should not raise

    def test_check_file_too_large(self, tmp_path: Path) -> None:
        """Test file size limit enforcement."""
        large_file = tmp_path / "large.txt"
        # Create file larger than MAX_FILE_SIZE_MB
        size_bytes = (MAX_FILE_SIZE_MB + 1) * 1024 * 1024
        large_file.write_bytes(b"x" * int(size_bytes))

        with pytest.raises(ValueError, match="File size .* exceeds limit"):
            _check_size_bounds(large_file)

    def test_check_directory_size(self, tmp_path: Path) -> None:
        """Test directory size check passes for small directory."""
        for i in range(5):
            (tmp_path / f"file{i}.txt").write_text(f"content {i}")

        _check_size_bounds(tmp_path)  # Should not raise

    def test_check_directory_too_large(self, tmp_path: Path) -> None:
        """Test directory total size limit enforcement."""
        # Create directory exceeding MAX_TOTAL_SIZE_MB
        size_per_file = (MAX_TOTAL_SIZE_MB + 10) * 1024 * 1024
        (tmp_path / "huge.bin").write_bytes(b"x" * int(size_per_file))

        with pytest.raises(ValueError, match="Total size .* exceeds limit"):
            _check_size_bounds(tmp_path)

    def test_check_too_many_files(self, tmp_path: Path) -> None:
        """Test file count limit enforcement."""
        # This test would be slow, so we'll mock the count
        with patch.object(Path, "rglob") as mock_rglob:
            mock_files = [MagicMock(is_file=lambda: True) for _ in range(MAX_FILES_COUNT + 1)]
            mock_rglob.return_value = mock_files

            with pytest.raises(ValueError, match="File count .* exceeds limit"):
                _check_size_bounds(tmp_path)


class TestZipExtraction:
    """Test ZIP archive extraction."""

    def test_extract_simple_zip(self, tmp_path: Path) -> None:
        """Test extraction of simple ZIP archive."""
        # Create a test ZIP
        zip_path = tmp_path / "test.zip"
        dest_dir = tmp_path / "extracted"
        dest_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("subdir/file2.txt", "content2")

        _extract_zip(zip_path, dest_dir)

        assert (dest_dir / "file1.txt").exists(), "Condition must be true"
        assert (dest_dir / "subdir" / "file2.txt").exists(), "Condition must be true"
        assert (dest_dir / "file1.txt").read_text() == "content1", "Content must not be empty"

    def test_extract_zip_creates_directories(self, tmp_path: Path) -> None:
        """Test ZIP extraction creates necessary directories."""
        zip_path = tmp_path / "test.zip"
        dest_dir = tmp_path / "extracted"
        dest_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("a/b/c/file.txt", "nested content")

        _extract_zip(zip_path, dest_dir)

        assert (dest_dir / "a" / "b" / "c" / "file.txt").exists(), "Condition must be true"

    def test_extract_zip_path_traversal_protection(self, tmp_path: Path) -> None:
        """Test ZIP extraction prevents path traversal."""
        zip_path = tmp_path / "malicious.zip"
        dest_dir = tmp_path / "extracted"
        dest_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            # Try to write outside dest_dir
            zf.writestr("../../etc/passwd", "malicious")

        with pytest.raises(ValueError):
            _extract_zip(zip_path, dest_dir)


class TestIngestSingleFile:
    """Test ingestion of single files."""

    def test_ingest_python_file(self, tmp_path: Path) -> None:
        """Test ingesting a single Python file."""
        source_file = tmp_path / "test.py"
        source_file.write_text("print('test')")

        artifacts_dir = tmp_path / "artifacts"
        snapshot = ingest(source_file, artifacts_dir=artifacts_dir)

        assert snapshot.snapshot_id.startswith(snapshot.created_at.strftime("%Y%m%d")), "Condition must be true"
        assert snapshot.source_path == str(source_file), "source_path is not valid"
        assert snapshot.content_hash, "Content must not be empty"
        assert snapshot.snapshot_dir.exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "source" / "test.py").exists(), "Condition must be true"

    def test_ingest_with_custom_snapshot_id(self, tmp_path: Path) -> None:
        """Test ingestion with custom snapshot ID."""
        source_file = tmp_path / "test.py"
        source_file.write_text("content")

        artifacts_dir = tmp_path / "artifacts"
        snapshot = ingest(
            source_file,
            snapshot_id="custom-id-123",
            artifacts_dir=artifacts_dir,
        )

        assert snapshot.snapshot_id == "custom-id-123", "snapshot_id is not valid"
        assert (artifacts_dir / "custom-id-123").exists(), "Condition must be true"

    def test_ingest_creates_metadata(self, tmp_path: Path) -> None:
        """Test that ingestion creates snapshot metadata."""
        source_file = tmp_path / "test.py"
        source_file.write_text("# test file")

        artifacts_dir = tmp_path / "artifacts"
        snapshot = ingest(source_file, artifacts_dir=artifacts_dir)

        meta_file = snapshot.snapshot_dir / "snapshot-meta.json"
        assert meta_file.exists(), "Condition must be true"

        with meta_file.open() as f:
            meta = json.load(f)

        assert meta["snapshot_id"] == snapshot.snapshot_id, "Condition must be true"
        assert meta["content_hash"] == snapshot.content_hash, "Content must not be empty"
        assert "created_at" in meta, "Condition must be true"
        assert meta["file_count"] == 1, "Count must be greater than zero"


class TestIngestDirectory:
    """Test ingestion of directories."""

    def test_ingest_directory(self, tmp_path: Path) -> None:
        """Test ingesting a directory."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.py").write_text("content1")
        (source_dir / "file2.py").write_text("content2")
        (source_dir / "subdir").mkdir()
        (source_dir / "subdir" / "file3.py").write_text("content3")

        artifacts_dir = tmp_path / "artifacts"
        snapshot = ingest(source_dir, artifacts_dir=artifacts_dir)

        snap_source = snapshot.snapshot_dir / "source"
        assert (snap_source / "file1.py").exists(), "Condition must be true"
        assert (snap_source / "file2.py").exists(), "Condition must be true"
        assert (snap_source / "subdir" / "file3.py").exists(), "Condition must be true"

    def test_ingest_directory_creates_artifact_dirs(self, tmp_path: Path) -> None:
        """Test ingestion creates artifact directories."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("content")

        artifacts_dir = tmp_path / "artifacts"
        snapshot = ingest(source_dir, artifacts_dir=artifacts_dir)

        assert (snapshot.snapshot_dir / "patches").exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "tests" / "codex_generated").exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "llm_provenance").exists(), "Condition must be true"


class TestIngestZipArchive:
    """Test ingestion of ZIP archives."""

    def test_ingest_zip_archive(self, tmp_path: Path) -> None:
        """Test ingesting a ZIP archive."""
        # Create ZIP
        zip_path = tmp_path / "archive.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.py", "content1")
            zf.writestr("dir/file2.py", "content2")

        artifacts_dir = tmp_path / "artifacts"
        snapshot = ingest(zip_path, artifacts_dir=artifacts_dir)

        snap_source = snapshot.snapshot_dir / "source"
        assert (snap_source / "file1.py").exists(), "Condition must be true"
        assert (snap_source / "dir" / "file2.py").exists(), "Condition must be true"


class TestIngestErrors:
    """Test error handling in ingestion."""

    def test_ingest_nonexistent_source(self, tmp_path: Path) -> None:
        """Test ingestion fails for nonexistent source."""
        nonexistent = tmp_path / "does_not_exist.py"
        artifacts_dir = tmp_path / "artifacts"

        with pytest.raises(FileNotFoundError):
            ingest(nonexistent, artifacts_dir=artifacts_dir)

    def test_ingest_file_too_large(self, tmp_path: Path) -> None:
        """Test ingestion fails for oversized file."""
        large_file = tmp_path / "large.py"
        size_bytes = (MAX_FILE_SIZE_MB + 1) * 1024 * 1024
        large_file.write_bytes(b"x" * int(size_bytes))

        artifacts_dir = tmp_path / "artifacts"

        with pytest.raises(ValueError, match="File size .* exceeds limit"):
            ingest(large_file, artifacts_dir=artifacts_dir)
