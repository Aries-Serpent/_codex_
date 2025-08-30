import importlib.util
import pytest

from ingestion.utils import read_text


@pytest.mark.skipif(
    importlib.util.find_spec("charset_normalizer") is None,
    reason="charset_normalizer missing",
)
@pytest.mark.xfail(reason="encoding detection may vary across platforms")
def test_read_text_auto(tmp_path):
    text = "café £"
    p = tmp_path / "sample.txt"
    p.write_bytes(text.encode("cp1252"))
    out = read_text(p, encoding="auto")
    assert isinstance(out, str) and out
