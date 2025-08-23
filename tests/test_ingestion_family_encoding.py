import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion.file_ingestor import read_file
from ingestion.json_ingestor import load_json
from ingestion.csv_ingestor import load_csv
from ingestion.utils import read_text_file

ENCODINGS = ["iso-8859-1", "cp1252", "utf-16", "auto"]


@pytest.mark.parametrize("enc", ENCODINGS)
def test_family_encoding_hooks(tmp_path: Path, enc: str) -> None:
    text = "café £"
    file_enc = "cp1252" if enc == "auto" else enc

    t = tmp_path / f"text_{file_enc}.txt"
    t.write_text(text, encoding=file_enc)

    j = tmp_path / f"data_{file_enc}.json"
    j.write_text(json.dumps({"msg": text}, ensure_ascii=False), encoding=file_enc)

    c = tmp_path / f"data_{file_enc}.csv"
    c.write_text(f"msg\n{text}\n", encoding=file_enc)

    assert read_file(t, encoding=enc) == text
    assert read_text_file(t, encoding=enc) == text
    assert load_json(j, encoding=enc)["msg"] == text
    rows = load_csv(c, encoding=enc)
    assert rows == [["msg"], [text]]
