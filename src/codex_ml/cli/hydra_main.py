"""Hydra CLI entrypoint for Codex training using structured configs."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from codex_ml.cli.config import AppConfig, register_configs
from codex_ml.training import run_functional_training

try:  # pragma: no cover - hydra optional at runtime
    import hydra
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - degrade gracefully when hydra missing
    hydra = None
    DictConfig = type("_DictConfig", (), {})
    OmegaConf = None


register_configs()


def _to_mapping(cfg: Any) -> Mapping[str, Any]:
    """Convert Hydra config objects to a plain mapping."""

    if OmegaConf is not None and isinstance(cfg, DictConfig):
        container = OmegaConf.to_container(cfg, resolve=True)
        if isinstance(container, Mapping):
            return container
        return {"config": container}

    if is_dataclass(cfg):
        return asdict(cfg)

    if isinstance(cfg, Mapping):
        return dict(cfg)

    return {"config": cfg}


if hydra is not None:  # pragma: no cover - executed when hydra available

    @hydra.main(version_base="1.3", config_path=None, config_name="app")
    def main(cfg: AppConfig) -> Mapping[str, Any]:
        """Hydra entrypoint that resolves configs and runs training."""

        resolved = _to_mapping(cfg)
        return run_functional_training(resolved)

else:  # pragma: no cover - hydra missing, provide informative failure

    def main(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("hydra is not available; install hydra-core to use this entrypoint")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
