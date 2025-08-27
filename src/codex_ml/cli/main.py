# BEGIN: HYDRA_CLI_MAIN
"""Hydra CLI entrypoint for codex_ml.
Supports overrides, e.g.:
  python -m codex_ml.cli.main +dry_run=true train.epochs=2 tokenizer.name=gpt2
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:  # pragma: no cover - hydra is optional
    import hydra
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover
    hydra = None
    DictConfig = OmegaConf = None  # type: ignore

from ..tracking.cli import add_mlflow_flags
from ..tracking.mlflow_utils import (
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

            tokenizer = load_tokenizer(cfg.tokenizer.name)
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
            _save_effective_cfg(
                OmegaConf.create(state["metrics"]), HY_OUT / "metrics.yaml"
            )
        else:
            raise ValueError(f"Unknown pipeline step: {step}")
    return 0


if hydra is not None:

    @hydra.main(
        version_base="1.3", config_path="../../../configs", config_name="config"
    )
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
            log_params(
                {"epochs": cfg.train.epochs, "lr": cfg.train.lr}, enabled=enabled
            )
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

else:  # hydra missing

    def main(*args, **kwargs) -> None:  # type: ignore[unused-argument]
        _log("[hydra] missing Hydra; skipping execution")
        sys.exit(0)


def cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(add_help=False)
    add_mlflow_flags(parser)
    args, hydra_overrides = parser.parse_known_args(argv)
    if hydra is None:
        _log("[hydra] CLI no-op; Hydra not installed")
        return
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
