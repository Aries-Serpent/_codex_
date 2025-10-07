from __future__ import annotations

import hashlib
import random
from pathlib import Path

from codex_ml.data.loader import load_dataset


def _hash_list(lst):
    h = hashlib.sha256()
    for v in lst:
        h.update(v.encode("utf-8"))
    return h.hexdigest()


def test_dataset_determinism_across_runs(tmp_path: Path):
    ds = tmp_path / "data.jsonl"
    ds.write_text('{"text":"a"}\n{"text":"b"}\n{"text":"c"}\n', encoding="utf-8")
    first = load_dataset(ds, cache_dir=tmp_path)
    second = load_dataset(ds, cache_dir=tmp_path)
    assert first == second
    assert _hash_list(first) == _hash_list(second)


def test_seed_shuffle_variation():
    base = list(range(20))
    a = base[:]
    b = base[:]
    random.Random(1).shuffle(a)
    random.Random(2).shuffle(b)
    assert a != b
