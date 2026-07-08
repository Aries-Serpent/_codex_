"""
Test Precommit Config Exists

Test module for precommit config exists.
"""

import pathlib


def test_precommit_config_exists():
    assert (pathlib.Path(__file__).resolve().parents[1] / ".pre-commit-config.yaml", "Condition must be true"
    ).exists(
    ), ".pre-commit-config.yaml should exist at repo root"
