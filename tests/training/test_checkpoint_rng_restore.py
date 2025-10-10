from __future__ import annotations

import random
from pathlib import Path

from src.codex_ml.utils.checkpoint_core import save_checkpoint, load_checkpoint


def test_rng_restore_python_random(tmp_path: Path):
    # Establish a known RNG state
    random.seed(1337)

    # Save a checkpoint which snapshots RNG
    _ck, meta = save_checkpoint(tmp_path, {"dummy": 1}, metric_value=0.0)

    # Generate the "expected" next value from the saved RNG state
    expected_next = random.random()

    # Disturb RNG with additional draws
    for _ in range(5):
        _ = random.random()

    # Restore RNG by loading with restore_rng=True
    _state, _meta = load_checkpoint(_ck, restore_rng=True)

    # After restore, the next value should match what would have been next after save
    actual_next = random.random()
    assert actual_next == expected_next