import pytest

def test_hydra_is_library_or_skip():
    try:
        import hydra
    except ImportError:
        pytest.skip("hydra-core not installed; skipping shadowing test.")
        return
    assert "site-packages" in getattr(hydra, "__file__", ""), "CRITICAL: Local 'hydra/' dir is shadowing PyPI package!"
