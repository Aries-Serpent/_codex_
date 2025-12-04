"""Evaluation scaffolding for _codex_.

Provides evaluation functions for model assessment. Supports both lightweight
smoke tests via evaluate_constant() and full model evaluation via run_evaluator()
which computes metrics over predictions vs targets.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

from .metrics import perplexity, token_accuracy

torch, _HAS_TORCH = optional_import("torch")
datasets, _HAS_DATASETS = optional_import("datasets")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")

Dataset = datasets.Dataset if _HAS_DATASETS else None  # type: ignore[attr-defined,assignment]
AutoModelForCausalLM = (
    transformers.AutoModelForCausalLM if _HAS_TRANSFORMERS else None  # type: ignore[attr-defined,assignment]
)
AutoTokenizer = (
    transformers.AutoTokenizer if _HAS_TRANSFORMERS else None  # type: ignore[attr-defined,assignment]
)


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
    ds = Dataset.from_dict({"text": list(texts)})
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
        revision=get_hf_revision(),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_from_pretrained(
        AutoModelForCausalLM,
        model_name,
        revision=get_hf_revision(),
    )
    return evaluate_model(model, tokenizer, texts)


def evaluate_constant(predictions, targets) -> float:
    """Return a dummy accuracy-style score for smoke tests."""
    if not predictions:
        return 0.0
    correct = sum(1 for p, t in zip(predictions, targets) if p == t)
    return correct / max(len(predictions), 1)
