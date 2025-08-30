from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ingestion.io_text import read_text
from ingestion.utils import deterministic_shuffle

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
    assert out == text
    assert used.lower().replace("-", "") == enc.replace("-", "")


@pytest.mark.parametrize("enc,text", ENCODINGS)
def test_read_text_auto(tmp_path: Path, enc: str, text: str) -> None:
    pytest.importorskip("charset_normalizer")
    p = tmp_path / "sample.txt"
    p.write_text(text, encoding=enc)
    out, used = read_text(p, encoding="auto")
    assert out == text
    assert used


def test_read_text_auto_without_normalizer(tmp_path: Path, monkeypatch) -> None:
    p = tmp_path / "sample.txt"
    p.write_text("hello", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "charset_normalizer", None)
    from importlib import reload

    from ingestion import encoding_detect as ed

    reload(ed)
    from ingestion.io_text import read_text as rt

    out, used = rt(p, encoding="auto")
    assert out == "hello" and used == "utf-8"


def test_deterministic_shuffle() -> None:
    data = list(range(5))
    a = deterministic_shuffle(data, seed=123)
    b = deterministic_shuffle(data, seed=123)
    assert a == b and a != data
