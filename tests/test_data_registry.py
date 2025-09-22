from __future__ import annotations

import pytest

from codex_ml.data.registry import get_dataset


def test_offline_tiny_corpus_loads_from_path(tmp_path):
    data_file = tmp_path / "tiny.txt"
    data_file.write_text("alpha\nbeta\n", encoding="utf-8")

    records = get_dataset("offline:tiny-corpus", path=str(data_file), shuffle=False)
    assert records == ["alpha", "beta"]


def test_offline_tiny_corpus_missing(tmp_path, monkeypatch):
    missing = tmp_path / "missing.txt"
    monkeypatch.delenv("CODEX_ML_TINY_CORPUS_PATH", raising=False)
    monkeypatch.setenv("CODEX_ML_OFFLINE_DATASETS_DIR", str(tmp_path / "other"))

    with pytest.raises(FileNotFoundError):
        get_dataset("offline:tiny-corpus", path=str(missing))
