from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.data_utils import cache_tokenized


class DummyTokenizer:
    def encode(self, text: str) -> list[int]:
        return [ord(char) % 10 for char in text]


@pytest.mark.data
def test_cache_tokenized_writes_manifest(tmp_path: Path) -> None:
    dataset = ["hello", "world"]
    tokenized = cache_tokenized(dataset, DummyTokenizer(), tmp_path)
    manifest_path = tmp_path / "manifest.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest) == len(dataset)
    for entry, expected in zip(manifest, tokenized, strict=False):
        sample_file = tmp_path / entry["path"]
        if sample_file.suffix == ".pt":
            torch = pytest.importorskip("torch")
            if hasattr(torch, "load"):
                stored = torch.load(sample_file)
            else:
                stored = json.loads(sample_file.read_text(encoding="utf-8"))
        else:
            stored = json.loads(sample_file.read_text(encoding="utf-8"))
        assert stored == expected
        assert entry["sha256"]
