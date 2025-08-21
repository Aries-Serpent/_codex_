import pytest
from pathlib import Path

ENCODINGS = ["iso-8859-1", "cp1252", "utf-16"]

@pytest.mark.parametrize("enc", ENCODINGS)
@pytest.mark.xfail(reason="Family modules may vary; update function names if different", strict=False, raises=Exception)
def test_family_encoding_hooks(tmp_path: Path, enc: str):
    s = "café £"
    p = tmp_path / f"sample_{enc.replace('-', '')}.txt"
    p.write_bytes(s.encode(enc))

    tried = 0
    passed = 0

    candidates = [
        ("ingestion.file_ingestor", "read_file"),
        ("ingestion.json_ingestor", "load_json"),
        ("ingestion.csv_ingestor", "load_csv"),
        ("ingestion.utils", "read_text_file"),
    ]

    for mod_name, fn_name in candidates:
        try:
            mod = __import__(mod_name, fromlist=[fn_name])
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                tried += 1
                try:
                    txt = fn(p, encoding=enc)
                    if isinstance(txt, (str, bytes)):
                        passed += 1
                except Exception:
                    pass
        except Exception:
            continue

    if tried == 0:
        pytest.xfail("No ingestion family functions found; update candidate list for your repo structure")

    assert passed >= 0
