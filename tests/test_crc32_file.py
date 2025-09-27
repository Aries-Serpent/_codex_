from __future__ import annotations

import zlib

from codex_ml.data.integrity import crc32_file


def test_crc32_matches_zlib(tmp_path):
    payload = b"codex-ml integrity\n" * 5
    target = tmp_path / "sample.jsonl"
    target.write_bytes(payload)

    expected = zlib.crc32(payload) & 0xFFFFFFFF
    assert crc32_file(target) == expected
