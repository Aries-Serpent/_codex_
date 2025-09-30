import os
import json
import random
from pathlib import Path

import pytest


def test_rng_roundtrip(tmp_path: Path):
    # Import lazily to avoid hard dependency on torch/numpy in environments
    # where those packages are not present.
    from codex_utils import repro

    # 1) Set a seed and capture initial samples
    state = repro.set_seed(1234, deterministic=True)
    seq1 = [random.random() for _ in range(3)]
    try:
        import numpy as np  # type: ignore

        np_seq1 = np.random.rand(3).tolist()
    except Exception:
        np_seq1 = None

    # 2) Save the RNG state to disk
    out = tmp_path / "rng.json"
    repro.save_rng(str(out), state)
    assert out.exists(), "RNG state file was not written"
    assert json.loads(out.read_text(encoding="utf-8")).get("py_random_state") is not None

    # 3) Mutate RNG streams
    _ = [random.random() for _ in range(5)]
    try:
        import numpy as np  # type: ignore

        _ = np.random.rand(5).tolist()
    except Exception:
        pass

    # 4) Restore RNG and re-sample; sequences should match
    restored = repro.load_rng(str(out))
    repro.restore_rng(restored)
    seq2 = [random.random() for _ in range(3)]
    assert seq1 == seq2, "Python RNG did not restore deterministically"
    try:
        import numpy as np  # type: ignore

        np_seq2 = np.random.rand(3).tolist()
    except Exception:
        np_seq2 = None
    if np_seq1 is not None and np_seq2 is not None:
        assert np_seq1 == np_seq2, "NumPy RNG did not restore deterministically"

