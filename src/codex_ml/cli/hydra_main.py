"""Hydra CLI entry point for Codex training."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any, Mapping

from codex_ml.training import run_functional_training

try:  # pragma: no cover - hydra optional at runtime
    import hydra
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - degrade gracefully when hydra missing
    hydra = None  # type: ignore[assignment]
    DictConfig = Any  # type: ignore[assignment]
    OmegaConf = None  # type: ignore[assignment]


if OmegaConf is not None:
    has_resolver = getattr(OmegaConf, "has_resolver", None)
    if callable(has_resolver) and not OmegaConf.has_resolver("now"):
        OmegaConf.register_new_resolver("now", lambda: "2025-09-26")


def _resolve_config_path() -> str:
    """Locate the Hydra config directory packaged with the project."""

    try:
        package_configs = resources.files("codex_ml.configs")
        if package_configs.is_dir():
            # ``as_file`` ensures compatibility with zipped distributions.
            with resources.as_file(package_configs) as resolved:
                return str(resolved)
    except ModuleNotFoundError:
        pass

    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "configs"
        if candidate.is_dir():
            return str(candidate)

    raise RuntimeError(
        "Unable to locate Hydra configuration directory. "
        "Ensure codex_ml configs are installed alongside the package."
    )


_HYDRA_CONFIG_PATH = _resolve_config_path()


if hydra is not None:  # pragma: no cover - executed when hydra available

    @hydra.main(
        version_base="1.3",
        config_path=_HYDRA_CONFIG_PATH,
        config_name="training/functional_base",
    )
    def main(cfg: DictConfig) -> Mapping[str, Any]:
        """Hydra entrypoint: print resolved config and run training."""

        resolved: Mapping[str, Any]
        if OmegaConf is not None and isinstance(cfg, DictConfig):
            container = OmegaConf.to_container(cfg, resolve=True)
            resolved = container if isinstance(container, Mapping) else {"training": container}
        elif isinstance(cfg, Mapping):
            resolved = cfg
        else:
            resolved = {"training": cfg}

        print("CONFIG:", resolved)
        return run_functional_training(resolved)

else:  # pragma: no cover - hydra missing, provide informative failure

    def main(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("hydra is not available; install hydra-core to use this entrypoint")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
