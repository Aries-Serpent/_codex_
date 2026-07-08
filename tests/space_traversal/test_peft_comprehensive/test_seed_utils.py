"""
pytest.importorskip("tensorboard")
Test Seed Utils

Test module for seed utils.
"""

from __future__ import annotations

import pytest

pytest.importorskip("numpy", reason="numpy required")

import os
import random
from pathlib import Path

from training.seed_utils import set_all_seeds


@pytest.fixture(autouse=True)
def isolate_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure PYTHONHASHSEED doesn't persist between tests."""
    # Save and restore PYTHONHASHSEED to prevent cross-test pollution
    original_hashseed = os.environ.get("PYTHONHASHSEED")
    yield
    # Restore original value after test
    if original_hashseed is not None:
        os.environ["PYTHONHASHSEED"] = original_hashseed
    elif "PYTHONHASHSEED" in os.environ:
        del os.environ["PYTHONHASHSEED"]


def test_set_all_seeds_reproducible_python(tmp_path: Path) -> None:
    res1 = set_all_seeds(2025, deterministic=True)
    seq1 = [random.random() for _ in range(3)]

    res2 = set_all_seeds(2025, deterministic=True)
    seq2 = [random.random() for _ in range(3)]

    assert seq1 == seq2, "seq1 is not valid"
    assert res1["PYTHONHASHSEED"] == str(2025), "Condition must be true"
    assert res2["PYTHONHASHSEED"] == str(2025), "Condition must be true"
    assert os.environ.get("PYTHONHASHSEED") == str(2025), "Condition must be true"


def test_set_all_seeds_handles_missing_torch() -> None:
    res = set_all_seeds(1337, deterministic=True)
    assert "torch" in res, "Condition must be true"
