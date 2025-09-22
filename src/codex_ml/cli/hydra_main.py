"""Hydra CLI entry point for Codex training."""

from __future__ import annotations

from typing import Any, Dict

from codex_ml.training import run_functional_training

try:  # pragma: no cover - hydra optional at runtime
    import hydra
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - degrade gracefully when hydra missing
    hydra = None  # type: ignore[assignment]
    DictConfig = Any  # type: ignore[assignment]
    OmegaConf = None  # type: ignore[assignment]


def _prepare_training_cfg(cfg: DictConfig | Dict[str, Any]) -> Dict[str, Any]:
    if OmegaConf is not None and isinstance(cfg, DictConfig):  # type: ignore[arg-type]
        container = OmegaConf.to_container(cfg, resolve=True)  # type: ignore[union-attr]
    else:
        container = cfg  # type: ignore[assignment]
    if isinstance(container, dict):
        training_section = container.get("training")
        if isinstance(training_section, dict):
            return training_section
    return container if isinstance(container, dict) else {}


if hydra is not None:  # pragma: no cover - executed when hydra available

    @hydra.main(
        version_base="1.3",
        config_path="../../../configs",
        config_name="training/functional_base",
    )
    def main(cfg: DictConfig) -> None:
        """Hydra entrypoint: convert DictConfig into mapping and run training."""

        training_cfg = _prepare_training_cfg(cfg)
        run_functional_training(training_cfg)

else:  # pragma: no cover - hydra missing, provide informative failure

    def main(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("hydra is not available; install hydra-core to use this entrypoint")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
