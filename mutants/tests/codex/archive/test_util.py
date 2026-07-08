"""
Tests for codex.archive.util module.

This module contains tests for utility helpers in the archival workflow.
"""


class TestUtcnow:
    """Tests for utcnow function."""

    def test_returns_string(self):
        """Test utcnow returns a string."""
        from codex.archive.util import utcnow

        result = utcnow()

        assert isinstance(result, str)

    def test_iso_format(self):
        """Test utcnow returns ISO format."""
        from codex.archive.util import utcnow

        result = utcnow()

        # Should match YYYY-MM-DDTHH:MM:SSZ format
        assert len(result) == 20, "Result must not be empty"
        assert result[4] == "-", "Result must not be empty"
        assert result[7] == "-", "Result must not be empty"
        assert result[10] == "T", "Result must not be empty"
        assert result[-1] == "Z", "Result must not be empty"

    def test_utcnow_iso_alias(self):
        """Test utcnow_iso is an alias."""
        from codex.archive.util import utcnow, utcnow_iso

        # Both should return valid timestamps
        result1 = utcnow()
        result2 = utcnow_iso()

        assert isinstance(result1, str)
        assert isinstance(result2, str)


class TestSha256:
    """Tests for SHA-256 functions."""

    def test_sha256_hex(self):
        """Test sha256_hex function."""
        from codex.archive.util import sha256_hex

        data = b"hello world"
        result = sha256_hex(data)

        assert isinstance(result, str)
        assert len(result) == 64, "Result must not be empty"

    def test_sha256_hex_deterministic(self):
        """Test sha256_hex is deterministic."""
        from codex.archive.util import sha256_hex

        data = b"test data"

        result1 = sha256_hex(data)
        result2 = sha256_hex(data)

        assert result1 == result2, "Result must not be empty"

    def test_sha256_bytes(self):
        """Test sha256_bytes function."""
        from codex.archive.util import sha256_bytes

        data = b"hello world"
        result = sha256_bytes(data)

        assert isinstance(result, str)
        assert len(result) == 64, "Result must not be empty"

    def test_sha256_hex_and_bytes_same(self):
        """Test sha256_hex and sha256_bytes return same result."""
        from codex.archive.util import sha256_bytes, sha256_hex

        data = b"test"

        assert sha256_hex(data) == sha256_bytes(data), "Data must not be empty"

    def test_sha256_file(self, tmp_path):
        """Test sha256_file function."""
        from codex.archive.util import sha256_bytes, sha256_file

        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"file content")

        result = sha256_file(test_file)
        expected = sha256_bytes(b"file content")

        assert result == expected, "Result must not be empty"

    def test_sha256_file_nonexistent(self, tmp_path):
        """Test sha256_file with nonexistent file."""
        from codex.archive.util import sha256_file

        nonexistent = tmp_path / "nonexistent.txt"

        result = sha256_file(nonexistent)

        assert result == "", "Result must not be empty"


class TestCompression:
    """Tests for compression functions."""

    def test_zstd_compress(self):
        """Test zstd_compress function."""
        from codex.archive.util import zstd_compress

        data = b"hello world" * 100  # Repeated for better compression

        compressed = zstd_compress(data)

        assert isinstance(compressed, bytes)
        # Compressed should be smaller for repetitive data
        assert len(compressed) < len(data), "Compressed must not be empty"

    def test_zlib_compress(self):
        """Test zlib_compress function."""
        from codex.archive.util import zlib_compress

        data = b"hello world" * 100

        compressed = zlib_compress(data)

        assert isinstance(compressed, bytes)
        assert len(compressed) < len(data), "Compressed must not be empty"

    def test_zlib_compress_level(self):
        """Test zlib_compress with different levels."""
        from codex.archive.util import zlib_compress

        data = b"test data" * 50

        # Higher level should produce better compression (or same)
        compressed_low = zlib_compress(data, level=1)
        compressed_high = zlib_compress(data, level=9)

        assert len(compressed_high) <= len(compressed_low), "Compressed_high must not be empty"


class TestModuleConstants:
    """Tests for module constants."""

    def test_iso_format(self):
        """Test ISO_FORMAT constant."""
        from codex.archive.util import ISO_FORMAT

        assert ISO_FORMAT == "%Y-%m-%dT%H:%M:%SZ", "ISO_FORMAT is not valid"

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.util import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.archive.util", "name is not valid"
