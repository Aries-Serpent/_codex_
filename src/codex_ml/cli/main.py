# BEGIN: HYDRA_CLI_MAIN
"""Hydra CLI entrypoint for codex_ml.
Supports overrides, e.g.:
  python -m codex_ml.cli.main +dry_run=true train.epochs=2 tokenizer.name=gpt2
"""

from __future__ import annotations

import argparse
import contextlib
import os
import sys
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from codex_ml.config_schema import validate_config
from codex_ml.tracking.cli import add_mlflow_flags
from codex_ml.tracking.mlflow_utils import (
    ensure_local_artifacts,
    log_artifacts,
    log_metrics,
    log_params,
    start_run,
)
from codex_ml.utils.provenance import snapshot_hydra_config

REPO = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO / "configs"
CODEX = REPO / ".codex"
(HY_OUT := CODEX / "hydra_last").mkdir(parents=True, exist_ok=True)


def _log(msg: str) -> None:
    print(msg, flush=True)


def _save_effective_cfg(cfg: DictConfig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(OmegaConf.to_yaml(cfg))


def _dispatch_pipeline(cfg: DictConfig) -> int:
    """Execute pipeline steps defined in the Hydra config.

    This is a lightweight orchestration layer that mirrors the behaviour of
    ``scripts/deploy_codex_pipeline.py`` but driven entirely via Hydra.  The
    steps are intentionally simple and operate on in-memory toy data so that
    the CLI remains self‑contained for testing purposes.
    """

    # Local state passed between steps
    state: dict[str, object] = {}

    for step in list(cfg.pipeline.steps):
        _log(f"[pipeline] step={step} dry_run={cfg.dry_run}")
        if cfg.dry_run:
            continue
        if step == "load_data":
            # Minimal synthetic dataset reused across stages
            state["corpus"] = ["def add(a,b): return a+b", "print('hi')"]
            state["demos"] = [{"prompt": "p1", "completion": "c1"}]
            state["prefs"] = [("p1", "good", "bad", 1)]
        elif step == "tokenize":
            from codex_ml.tokenization import load_tokenizer

            tokenizer = load_tokenizer(
                cfg.tokenizer.name, use_fast=cfg.tokenizer.get("use_fast", True)
            )
            state["tokenizer"] = tokenizer
        elif step == "train":
            from functional_training import run_functional_training

            summary = run_functional_training(
                state.get("corpus", []),
                state.get("demos", []),
                state.get("prefs", []),
                tokenizer=state.get("tokenizer"),
            )
            state["train_summary"] = summary
        elif step == "evaluate":
            summary = state.get("train_summary", {})
            losses = summary.get("losses", []) if isinstance(summary, dict) else []
            if losses:
                avg_loss = float(sum(losses) / len(losses))
            else:
                avg_loss = float("nan")
            state["metrics"] = {"avg_loss": avg_loss}
            _save_effective_cfg(OmegaConf.create(state["metrics"]), HY_OUT / "metrics.yaml")
        else:
            raise ValueError(f"Unknown pipeline step: {step}")
    return 0


@hydra.main(version_base="1.3", config_path=str(CONFIG_DIR), config_name="config")
def main(cfg: DictConfig) -> None:
    validate_config(OmegaConf.to_container(cfg, resolve=True))
    _log("[hydra] composed config:\n" + OmegaConf.to_yaml(cfg))
    _save_effective_cfg(cfg, HY_OUT / "config.yaml")
    try:
        from hydra.core.hydra_config import HydraConfig

        runtime_dir = Path(HydraConfig.get().runtime.output_dir)
        snapshot_hydra_config(cfg, runtime_dir, HydraConfig.get().overrides.task)
    except Exception:  # pragma: no cover - HydraConfig may be unavailable
        snapshot_hydra_config(cfg, HY_OUT)
    Path("runs").mkdir(exist_ok=True)
    if cfg.wandb.enable:
        import wandb

        wandb.init(
            project=os.getenv("WANDB_PROJECT", "codex"),
            config={"epochs": cfg.train.epochs, "lr": cfg.train.lr},
        )
    run_ctx = (
        start_run(cfg.mlflow.experiment, cfg.mlflow.tracking_uri)
        if cfg.mlflow.enable
        else contextlib.nullcontext(None)
    )
    with run_ctx as run:
        enabled = run is not None
        log_params({"epochs": cfg.train.epochs, "lr": cfg.train.lr}, enabled=enabled)
        if cfg.get("symbolic_pipeline") and cfg.symbolic_pipeline.enabled:
            _log("[symbolic_pipeline] enabled but not implemented")
        rc = _dispatch_pipeline(cfg)
        summary = {"return_code": rc}
        ensure_local_artifacts(HY_OUT, summary, {"train_seed": getattr(cfg.train, "seed", 0)})
        log_metrics({"return_code": float(rc)}, step=0, enabled=enabled)
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
            log_metrics({"gpu_util": float(util)}, step=0, enabled=cfg.mlflow.enable)
    except Exception:  # noqa: BLE001
        pass
    sys.exit(rc)


def cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(add_help=False)
    add_mlflow_flags(parser)
    parser.add_argument("--override-file", type=str, default=None)
    parser.add_argument(
        "--set",
        dest="sets",
        action="append",
        default=[],
        help="Repeatable key=value overrides",
    )
    args, hydra_overrides = parser.parse_known_args(argv)
    if args.override_file:
        for line in Path(args.override_file).read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                hydra_overrides.append(line)
    for kv in args.sets:
        hydra_overrides.append(kv)
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
