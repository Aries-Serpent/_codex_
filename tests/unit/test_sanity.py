def test_sanity():
    # Minimal gating test to validate setup
    assert 1 + 1 == 2


def test_package_import():
    try:
        import hhg_logistics
    except Exception as e:
        raise AssertionError(f"Failed to import package: {e}") from e
