from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from contextlib import suppress
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
    transformers.AutoModelForCausalLM if _HAS_TRANSFORMERS else None
)  # type: ignore[attr-defined,assignment]
AutoTokenizer = (
    transformers.AutoTokenizer if _HAS_TRANSFORMERS else None
)  # type: ignore[attr-defined,assignment]


def evaluate_model(model, tokenizer, texts: Iterable[str]) -> dict[str, float]:
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


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float) and not isinstance(value, bool):
        return float(value)
    for attr in ("item", "detach", "cpu"):
        attr_fn = getattr(value, attr, None)
        if attr_fn is None:
            continue
        with suppress(Exception):
            attr_value = attr_fn()
            if attr == "item":
                with suppress(Exception):
                    return float(attr_value)
            else:
                converted = _to_float(attr_value)
                if converted is not None:
                    return converted
    if hasattr(value, "numpy"):
        with suppress(Exception):
            array = value.numpy()
            with suppress(Exception):
                return float(array)
    return None


def _normalize_metrics(record: Mapping[str, Any]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for key, value in record.items():
        numeric = _to_float(value)
        if numeric is not None:
            normalized[key] = numeric
    return normalized


def _move_batch_to_device(batch: Any, device: Any) -> Any:
    if device is None:
        return batch
    if isinstance(batch, Mapping):
        return {k: _move_batch_to_device(v, device) for k, v in batch.items()}
    if isinstance(batch, list | tuple):
        return type(batch)(_move_batch_to_device(v, device) for v in batch)
    if hasattr(batch, "to"):
        try:
            return batch.to(device)
        except Exception:  # pragma: no cover - defensive fallback
            return batch
    return batch


def _invoke_model(model: Any, batch: Any):
    if isinstance(batch, Mapping):
        return model(**batch)
    if isinstance(batch, list | tuple):
        return model(*batch)
    return model(batch)


def _collect_metric_candidates(
    outputs: Any, metric_keys: Sequence[str]
) -> MutableMapping[str, Any]:
    metrics: dict[str, Any] = {}
    loss = getattr(outputs, "loss", None)
    if isinstance(outputs, Mapping):
        if loss is None and "loss" in outputs:
            loss = outputs.get("loss")
        for key in metric_keys:
            if key in outputs:
                metrics[key] = outputs[key]
    else:
        for key in metric_keys:
            metrics[key] = getattr(outputs, key, None)
    if loss is not None:
        metrics.setdefault("loss", loss)
    elif isinstance(outputs, Mapping) and "loss" in outputs:
        metrics.setdefault("loss", outputs["loss"])
    return {k: v for k, v in metrics.items() if v is not None}


class _MetricAggregator:
    def __init__(self) -> None:
        self._totals: dict[str, float] = {}
        self._counts: dict[str, int] = {}
        self._batch_count = 0
        self._sample_count = 0

    def update(self, metrics: Mapping[str, Any], *, batch_size: int | None) -> None:
        normalized = _normalize_metrics(metrics)
        for key, value in normalized.items():
            self._totals[key] = self._totals.get(key, 0.0) + value
            self._counts[key] = self._counts.get(key, 0) + 1
        self._batch_count += 1
        if batch_size is not None:
            with suppress(Exception):
                self._sample_count += int(batch_size)

    def summary(self) -> dict[str, float]:
        summary: dict[str, float] = {
            key: self._totals[key] / self._counts[key]
            for key in self._totals
            if self._counts.get(key)
        }
        summary["batches"] = float(self._batch_count)
        if self._sample_count:
            summary["samples"] = float(self._sample_count)
        return summary


def _infer_batch_size(batch: Any) -> int | None:
    if isinstance(batch, Mapping):
        for value in batch.values():
            size = _infer_batch_size(value)
            if size is not None:
                return size
        return None
    if isinstance(batch, list | tuple):
        if not batch:
            return None
        return _infer_batch_size(batch[0])
    if hasattr(batch, "shape"):
        try:
            shape = batch.shape
            if isinstance(shape, list | tuple) and shape:
                return int(shape[0])
        except Exception:  # pragma: no cover - defensive fallback
            return None
    if hasattr(batch, "size") and not callable(batch.size):
        try:
            size_value = batch.size
            if isinstance(size_value, list | tuple) and size_value:
                return int(size_value[0])
        except Exception:  # pragma: no cover - defensive fallback
            return None
    return None


def evaluate_dataloader(
    model: Any,
    dataloader: Iterable[Any],
    cfg: Mapping[str, Any] | None,
    device: Any,
) -> dict[str, float]:
    """Evaluate ``model`` on ``dataloader`` collecting averaged metrics.

    The helper mirrors the audit plan for a reusable evaluation routine:

    * Executes the loop under ``torch.no_grad`` to avoid gradient tracking.
    * Moves nested batch structures to the requested ``device`` best-effort.
    * Extracts ``loss`` and any additional ``metric_keys`` provided in ``cfg``.
    * Allows callers to supply a ``metric_fn`` producing additional scalar metrics
      per batch; returned values are averaged across iterations.

    Parameters
    ----------
    model:
        PyTorch module exposing ``eval``/``train`` methods and returning a mapping or
        object with attributes for ``loss`` and optional custom metrics.
    dataloader:
        Iterable yielding batches compatible with the model call signature.
    cfg:
        Optional mapping supporting keys ``metric_keys`` (sequence of metric names),
        ``metric_fn`` (callable accepting ``(outputs, batch)``), and ``max_batches``.
    device:
        Device specifier passed to ``tensor.to(device)`` where available.
    """

    if not _HAS_TORCH or torch is None:
        raise ImportError("torch is required for evaluate_dataloader")

    config: Mapping[str, Any] = cfg or {}
    metric_keys: list[str] = []
    if isinstance(config, Mapping):
        raw_metric_keys = config.get("metric_keys", [])
        if isinstance(raw_metric_keys, str):
            metric_keys = [raw_metric_keys]
        elif isinstance(raw_metric_keys, Sequence):
            metric_keys = [str(key) for key in raw_metric_keys]
    metric_fn: Callable[[Any, Any], Mapping[str, Any]] | None = None
    if isinstance(config, Mapping):
        candidate = config.get("metric_fn")
        if callable(candidate):
            metric_fn = candidate  # type: ignore[assignment]
    max_batches = 0
    if isinstance(config, Mapping):
        with suppress(Exception):
            max_batches = int(config.get("max_batches", 0) or 0)

    aggregator = _MetricAggregator()
    was_training = getattr(model, "training", False)

    if hasattr(model, "eval"):
        model.eval()

    try:
        with torch.no_grad():
            for idx, batch in enumerate(dataloader):
                if max_batches and idx >= max_batches:
                    break
                moved_batch = _move_batch_to_device(batch, device)
                outputs = _invoke_model(model, moved_batch)
                metrics: MutableMapping[str, Any] = _collect_metric_candidates(outputs, metric_keys)
                if metric_fn is not None:
                    try:
                        extra_metrics = metric_fn(outputs, moved_batch)
                    except Exception as exc:  # pragma: no cover - surfacing user errors
                        raise RuntimeError("metric_fn raised an exception") from exc
                    else:
                        if extra_metrics:
                            metrics.update(dict(extra_metrics))
                aggregator.update(metrics, batch_size=_infer_batch_size(moved_batch))
    finally:
        if hasattr(model, "train"):
            model.train(was_training)

    return aggregator.summary()


def run_evaluator(model_name: str, texts: Iterable[str]) -> dict[str, float]:
    if not _HAS_TRANSFORMERS:
        raise ImportError("transformers is required for run_evaluator")
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


__all__ = [
    "evaluate_model",
    "evaluate_dataloader",
    "run_evaluator",
]
