"""
Test Reproducibility Utils

Test module for reproducibility utils.
"""

from codex_ml.utils import reproducibility as repro


def test_set_global_seed_sets_env_and_is_idempotent(monkeypatch):
    monkeypatch.setenv("CODEX_GLOBAL_SEED", "unset")
    cfg1 = repro.set_global_seed(123, set_env=True)
    cfg2 = repro.set_global_seed(123, set_env=True)

    assert cfg1.seed == cfg2.seed == 123, "seed is not valid"
    assert "CODEX_GLOBAL_SEED" in __import__("os").environ, "Condition must be true"
    assert __import__("os").environ["CODEX_GLOBAL_SEED"] == "123", "__imp is not valid"


def test_capture_rng_snapshot_has_expected_keys():
    snapshot = repro.capture_rng_snapshot()
    assert "env_seed" in snapshot, "Condition must be true"
    assert "random_state_hint" in snapshot, "Condition must be true"
    assert "numpy_state_hint" in snapshot, "Condition must be true"
    assert "torch_rng_hint" in snapshot, "Condition must be true"
