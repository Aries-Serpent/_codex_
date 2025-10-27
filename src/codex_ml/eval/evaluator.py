from __future__ import annotations

import argparse
import json
import math
import re
import uuid
from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
import os
import sys
from typing import Any

from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

from .fallback import synthetic_alignment
from .metrics import perplexity, token_accuracy
from ..tracking.writers import NdjsonWriter

torch, _HAS_TORCH = optional_import("torch")
datasets, _HAS_DATASETS = optional_import("datasets")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")
sympy, _HAS_SYMPY = optional_import("sympy")
jsonschema, _HAS_JSONSCHEMA = optional_import("jsonschema")

try:  # pragma: no cover - optional dependency
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - optional dependency absent
    DictConfig = OmegaConf = None  # type: ignore[assignment]
else:  # pragma: no cover - register lightweight env resolver
    with suppress(Exception):
        if not OmegaConf.has_resolver("oc.env"):
            OmegaConf.register_new_resolver(
                "oc.env",
                lambda key, default=None: os.environ.get(key, default),
            )

try:  # pragma: no cover - optional dependency
    import hydra
except Exception:  # pragma: no cover - optional dependency absent
    hydra = None  # type: ignore[assignment]

if _HAS_SYMPY:
    simplify = getattr(sympy, "simplify", None)
    sympify = getattr(sympy, "sympify", None)
else:  # pragma: no cover - optional dependency absent
    simplify = sympify = None  # type: ignore[assignment]

if _HAS_JSONSCHEMA:
    Draft7Validator = getattr(jsonschema, "Draft7Validator", None)
else:  # pragma: no cover - optional dependency absent
    Draft7Validator = None  # type: ignore[assignment]

ReasoningRecord = Mapping[str, Any]
ReasoningDatasetMap = Mapping[str, Sequence[ReasoningRecord]]
ProbeResult = Mapping[str, float | int | None]

Dataset = datasets.Dataset if _HAS_DATASETS else None  # type: ignore[attr-defined,assignment]
AutoModelForCausalLM = (
    transformers.AutoModelForCausalLM if _HAS_TRANSFORMERS else None
)  # type: ignore[attr-defined,assignment]
AutoTokenizer = (
    transformers.AutoTokenizer if _HAS_TRANSFORMERS else None
)  # type: ignore[attr-defined,assignment]


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


def _missing_dependencies(require_transformers: bool = False) -> list[str]:
    missing: list[str] = []
    if not _HAS_TORCH:
        missing.append("torch")
    if not _HAS_DATASETS:
        missing.append("datasets")
    if require_transformers and not _HAS_TRANSFORMERS:
        missing.append("transformers")
    return missing


def evaluate_model(model, tokenizer, texts: Iterable[str]) -> dict[str, float]:
    missing = _missing_dependencies()
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

    missing = _missing_dependencies()
    if missing:
        raise EvaluationDependencyError(missing)

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
    missing = _missing_dependencies(require_transformers=True)
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


def lite_sequence_evaluation(
    predictions: Iterable[str], references: Iterable[str]
) -> dict[str, float]:
    """Compute lightweight metrics without importing torch/datasets."""

    summary = synthetic_alignment(predictions, references)
    return summary.as_dict()


_NUMERIC_PATTERN = re.compile(r"-?\d+(?:\.\d+)?(?:/[1-9]\d*(?:\.\d+)?)?")
_TOOL_PATTERN = re.compile(r"Tool\[(?P<name>[^\]]+)\]", re.IGNORECASE)
_ENV_PATTERN = re.compile(r"\${oc\.env:([^,}]+)(?:,\s*([^}]+))?}")
_HYDRA_CWD_PATTERN = re.compile(r"\${hydra:runtime\.cwd}")


def _resolve_string_placeholders(text: str) -> str:
    result = text
    if not result:
        return result
    result = _HYDRA_CWD_PATTERN.sub(Path.cwd().as_posix(), result)
    while True:
        match = _ENV_PATTERN.search(result)
        if not match:
            break
        var = match.group(1).strip()
        default = match.group(2)
        default_value = default.strip() if default is not None else ""
        replacement = os.environ.get(var, default_value)
        replacement_str = _resolve_string_placeholders(str(replacement)) if isinstance(replacement, str) else str(replacement)
        result = result[: match.start()] + replacement_str + result[match.end():]
    return os.path.expanduser(result)


def _resolve_structure_placeholders(value: Any) -> Any:
    if isinstance(value, str):
        return _resolve_string_placeholders(value)
    if isinstance(value, Mapping):
        return {key: _resolve_structure_placeholders(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_resolve_structure_placeholders(item) for item in value]
    if isinstance(value, tuple):
        return type(value)(_resolve_structure_placeholders(item) for item in value)
    return value


def _load_reasoning_records(path: str | Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Reasoning dataset not found: {file_path}")
    records: list[dict[str, Any]] = []
    if file_path.suffix.lower() in {".jsonl", ".ndjson"}:
        with file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                text = line.strip()
                if not text:
                    continue
                payload = json.loads(text)
                if not isinstance(payload, Mapping):
                    raise ValueError(
                        f"Reasoning dataset rows must be mappings (found {type(payload)!r})"
                    )
                records.append(dict(payload))
                if limit is not None and len(records) >= int(limit):
                    break
    elif file_path.suffix.lower() == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            for entry in payload:
                if not isinstance(entry, Mapping):
                    raise ValueError(
                        f"Reasoning dataset entries must be mappings (found {type(entry)!r})"
                    )
                records.append(dict(entry))
                if limit is not None and len(records) >= int(limit):
                    break
        elif isinstance(payload, Mapping):
            records.append(dict(payload))
        else:  # pragma: no cover - defensive guard
            raise ValueError(
                f"Unsupported JSON payload type for reasoning dataset: {type(payload)!r}"
            )
    else:
        raise ValueError(
            f"Unsupported reasoning dataset format: {file_path.suffix or 'unknown'}"
        )
    return records


def _coerce_structured(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        data = dict(value)
        if isinstance(data.get("metadata"), Mapping):
            data["metadata"] = dict(data["metadata"])
        return data
    if isinstance(value, str):
        text = value
        with suppress(json.JSONDecodeError):
            parsed = json.loads(value)
            if isinstance(parsed, Mapping):
                data = dict(parsed)
                data.setdefault("text", text)
                return data
        return {"text": text}
    return {}


def _normalise_label(label: Any) -> str | None:
    if label is None:
        return None
    if isinstance(label, bool):
        return "proved" if label else "disproved"
    text = str(label).strip().lower()
    truthy = {"true", "valid", "proved", "proven", "success", "satisfied"}
    falsy = {"false", "invalid", "disproved", "counterexample", "failed"}
    if text in truthy:
        return "proved"
    if text in falsy:
        return "disproved"
    return text or None


def _to_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        with suppress(ValueError):
            return float(text)
        if _HAS_SYMPY and sympify is not None:
            with suppress(Exception):
                expr = sympify(text)
                if expr is not None and getattr(expr, "is_real", False):
                    evaluated = float(expr)
                    if math.isfinite(evaluated):
                        return evaluated
        match = _NUMERIC_PATTERN.search(text)
        if match:
            return _to_number(match.group(0))
    return None


def _extract_numeric_answer(structured: Mapping[str, Any]) -> float | None:
    for key in ("answer", "value", "numeric", "result", "final", "solution"):
        candidate = structured.get(key)
        number = _to_number(candidate)
        if number is not None:
            return number
    text = structured.get("text")
    if isinstance(text, str):
        return _to_number(text)
    return None


def _extract_conclusion(structured: Mapping[str, Any]) -> str | None:
    for key in (
        "conclusion",
        "final_statement",
        "claim",
        "result",
        "goal",
        "statement",
        "text",
    ):
        value = structured.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _symbolic_match(lhs: str | None, rhs: str | None) -> bool | None:
    if not lhs or not rhs:
        return None
    if not _HAS_SYMPY or sympify is None or simplify is None:
        return None
    with suppress(Exception):
        left_expr = sympify(lhs)
        right_expr = sympify(rhs)
        diff = simplify(left_expr - right_expr)
        if getattr(diff, "is_zero", False):
            return True
        eq = getattr(sympy, "Eq", None)
        if callable(eq):
            result = eq(left_expr, right_expr)
            if getattr(result, "is_True", False):
                return True
    return None


def _extract_tool_calls(structured: Mapping[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    payload = structured.get("tool_calls") or structured.get("tools")
    if isinstance(payload, Mapping):
        payload = [payload]
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for item in payload:
            if isinstance(item, Mapping):
                entry = {
                    "name": str(item.get("name", "")).strip(),
                    "arguments": item.get("arguments"),
                    "observation": item.get("observation"),
                }
                calls.append(entry)
            elif isinstance(item, str):
                calls.append({"name": item.strip()})
    text = structured.get("text")
    if isinstance(text, str):
        for match in _TOOL_PATTERN.finditer(text):
            name = match.group("name").strip()
            if name:
                calls.append({"name": name})
    normalised: list[dict[str, Any]] = []
    for call in calls:
        name = call.get("name")
        if isinstance(name, str):
            call = dict(call)
            call["name"] = name.strip().lower()
            normalised.append(call)
    return normalised


def _validate_tool_calls(calls: Sequence[Mapping[str, Any]]) -> int:
    if not (_HAS_JSONSCHEMA and Draft7Validator is not None):
        return 0
    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "arguments": {"type": ["object", "array", "string", "null"]},
            "observation": {"type": ["string", "number", "boolean", "null"]},
        },
    }
    validator = Draft7Validator(schema)
    failures = 0
    for call in calls:
        try:
            errors = list(validator.iter_errors(call))
        except Exception:
            failures += 1
            continue
        failures += len(errors)
    return failures


def _arguments_match(expected: Any, observed: Any) -> bool:
    if expected is None:
        return True
    if isinstance(expected, Mapping):
        if not isinstance(observed, Mapping):
            return False
        for key, value in expected.items():
            if key not in observed:
                return False
            if str(observed[key]) != str(value):
                return False
        return True
    return expected == observed


def _select_records(datasets: ReasoningDatasetMap, *aliases: str) -> list[ReasoningRecord]:
    lower_map = {name.lower(): list(records) for name, records in datasets.items()}
    for alias in aliases:
        key = alias.lower()
        if key in lower_map:
            return lower_map[key]
    for key, records in lower_map.items():
        for alias in aliases:
            if alias.lower() in key:
                return records
    return []


def _theorem_proving_probe(datasets: ReasoningDatasetMap) -> dict[str, float]:
    records = _select_records(datasets, "proof_logs", "proof", "theorem")
    total = len(records)
    correct = 0
    attempted = 0
    missing = 0
    symbolic_attempts = 0
    symbolic_matches = 0
    for record in records:
        prediction = _coerce_structured(record.get("prediction"))
        target = _coerce_structured(record.get("target"))
        metadata = record.get("metadata") if isinstance(record.get("metadata"), Mapping) else {}
        expected_label = _normalise_label(
            (metadata or {}).get("verdict")
            or (metadata or {}).get("label")
            or target.get("verdict")
            or target.get("status")
            or "proved"
        )
        predicted_label = _normalise_label(
            prediction.get("verdict")
            or prediction.get("status")
            or prediction.get("result")
        )
        if predicted_label is None:
            text = prediction.get("text")
            if isinstance(text, str):
                lowered = text.lower()
                if any(token in lowered for token in ("disprove", "contradiction", "false")):
                    predicted_label = "disproved"
                elif any(token in lowered for token in ("prove", "therefore", "thus", "qed")):
                    predicted_label = "proved"
        if predicted_label is None:
            missing += 1
            continue
        attempted += 1
        if predicted_label == expected_label:
            correct += 1
        conclusion_pred = _extract_conclusion(prediction)
        conclusion_target = _extract_conclusion(target)
        match = _symbolic_match(conclusion_pred, conclusion_target)
        if match is not None:
            symbolic_attempts += 1
            if match:
                symbolic_matches += 1
    metrics: dict[str, float] = {}
    metrics["total"] = float(total)
    metrics["coverage"] = float(attempted) / float(total) if total else 0.0
    metrics["accuracy"] = float(correct) / float(attempted) if attempted else 0.0
    metrics["missing_verdict"] = float(missing)
    if symbolic_attempts:
        metrics["symbolic_consistency"] = float(symbolic_matches) / float(symbolic_attempts)
        metrics["symbolic_checks"] = float(symbolic_attempts)
    else:
        metrics["symbolic_consistency"] = 0.0
        metrics["symbolic_checks"] = 0.0
    return metrics


def _math_verification_probe(datasets: ReasoningDatasetMap) -> dict[str, float]:
    records = _select_records(datasets, "math_word_problems", "math", "arithmetic")
    total = len(records)
    attempted = 0
    exact = 0
    tolerant = 0
    max_error = 0.0
    for record in records:
        prediction = _coerce_structured(record.get("prediction"))
        target = _coerce_structured(record.get("target"))
        pred_value = _extract_numeric_answer(prediction)
        target_value = _extract_numeric_answer(target)
        if target_value is None:
            metadata = record.get("metadata") if isinstance(record.get("metadata"), Mapping) else {}
            if isinstance(metadata, Mapping):
                target_value = _to_number(metadata.get("answer"))
        if target_value is None or pred_value is None:
            continue
        attempted += 1
        if pred_value == target_value:
            exact += 1
        if math.isclose(pred_value, target_value, rel_tol=1e-6, abs_tol=1e-6):
            tolerant += 1
        max_error = max(max_error, abs(pred_value - target_value))
    metrics: dict[str, float] = {}
    metrics["total"] = float(total)
    metrics["attempted"] = float(attempted)
    metrics["exact_match"] = float(exact) / float(attempted) if attempted else 0.0
    metrics["tolerance_match"] = float(tolerant) / float(attempted) if attempted else 0.0
    metrics["max_error"] = float(max_error) if attempted else 0.0
    return metrics


def _tool_audit_probe(datasets: ReasoningDatasetMap) -> dict[str, float]:
    records = _select_records(datasets, "tool_traces", "tools", "trace")
    total = len(records)
    expected_total = 0
    matched = 0
    arg_matches = 0
    schema_failures = 0
    complete = 0
    extra_calls = 0
    for record in records:
        metadata = record.get("metadata") if isinstance(record.get("metadata"), Mapping) else {}
        expected_calls: list[dict[str, Any]] = []
        tools = metadata.get("tools") if isinstance(metadata, Mapping) else None
        if isinstance(tools, Mapping):
            tools = [tools]
        if isinstance(tools, Sequence) and not isinstance(tools, (str, bytes)):
            for item in tools:
                if isinstance(item, Mapping):
                    expected_calls.append(dict(item))
        expected_total += len(expected_calls)
        prediction = _coerce_structured(record.get("prediction"))
        predicted_calls = _extract_tool_calls(prediction)
        schema_failures += _validate_tool_calls(predicted_calls)
        available = list(predicted_calls)
        local_matches = 0
        local_arg_matches = 0
        for expected_call in expected_calls:
            expected_name = str(expected_call.get("name", "")).strip().lower()
            if not expected_name:
                continue
            match_index = None
            for idx, candidate in enumerate(available):
                if candidate.get("name") == expected_name:
                    match_index = idx
                    break
            if match_index is None:
                continue
            candidate = available.pop(match_index)
            local_matches += 1
            if _arguments_match(expected_call.get("arguments"), candidate.get("arguments")):
                local_arg_matches += 1
        matched += local_matches
        arg_matches += local_arg_matches
        if expected_calls and local_matches == len(expected_calls):
            complete += 1
        if len(predicted_calls) > len(expected_calls):
            extra_calls += len(predicted_calls) - len(expected_calls)
    metrics: dict[str, float] = {}
    metrics["records"] = float(total)
    metrics["expected_calls"] = float(expected_total)
    metrics["matched_calls"] = float(matched)
    metrics["argument_matches"] = float(arg_matches)
    metrics["name_match_rate"] = float(matched) / float(expected_total) if expected_total else 0.0
    metrics["argument_match_rate"] = float(arg_matches) / float(expected_total) if expected_total else 0.0
    metrics["complete_traces"] = float(complete)
    metrics["schema_issues"] = float(schema_failures)
    metrics["extra_calls"] = float(extra_calls)
    return metrics


_REASONING_PROBES: dict[str, tuple[str, Callable[[ReasoningDatasetMap], dict[str, float]]]] = {
    "theorem_proving": ("theorem_proving", _theorem_proving_probe),
    "theorem_proving_accuracy": ("theorem_proving", _theorem_proving_probe),
    "math_verification": ("math_verification", _math_verification_probe),
    "math": ("math_verification", _math_verification_probe),
    "tool_audit": ("tool_audit", _tool_audit_probe),
    "tool_execution": ("tool_audit", _tool_audit_probe),
}


def run_reasoning_probes(
    datasets: ReasoningDatasetMap,
    *,
    probes: Sequence[str] | None = None,
    output_dir: str | Path | None = None,
    summary_filename: str = "summary.json",
    records_filename: str = "records.ndjson",
    metrics_filename: str = "metrics.ndjson",
    tags: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    materialised: dict[str, list[ReasoningRecord]] = {
        name: list(records) for name, records in datasets.items()
    }
    requested = list(probes) if probes is not None else [
        "theorem_proving",
        "math_verification",
        "tool_audit",
    ]
    executed: dict[str, dict[str, float]] = {}
    for probe_name in requested:
        key = probe_name.lower()
        if key not in _REASONING_PROBES:
            raise ValueError(f"Unknown reasoning probe '{probe_name}'")
        canonical, fn = _REASONING_PROBES[key]
        if canonical in executed:
            continue
        executed[canonical] = fn(materialised)
    metrics: dict[str, Any] = {}
    for canonical, values in executed.items():
        for metric_name, metric_value in values.items():
            key = f"{canonical}.{metric_name}"
            if isinstance(metric_value, (int, float)) and not isinstance(metric_value, bool):
                metrics[key] = float(metric_value)
            else:
                metrics[key] = metric_value
    dataset_counts = {name: float(len(records)) for name, records in materialised.items()}
    run_id = uuid.uuid4().hex
    result: dict[str, Any] = {
        "run_id": run_id,
        "metrics": metrics,
        "datasets": dataset_counts,
    }
    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        summary_path = out_dir / summary_filename
        summary_payload = {
            "run_id": run_id,
            "created_at": timestamp,
            "metrics": metrics,
            "datasets": dataset_counts,
        }
        summary_path.write_text(
            json.dumps(summary_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        result["summary_path"] = str(summary_path)
        if records_filename:
            records_path = out_dir / records_filename
            with records_path.open("w", encoding="utf-8") as handle:
                for dataset_name, records in materialised.items():
                    for index, record in enumerate(records):
                        row = {
                            "dataset": dataset_name,
                            "index": index,
                        }
                        for field in ("input", "prediction", "target", "metadata"):
                            if field in record:
                                row[field] = record[field]
                        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            result["records_path"] = str(records_path)
        metrics_path = out_dir / metrics_filename
        ndjson_writer = NdjsonWriter(metrics_path, run_id=run_id)
        tag_payload = {"phase": "reasoning"}
        if isinstance(tags, Mapping):
            tag_payload.update(tags)
        for step, (metric_name, metric_value) in enumerate(metrics.items()):
            ndjson_writer.log(
                {
                    "metric": metric_name,
                    "value": metric_value,
                    "step": step,
                    "split": "reasoning",
                    "dataset": "reasoning_probes",
                    "dataset_path": None,
                    "num_records": sum(dataset_counts.values()),
                    "tags": tag_payload,
                }
            )
        ndjson_writer.close()
        result["metrics_path"] = str(metrics_path)
    return result


def run_reasoning_from_config(cfg: Mapping[str, Any]) -> dict[str, Any]:
    resolved_cfg = _resolve_structure_placeholders(cfg) if isinstance(cfg, Mapping) else cfg
    datasets_cfg = resolved_cfg.get("datasets", {}) if isinstance(resolved_cfg, Mapping) else {}
    datasets: dict[str, list[ReasoningRecord]] = {}
    for name, params in datasets_cfg.items():
        if not isinstance(params, Mapping):
            continue
        path = params.get("path")
        if not path:
            continue
        limit_value: int | None = None
        if params.get("limit") is not None:
            with suppress(Exception):
                limit_value = int(params.get("limit"))
        records = _load_reasoning_records(path, limit=limit_value)
        if all("prediction" not in rec for rec in records):
            for rec in records:
                if "target" in rec and "prediction" not in rec:
                    rec["prediction"] = rec["target"]
        datasets[name] = records

    output_cfg = resolved_cfg.get("output", {}) if isinstance(resolved_cfg, Mapping) else {}
    output_dir = output_cfg.get("dir") if isinstance(output_cfg, Mapping) else None
    summary_raw = output_cfg.get("summary_filename") if isinstance(output_cfg, Mapping) else None
    summary_filename = str(summary_raw) if isinstance(summary_raw, str) and summary_raw else "summary.json"

    records_filename_raw = (
        output_cfg.get("records_filename") if isinstance(output_cfg, Mapping) else None
    )
    if records_filename_raw is False:
        records_filename: str | None = None
    elif isinstance(records_filename_raw, str) and records_filename_raw.strip():
        records_filename = records_filename_raw
    elif records_filename_raw is None:
        records_filename = "records.ndjson"
    else:
        records_filename = None

    metrics_raw = output_cfg.get("metrics_filename") if isinstance(output_cfg, Mapping) else None
    metrics_filename = (
        metrics_raw if isinstance(metrics_raw, str) and metrics_raw else "metrics.ndjson"
    )

    probes_cfg = resolved_cfg.get("probes") if isinstance(resolved_cfg, Mapping) else None
    probes: Sequence[str] | None
    if isinstance(probes_cfg, str):
        probes = [probes_cfg]
    elif isinstance(probes_cfg, Sequence) and not isinstance(probes_cfg, (str, bytes)):
        probes = [str(item) for item in probes_cfg]
    else:
        probes = None

    logging_cfg = resolved_cfg.get("logging") if isinstance(resolved_cfg, Mapping) else None
    tags_cfg = logging_cfg.get("tags") if isinstance(logging_cfg, Mapping) else None
    tags = dict(tags_cfg) if isinstance(tags_cfg, Mapping) else None
    result = run_reasoning_probes(
        datasets,
        probes=probes,
        output_dir=output_dir,
        summary_filename=summary_filename,
        records_filename=records_filename,
        metrics_filename=metrics_filename,
        tags=tags,
    )
    return result


if hydra is not None and DictConfig is not None:  # pragma: no cover - CLI hook

    @hydra.main(
        version_base=None,
        config_path="../../configs/evaluation/reasoning",
        config_name="default",
    )
    def reasoning_main(cfg: DictConfig) -> None:
        if OmegaConf is not None:
            resolved = OmegaConf.to_container(cfg, resolve=True)  # type: ignore[arg-type]
        else:  # pragma: no cover - OmegaConf missing under Hydra
            resolved = cfg
        if isinstance(resolved, Mapping):
            result = run_reasoning_from_config(resolved)
        else:
            result = {}
        print(json.dumps(result, indent=2, sort_keys=True))

else:  # pragma: no cover - fallback when hydra unavailable

    def reasoning_main(argv: Sequence[str] | None = None) -> None:
        parser = argparse.ArgumentParser(
            description="Run reasoning evaluation probes without Hydra."
        )
        default_config_path = (
            Path(__file__).resolve().parents[3]
            / "configs"
            / "evaluation"
            / "reasoning"
        )
        parser.add_argument(
            "--config-name",
            default="default",
            help="Reasoning config filename (with or without .yaml)",
        )
        parser.add_argument(
            "--config-path",
            default=str(default_config_path),
            help="Directory containing reasoning evaluation configs.",
        )
        args = parser.parse_args(list(argv) if argv is not None else sys.argv[1:])
        config_dir = Path(args.config_path).expanduser()
        config_name = str(args.config_name)
        config_file = (
            config_dir / config_name
            if config_name.endswith(".yaml")
            else config_dir / f"{config_name}.yaml"
        )
        if not config_file.exists():
            raise FileNotFoundError(f"Reasoning config not found: {config_file}")
        if OmegaConf is None:
            raise RuntimeError(
                "OmegaConf is required to parse reasoning configs without Hydra"
            )
        cfg_obj = OmegaConf.load(str(config_file))  # type: ignore[operator]
        resolved = OmegaConf.to_container(cfg_obj, resolve=True)  # type: ignore[arg-type]
        if not isinstance(resolved, Mapping):
            raise RuntimeError(
                f"Reasoning config '{config_file}' did not resolve to a mapping"
            )
        result = run_reasoning_from_config(resolved)
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    reasoning_main()


__all__ = [
    "evaluate_model",
    "evaluate_dataloader",
    "run_evaluator",
    "EvaluationDependencyError",
    "lite_sequence_evaluation",
    "run_reasoning_probes",
    "run_reasoning_from_config",
    "reasoning_main",
]
