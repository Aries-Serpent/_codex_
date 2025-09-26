"""Evaluation CLI using Hydra for configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

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
    return Path(to_absolute_path(str(value)))


def _to_tensor(value: Any) -> torch.Tensor:
    if isinstance(value, torch.Tensor):
        return value
    try:
        tensor = torch.as_tensor(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
        raise TypeError("logits output is not convertible to tensor") from exc
    if tensor.ndim == 0:
        raise TypeError("logits tensor must be at least 1D")
    return tensor


def _extract_logits(output: Any) -> torch.Tensor:
    if isinstance(output, torch.Tensor):
        return output
    if hasattr(output, "logits"):
        return _to_tensor(output.logits)
    if isinstance(output, dict) and "logits" in output:
        return _to_tensor(output["logits"])
    if isinstance(output, (tuple, list)) and output:
        first = output[0]
        if isinstance(first, torch.Tensor):
            return first
        if hasattr(first, "logits"):
            return _to_tensor(first.logits)
    raise TypeError("model output does not contain logits tensor")


@hydra.main(version_base=None, config_path="../../../configs/eval", config_name="default")
def main(cfg: DictConfig) -> None:
    set_reproducible(int(cfg.seed))
    dataset_cfg = cfg.dataset
    dataset_path = to_absolute_path(str(dataset_cfg.path))
    params = dict(dataset_cfg.get("params", {}))
    dataset = get_dataset(dataset_cfg.loader, path=dataset_path, **params)

    records = _select_records(dataset)
    limit = cfg.get("limit")
    if limit is not None:
        records = records[: int(limit)]

    tokenizer = get_tokenizer(cfg.tokenizer.name, **dict(cfg.tokenizer.get("cfg", {})))
    model = get_model(cfg.model.name, dict(cfg.model.get("cfg", {})), device="cpu")
    model.eval()

    output_dir = _to_path(cfg.output_dir) or Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    ndjson_path = output_dir / "predictions.ndjson"
    summary_path = output_dir / "summary.json"
    csv_path = cfg.get("output_csv")
    if csv_path:
        csv_path = _to_path(csv_path)
        if csv_path:
            csv_path.parent.mkdir(parents=True, exist_ok=True)

    preds_all: List[int] = []
    targets_all: List[int] = []
    logits_all: List[List[float]] = []

    for record in records:
        source = record.get("input") or record.get("text", "")
        target = record.get("target", "")
        input_ids = tokenizer.encode(source)
        if not input_ids:
            continue
        input_tensor = torch.tensor([input_ids], dtype=torch.long)
        with torch.no_grad():
            logits = _extract_logits(model(input_tensor))
        logits_seq = logits[0].tolist()
        pred_tokens = [int(max(range(len(row)), key=row.__getitem__)) for row in logits_seq]
        target_tokens = tokenizer.encode(target)
        length = min(len(pred_tokens), len(target_tokens))
        if length == 0:
            continue
        pred_tokens = pred_tokens[:length]
        target_tokens = target_tokens[:length]
        preds_all.extend(pred_tokens)
        targets_all.extend(target_tokens)
        logits_all.extend(logits_seq[:length])
        payload = {
            "input": source,
            "target": target,
            "prediction": tokenizer.decode(pred_tokens),
            "tokens": len(pred_tokens),
        }
        write_ndjson(ndjson_path, payload)
        if csv_path:
            import csv

            write_header = not csv_path.exists()
            with csv_path.open("a", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(payload.keys()))
                if write_header:
                    writer.writeheader()
                writer.writerow(payload)

    metrics: Dict[str, float] = {}
    for metric_name in cfg.metrics:
        func = METRIC_FUNCS.get(metric_name)
        if func is None:
            continue
        if metric_name == "perplexity":
            metrics[metric_name] = float(func(logits_all, targets_all, from_logits=True))  # type: ignore[arg-type]
        elif metric_name == "f1":
            metrics[metric_name] = float(func(preds_all, targets_all, average="micro"))  # type: ignore[arg-type]
        else:
            metrics[metric_name] = float(func(preds_all, targets_all))  # type: ignore[arg-type]

    summary_path.write_text(
        json.dumps({"metrics": metrics, "num_examples": len(records)}, indent=2),
        encoding="utf-8",
    )

    if cfg.mlflow.enable and _HAS_MLFLOW:
        mlflow.set_tracking_uri(str(cfg.mlflow.uri))
        mlflow.set_experiment(str(cfg.mlflow.experiment))
        mlflow.start_run()
        mlflow.log_params({"dataset": dataset_cfg.loader, "num_examples": len(records)})
        mlflow.log_metrics(metrics)
        mlflow.end_run()


if __name__ == "__main__":  # pragma: no cover
    main()
