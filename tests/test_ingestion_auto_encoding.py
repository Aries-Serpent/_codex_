from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion import Ingestor

ENCODINGS = ["iso-8859-1", "cp1252", "utf-16", "auto"]


@pytest.mark.parametrize("enc", ENCODINGS[:-1])
def test_auto_detect_handles_encodings(tmp_path: Path, enc: str) -> None:
    text = "café £"
    p = tmp_path / f"sample_{enc.replace('-', '')}.txt"
    p.write_bytes(text.encode(enc))
    out = Ingestor.ingest(p, encoding="auto")
    assert out == text
