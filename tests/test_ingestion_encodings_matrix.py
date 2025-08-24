import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion import Ingestor  # noqa: E402

ENCODINGS = ["iso-8859-1", "cp1252", "utf-16", "auto"]


@pytest.mark.parametrize("enc", ENCODINGS)
def test_ingestion_encoding_matrix(tmp_path: Path, enc: str) -> None:
    text_in = "café £"
    file_enc = "cp1252" if enc == "auto" else enc
    f = tmp_path / f"sample_{file_enc.replace('-', '')}.txt"
    f.write_bytes(text_in.encode(file_enc))
    out = Ingestor.ingest(f, encoding=enc)
    assert isinstance(out, str)
    assert "café" in out and "£" in out
