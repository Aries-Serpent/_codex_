import os
from contextlib import contextmanager
from pathlib import Path

from hydra import compose
from omegaconf import OmegaConf

os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")

CONF_DIR = Path(__file__).resolve().parents[2] / "src" / "hhg_logistics" / "conf"

try:
    from hydra import initialize
except ImportError:  # Fallback to stub API
    from hydra import initialize_config_dir as _initialize_config_dir

    @contextmanager
    def initialize(*, version_base: str | None = None, config_path: str) -> None:
        cfg_dir = Path(config_path)
        with _initialize_config_dir(version_base=version_base, config_dir=cfg_dir):
            yield


def test_compose_overrides():
    with initialize(version_base="1.3", config_path=str(CONF_DIR)):
        cfg = compose(config_name="config", overrides=["train.epochs=2", "model=baseline"])
    container = cfg if isinstance(cfg, dict) else OmegaConf.to_container(cfg, resolve=True)

    assert container["train"]["epochs"] == 2
    model_section = container.get("model")
    if isinstance(model_section, dict):
        assert model_section.get("type") == "BaselineModel"
    else:
        assert model_section == "baseline"
