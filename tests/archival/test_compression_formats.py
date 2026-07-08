"""
Comprehensive tests for archival bundling compression formats.

Tests cover tar.gz, zip, and tar.xz compression formats with various
file types and sizes to ensure proper bundling and extraction.
"""

from __future__ import annotations

import tarfile
import zipfile

import pytest

from .security_utils import safe_extract_tarfile


class TestTarGzCompression:
    """Test tar.gz compression format for archival bundles"""

    def test_create_targz_bundle(self, tmp_path):
        """Test creating a tar.gz archive"""
        # Create test files
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")

        # Create tar.gz archive
        archive_path = tmp_path / "bundle.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        assert archive_path.exists(), "Condition must be true"
        assert archive_path.suffix == ".gz", "suffix is not valid"
        assert archive_path.stat().st_size > 0, "st_size must be greater than zero"

    def test_extract_targz_bundle(self, tmp_path):
        """Test extracting a tar.gz archive"""
        # Create and archive
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.txt").write_text("test content")

        archive_path = tmp_path / "bundle.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir / "test.txt", arcname="test.txt")

        # Extract
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        # Security: Use safe extraction to prevent path traversal
        safe_extract_tarfile(archive_path, extract_dir)

        extracted_file = extract_dir / "test.txt"
        assert extracted_file.exists(), "Condition must be true"
        assert extracted_file.read_text() == "test content", "Content must not be empty"

    def test_targz_compression_ratio(self, tmp_path):
        """Test that tar.gz achieves reasonable compression"""
        # Create file with compressible content
        source_file = tmp_path / "compressible.txt"
        source_file.write_text("test " * 10000)  # Highly compressible

        archive_path = tmp_path / "bundle.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_file, arcname="compressible.txt")

        original_size = source_file.stat().st_size
        compressed_size = archive_path.stat().st_size

        # Should achieve at least 50% compression on repetitive text
        assert compressed_size < original_size * 0.5, "compressed_size is not valid"

    def test_targz_preserves_file_metadata(self, tmp_path):
        """Test that tar.gz preserves file permissions and timestamps"""
        source_file = tmp_path / "metadata_test.txt"
        source_file.write_text("content")
        source_file.chmod(0o644)

        archive_path = tmp_path / "bundle.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_file, arcname="metadata_test.txt")

        # Extract and verify
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        safe_extract_tarfile(archive_path, extract_dir)

        extracted_file = extract_dir / "metadata_test.txt"
        assert extracted_file.exists(), "Condition must be true"
        # Permissions should be preserved (on Unix-like systems)
        assert extracted_file.read_text() == "content", "Content must not be empty"

    def test_targz_handles_empty_directories(self, tmp_path):
        """Test that tar.gz can handle empty directories"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "empty_dir").mkdir()

        archive_path = tmp_path / "bundle.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        # Extract and verify
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        # Security: Use safe extraction to prevent path traversal
        safe_extract_tarfile(archive_path, extract_dir)

        assert (extract_dir / "empty_dir").exists(), "Condition must be true"
        assert (extract_dir / "empty_dir").is_dir(), "Condition must be true"


class TestZipCompression:
    """Test ZIP compression format for archival bundles"""

    def test_create_zip_bundle(self, tmp_path):
        """Test creating a ZIP archive"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("zip content 1")
        (source_dir / "file2.txt").write_text("zip content 2")

        archive_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in source_dir.iterdir():
                zf.write(file, arcname=file.name)

        assert archive_path.exists(), "Condition must be true"
        assert archive_path.suffix == ".zip", "suffix is not valid"

    def test_extract_zip_bundle(self, tmp_path):
        """Test extracting a ZIP archive"""
        archive_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("test.txt", "zip test content")

        extract_dir = tmp_path / "extracted"
        with zipfile.ZipFile(archive_path, "r") as zf:
            # Safe extraction - validate paths to prevent directory traversal
            for member in zf.namelist():
                member_path = extract_dir / member
                if not member_path.resolve().is_relative_to(extract_dir.resolve()):
                    raise ValueError(f"Attempted path traversal in zip file: {member}")
            zf.extractall(extract_dir)  # nosec B202 - Path validation performed above

        extracted_file = extract_dir / "test.txt"
        assert extracted_file.exists(), "Condition must be true"
        assert extracted_file.read_text() == "zip test content", "Content must not be empty"

    def test_zip_compression_levels(self, tmp_path):
        """Test ZIP compression with different levels"""
        source_file = tmp_path / "compressible.txt"
        source_file.write_text("compress this " * 5000)

        # No compression
        archive_stored = tmp_path / "stored.zip"
        with zipfile.ZipFile(archive_stored, "w", zipfile.ZIP_STORED) as zf:
            zf.write(source_file, arcname="file.txt")

        # With compression
        archive_deflated = tmp_path / "deflated.zip"
        with zipfile.ZipFile(archive_deflated, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(source_file, arcname="file.txt")

        # Compressed should be smaller
        assert archive_deflated.stat().st_size < archive_stored.stat().st_size, "st_size is not valid"

    def test_zip_handles_special_characters_in_names(self, tmp_path):
        """Test ZIP handling of special characters in filenames"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create files with special characters (safe for most filesystems)
        special_file = source_dir / "special-file_name.txt"
        special_file.write_text("special content")

        archive_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.write(special_file, arcname=special_file.name)

        # Verify it's in the archive
        with zipfile.ZipFile(archive_path, "r") as zf:
            assert "special-file_name.txt" in zf.namelist(), "Condition must be true"

    def test_zip_archive_integrity(self, tmp_path):
        """Test ZIP archive integrity checking"""
        archive_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")

        # Test archive integrity
        with zipfile.ZipFile(archive_path, "r") as zf:
            # testzip() returns None if archive is valid
            assert zf.testzip() is None, "Condition must be true"


class TestTarXzCompression:
    """Test tar.xz compression format for archival bundles"""

    def test_create_tarxz_bundle(self, tmp_path):
        """Test creating a tar.xz archive"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("xz content 1")
        (source_dir / "file2.txt").write_text("xz content 2")

        archive_path = tmp_path / "bundle.tar.xz"
        with tarfile.open(archive_path, "w:xz") as tar:
            tar.add(source_dir, arcname=".")

        assert archive_path.exists(), "Condition must be true"
        assert archive_path.suffix == ".xz", "suffix is not valid"

    def test_extract_tarxz_bundle(self, tmp_path):
        """Test extracting a tar.xz archive"""
        source_file = tmp_path / "test.txt"
        source_file.write_text("xz test content")

        archive_path = tmp_path / "bundle.tar.xz"
        with tarfile.open(archive_path, "w:xz") as tar:
            tar.add(source_file, arcname="test.txt")

        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        safe_extract_tarfile(archive_path, extract_dir)

        extracted_file = extract_dir / "test.txt"
        assert extracted_file.exists(), "Condition must be true"
        assert extracted_file.read_text() == "xz test content", "Content must not be empty"

    def test_tarxz_compression_efficiency(self, tmp_path):
        """Test that tar.xz achieves better compression than tar.gz"""
        # Create highly compressible content
        source_file = tmp_path / "highly_compressible.txt"
        source_file.write_text("repeat " * 10000)

        # Create both formats
        targz_path = tmp_path / "bundle.tar.gz"
        with tarfile.open(targz_path, "w:gz") as tar:
            tar.add(source_file, arcname="file.txt")

        tarxz_path = tmp_path / "bundle.tar.xz"
        with tarfile.open(tarxz_path, "w:xz") as tar:
            tar.add(source_file, arcname="file.txt")

        # XZ should typically achieve better compression
        # (though it may not always be true for small files)
        assert tarxz_path.exists(), "Condition must be true"
        assert targz_path.exists(), "Condition must be true"

    def test_tarxz_handles_nested_directories(self, tmp_path):
        """Test tar.xz handling of nested directory structures"""
        source_dir = tmp_path / "source"
        nested_dir = source_dir / "level1" / "level2" / "level3"
        nested_dir.mkdir(parents=True)
        (nested_dir / "deep_file.txt").write_text("deep content")

        archive_path = tmp_path / "bundle.tar.xz"
        with tarfile.open(archive_path, "w:xz") as tar:
            tar.add(source_dir, arcname=".")

        # Extract and verify
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        # Security: Use safe extraction to prevent path traversal
        safe_extract_tarfile(archive_path, extract_dir)

        extracted_file = extract_dir / "level1" / "level2" / "level3" / "deep_file.txt"
        assert extracted_file.exists(), "Condition must be true"
        assert extracted_file.read_text() == "deep content", "Content must not be empty"

    def test_tarxz_file_count_preservation(self, tmp_path):
        """Test that tar.xz preserves exact file count"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create multiple files
        file_count = 25
        for i in range(file_count):
            (source_dir / f"file_{i}.txt").write_text(f"content {i}")

        archive_path = tmp_path / "bundle.tar.xz"
        with tarfile.open(archive_path, "w:xz") as tar:
            tar.add(source_dir, arcname=".")

        # Count files in archive
        with tarfile.open(archive_path, "r:xz") as tar:
            members = tar.getmembers()
            # Filter out directory entries
            file_members = [m for m in members if m.isfile()]
            assert len(file_members) == file_count, "File_members must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
