"""Tests for encoding detection helpers."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_detect_encoding_handles_various_encodings(tmp_path: Path) -> None:
    from ingestion.encoding_detect import detect_encoding, autodetect_encoding

    utf8 = tmp_path / "utf8.txt"
    utf8.write_text("hello", encoding="utf-8")
    assert "utf" in detect_encoding(utf8).lower()
    assert autodetect_encoding(utf8).lower().startswith("utf")

    latin = tmp_path / "latin1.txt"
    latin.write_bytes("Héllo".encode("latin-1"))
    enc = detect_encoding(latin)
    assert enc


def test_detect_encoding_missing_file_returns_default(tmp_path: Path) -> None:
    from ingestion.encoding_detect import detect_encoding

    missing = tmp_path / "missing.txt"
    assert detect_encoding(missing, default="utf-8") == "utf-8"
