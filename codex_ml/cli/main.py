from __future__ import annotations

import sys

import hydra
from omegaconf import DictConfig, OmegaConf

try:  # best-effort imports; functions are optional
    from codex_ml.trainer import run_training  # type: ignore
except Exception:  # pragma: no cover

    def run_training(cfg):  # type: ignore
        return None


try:
    from codex_ml.eval.eval_runner import evaluate_datasets  # type: ignore
except Exception:  # pragma: no cover

    def evaluate_datasets(*args, **kwargs):  # type: ignore
        return None


@hydra.main(version_base="1.3", config_path="../../configs", config_name="config")
def main(cfg: DictConfig) -> None:  # pragma: no cover - simple dispatcher
    """Hydra CLI for Codex ML."""
    print(OmegaConf.to_yaml(cfg))
    for step in cfg.pipeline.steps:
        if step == "train":
            run_training(cfg.train)
        elif step == "evaluate":
            eval_cfg = OmegaConf.select(cfg, "eval")
            if eval_cfg is None:
                print("Eval config not found; skipping evaluate step", file=sys.stderr)
                continue
            datasets = eval_cfg.get("datasets", [])
            metrics = eval_cfg.get("metrics", [])
            output_dir = cfg.get("output_dir", "runs/eval")
            evaluate_datasets(datasets, metrics, output_dir)
    sys.exit(0)


def cli(argv: list[str] | None = None) -> None:
    if argv is not None:
        sys.argv = [sys.argv[0]] + list(argv)
    main()


if __name__ == "__main__":  # pragma: no cover
    cli()
