"""Evaluation scaffolding for _codex_.

Provides evaluation functions for model assessment. Supports both lightweight
smoke tests via evaluate_constant() and full model evaluation via run_evaluator()
which computes metrics over predictions vs targets.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Iterable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.utils.hf_pinning import load_from_pretrained  # noqa: E402
from codex_ml.utils.optional import optional_import  # noqa: E402

from .metrics import perplexity, token_accuracy  # noqa: E402

torch, _HAS_TORCH = optional_import("torch")
datasets, _HAS_DATASETS = optional_import("datasets")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")

_HAS_DATASETS = bool(_HAS_DATASETS and datasets is not None and hasattr(datasets, "Dataset"))
Dataset = datasets.Dataset if _HAS_DATASETS else None
AutoModelForCausalLM = transformers.AutoModelForCausalLM if _HAS_TRANSFORMERS else None
AutoTokenizer = transformers.AutoTokenizer if _HAS_TRANSFORMERS else None


class EvaluationDependencyError(ImportError):
    """Raised when optional evaluation dependencies are unavailable."""

    def __init__(self, missing: Sequence[str]) -> None:
        self.missing = tuple(missing)
        super().__init__("Evaluation requires optional packages: " + ", ".join(self.missing))

    @property
    def hint(self) -> str:
        return (
            "Install the evaluation extras or call "
            "`codex_ml.eval.fallback.synthetic_alignment` for lightweight metrics."
        )


def _missing_dependencies(
    require_transformers: bool = False, *, require_datasets: bool = False
) -> list[str]:
    """Check for missing optional dependencies needed for evaluation."""
    missing: list[str] = []
    if not _HAS_TORCH:
        missing.append("torch")
    if require_datasets and not _HAS_DATASETS:
        missing.append("datasets")
    if require_transformers and not _HAS_TRANSFORMERS:
        missing.append("transformers")
    return missing


def evaluate_model(model: Any, tokenizer: Any, texts: Iterable[str]) -> dict[str, float]:
    """Evaluate a model on the given texts and return metrics.

    Parameters
    ----------
    model : Any
        A Hugging Face model instance (e.g., AutoModelForCausalLM).
    tokenizer : Any
        A Hugging Face tokenizer instance (e.g., AutoTokenizer).
    texts : Iterable[str]
        Text samples to evaluate on.

    Returns
    -------
    dict[str, float]
        Dictionary containing 'token_accuracy' and 'perplexity' metrics.
    """
    missing = _missing_dependencies(require_datasets=True)
    if missing:
        raise EvaluationDependencyError(missing)
    ds = Dataset.from_dict({"text": list(texts)})  # type: ignore[union-attr]
    column = list(ds["text"])
    toks = tokenizer(column, return_tensors="pt", padding=True)
    input_ids = toks["input_ids"]
    with torch.no_grad():
        out = model(input_ids, labels=input_ids)
    logits = out.logits
    pred_ids = logits.argmax(-1).reshape(-1).tolist()
    target_ids = input_ids.reshape(-1).tolist()
    pad = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else -100
    acc = token_accuracy(pred_ids, target_ids, ignore_index=pad)
    ppl = perplexity(logits.reshape(-1, logits.shape[-1]).tolist(), target_ids, ignore_index=pad)
    return {"token_accuracy": acc, "perplexity": ppl}


def run_evaluator(model_name: str, texts: Iterable[str]) -> dict[str, float]:
    """Load a model by name and evaluate it on the given texts.

    Parameters
    ----------
    model_name : str
        Name or path of the Hugging Face model to load.
    texts : Iterable[str]
        Text samples to evaluate on.

    Returns
    -------
    dict[str, float]
        Dictionary containing evaluation metrics.
    """
    missing = _missing_dependencies(require_transformers=True, require_datasets=True)
    if missing:
        raise EvaluationDependencyError(missing)
    tokenizer = load_from_pretrained(
        AutoTokenizer,
        model_name,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_from_pretrained(
        AutoModelForCausalLM,
        model_name,
    )
    return evaluate_model(model, tokenizer, texts)


def lite_sequence_evaluation(
    predictions: Sequence[str], references: Sequence[str]
) -> dict[str, float]:
    """
    Lightweight sequence evaluation without heavy dependencies.

    Computes basic text metrics for sequence-to-sequence tasks.

    Args:
        predictions: Predicted text sequences
        references: Reference/target text sequences

    Returns:
        Dictionary with metrics: token_accuracy, exact_match, perplexity_proxy, samples
    """
    if not predictions or not references:
        return {
            "token_accuracy": 0.0,  # nosec B105
            "exact_match": 0.0,
            "perplexity_proxy": float("inf"),
            "samples": 0.0,
        }

    n_samples = min(len(predictions), len(references))
    exact_matches = sum(p == r for p, r in zip(predictions, references, strict=False))

    # Token-level accuracy (simple word-based)
    total_tokens = 0
    correct_tokens = 0
    for pred, ref in zip(predictions, references, strict=False):
        pred_tokens = pred.split()
        ref_tokens = ref.split()
        total_tokens += len(ref_tokens)
        # Count matching tokens at same positions
        for i in range(min(len(pred_tokens), len(ref_tokens))):
            if pred_tokens[i] == ref_tokens[i]:
                correct_tokens += 1

    token_acc = correct_tokens / total_tokens if total_tokens > 0 else 0.0
    exact_match = exact_matches / n_samples if n_samples > 0 else 0.0

    # Perplexity proxy: lower is better, based on length mismatch
    avg_length_diff = (
        sum(
            abs(len(p.split()) - len(r.split()))
            for p, r in zip(predictions, references, strict=False)
        )
        / n_samples
    )
    perplexity_proxy = 1.0 + avg_length_diff  # Simple proxy

    return {
        "token_accuracy": token_acc,
        "exact_match": exact_match,
        "perplexity_proxy": perplexity_proxy,
        "samples": float(n_samples),
    }


def evaluate_constant(predictions: Sequence[Any], targets: Sequence[Any]) -> float:
    """Return a dummy accuracy-style score for smoke tests."""
    if not predictions:
        return 0.0
    correct = sum(1 for p, t in zip(predictions, targets, strict=False) if p == t)
    return correct / max(len(predictions), 1)


def evaluate_dataloader(
    model: Any, dataloader: Iterable[dict[str, Any]], eval_cfg, device: Any
) -> dict[str, float]:
    """Evaluate a model over a dataloader while restoring training mode.

    This lightweight helper mirrors the legacy evaluator surface used by the
    smoke tests. It averages loss and any requested metric keys exposed by the
    model output while ensuring the model's training flag is restored after the
    run.
    """

    if not _HAS_TORCH or torch is None:
        raise ImportError("evaluate_dataloader requires the optional torch dependency")

    metric_keys = set(eval_cfg.get("metric_keys", []) if eval_cfg else [])
    device = torch.device(device) if device is not None else torch.device("cpu")

    was_training = bool(getattr(model, "training", False))
    if hasattr(model, "eval"):
        model.eval()

    totals: dict[str, float] = {key: 0.0 for key in metric_keys}
    loss_total = 0.0
    loss_steps = 0
    batches = 0
    samples = 0

    try:
        for batch in dataloader:
            batches += 1
            samples += 1
            moved = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in batch.items()}
            with torch.no_grad():
                outputs = model(**moved)

            output_mapping: dict[str, Any]
            if isinstance(outputs, dict):
                output_mapping = outputs
            else:
                # Use vars(outputs) if possible for efficiency; otherwise, cache getattr
                try:
                    output_mapping = {
                        name: value
                        for name, value in vars(outputs).items()
                        if not name.startswith("_") and not callable(value)
                    }
                except TypeError as e:
                    type(e).__name__
                    logger.debug("TypeError: <ERROR_TYPE>")
                    logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
                    # vars() raises TypeError for objects without __dict__ (e.g., some namedtuples, classes with __slots__)  # noqa: E501
                    output_mapping = {
                        name: value
                        for name in (n for n in dir(outputs) if not n.startswith("_"))
                        if not callable(value := getattr(outputs, name))
                    }

            loss_val = output_mapping.get("loss")
            if loss_val is not None:
                loss_total += float(loss_val.detach().cpu().item())
                loss_steps += 1

            for key in metric_keys:
                if key in output_mapping and output_mapping[key] is not None:
                    totals[key] += float(output_mapping[key].detach().cpu().item())
    finally:
        if was_training and hasattr(model, "train"):
            model.train(True)

    metrics: dict[str, float] = {}
    if loss_steps:
        metrics["loss"] = loss_total / float(loss_steps)
    for key in metric_keys:
        if batches:
            metrics[key] = totals[key] / float(batches)

    metrics["batches"] = float(batches)
    metrics["samples"] = float(samples)
    return metrics
