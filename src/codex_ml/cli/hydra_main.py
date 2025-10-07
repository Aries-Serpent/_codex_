"""Hydra CLI entrypoint for Codex training using structured configs."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import logging
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

from codex_ml.cli.config import AppConfig, register_configs
from codex_ml.training import run_functional_training
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = (ArgparseJSONParser, run_cmd)

try:  # pragma: no cover - hydra optional at runtime
    import hydra
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - degrade gracefully when hydra missing
    hydra = None
    DictConfig = type("_DictConfig", (), {})
    OmegaConf = None


register_configs()


LOGGER = logging.getLogger(__name__)


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


def _load_yaml_defaults() -> Mapping[str, Any]:
    if OmegaConf is None:
        return {}
    config_dir = Path(__file__).resolve().parents[2] / "configs"
    default_yaml = config_dir / "default.yaml"
    if not default_yaml.is_file():
        return {}
    try:
        loaded = OmegaConf.load(str(default_yaml))  # type: ignore[no-untyped-call]
        container = OmegaConf.to_container(loaded, resolve=True)
        if isinstance(container, Mapping):
            return container
    except Exception:
        LOGGER.debug("Failed to load YAML defaults from %s", default_yaml, exc_info=True)
    return {}


if hydra is not None:  # pragma: no cover - executed when hydra available

    @hydra.main(version_base="1.3", config_path=None, config_name="app")
    def main(cfg: AppConfig) -> Mapping[str, Any]:
        """Hydra entrypoint that resolves configs and runs training."""

        logger = init_json_logging()
        arg_list = sys.argv[1:]
        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)

            resolved = _to_mapping(cfg)
            defaults = _load_yaml_defaults()
            if defaults:
                try:
                    defaults_cfg = OmegaConf.create(defaults)  # type: ignore[no-untyped-call]
                    resolved_cfg = OmegaConf.create(resolved)
                    merged_cfg = OmegaConf.merge(defaults_cfg, resolved_cfg)
                    resolved = OmegaConf.to_container(merged_cfg, resolve=True)  # type: ignore[assignment]
                except Exception:
                    LOGGER.debug("Hydra defaults merge failed", exc_info=True)
                    combined = dict(defaults)
                    combined.update(dict(resolved))
                    resolved = combined
            result = run_functional_training(resolved)
            log_event(
                logger,
                "cli.finish",
                prog=sys.argv[0],
                status="ok",
                exit_status="success",
            )
            return result

else:  # pragma: no cover - hydra missing, provide informative failure

    def main(argv: Sequence[str] | None = None) -> int:
        guidance = "hydra-core is required for codex-train; install it with `pip install hydra-core` before running."
        logger = init_json_logging()
        arg_list = list(argv) if argv is not None else sys.argv[1:]

        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
            if any(flag in arg_list for flag in ("-h", "--help")) or not arg_list:
                print(guidance, file=sys.stderr)
                log_event(logger, "cli.finish", prog=sys.argv[0], status="ok", exit_code=0)
                raise SystemExit(0)
            log_event(logger, "cli.finish", prog=sys.argv[0], status="error", exit_code=1)
            raise RuntimeError(guidance)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    result = main()
    if isinstance(result, int):
        raise SystemExit(result)
