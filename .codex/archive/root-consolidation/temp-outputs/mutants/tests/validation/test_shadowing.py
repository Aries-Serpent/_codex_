"""
Test Shadowing

Test module for shadowing.
"""

import sys

import pytest


def test_hydra_resolves_to_site_packages():
    """
    Verify that 'import hydra' resolves to the installed hydra-core package
    from site-packages (or dist-packages), not a local directory.

    This test ensures the repository root does not contain a 'hydra/' directory
    that would shadow the installed package.
    """
    try:
        sys.modules.pop("hydra", None)
        import hydra
    except ImportError:
        pytest.skip("hydra-core not installed; skipping shadowing test.")
    else:
        hydra_file = getattr(hydra, "__file__", "")

        # Accept both site-packages and dist-packages (common on Debian-based systems)
        is_from_package_manager = "site-packages" in hydra_file or "dist-packages" in hydra_file

        assert is_from_package_manager, (
            f"CRITICAL: Local 'hydra/' directory is shadowing the installed hydra-core package!\n"
            f"  Expected: hydra to be loaded from site-packages or dist-packages\n"
            f"  Actual location: {hydra_file}\n"
            f"  Remediation: Ensure no 'hydra/' directory exists at repository root.\n"
            f"               The legacy shim has been moved to 'config_legacy/'."
        )


def test_yaml_resolves_to_site_packages():
    """
    Verify that 'import yaml' resolves to the installed PyYAML package
    from site-packages, not a local directory.
    """
    try:
        sys.modules.pop("yaml", None)
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed; skipping yaml shadowing test.")
    else:
        yaml_file = getattr(yaml, "__file__", "")

        # Accept both site-packages and dist-packages
        is_from_package_manager = "site-packages" in yaml_file or "dist-packages" in yaml_file

        assert is_from_package_manager, (
            f"CRITICAL: Local 'yaml/' directory is shadowing the installed PyYAML package!\n"
            f"  Expected: yaml to be loaded from site-packages or dist-packages\n"
            f"  Actual location: {yaml_file}\n"
            f"  Remediation: Ensure no 'yaml/' directory exists at repository root.\n"
            f"               Any legacy yaml module should be moved to 'yaml_legacy/'."
        )
