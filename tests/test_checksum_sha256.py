from __future__ import annotations

import hashlib

from codex_ml.utils.checksum import sha256sum


def test_sha256sum_matches_hashlib(tmp_path):
    payload = b"checkpoint-bytes\x00with\nnewlines"
    target = tmp_path / "sample.bin"
    target.write_bytes(payload)

    expected = hashlib.sha256(payload).hexdigest()
    assert sha256sum(target) == expected


def test_sha256sum_handles_large_files(tmp_path):
    # Create a file larger than the default chunk size to ensure streaming works.
    block = b"0123456789abcdef" * 8192
    target = tmp_path / "large.bin"
    target.write_bytes(block * 4)

    expected = hashlib.sha256(block * 4).hexdigest()
    assert sha256sum(target) == expected
