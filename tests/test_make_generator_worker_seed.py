from __future__ import annotations

import random

import pytest

from codex_ml.training.dataloader_utils import make_generator, seed_worker


def test_seed_worker_sets_random_seed(monkeypatch):
    original_state = random.getstate()
    try:
        monkeypatch.setattr(random, "getrandbits", lambda _: 123456)
        seed_worker(0)
        assert random.random() == pytest.approx(0.8056271362589)
    finally:
        random.setstate(original_state)


def test_make_generator_reproducible():
    torch = pytest.importorskip("torch", reason="torch is required for this test")

    generator_a = make_generator(9876)
    generator_b = make_generator(9876)

    assert generator_a is not None
    assert generator_b is not None

    seq_a = torch.randint(0, 1000, (3,), generator=generator_a)
    seq_b = torch.randint(0, 1000, (3,), generator=generator_b)
    assert torch.equal(seq_a, seq_b)
