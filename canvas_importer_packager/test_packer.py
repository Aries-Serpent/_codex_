"""Unit tests for packer module (chunking and packaging functionality).

These tests are structured but not fully implemented. Each test has a docstring explaining what to verify. The actual assertions and test logic should be filled in once the packer functions are implemented.

We use pytest-style function tests (or could use unittest classes)."""

import json
import zipfile

import pytest
from packer import build_header, chunk_file, is_binary_content, make_panel_filename, pack_directory


def test_make_panel_filename_basic():
    """Test that make_panel_filename produces a stable and correctly formatted name."""
    file_path = "path/to/Example.txt"
    name = make_panel_filename(file_path, part_index=1, total_parts=10)
    # The name should contain the 8-char prefix, slugified path, and part numbers.
    assert "__path_to_Example.txt__part_0001_of_0010.txt" in name or name.endswith(
        "__part_0001_of_0010.txt"
    ), "Panel filename format is incorrect or slug generation failed."
    # Check that two calls produce the same prefix for same path.
    name2 = make_panel_filename(file_path, part_index=2, total_parts=10)
    prefix1 = name.split("__")[0]
    prefix2 = name2.split("__")[0]
    assert prefix1 == prefix2, "Prefix hash inconsistent for same file path."


def test_is_binary_content_null_bytes():
    """Files containing null byte in early content should be detected as binary."""
    data = b"This is text\x00with null"  # contains a null byte in the middle
    assert is_binary_content(data) is True, "Null byte not detected as binary content."
    data2 = b"Hello\x00\x00\x00"  # starts with printable but contains nulls
    assert is_binary_content(data2) is True
    data3 = b"No null here\nJust text"
    assert is_binary_content(data3) is False


def test_chunk_file_bytes_strategy():
    """chunk_file with 'bytes' strategy should split content into chunks of at most budget bytes."""
    content = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 26 bytes
    chunks = chunk_file("dummy.txt", content, strategy="bytes", budget=10, model=None)
    # Expect 3 chunks: 10 bytes, 10 bytes, 6 bytes.
    assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
    assert all(len(c) <= 10 for c in chunks), "A chunk exceeds byte budget."
    reconstructed = b"".join(chunks)
    assert (
        reconstructed == content
    ), "Reconstructed content does not match original for 'bytes' strategy."


def test_chunk_file_token_strategy(monkeypatch):
    """chunk_file with 'tokens' strategy should respect token limits (simple scenario)."""
    # This test will monkeypatch tiktoken to simulate tokenization without requiring the actual library.
    dummy_text = "one two three four five"
    content = dummy_text.encode("utf-8")

    # Monkeypatch tiktoken encoding to count words as tokens for simplicity
    class DummyEncoding:
        def encode(self, text):
            # naive tokenization: split on space
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    monkeypatch.setattr("tiktoken.encoding_for_model", lambda model: DummyEncoding())
    chunks = chunk_file("dummy.txt", content, strategy="tokens", budget=3, model="gpt-4")
    # With 5 words and budget 3 tokens, expect 2 chunks: first 3 words, then 2 words.
    decoded_chunks = [c.decode("utf-8") for c in chunks]
    assert decoded_chunks[0].count(" ") == 2  # 3 words -> 2 spaces
    assert decoded_chunks[1].count(" ") == 1  # 2 words -> 1 space
    combined = " ".join(decoded_chunks)
    assert combined == dummy_text, "Token chunks reassembled text doesn't match original."


def test_pack_directory_and_manifest(tmp_path):
    """Integration test: pack_directory creates a bundle with manifest that matches input files."""
    # Create a temporary directory structure with a couple of files
    root = tmp_path / "proj"
    root.mkdir()
    file1 = root / "a.txt"
    file1.write_text("Hello\nWorld\n")
    file2 = root / "subdir"
    file2.mkdir()
    file3 = file2 / "b.txt"
    file3.write_text("Python\nTesting\nCanvas\n")
    bundle_path = tmp_path / "bundle.zip"
    pack_directory(root_path=str(root), output_zip=str(bundle_path), strategy="bytes", budget=10)

    # Now read the bundle and check manifest and files
    with zipfile.ZipFile(bundle_path, "r") as z:
        manifest = json.loads(z.read("manifest.json"))
        # Check manifest has correct number of sources (2 files)
        assert len(manifest["sources"]) == 2
        # Check each source in manifest has panels and correct path
        paths = [src["path"] for src in manifest["sources"]]
        assert "a.txt" in paths or "proj/a.txt" in paths
        assert "subdir/b.txt" in paths or "proj/subdir/b.txt" in paths
        # Check that each panel file exists in the zip
        for src in manifest["sources"]:
            for panel in src["panels"]:
                fname = panel["file"] if isinstance(panel, dict) else panel
                try:
                    z.getinfo(fname)
                except KeyError:
                    pytest.fail(f"Panel file {fname} listed in manifest not found in bundle")


def test_build_and_strip_header():
    """Test that building a header and then stripping it yields the original content back."""
    file_path = "docs/README.md"
    file_sha = "abcd1234"
    strategy = "semantic"
    header = build_header(file_path, file_sha, strategy, part_index=1, total_parts=1)
    content = "Some content\nLine2\n".encode("utf-8")
    panel_bytes = header.encode("utf-8") + content
    # strip_header should return the original content bytes
    from verifier import strip_header

    stripped = strip_header(panel_bytes)
    assert stripped == content, "Header stripping failed to return original content."
