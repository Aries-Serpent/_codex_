import hashlib

from codex_ml.data_utils import split_dataset


def test_split_dataset_writes_checksum(tmp_path):
    texts = ["a", "b", "c"]
    chk = tmp_path / "chk.txt"
    split_dataset(texts, checksum_path=chk)
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
    assert chk.read_text() == h.hexdigest()
