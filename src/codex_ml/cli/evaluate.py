"""
Evaluate CLI (skeleton) leveraging checkpoint + model registry.

Usage:
    python -m codex_ml.cli.evaluate checkpoint.dir=artifacts/ckpts model_name=MiniLM

Hydra-style optional; falls back to argparse if hydra not installed.
Evaluation:
- Loads latest checkpoint (model + optimizer + scheduler states)
- Produces simple metrics (epoch, model_params)
- Placeholder for future dataset-driven evaluation.

"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Dict, List

import hydra
import torch
from codex_ml.data.registry import get_dataset
from codex_ml.eval.metrics import (
    accuracy,
    classification_f1,
    perplexity,
    token_accuracy,
)
from codex_ml.monitoring.codex_logging import write_ndjson
from codex_ml.registry.models import get_model
from codex_ml.registry.tokenizers import get_tokenizer
from codex_ml.utils.seeding import set_reproducible
from hydra.utils import to_absolute_path
from omegaconf import DictConfig

try:  # optional dependency
    import mlflow

    _HAS_MLFLOW = True
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore
    _HAS_MLFLOW = False


def _select_records(dataset: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
    for split in ("test", "val", "train"):
        if dataset.get(split):
            return list(dataset[split])
    return []


METRIC_FUNCS = {
    "accuracy": accuracy,
    "token_accuracy": token_accuracy,
    "f1": classification_f1,
    "perplexity": perplexity,
}


def _to_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    return None


def evaluate(checkpoint_dir: str, model_name: Optional[str] = None, device: Optional[str] = None):
    epoch_dir = _load_latest_checkpoint_dir(checkpoint_dir)
    if epoch_dir is None:
        return {"error": "No latest checkpoint found", "checkpoint_dir": checkpoint_dir}

    model_params = None
    model = None
    optimizer = None
    scheduler = None

    if model_name and get_model and _HAS_TORCH:
        try:
            model = get_model(name=model_name, device=device or "cpu", dtype=None, local_files_only=True)
        except Exception as e:  # noqa
            return {"error": f"Failed to load model: {e}"}

    ckpt_file = epoch_dir / "checkpoint.pt"
    if model is not None and ckpt_file.exists():
        try:
            load_checkpoint(ckpt_file, model=model, optimizer=optimizer, scheduler=scheduler)
            if _HAS_TORCH:
                model_params = sum(p.numel() for p in model.parameters())
        except Exception as e:  # noqa
            return {"error": f"Failed to load checkpoint: {e}"}

    metrics = {
        "evaluated_epoch_dir": str(epoch_dir),
        "model_name": model_name,
        "model_params": model_params,
        "status": "ok",
    }
    return metrics


# Hydra entry (optional)
if _HAS_HYDRA:

    @hydra.main(version_base=None, config_path="../../configs/evaluate", config_name="default")
    def main(cfg: DictConfig):
        cfg_map = OmegaConf.to_container(cfg, resolve=True)
        checkpoint_dir = cfg_map.get("checkpoint", {}).get("dir") or cfg_map.get("checkpoint_dir")
        model_name = cfg_map.get("model_name")
        device = cfg_map.get("device")
        result = evaluate(checkpoint_dir=checkpoint_dir, model_name=model_name, device=device)
        print(json.dumps(result, indent=2))


else:
    def main():
        # Fallback argparse
        import argparse
        ap = argparse.ArgumentParser(description="Evaluate latest checkpoint (skeleton).")
        ap.add_argument("--checkpoint-dir", required=True)
        ap.add_argument("--model-name", default=None)
        ap.add_argument("--device", default=None)
        args = ap.parse_args()
        result = evaluate(checkpoint_dir=args.checkpoint_dir, model_name=args.model_name, device=args.device)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()