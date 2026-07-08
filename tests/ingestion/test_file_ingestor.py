"""Smoke tests for ingestion.file_ingestor."""

from __future__ import annotations

from pathlib import Path

from ingestion.file_ingestor import read_file


def test_read_file_with_auto_encoding(tmp_path: Path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("héllo", encoding="utf-8")

    content = read_file(target, encoding="auto")
    assert "héllo" in content, "Content must not be empty"


def test_read_file_with_explicit_encoding(tmp_path: Path) -> None:
    target = tmp_path / "latin1.txt"
    target.write_text("café", encoding="latin-1")

    content = read_file(target, encoding="latin-1")
    assert "café" in content, "Content must not be empty"
