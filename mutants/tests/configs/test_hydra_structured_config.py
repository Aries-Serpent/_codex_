"""
Test Hydra Structured Config

Test module for hydra structured config.
"""

from __future__ import annotations

import pytest

pytest.importorskip("hydra")
pytest.importorskip("hydra.core")


def test_register_schema_and_compose_from_dataclass() -> None:
    from configs.schemas import register_schema
    from hydra import compose, initialize
    from hydra.core.global_hydra import GlobalHydra

    global_hydra = GlobalHydra.instance()
    checker = getattr(global_hydra, "is_initialized", None)
    if callable(checker):
        if checker():
            global_hydra.clear()
    elif getattr(global_hydra, "initialized", False):
        global_hydra.clear()

    register_schema(name="app_schema_test")
    with initialize(version_base=None):
        cfg = compose(config_name="app_schema_test", overrides=["data.dataset_name=demo"])

    assert cfg.data.dataset_name == "demo"
    assert cfg.train.seed == 1337
