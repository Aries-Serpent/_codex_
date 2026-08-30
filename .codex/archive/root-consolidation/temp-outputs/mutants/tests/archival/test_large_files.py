"""
Tests for archival bundling with large files.

Tests handling of large files (>1GB simulated), memory efficiency,
streaming operations, and chunked processing.
"""

from __future__ import annotations

import hashlib
import tarfile
import zipfile

import pytest

from .security_utils import safe_extract_tarfile


class TestLargeFileHandling:
    """Test archival operations with large files"""

    def test_create_large_file_simulation(self, tmp_path):
        """Test creating a simulated large file (10MB for speed)"""
        large_file = tmp_path / "large_file.bin"

        # Create 10MB file (simulating large file operations)
        chunk_size = 1024 * 1024  # 1MB chunks
        num_chunks = 10

        with open(large_file, "wb") as f:
            for _ in range(num_chunks):
                f.write(b"X" * chunk_size)

        assert large_file.exists(), "Condition must be true"
        assert large_file.stat().st_size == chunk_size * num_chunks, "st_size is not valid"

    def test_archive_large_file_in_chunks(self, tmp_path):
        """Test archiving large file using chunked reading"""
        # Create 5MB test file
        large_file = tmp_path / "large.bin"
        size_mb = 5
        with open(large_file, "wb") as f:
            f.write(b"A" * (size_mb * 1024 * 1024))

        archive_path = tmp_path / "large.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(large_file, arcname=large_file.name)

        assert archive_path.exists(), "Condition must be true"
        assert archive_path.stat().st_size > 0, "st_size must be greater than zero"

    def test_extract_large_file_streaming(self, tmp_path):
        """Test extracting large file with streaming"""
        # Create and archive large file
        source_file = tmp_path / "large_source.bin"
        size_mb = 3
        with open(source_file, "wb") as f:
            f.write(b"B" * (size_mb * 1024 * 1024))

        archive_path = tmp_path / "large.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_file, arcname="large_source.bin")

        # Extract
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        safe_extract_tarfile(archive_path, extract_dir)

        extracted_file = extract_dir / "large_source.bin"
        assert extracted_file.exists(), "Condition must be true"
        assert extracted_file.stat().st_size == source_file.stat().st_size, "st_size is not valid"

    def test_checksum_large_file_chunked(self, tmp_path):
        """Test checksumming large file in chunks (memory efficient)"""
        large_file = tmp_path / "large.bin"
        size_mb = 10

        # Create file
        with open(large_file, "wb") as f:
            f.write(b"C" * (size_mb * 1024 * 1024))

        # Calculate checksum in chunks (memory efficient)
        sha256_hash = hashlib.sha256()
        chunk_size = 1024 * 1024  # 1MB chunks

        with open(large_file, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha256_hash.update(chunk)

        checksum = sha256_hash.hexdigest()
        assert len(checksum) == 64, "Checksum must not be empty"

    def test_multiple_large_files_bundling(self, tmp_path):
        """Test bundling multiple large files"""
        source_dir = tmp_path / "large_files"
        source_dir.mkdir()

        # Create multiple 2MB files
        num_files = 5
        for i in range(num_files):
            large_file = source_dir / f"large_{i}.bin"
            with open(large_file, "wb") as f:
                f.write(b"D" * (2 * 1024 * 1024))

        # Archive all files
        archive_path = tmp_path / "multiple_large.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        assert archive_path.exists(), "Condition must be true"

        # Verify all files in archive
        with tarfile.open(archive_path, "r:gz") as tar:
            members = [m for m in tar.getmembers() if m.isfile()]
            assert len(members) == num_files, "Members must not be empty"

    def test_sparse_file_handling(self, tmp_path):
        """Test handling of sparse file-like structures"""
        # Simulate sparse file behavior (for systems that support it)
        sparse_file = tmp_path / "sparse.bin"

        # Write data with gaps (simulated sparse file)
        with open(sparse_file, "wb") as f:
            f.write(b"START")
            f.seek(10 * 1024 * 1024)  # Seek ahead (would be sparse on supporting systems)
            f.write(b"END")

        # Archive it
        archive_path = tmp_path / "sparse.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(sparse_file, arcname="sparse.bin")

        assert archive_path.exists(), "Condition must be true"

    def test_large_file_count_handling(self, tmp_path):
        """Test handling archives with many files"""
        source_dir = tmp_path / "many_files"
        source_dir.mkdir()

        # Create many small files (simulates large archive)
        num_files = 1000
        for i in range(num_files):
            (source_dir / f"file_{i:04d}.txt").write_text(f"content {i}")

        archive_path = tmp_path / "many_files.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        # Verify file count
        with tarfile.open(archive_path, "r:gz") as tar:
            members = tar.getmembers()
            file_members = [m for m in members if m.isfile()]
            assert len(file_members) == num_files, "File_members must not be empty"

    def test_zip_large_file_compression(self, tmp_path):
        """Test ZIP format with large file"""
        large_file = tmp_path / "large.bin"
        size_mb = 8

        # Create file with pattern for compression
        with open(large_file, "wb") as f:
            pattern = b"PATTERN" * 1024
            for _ in range(size_mb * 1024 // len(pattern)):
                f.write(pattern)

        archive_path = tmp_path / "large.zip"
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(large_file, arcname=large_file.name)

        # Should achieve compression
        assert archive_path.stat().st_size < large_file.stat().st_size, "st_size is not valid"


class TestMemoryEfficientOperations:
    """Test memory-efficient archival operations"""

    def test_streaming_archive_creation(self, tmp_path):
        """Test creating archive without loading all content in memory"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create several files
        for i in range(10):
            (source_dir / f"file_{i}.txt").write_text(f"data {i}" * 1000)

        archive_path = tmp_path / "streamed.tar.gz"

        # Use streaming mode (don't load all in memory)
        with tarfile.open(archive_path, "w:gz") as tar:
            for file_path in sorted(source_dir.iterdir()):
                tar.add(file_path, arcname=file_path.name)

        assert archive_path.exists(), "Condition must be true"

    def test_incremental_checksum_calculation(self, tmp_path):
        """Test calculating checksums incrementally"""
        test_file = tmp_path / "data.bin"

        # Write in chunks
        chunk_size = 1024 * 1024
        num_chunks = 5

        with open(test_file, "wb") as f:
            for i in range(num_chunks):
                f.write(bytes([i % 256]) * chunk_size)

        # Calculate checksum incrementally
        sha256 = hashlib.sha256()
        with open(test_file, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha256.update(chunk)

        checksum = sha256.hexdigest()
        assert len(checksum) == 64, "Checksum must not be empty"
        assert checksum.isalnum(), "Condition must be true"

    def test_generator_based_file_processing(self, tmp_path):
        """Test processing files using generators (memory efficient)"""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create test files
        for i in range(20):
            (source_dir / f"item_{i}.txt").write_text(f"item {i}")

        # Generator for files
        def file_generator(directory):
            for file_path in sorted(directory.iterdir()):
                if file_path.is_file():
                    yield file_path

        # Process using generator
        file_count = 0
        for file_path in file_generator(source_dir):
            assert file_path.exists(), "Condition must be true"
            file_count += 1

        assert file_count == 20, "Count must be greater than zero"

    def test_buffered_extraction(self, tmp_path):
        """Test extraction with buffering for memory efficiency"""
        # Create archive
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        for i in range(15):
            (source_dir / f"file_{i}.txt").write_text(f"content {i}" * 100)

        archive_path = tmp_path / "buffered.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        # Extract with buffering
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        with tarfile.open(archive_path, "r:gz") as tar:
            # Extract one member at a time (memory efficient)
            for member in tar.getmembers():
                tar.extract(member, extract_dir)

        # Verify extraction
        extracted_files = list(extract_dir.rglob("*.txt"))
        assert len(extracted_files) == 15, "Extracted_files must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
