"""Evaluate the latest checkpoint saved by the training loop."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from codex_ml.eval.metrics import (
    MetricError,
    accuracy,
    classification_f1,
    perplexity,
    token_accuracy,
)
from codex_ml.registry.models import get_model
from codex_ml.utils.checkpoint import load_checkpoint
from codex_ml.utils.optional import optional_import

hydra, _HAS_HYDRA = optional_import("hydra")
if _HAS_HYDRA:  # pragma: no cover - optional dependency
    from hydra.utils import to_absolute_path as _hydra_to_absolute_path
    from omegaconf import DictConfig, OmegaConf
else:  # pragma: no cover - optional dependency
    DictConfig = Any  # type: ignore
    OmegaConf = None  # type: ignore

torch, _HAS_TORCH = optional_import("torch")

try:  # optional dependency
    import mlflow  # noqa: F401

    _HAS_MLFLOW = True
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore
    _HAS_MLFLOW = False


METRIC_FUNCS = {
    "accuracy": accuracy,
    "token_accuracy": token_accuracy,
    "f1": classification_f1,
    "perplexity": perplexity,
}


def _to_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    if isinstance(value, Path):
        return value
    if _HAS_HYDRA:
        return Path(_hydra_to_absolute_path(str(value)))
    return Path(value).expanduser().resolve()


def _resolve_checkpoint_dir(value: str | Path | None) -> Path | None:
    path = _to_path(value)
    if path is None:
        return None
    if not path.exists():
        return None
    return path


def _load_latest_checkpoint_dir(checkpoint_dir: str | Path | None) -> Path | None:
    root = _resolve_checkpoint_dir(checkpoint_dir)
    if root is None:
        return None

    latest_file = root / "latest.json"
    if latest_file.exists():
        try:
            payload = json.loads(latest_file.read_text(encoding="utf-8"))
            candidate = payload.get("path")
            if isinstance(candidate, str) and candidate:
                candidate_path = Path(candidate)
                if not candidate_path.is_absolute():
                    candidate_path = root / candidate_path
                if candidate_path.exists():
                    if candidate_path.is_dir():
                        return candidate_path
                    parent = candidate_path.parent
                    if parent.exists():
                        return parent
        except json.JSONDecodeError:
            pass

    epoch_dirs = sorted(
        (item for item in root.iterdir() if item.is_dir() and item.name.startswith("epoch-")),
        key=lambda p: p.stat().st_mtime,

    )
    if epoch_dirs:
        return epoch_dirs[-1]

    fallback_dirs = sorted(
        (item for item in root.iterdir() if item.is_dir()), key=lambda p: p.stat().st_mtime
    )
    if fallback_dirs:
        return fallback_dirs[-1]

    if (root / "model.pt").exists():
        return root

    return None


def evaluate(
    checkpoint_dir: str | Path | None,
    model_name: Optional[str] = None,
    device: Optional[str] = None,
) -> Dict[str, Any]:
    epoch_dir = _load_latest_checkpoint_dir(checkpoint_dir)
    if epoch_dir is None:
        return {
            "error": "No latest checkpoint found",
            "checkpoint_dir": str(checkpoint_dir) if checkpoint_dir is not None else None,
        }

    model_params: Optional[int] = None
    model = None

    if model_name and get_model is not None and _HAS_TORCH:
        try:
            model = get_model(
                name=model_name, device=device or "cpu", dtype=None, local_files_only=True
            )
        except Exception as exc:  # pragma: no cover - defensive
            return {"error": f"Failed to load model: {exc}"}

    ckpt_dir = epoch_dir
    if model is not None and ckpt_dir.exists():
        try:
            load_checkpoint(
                model=model,
                optimizer=None,
                scheduler=None,
                ckpt_dir=ckpt_dir,
                map_location=device or "cpu",
            )
            model_params = sum(p.numel() for p in model.parameters()) if _HAS_TORCH else None
        except Exception as exc:  # pragma: no cover - defensive
            return {"error": f"Failed to load checkpoint: {exc}"}

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
    def main(cfg: DictConfig) -> None:
        cfg_map = OmegaConf.to_container(cfg, resolve=True)  # type: ignore[union-attr]
        checkpoint_dir = (
            cfg_map.get("checkpoint", {}).get("dir")  # type: ignore[assignment]
            if isinstance(cfg_map, dict)
            else None
        )
        if isinstance(cfg_map, dict) and "checkpoint_dir" in cfg_map and not checkpoint_dir:
            checkpoint_dir = cfg_map.get("checkpoint_dir")
        model_name = cfg_map.get("model_name") if isinstance(cfg_map, dict) else None
        device = cfg_map.get("device") if isinstance(cfg_map, dict) else None
        result = evaluate(checkpoint_dir=checkpoint_dir, model_name=model_name, device=device)
        print(json.dumps(result, indent=2))

else:

    def main() -> None:
        # Fallback argparse
        import argparse

        ap = argparse.ArgumentParser(description="Evaluate latest checkpoint (skeleton).")
        ap.add_argument("--checkpoint-dir", required=True)
        ap.add_argument("--model-name", default=None)
        ap.add_argument("--device", default=None)
        args = ap.parse_args()
        result = evaluate(
            checkpoint_dir=args.checkpoint_dir, model_name=args.model_name, device=args.device
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
