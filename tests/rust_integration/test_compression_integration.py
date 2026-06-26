"""
Python integration tests for Compression
"""

import time

import pytest


def test_lz4_compression():
    """Test LZ4 compression and decompression."""
    try:
        from codex_engine import CompressionPipeline

        pipeline = CompressionPipeline("lz4")

        data = b"Hello, World! This is test data." * 100
        compressed = pipeline.compress(data)
        decompressed = pipeline.decompress(compressed)

        assert data == bytes(decompressed), "Data must not be empty"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_zstd_compression():
    """Test Zstd compression and decompression."""
    try:
        from codex_engine import CompressionPipeline

        pipeline = CompressionPipeline("zstd", 3)

        data = b"Hello, World! This is test data." * 100
        compressed = pipeline.compress(data)
        decompressed = pipeline.decompress(compressed)

        assert data == bytes(decompressed), "Data must not be empty"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_compression_ratio():
    """Test compression ratio on repetitive data."""
    try:
        from codex_engine import CompressionPipeline

        pipeline = CompressionPipeline("lz4")

        # Highly compressible data
        data = b"x" * (1024 * 1024)  # 1MB of 'x'
        compressed = pipeline.compress(data)

        ratio = len(data) / len(compressed)
        assert ratio > 10.0, f"Compression ratio: {ratio:.2f}x"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_compression_performance():
    """Test LZ4 compression performance."""
    try:
        from codex_engine import CompressionPipeline

        pipeline = CompressionPipeline("lz4")

        data = b"\x00" * (1024 * 1024)  # 1MB

        start = time.time()
        for _ in range(100):
            compressed = pipeline.compress(data)
        compress_time = time.time() - start

        start = time.time()
        for _ in range(100):
            _ = pipeline.decompress(compressed)
        decompress_time = time.time() - start

        # Should be very fast
        assert compress_time < 1.0, f"Compression took {compress_time:.3f}s"
        assert decompress_time < 1.0, f"Decompression took {decompress_time:.3f}s"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_different_data_types():
    """Test compression with different data patterns."""
    try:
        from codex_engine import CompressionPipeline

        pipeline = CompressionPipeline("lz4")

        test_cases = [
            b"",  # Empty
            b"a",  # Single byte
            b"Hello, World!",  # Short string
            b"x" * 10000,  # Repetitive
            bytes(range(256)) * 100,  # Random-ish
        ]

        for data in test_cases:
            compressed = pipeline.compress(data)
            decompressed = pipeline.decompress(compressed)
            assert data == bytes(decompressed), "Data must not be empty"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_invalid_codec():
    """Test that invalid codec raises error."""
    try:
        from codex_engine import CompressionPipeline

        with pytest.raises(ValueError):
            CompressionPipeline("invalid_codec")
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_zstd_compression_levels():
    """Test different Zstd compression levels."""
    try:
        from codex_engine import CompressionPipeline

        data = b"Test data" * 1000

        for level in [1, 3, 10]:
            pipeline = CompressionPipeline("zstd", level)
            compressed = pipeline.compress(data)
            decompressed = pipeline.decompress(compressed)
            assert data == bytes(decompressed), "Data must not be empty"
    except ImportError:
        pytest.skip("codex_engine not built yet")


def test_large_data_compression():
    """Test compression of large data."""
    try:
        from codex_engine import CompressionPipeline

        pipeline = CompressionPipeline("lz4")

        # 10MB of data
        data = b"large_data_block" * (1024 * 1024 // 16)

        compressed = pipeline.compress(data)
        decompressed = pipeline.decompress(compressed)

        assert len(data) == len(decompressed), "Data must not be empty"
        assert data == bytes(decompressed), "Data must not be empty"
    except ImportError:
        pytest.skip("codex_engine not built yet")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
