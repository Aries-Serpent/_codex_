"""
Test Io Text

Test module for io text.
"""
from __future__ import annotations
    pytest.importorskip("charset_normalizer")
import sys
from pathlib import Path
from ingestion.io_text import read_text
from ingestion.utils import deterministic_shuffle
    from importlib import reload
    from ingestion import encoding_detect as ed
    from ingestion.io_text import read_text as rt





ENCODINGS = [
    ("utf-8", "héllo"),
    ("cp1252", "héllo"),
    ("utf-16", "héllo"),
]


@pytest.mark.parametrize("enc,text", ENCODINGS)
def test_read_text_explicit(tmp_path: Path, enc: str, text: str) -> None:
    p = tmp_path / "sample.txt"
    p.write_text(text, encoding=enc)
    out, used = read_text(p, encoding=enc)
    assert out == text, "out is not valid"
    assert used.lower().replace("-", "") == enc.replace("-", "")


@pytest.mark.parametrize("enc,text", ENCODINGS)
def test_read_text_auto(tmp_path: Path, enc: str, text: str) -> None:
    p = tmp_path / "sample.txt"
    p.write_text(text, encoding=enc)
    out, used = read_text(p, encoding="auto")
    assert out == text, "out is not valid"
    assert used, "used is not valid"


def test_read_text_auto_without_normalizer(tmp_path: Path, monkeypatch) -> None:
    p = tmp_path / "sample.txt"
    p.write_text("hello", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "charset_normalizer", None)


    reload(ed)

    out, used = rt(p, encoding="auto")
    assert out == "hello" and used == "utf-8", "out is not valid"


def test_deterministic_shuffle() -> None:
    data = list(range(5))
    a = deterministic_shuffle(data, seed=123)
    b = deterministic_shuffle(data, seed=123)
    assert a == b and a != data, "Data must not be empty"
