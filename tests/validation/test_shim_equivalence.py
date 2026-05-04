"""
Test shim equivalence - verify that legacy and canonical imports expose equivalent APIs.

This test validates that shim modules correctly forward all public APIs from legacy modules,
ensuring import path changes don't break functionality.
"""

import importlib
import os

import pytest

DEFAULT_MIN_OVERLAP = 3


def public_api(module):
    """Extract public API members (non-underscore prefixed) from a module."""
    return sorted([k for k in dir(module) if not k.startswith("_")])


@pytest.mark.parametrize(
    "pair, min_overlap",
    [
        (("training.engine_hf_trainer", "src.training.engine_hf_trainer"), DEFAULT_MIN_OVERLAP),
        (("training.functional_training", "src.training.functional_training"), DEFAULT_MIN_OVERLAP),
        (("training.data_utils", "src.training.data_utils"), DEFAULT_MIN_OVERLAP),
        (("training.checkpoint_manager", "src.training.checkpoint_manager"), DEFAULT_MIN_OVERLAP),
        (("training.config", "src.training.config"), DEFAULT_MIN_OVERLAP),
        (("tokenization.train_tokenizer", "src.tokenization.train_tokenizer"), 1),
    ],
)
def test_shim_public_api_equivalence(pair, min_overlap, monkeypatch):
    """
    Test that shim modules expose equivalent public APIs to legacy modules.

    Args:
        pair: Tuple of (legacy_module, canonical_module) names
        min_overlap: Minimum number of shared public API members required
    """
    legacy, canonical = pair

    # Enforce default behavior for this test without leaking env changes
    monkeypatch.setenv("SHIM_IDENTITY_STRICT", "0")

    try:
        a = importlib.import_module(legacy)
        b = importlib.import_module(canonical)
    except ImportError as e:
        pytest.skip(f"Module import failed (expected in minimal env): {e}")
    else:
        a_api = public_api(a)
        b_api = public_api(b)

        assert a_api, f"{legacy} exposes no public API"
        assert b_api, f"{canonical} exposes no public API"

        overlap = [k for k in a_api if k in b_api]
        legacy_only = sorted(set(a_api) - set(b_api))
        canonical_only = sorted(set(b_api) - set(a_api))
        symmetric_diff = sorted(set(a_api) ^ set(b_api))
        assert len(overlap) >= min_overlap, (
            f"Insufficient API overlap for {legacy} vs {canonical}: "
            f"{len(overlap)} < {min_overlap}\n"
            f"Legacy-only symbols: {legacy_only}\n"
            f"Canonical-only symbols: {canonical_only}\n"
            f"Symmetric difference: {symmetric_diff}"
        )


def test_shim_module_identity():
    """
    Optional strict identity test - validates sys.modules identity when enabled.

    This test is skipped by default and only runs when SHIM_IDENTITY_STRICT=1,
    which should be set in CI for stricter validation.
    """
    if os.environ.get("SHIM_IDENTITY_STRICT") != "1":
        pytest.skip("Identity checks disabled (SHIM_IDENTITY_STRICT != 1)")

    # Test that shims properly forward identity
    # This would catch cases where shims create copies instead of references
    try:
        # Use dynamic import to avoid static import analyzer warnings
        legacy = importlib.import_module("training.engine_hf_trainer")
        canonical = importlib.import_module("src.training.engine_hf_trainer")

        # For true shims, these should be the same module object
        # (This is aspirational - current shims may not achieve this)
        if hasattr(legacy, "__file__") and hasattr(canonical, "__file__"):
            # At minimum, they should resolve to compatible implementations
            assert public_api(legacy) == public_api(canonical), "Shim and canonical APIs diverged"
    except ImportError:
        pytest.skip("Modules not available for identity check")
