"""Tests for ingestion utilities."""
import pytest

pytest.importorskip("charset_normalizer")

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion import Ingestor, ingest


def _call_ingest(p, **kwargs):
    """Helper that uses module-level ingest or Ingestor.ingest."""
    if hasattr(Ingestor, "ingest"):
        return Ingestor.ingest(p, **kwargs)
    return ingest(p, **kwargs)


ENCODINGS = ["iso-8859-1", "cp1252", "utf-16", "auto"]


def test_full_read_default_encoding(tmp_path: Path) -> None:
    p = tmp_path / "hello.txt"
    text = "héllø—世界"
    p.write_text(text, encoding="utf-8")
    out = _call_ingest(p)
    assert isinstance(out, str)
    assert out == text, "out is not valid"


@pytest.mark.parametrize(
    "enc,text",
    [
        ("iso-8859-1", "café £"),
        ("cp1252", "naïve £"),
        ("utf-16", "héllø"),
        ("auto", "café £"),
    ],
)
def test_read_various_encodings(tmp_path: Path, enc: str, text: str) -> None:
    file_enc = "cp1252" if enc == "auto" else enc
    p = tmp_path / f"sample_{file_enc.replace('-', '')}.txt"
    p.write_text(text, encoding=file_enc)
    out = _call_ingest(p, encoding=enc)
    assert out == text, "out is not valid"


def test_chunked_read_and_reassembly(tmp_path: Path) -> None:
    p = tmp_path / "lorem.txt"
    text = "abc" * 5000
    p.write_text(text, encoding="utf-8")
    chunks = list(_call_ingest(p, chunk_size=4096))
    assert all(isinstance(c, str) for c in chunks)
    assert "".join(chunks) == text, "Condition must be true"
    assert all(len(c) <= 4096 for c in chunks), "C must not be empty"


def test_accepts_str_path(tmp_path: Path) -> None:
    p = tmp_path / "s.txt"
    p.write_text("OK", encoding="utf-8")
    out = _call_ingest(str(p))
    assert out == "OK", "out is not valid"


def test_directory_raises_filenotfound(tmp_path: Path) -> None:
    d = tmp_path / "dir"
    d.mkdir()
    with pytest.raises(FileNotFoundError):
        _call_ingest(d)
