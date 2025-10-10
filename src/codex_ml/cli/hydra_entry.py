from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from codex_ml.training.unified_training import UnifiedTrainingConfig


def _print_missing(pkg: str) -> int:
    msg = {
        "ok": False,
        "reason": f"'{pkg}' is not installed; install to use Hydra-driven training.",
        "hint": "pip install hydra-core omegaconf",
    }
    print(json.dumps(msg))
    return 0


def _cfg_to_unified(cfg: Mapping[str, Any]) -> UnifiedTrainingConfig:
    from codex_ml.training.unified_training import UnifiedTrainingConfig

    train = cfg.get("train", {}) if isinstance(cfg, Mapping) else {}
    run = cfg.get("run", {}) if isinstance(cfg, Mapping) else {}
    model = cfg.get("model", {}) if isinstance(cfg, Mapping) else {}
    data_cfg = cfg.get("data", {}) if isinstance(cfg, Mapping) else {}
    tracking_cfg = cfg.get("tracking", {}) if isinstance(cfg, Mapping) else {}
    return UnifiedTrainingConfig(
        epochs=int(train.get("epochs", 1) or 1),
        grad_accum=int(train.get("grad_accum", 1) or 1),
        grad_clip_norm=train.get("grad_clip_norm"),
        seed=int(run.get("seed", 42) or 42),
        dtype=str(model.get("dtype", "fp32")),
        extra={
            "data": data_cfg,
            "tracking": tracking_cfg,
        },
    )


def main(argv=None) -> int:
    try:
        import hydra
        from omegaconf import DictConfig, OmegaConf
    except Exception:
        return _print_missing("hydra-core")

    from codex_ml.training.unified_training import run_unified_training

    @hydra.main(config_path=str(Path("configs")), config_name="defaults", version_base=None)
    def _entry(cfg: DictConfig) -> int:
        show_cfg = os.environ.get("CODEX_SHOW_CFG", "0")
        if show_cfg.lower() in {"1", "true", "yes"}:
            print(OmegaConf.to_yaml(cfg, resolve=True))
            return 0

        cfg_dict = OmegaConf.to_container(cfg, resolve=True)
        utc = _cfg_to_unified(cfg_dict if isinstance(cfg_dict, Mapping) else {})
        ndjson_env = os.environ.get("CODEX_NDJSON_LOG") or os.environ.get("CODEX_METRICS_PATH")
        ndjson_path = Path(ndjson_env or "artifacts/metrics.ndjson")
        ndjson_path.parent.mkdir(parents=True, exist_ok=True)
        result = run_unified_training(
            utc,
            callbacks=None,
            ndjson_log_path=str(ndjson_path),
        )
        print(json.dumps({"ok": True, "train_result": result, "config": asdict(utc)}))
        return 0

    overrides = list(argv or [])
    original_argv = sys.argv[:]
    if overrides:
        sys.argv = [original_argv[0] if original_argv else "codex_ml.hydra"] + overrides
    try:
        return _entry()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    sys.exit(main())
