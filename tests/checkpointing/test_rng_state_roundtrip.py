from __future__ import annotations

import random

from codex_ml.utils import checkpoint_core


def test_rng_state_roundtrip() -> None:
    random.seed(1234)
    state = checkpoint_core.capture_rng_state()
    seq1 = [random.random() for _ in range(5)]
    checkpoint_core.restore_rng_state(state)
    seq2 = [random.random() for _ in range(5)]
    assert seq1 == seq2
