"""Hydra CLI entrypoint for Codex training using structured configs."""

from __future__ import annotations

import argparse
import json
import logging
import platform
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from codex_ml.cli.config import AppConfig, register_configs
from codex_ml.training import run_functional_training

try:
    from codex_ml import distributed as _distributed  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - safe fallback

    def init_distributed_if_needed(*_args, **_kwargs):  # type: ignore[return-value]
        return False

    def cleanup_distributed() -> None:  # type: ignore[return-value]
        return None

else:  # pragma: no cover - executed when distributed helpers are available
    init_distributed_if_needed = _distributed.init_distributed_if_needed  # type: ignore[attr-defined]
    cleanup_distributed = _distributed.cleanup  # type: ignore[attr-defined]


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


def _probe_payload() -> dict[str, Any]:
    ok = hydra is not None
    reason = None if ok else "hydra-missing"
    return {
        "ok": ok,
        "reason": reason,
        "component": "codex-train",
        "python": ".".join(map(str, sys.version_info[:3])),
        "platform": platform.platform(),
    }


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
    def _hydra_entry(cfg: AppConfig) -> Mapping[str, Any]:
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
            initialized = False
            result = None
            try:
                initialized = bool(init_distributed_if_needed())
                if not initialized:
                    sys.stderr.write(
                        "[codex-ddp] disabled (env not set or torch.distributed unavailable)\n"
                    )
                result = run_functional_training(resolved)
            finally:
                if initialized:
                    cleanup_distributed()
            log_event(
                logger,
                "cli.finish",
                prog=sys.argv[0],
                status="ok",
                exit_status="success",
            )
            return result

else:  # pragma: no cover - hydra missing, provide informative failure
    _hydra_entry = None  # type: ignore[assignment]


def _hydra_missing_main(args: Sequence[str], prog: str) -> int:
    guidance = (
        "hydra-core is required for codex-train; "
        "install it with `pip install hydra-core` before running."
    )
    logger = init_json_logging()
    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=prog, args=list(args))
        print(guidance, file=sys.stderr)
        log_event(
            logger,
            "cli.finish",
            prog=prog,
            status="ok",
            exit_code=0,
            reason="hydra-core missing",
        )
        return 0


def main(argv: Sequence[str] | None = None) -> Any:
    parser_cls = ArgparseJSONParser if ArgparseJSONParser is not None else argparse.ArgumentParser
    parser = parser_cls(prog="codex-train", add_help=False)
    parser.add_argument("--probe-json", action="store_true", help=argparse.SUPPRESS)

    arg_list = list(argv) if argv is not None else sys.argv[1:]
    namespace, remaining = parser.parse_known_args(arg_list)

    if namespace.probe_json:
        logger = init_json_logging()
        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=parser.prog, args=arg_list)
            print(json.dumps(_probe_payload()))
            log_event(
                logger,
                "cli.finish",
                prog=parser.prog,
                status="ok",
                mode="probe-json",
                rc=0,
            )
            return 0

    prog_name = sys.argv[0] if argv is None else parser.prog
    if hydra is None or _hydra_entry is None:
        return _hydra_missing_main(remaining, prog_name)

    backup_argv = sys.argv[:]
    try:
        sys.argv = [prog_name, *remaining]
        return _hydra_entry()  # type: ignore[misc]
    finally:
        sys.argv = backup_argv


if __name__ == "__main__":  # pragma: no cover - CLI entry
    result = main()
    if isinstance(result, int):
        raise SystemExit(result)
