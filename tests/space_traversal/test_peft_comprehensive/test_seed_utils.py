from __future__ import annotations

import os
import random
from pathlib import Path

from src.training.seed_utils import set_all_seeds


def test_set_all_seeds_reproducible_python(tmp_path: Path) -> None:
    res1 = set_all_seeds(2025, deterministic=True)
    seq1 = [random.random() for _ in range(3)]

    res2 = set_all_seeds(2025, deterministic=True)
    seq2 = [random.random() for _ in range(3)]

    assert seq1 == seq2
    assert res1["PYTHONHASHSEED"] == str(2025)
    assert res2["PYTHONHASHSEED"] == str(2025)
    assert os.environ.get("PYTHONHASHSEED") == str(2025)


def test_set_all_seeds_handles_missing_torch() -> None:
    res = set_all_seeds(1337, deterministic=True)
    assert "torch" in res
