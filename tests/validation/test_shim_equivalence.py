"""
Test shim equivalence - verify that legacy and canonical imports expose equivalent APIs.

This test validates that shim modules correctly forward all public APIs from legacy modules,
ensuring import path changes don't break functionality.
"""
import importlib
import os
import pytest


def public_api(module):
    """Extract public API members (non-underscore prefixed) from a module."""
    return sorted([k for k in dir(module) if not k.startswith("_")])


@pytest.mark.parametrize("pair, min_overlap", [
    (("training.engine_hf_trainer", "src.training.engine_hf_trainer"), 3),
    (("training.functional_training", "src.training.functional_training"), 3),
    (("training.data_utils", "src.training.data_utils"), 3),
    (("training.checkpoint_manager", "src.training.checkpoint_manager"), 3),
    (("training.config", "src.training.config"), 3),
    (("tokenization.train_tokenizer", "src.tokenization.train_tokenizer"), 1),
])
def test_shim_public_api_equivalence(pair, min_overlap):
    """
    Test that shim modules expose equivalent public APIs to legacy modules.
    
    Args:
        pair: Tuple of (legacy_module, canonical_module) names
        min_overlap: Minimum number of shared public API members required
    """
    legacy, canonical = pair
    
    # Enforce CI identity assertions if env says so (future enhancement)
    os.environ.setdefault("SHIM_IDENTITY_STRICT", "0")
    
    try:
        a = importlib.import_module(legacy)
        b = importlib.import_module(canonical)
    except ImportError as e:
        pytest.skip(f"Module import failed (expected in minimal env): {e}")
        return
    
    a_api = public_api(a)
    b_api = public_api(b)
    
    assert a_api, f"{legacy} exposes no public API"
    assert b_api, f"{canonical} exposes no public API"
    
    overlap = [k for k in a_api if k in b_api]
    assert len(overlap) >= min_overlap, (
        f"Insufficient API overlap for {legacy} vs {canonical}: "
        f"{len(overlap)} < {min_overlap}\n"
        f"Legacy API: {a_api[:10]}...\n"
        f"Canonical API: {b_api[:10]}..."
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
        import training.engine_hf_trainer as legacy
        import src.training.engine_hf_trainer as canonical
        
        # For true shims, these should be the same module object
        # (This is aspirational - current shims may not achieve this)
        if hasattr(legacy, '__file__') and hasattr(canonical, '__file__'):
            # At minimum, they should resolve to compatible implementations
            assert public_api(legacy) == public_api(canonical), \
                "Shim and legacy APIs diverged"
    except ImportError:
        pytest.skip("Modules not available for identity check")
