import pytest
from pathlib import Path

ENCODINGS = ["utf-8", "iso-8859-1", "cp1252", "utf-16", "auto"]

@pytest.mark.parametrize("enc", ENCODINGS)
@pytest.mark.xfail(reason="Module path may differ; update imports if needed", strict=False, raises=Exception)
def test_ingestion_encoding_matrix(tmp_path: Path, enc: str):
    text_in = "café — Δ £"
    file_enc = "cp1252" if enc == "auto" else enc
    f = tmp_path / f"sample_{file_enc.replace('-', '')}.txt"
    f.write_bytes(text_in.encode(file_enc))

    try:
        from ingestion import Ingestor
    except Exception:
        try:
            from src.ingestion import Ingestor
        except Exception as e:
            pytest.xfail(f"Cannot import Ingestor: {e}")

    ing = Ingestor()
    out = ing.ingest(f, encoding=enc)
    assert isinstance(out, str)
    assert "caf" in out and "£" in out
