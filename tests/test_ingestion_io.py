"""Tests for ingestion utilities."""

from pathlib import Path

import pytest


def _call_ingest(p, **kwargs):
    """Helper that uses module-level ingest or Ingestor.ingest."""
    import importlib

    ingestion = importlib.import_module("ingestion")
    if hasattr(ingestion, "Ingestor") and hasattr(ingestion.Ingestor, "ingest"):
        return ingestion.Ingestor.ingest(p, **kwargs)
    return ingestion.ingest(p, **kwargs)


def test_full_read_default_encoding(tmp_path: Path) -> None:
    p = tmp_path / "hello.txt"
    text = "héllø—世界"
    p.write_text(text, encoding="utf-8")
    out = _call_ingest(p)
    assert isinstance(out, str)
    assert out == text


def test_chunked_read_and_reassembly(tmp_path: Path) -> None:
    p = tmp_path / "lorem.txt"
    text = "abc" * 5000
    p.write_text(text, encoding="utf-8")
    chunks = list(_call_ingest(p, chunk_size=4096))
    assert all(isinstance(c, str) for c in chunks)
    assert "".join(chunks) == text
    assert all(len(c) <= 4096 for c in chunks)


def test_accepts_str_path(tmp_path: Path) -> None:
    p = tmp_path / "s.txt"
    p.write_text("OK", encoding="utf-8")
    out = _call_ingest(str(p))
    assert out == "OK"


def test_reads_non_utf8_encoding(tmp_path: Path) -> None:
    """Ensure files saved with other encodings can be ingested."""
    p = tmp_path / "latin1.txt"
    text = "café £"
    p.write_text(text, encoding="iso-8859-1")
    out = _call_ingest(p, encoding="iso-8859-1")
    assert out == text


def test_directory_raises_filenotfound(tmp_path: Path) -> None:
    d = tmp_path / "dir"
    d.mkdir()
    with pytest.raises(FileNotFoundError):
        _call_ingest(d)
