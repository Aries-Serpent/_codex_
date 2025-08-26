# BEGIN: HYDRA_CLI_MAIN
"""Hydra CLI entrypoint for codex_ml.
Supports overrides, e.g.:
  python -m codex_ml.cli.main +dry_run=true train.epochs=2 tokenizer.name=gpt2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from codex_ml.tracking.cli import add_mlflow_flags
from codex_ml.tracking.mlflow_utils import (
    MlflowConfig,
    ensure_local_artifacts,
    log_artifacts,
    log_metrics,
    log_params,
    start_run,
)

REPO = Path(__file__).resolve().parents[3]
CODEX = REPO / ".codex"
(HY_OUT := CODEX / "hydra_last").mkdir(parents=True, exist_ok=True)


def _log(msg: str) -> None:
    print(msg, flush=True)


def _save_effective_cfg(cfg: DictConfig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(OmegaConf.to_yaml(cfg))


def _dispatch_pipeline(cfg: DictConfig) -> int:
    for step in list(cfg.pipeline.steps):
        _log(f"[pipeline] step={step} dry_run={cfg.dry_run}")
        if cfg.dry_run:
            continue
        # TODO: Implement real step handlers; here we simulate success
    return 0


@hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
def main(cfg: DictConfig) -> None:
    _log("[hydra] composed config:\n" + OmegaConf.to_yaml(cfg))
    _save_effective_cfg(cfg, HY_OUT / "config.yaml")
    Path("runs").mkdir(exist_ok=True)
    if cfg.wandb.enable:
        import wandb

        wandb.init(
            project=os.getenv("WANDB_PROJECT", "codex"),
            config={"epochs": cfg.train.epochs, "lr": cfg.train.lr},
        )
    mcfg = MlflowConfig(
        enable=cfg.mlflow.enable,
        tracking_uri=cfg.mlflow.tracking_uri,
        experiment=cfg.mlflow.experiment,
    )
    with start_run(mcfg) as run:
        enabled = bool(run)
        log_params({"epochs": cfg.train.epochs, "lr": cfg.train.lr}, enabled=enabled)
        rc = _dispatch_pipeline(cfg)
        summary = {"return_code": rc}
        ensure_local_artifacts(
            HY_OUT, summary, {"train_seed": getattr(cfg.train, "seed", 0)}
        )
        log_metrics({"return_code": float(rc)}, enabled=enabled)
        if cfg.wandb.enable:
            wandb.log({"return_code": float(rc)})
            artifact = wandb.Artifact("hydra-run", type="hydra-output")
            artifact.add_dir(str(HY_OUT))
            wandb.log_artifact(artifact)
        log_artifacts(HY_OUT, enabled=enabled)
    try:
        import pynvml
        import torch

        if torch.cuda.is_available():
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            if cfg.wandb.enable:
                wandb.log({"gpu_util": util})
            log_metrics({"gpu_util": float(util)}, enabled=cfg.mlflow.enable)
    except Exception:  # noqa: BLE001
        pass
    sys.exit(rc)


def cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(add_help=False)
    add_mlflow_flags(parser)
    args, hydra_overrides = parser.parse_known_args(argv)
    hydra_overrides.extend(
        [
            f"mlflow.enable={'true' if args.mlflow_enable else 'false'}",
            f"mlflow.tracking_uri={args.mlflow_tracking_uri}",
            f"mlflow.experiment={args.mlflow_experiment}",
        ]
    )
    sys.argv = [sys.argv[0]] + hydra_overrides
    main()


if __name__ == "__main__":
    cli()
