from pathlib import Path


def test_seeded_shuffle_deterministic():
    from ingestion.io_text import seeded_shuffle

    data = [str(i) for i in range(10)]
    a = seeded_shuffle(data, seed=123)
    b = seeded_shuffle(data, seed=123)
    assert a == b and a != data


def test_read_text_auto_utf8(tmp_path: Path):
    from ingestion.io_text import read_text

    p = tmp_path / "hello.txt"
    p.write_text("héllo", encoding="utf-8")
    out = read_text(p, encoding="auto")
    assert out == "héllo"

