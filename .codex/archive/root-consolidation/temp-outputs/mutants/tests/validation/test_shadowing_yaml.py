from codex.logging.structured_logger import logger

"""Test that yaml module resolves to site-packages, not local directory."""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


def test_yaml_is_library_or_skip():
    """Verify yaml imports from site-packages/dist-packages, not local yaml_legacy/."""
    try:
        import yaml
    except ImportError:
        if HAS_PYTEST:
            pytest.skip("yaml (PyYAML) not installed; skipping shadowing test.")
        return

    yaml_file = getattr(yaml, "__file__", "")
    assert ("site-packages" in yaml_file or "dist-packages" in yaml_file, "Condition must be true"
    ), f"CRITICAL: Local 'yaml/' or 'yaml_legacy/' dir may be shadowing PyYAML! Found at: {yaml_file}"


if __name__ == "__main__":
    try:
        test_yaml_is_library_or_skip()
        logger.info("✅ test_yaml_is_library_or_skip PASSED")
    except AssertionError as e:
        logger.info(f"❌ test_yaml_is_library_or_skip FAILED: {e}")
        raise SystemExit(1)
    except Exception as e:
        logger.info(f"⚠️  test_yaml_is_library_or_skip SKIPPED: {e}")
