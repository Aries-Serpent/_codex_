"""Tests for encoding detection helpers."""
from __future__ import annotations
import pytest
from pathlib import Path
    from ingestion.encoding_detect import autodetect_encoding, detect_encoding
    from ingestion.encoding_detect import detect_encoding




def test_detect_encoding_handles_various_encodings(tmp_path: Path) -> None:

    utf8 = tmp_path / "utf8.txt"
    utf8.write_text("hello", encoding="utf-8")
    assert "utf" in detect_encoding(utf8).lower(), "Condition must be true"
    assert autodetect_encoding(utf8).lower().startswith("utf"), "Condition must be true"

    latin = tmp_path / "latin1.txt"
    latin.write_bytes("Héllo".encode("latin-1"))
    enc = detect_encoding(latin)
    assert enc, "enc is not valid"


def test_detect_encoding_missing_file_returns_default(tmp_path: Path) -> None:

    missing = tmp_path / "missing.txt"
    assert detect_encoding(missing, default="utf-8") == "utf-8"
