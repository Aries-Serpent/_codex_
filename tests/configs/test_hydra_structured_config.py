from __future__ import annotations

from configs.schema import register_schema
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra


def test_register_schema_and_compose_from_dataclass() -> None:
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
