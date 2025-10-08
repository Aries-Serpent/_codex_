from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _print_missing(pkg: str) -> int:
    msg = {
        "ok": False,
        "reason": f"'{pkg}' is not installed; install to use Hydra-driven training.",
        "hint": "pip install hydra-core omegaconf",
    }
    print(json.dumps(msg))
    return 0


def main(argv=None) -> int:
    try:
        import hydra
        from omegaconf import DictConfig, OmegaConf
    except Exception:
        return _print_missing("hydra-core")

    from codex_ml.training.unified_training import (
        UnifiedTrainingConfig,
        run_unified_training,
    )

    @hydra.main(config_path=str(Path("configs")), config_name="defaults", version_base=None)
    def _entry(cfg: DictConfig) -> int:
        if os.environ.get("CODEX_SHOW_CFG") == "1":
            print(OmegaConf.to_yaml(cfg, resolve=True))

        ut = UnifiedTrainingConfig(
            seed=cfg.get("run", {}).get("seed", 42),
            epochs=cfg.get("train", {}).get("epochs", 1),
            extra={"hydra_cfg": OmegaConf.to_container(cfg, resolve=True)},
        )
        ndjson_path = Path(os.environ.get("CODEX_METRICS_PATH", "artifacts/metrics.ndjson"))
        ndjson_path.parent.mkdir(parents=True, exist_ok=True)

        status = run_unified_training(
            cfg=ut,
            callbacks=None,
            ndjson_log_path=str(ndjson_path),
        )
        print(json.dumps({"ok": True, "status": status}))
        return int(status or 0)

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
