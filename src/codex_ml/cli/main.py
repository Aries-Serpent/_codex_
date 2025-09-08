"""Hydra CLI for Codex ML.

This module dispatches pipeline steps based on a Hydra configuration. It is a
lightweight wrapper that calls the training and evaluation utilities when the
corresponding steps are present in the config. The config is composed from the
repository's ``configs`` directory by default.
"""

from __future__ import annotations

import sys
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

try:  # connect to training entry point if available
    from training.functional_training import main as _functional_training_main
except Exception:  # pragma: no cover - training optional
    _functional_training_main = None  # type: ignore[assignment]


def run_training(cfg: DictConfig | None, output_dir: str | None = None) -> None:
    """Invoke the functional training entry point with overrides from cfg.

    Parameters
    ----------
    cfg:
        Training configuration block (typically cfg.train).
    output_dir:
        Fallback path for training artifacts if not specified in ``cfg``.
    """
    if _functional_training_main is None:  # pragma: no cover - safety fallback
        raise RuntimeError("training.functional_training.main is unavailable")

    # Avoid Hydra already initialized errors between invocations in-process
    try:
        from hydra.core.global_hydra import GlobalHydra

        if GlobalHydra().is_initialized():
            GlobalHydra.instance().clear()
    except Exception:
        pass

    cfg_dict = {} if cfg is None else dict(OmegaConf.to_container(cfg, resolve=True))
    # Allow an explicit dry_run flag inside the train block to skip invoking the engine
    if cfg_dict.pop("dry_run", False):
        return

    texts = cfg_dict.pop("texts", None)
    val_texts = cfg_dict.pop("val_texts", None)
    cfg_output = cfg_dict.pop("output_dir", None) or output_dir

    # Map friendly keys to engine-specific names; pass through unknowns as-is
    mapping = {
        "epochs": "num_train_epochs",
        "lr": "learning_rate",
        "batch_size": "per_device_train_batch_size",
    }
    overrides = [f"{mapping.get(k, k)}={v}" for k, v in cfg_dict.items()]

    argv: list[str] = []
    if cfg_output:
        argv.extend(["--output-dir", str(cfg_output)])
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


_MANUAL_OVERRIDES: list[str] = []


@hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
def main(cfg: DictConfig) -> None:  # pragma: no cover - simple dispatcher
    """Dispatch pipeline steps defined in the Hydra config."""
    # Merge any manual dotlist overrides captured by the CLI wrapper
    out_dir = Path(".codex/hydra_last")
    out_dir.mkdir(parents=True, exist_ok=True)
    if _MANUAL_OVERRIDES:
        cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(_MANUAL_OVERRIDES))
    text = OmegaConf.to_yaml(cfg)
    print(text)
    (out_dir / "config.yaml").write_text(text)

    for step in getattr(cfg.pipeline, "steps", []):
        if step == "train":
            if cfg.get("dry_run"):
                continue
            run_training(cfg.get("train"), cfg.get("output_dir"))
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
    """Entry point used by console scripts.

    Supports:
      --override-file <path>   Load newline-delimited Hydra overrides from a file
      --set key value          Append a pair of Hydra overrides
    """
    global _MANUAL_OVERRIDES
    args = list(argv) if argv is not None else sys.argv[1:]
    overrides: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--override-file="):
            file = a.split("=", 1)[1]
            lines = Path(file).read_text().splitlines()
            overrides.extend(
                line.strip() for line in lines if line.strip() and not line.strip().startswith("#")
            )
            args.pop(i)
        elif a == "--override-file" and i + 1 < len(args):
            file = args[i + 1]
            lines = Path(file).read_text().splitlines()
            overrides.extend(
                line.strip() for line in lines if line.strip() and not line.strip().startswith("#")
            )
            del args[i : i + 2]
        elif a == "--set" and i + 1 < len(args):
            token = args[i + 1]
            if "=" in token or i + 2 >= len(args):
                overrides.append(token)
                del args[i : i + 2]
            else:
                key, value = token, args[i + 2]
                overrides.append(f"{key}={value}")
                del args[i : i + 3]
        else:
            i += 1
    _MANUAL_OVERRIDES = overrides
    sys.argv = [sys.argv[0]] + args
    main()


if __name__ == "__main__":  # pragma: no cover
    cli()
