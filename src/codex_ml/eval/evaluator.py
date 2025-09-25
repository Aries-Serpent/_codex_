from __future__ import annotations

from typing import Dict, Iterable

from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.optional import optional_import

from .metrics import perplexity, token_accuracy

torch, _HAS_TORCH = optional_import("torch")
datasets, _HAS_DATASETS = optional_import("datasets")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")

if _HAS_DATASETS:
    Dataset = datasets.Dataset  # type: ignore[attr-defined]
else:  # pragma: no cover - optional dependency
    Dataset = None  # type: ignore[assignment]

if _HAS_TRANSFORMERS:
    AutoModelForCausalLM = transformers.AutoModelForCausalLM  # type: ignore[attr-defined]
    AutoTokenizer = transformers.AutoTokenizer  # type: ignore[attr-defined]
else:  # pragma: no cover - optional dependency
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]


def evaluate_model(model, tokenizer, texts: Iterable[str]) -> Dict[str, float]:
    if not (_HAS_TORCH and _HAS_DATASETS):
        raise ImportError("torch and datasets are required for evaluation")
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


def run_evaluator(model_name: str, texts: Iterable[str]) -> Dict[str, float]:
    if not _HAS_TRANSFORMERS:
        raise ImportError("transformers is required for run_evaluator")
    tokenizer = load_from_pretrained(AutoTokenizer, model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_from_pretrained(AutoModelForCausalLM, model_name)
    return evaluate_model(model, tokenizer, texts)
