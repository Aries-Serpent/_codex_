"""Hydra CLI for Codex ML.

This module dispatches pipeline steps based on a Hydra configuration. It is a
lightweight wrapper that calls the training and evaluation utilities when the
corresponding steps are present in the config. The config is composed from the
repository's ``configs`` directory by default.
"""

from __future__ import annotations

import sys

import hydra
from omegaconf import DictConfig, OmegaConf

try:  # connect to training entry point if available
    from training.functional_training import main as _functional_training_main
except Exception:  # pragma: no cover - training optional
    _functional_training_main = None


def run_training(cfg: DictConfig | None) -> None:
    """Invoke the functional training entry point with overrides from cfg."""
    if _functional_training_main is None:  # pragma: no cover - safety fallback
        raise RuntimeError("training.functional_training.main is unavailable")

    cfg_dict = (
        {} if cfg is None else dict(OmegaConf.to_container(cfg, resolve=True))
    )
    texts = cfg_dict.pop("texts", None)
    val_texts = cfg_dict.pop("val_texts", None)
    overrides = [f"training.{k}={v}" for k, v in cfg_dict.items()]

    argv: list[str] = []
    if texts:
        argv.extend(["--texts", *[str(t) for t in texts]])
    if val_texts:
        argv.extend(["--val-texts", *[str(t) for t in val_texts]])
    if overrides:
        argv.extend(["--cfg-override", *overrides])

    _functional_training_main(argv)


try:  # pragma: no cover - evaluation is optional
    from codex_ml.eval.eval_runner import evaluate_datasets  # type: ignore
except Exception:  # pragma: no cover

    def evaluate_datasets(*args, **kwargs):  # type: ignore
        return None


@hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
def main(cfg: DictConfig) -> None:  # pragma: no cover - simple dispatcher
    """Dispatch pipeline steps defined in the Hydra config."""
    print(OmegaConf.to_yaml(cfg))
    for step in cfg.pipeline.steps:
        if step == "train":
            run_training(cfg.train)
        elif step == "evaluate":
            eval_cfg = OmegaConf.select(cfg, "eval")
            if eval_cfg is None:
                print(
                    "Eval config not found; skipping evaluate step",
                    file=sys.stderr,
                )
                continue
            datasets = eval_cfg.get("datasets", [])
            metrics = eval_cfg.get("metrics", [])
            output_dir = cfg.get("output_dir", "runs/eval")
            evaluate_datasets(datasets, metrics, output_dir)
    sys.exit(0)


def cli(argv: list[str] | None = None) -> None:
    """Entry point used by console scripts."""
    if argv is not None:
        sys.argv = [sys.argv[0]] + list(argv)
    main()


if __name__ == "__main__":  # pragma: no cover
    cli()
