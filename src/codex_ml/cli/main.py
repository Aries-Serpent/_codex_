"""Hydra CLI for Codex ML.

This module dispatches pipeline steps based on a Hydra configuration. It is a
lightweight wrapper that calls the training and evaluation utilities when the
corresponding steps are present in the config. The config is composed from the
repository's ``configs`` directory by default.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

import hydra
from omegaconf import DictConfig, OmegaConf

try:  # pragma: no cover - optional dependency
    from codex_digest.error_capture import log_error as _log_error
except Exception:  # pragma: no cover

    def _log_error(step_no: str, step_desc: str, msg: str, ctx: str) -> None:  # type: ignore[func-returns-value]
        """Fallback logger if codex_digest is not available."""
        return None


try:  # connect to training entry point if available
    from training.codex.training import main as _functional_training_main
except Exception:  # pragma: no cover - training optional
    _functional_training_main = None


def run_training(cfg: DictConfig | None, output_dir: str | None = None) -> None:
    """Invoke the functional training entry point with overrides from cfg.

    Parameters
    ----------
    cfg:
        Training configuration block.
    output_dir:
        Fallback path for training artifacts if not specified in ``cfg``.
    """
    if _functional_training_main is None:  # pragma: no cover - safety fallback
        raise RuntimeError("training.codex.training.main is unavailable")

    try:
        from hydra.core.global_hydra import GlobalHydra

        if GlobalHydra().is_initialized():
            GlobalHydra.instance().clear()
    except Exception:
        pass

    cfg_dict = {} if cfg is None else dict(OmegaConf.to_container(cfg, resolve=True))
    texts = cfg_dict.pop("texts", None)
    val_texts = cfg_dict.pop("val_texts", None)
    cfg_output = cfg_dict.pop("output_dir", None) or output_dir

    def _flatten(prefix: str, obj: Any) -> Iterable[tuple[str, Any]]:
        if isinstance(obj, dict):
            for ik, iv in obj.items():
                new_prefix = f"{prefix}.{ik}" if prefix else ik
                yield from _flatten(new_prefix, iv)
        else:
            yield prefix, obj

    overrides = [f"{key}={json.dumps(val)}" for key, val in _flatten("training", cfg_dict)]

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


@hydra.main(version_base="1.3", config_path="../../../configs", config_name="config")
def main(cfg: DictConfig) -> None:  # pragma: no cover - simple dispatcher
    """Dispatch pipeline steps defined in the Hydra config."""
    text = OmegaConf.to_yaml(cfg)
    print(text)
    out_dir = Path(".codex/hydra_last")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.yaml").write_text(text)
    for step in cfg.pipeline.steps:
        if step == "train":
            if cfg.get("dry_run"):
                continue
            run_training(cfg.train, cfg.get("output_dir"))
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
    args = list(argv) if argv is not None else sys.argv[1:]
    overrides: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--override-file="):
            file = a.split("=", 1)[1]
            overrides.extend(Path(file).read_text().splitlines())
            args.pop(i)
        elif a == "--override-file" and i + 1 < len(args):
            file = args[i + 1]
            overrides.extend(Path(file).read_text().splitlines())
            del args[i : i + 2]
        elif a == "--set" and i + 2 < len(args):
            overrides.extend(args[i + 1 : i + 3])
            del args[i : i + 3]
        else:
            i += 1
    sys.argv = [sys.argv[0]] + args + overrides
    try:
        main()
    except Exception as exc:  # pragma: no cover - logging path
        _log_error("STEP cli", "codex_ml.cli.main", str(exc), f"argv={args}")
        raise


if __name__ == "__main__":  # pragma: no cover
    cli()
