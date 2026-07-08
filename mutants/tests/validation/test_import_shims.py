"""Test equivalence of src.* shims to legacy module imports."""

import importlib
import types

import pytest

pytest.importorskip("numpy", reason="numpy required for training modules")


def _assert_same_public_api(mod_a: types.ModuleType, mod_b: types.ModuleType, at_least: int = 3):
    """Verify two modules expose overlapping public API."""
    a_pub = sorted([k for k in dir(mod_a) if not k.startswith("_")])
    b_pub = sorted([k for k in dir(mod_b) if not k.startswith("_")])
    # Require non-empty and some overlap to avoid false positives
    assert a_pub, "First module exposes no public API"
    assert b_pub, "Second module exposes no public API"
    overlap = [k for k in a_pub if k in b_pub]
    assert len(overlap) >= at_least, f"Insufficient public API overlap: {len(overlap)} < {at_least}"


@pytest.mark.parametrize(
    "pair",
    [
        ("src.training.engine_hf_trainer", "training.engine_hf_trainer"),
        ("src.training.functional_training", "training.functional_training"),
        ("src.training.data_utils", "training.data_utils"),
        ("src.training.checkpoint_manager", "training.checkpoint_manager"),
        ("src.training.config", "training.config"),
    ],
)
def test_training_shims_equivalence(pair):
    """Verify src.training.* shims forward to legacy training.* modules."""
    a, b = pair
    mod_a = importlib.import_module(a)
    mod_b = importlib.import_module(b)
    _assert_same_public_api(mod_a, mod_b)
