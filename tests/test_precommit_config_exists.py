import pathlib


def test_precommit_config_exists():
    assert (
        pathlib.Path(__file__).resolve().parents[1] / ".pre-commit-config.yaml"
    ).exists(), ".pre-commit-config.yaml should exist at repo root"
