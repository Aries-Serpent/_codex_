"""
Unit tests for verifier module (bundle verification functionality).

These tests use small synthetic bundles (creating zip files in memory) to verify that the verify_bundle logic catches mismatches and validates correct bundles.
"""

import hashlib
import io
import json
import zipfile

from verifier import verify_bundle


def create_test_bundle(files_data):
    """
    Helper to create an in-memory ZIP bundle with given files data.
    files_data: dict mapping filename -> content bytes.
    Returns bytes of the ZIP file.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zipf:
        for name, data in files_data.items():
            zipf.writestr(name, data)
    return buf.getvalue()


def test_verify_bundle_success(tmp_path):
    """verify_bundle should return True for a well-formed bundle."""
    # Create a minimal well-formed bundle with one file split into two panels.
    # Original file content and its hash:
    original_content = b"Hello, this is a test file.\nIt has two lines."
    original_hash = hashlib.sha256(original_content).hexdigest()
    # Split into two panels:
    part1 = b"Hello, this is a test file.\n"
    part2 = b"It has two lines."
    # Build headers (simple '#' comment header for example)
    header1 = (
        b"# SENTINEL_HEADER_BEGIN\n# source_path: test.txt\n# source_sha256: "
        + original_hash.encode("utf-8")
        + b"\n# part: 1 of 2\n# SENTINEL_HEADER_END\n"
    )
    header2 = (
        b"# SENTINEL_HEADER_BEGIN\n# source_path: test.txt\n# source_sha256: "
        + original_hash.encode("utf-8")
        + b"\n# part: 2 of 2\n# SENTINEL_HEADER_END\n"
    )
    panel1 = header1 + part1
    panel2 = header2 + part2
    panel1_name = "12345678__test.txt__part_0001_of_0002.txt"
    panel2_name = "12345678__test.txt__part_0002_of_0002.txt"
    # Create manifest
    manifest = {
        "strategy": "bytes",
        "budget": 100,
        "sources": [
            {
                "path": "test.txt",
                "sha256": original_hash,
                "size_bytes": len(original_content),
                "panels": [
                    {
                        "file": panel1_name,
                        "sha256": hashlib.sha256(part1).hexdigest(),
                        "part": 1,
                        "of": 2,
                    },
                    {
                        "file": panel2_name,
                        "sha256": hashlib.sha256(part2).hexdigest(),
                        "part": 2,
                        "of": 2,
                    },
                ],
            }
        ],
    }
    files = {
        "manifest.json": json.dumps(manifest).encode("utf-8"),
        panel1_name: panel1,
        panel2_name: panel2,
    }
    bundle_bytes = create_test_bundle(files)
    bundle_path = tmp_path / "test_bundle.zip"
    bundle_path.write_bytes(bundle_bytes)
    result = verify_bundle(str(bundle_path))
    assert result is True


def test_verify_bundle_detects_tamper(tmp_path):
    """verify_bundle should detect if a panel content is modified (hash mismatch)."""
    # Start from a correct bundle as above, then tamper with panel content.
    original_content = b"Secret data"
    original_hash = hashlib.sha256(original_content).hexdigest()
    part1 = original_content  # not actually splitting since very short
    header = (
        b"---\nsource_path: data.txt\nsource_sha256: "
        + original_hash.encode("utf-8")
        + b"\npart: 1 of 1\n---\n"
    )
    panel_name = "abcdef12__data.txt__part_0001_of_0001.txt"
    manifest = {
        "strategy": "bytes",
        "budget": 50,
        "sources": [
            {
                "path": "data.txt",
                "sha256": original_hash,
                "size_bytes": len(original_content),
                "panels": [
                    {
                        "file": panel_name,
                        "sha256": hashlib.sha256(part1).hexdigest(),
                        "part": 1,
                        "of": 1,
                    }
                ],
            }
        ],
    }
    files = {"manifest.json": json.dumps(manifest).encode(), panel_name: header + part1}
    bundle_bytes = create_test_bundle(files)
    # Tamper: flip a byte in the panel content in the zip bytes
    tampered_bytes = bytearray(bundle_bytes)
    idx = tampered_bytes.index(b"Secret")
    tampered_bytes[idx] = tampered_bytes[idx] ^ 0xFF  # arbitrary change to corrupt content
    bundle_path = tmp_path / "tampered.zip"
    bundle_path.write_bytes(bytes(tampered_bytes))
    result = verify_bundle(str(bundle_path))
    assert result is False, "Tampered bundle verification should fail."
