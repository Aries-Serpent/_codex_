"""Evaluation runner orchestrating metric computation and report generation."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from codex_ml.config import DataConfig, EvaluationConfig
from codex_ml.data.loader import CacheManifest
from codex_ml.eval import metrics
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.seeding import set_reproducible

__all__ = ["EvaluationError", "run_evaluation"]


class EvaluationError(RuntimeError):
    """Raised when evaluation cannot be completed."""


def _load_records(
    dataset_path: Path,
    fmt: str,
    *,
    prediction_field: str,
    target_field: str,
    text_field: str,
) -> List[Dict[str, Any]]:
    fmt = fmt.lower()
    records: List[Dict[str, Any]] = []
    if fmt in {"jsonl", "ndjson"}:
        for line in dataset_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise EvaluationError("Each line in JSONL must be an object")
            rec = {
                "prediction": obj.get(prediction_field),
                "target": obj.get(target_field),
                "text": obj.get(text_field),
            }
            rec.update({k: v for k, v in obj.items() if k not in rec})
            records.append(rec)
    elif fmt == "csv":
        import csv

        with dataset_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                rec = {
                    "prediction": row.get(prediction_field),
                    "target": row.get(target_field),
                    "text": row.get(text_field),
                }
                rec.update({k: v for k, v in row.items() if k not in rec})
                records.append(rec)
    elif fmt == "text":
        for line in dataset_path.read_text(encoding="utf-8").splitlines():
            rec = {"text": line, "prediction": line, "target": line}
            records.append(rec)
    else:
        raise EvaluationError(f"Unsupported dataset format: {fmt}")
    return records


def _encode_labels(
    values: Sequence[Any], metric_name: str, *, fallback: Optional[Dict[Any, int]] = None
) -> Tuple[List[int], Dict[Any, int]]:
    ints: List[int] = []
    mapping: Dict[Any, int]
    if fallback is None:
        mapping = {}
    else:
        mapping = fallback
    for value in values:
        if value is None:
            raise EvaluationError(f"Missing value for metric {metric_name}")
        if isinstance(value, bool):
            ints.append(int(value))
            continue
        if isinstance(value, int):
            ints.append(int(value))
            continue
        try:
            ints.append(int(value))
            continue
        except (TypeError, ValueError):
            pass
        if value not in mapping:
            mapping[value] = len(mapping)
        ints.append(mapping[value])
    return ints, mapping


def _coerce_token_sequence(record: Dict[str, Any], key: str, index: int) -> List[int]:
    tokens = record.get(key)
    if tokens is None:
        raise EvaluationError(f"Record {index} missing '{key}' field")
    try:
        coerced = [int(token) for token in tokens]
    except (TypeError, ValueError) as exc:
        raise EvaluationError(f"Record {index} has invalid '{key}' values: {exc}") from exc
    return coerced


def _collect_perplexity_inputs(
    records: Sequence[Dict[str, Any]],
) -> Tuple[List[Any], List[int], bool]:
    logits: List[Any] = []
    nll: List[float] = []
    targets: List[int] = []
    representation: Optional[str] = None
    for idx, rec in enumerate(records):
        target_tokens = rec.get("target_tokens")
        if target_tokens is None:
            raise EvaluationError("perplexity requires 'target_tokens' in each record")
        tokens = [int(t) for t in target_tokens]
        targets.extend(tokens)
        has_logits = "logits" in rec and rec["logits"] is not None
        has_nll = "nll" in rec and rec["nll"] is not None
        if not has_logits and not has_nll:
            raise EvaluationError("perplexity requires either 'logits' or 'nll' per record")
        if has_logits and has_nll:
            chosen_representation = representation or "logits"
        elif has_logits:
            chosen_representation = "logits"
        else:
            chosen_representation = "nll"
        if representation is None:
            representation = chosen_representation
        elif representation != chosen_representation:
            raise EvaluationError(
                "perplexity does not support mixing 'logits' and 'nll' representations"
            )
        if representation == "logits":
            if not has_logits:
                raise EvaluationError(
                    "perplexity requires 'logits' for every record when logits are provided"
                )
            record_logits = list(rec["logits"])
            if len(record_logits) != len(tokens):
                raise EvaluationError(
                    f"Record {idx} logits length {len(record_logits)} != target length {len(tokens)}"
                )
            logits.extend(record_logits)
        else:
            if not has_nll:
                raise EvaluationError(
                    "perplexity requires 'nll' for every record when nll values are provided"
                )
            record_nll = list(rec["nll"])
            if len(record_nll) != len(tokens):
                raise EvaluationError(
                    f"Record {idx} nll length {len(record_nll)} != target length {len(tokens)}"
                )
            nll.extend(float(v) for v in record_nll)
    using_logits = representation == "logits"
    return (logits if using_logits else nll, targets, using_logits)


def _compute_metrics(
    records: Sequence[Dict[str, Any]], metric_names: Sequence[str]
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    predictions = [rec.get("prediction") for rec in records]
    targets = [rec.get("target") for rec in records]
    for metric_name in metric_names:
        key = metric_name.lower()
        if key == "perplexity":
            values, targs, from_logits = _collect_perplexity_inputs(records)
            results[metric_name] = metrics.perplexity(values, targs, from_logits=from_logits)
        elif key == "accuracy":
            if not all(value is not None for value in predictions + targets):
                raise EvaluationError("accuracy requires prediction and target fields")
            results[metric_name] = metrics.accuracy(predictions, targets)
        elif key == "token_accuracy":
            pred_tokens: List[int] = []
            target_tokens: List[int] = []
            for idx, rec in enumerate(records):
                pred_seq = _coerce_token_sequence(rec, "prediction_tokens", idx)
                target_seq = _coerce_token_sequence(rec, "target_tokens", idx)
                if len(pred_seq) != len(target_seq):
                    raise EvaluationError(
                        "token_accuracy requires prediction and target token counts to match "
                        f"per record (record {idx} has {len(pred_seq)} prediction tokens and "
                        f"{len(target_seq)} target tokens)"
                    )
                pred_tokens.extend(pred_seq)
                target_tokens.extend(target_seq)
            results[metric_name] = metrics.token_accuracy(pred_tokens, target_tokens)
        elif key in {"micro_f1", "macro_f1", "f1"}:
            if not all(value is not None for value in predictions + targets):
                raise EvaluationError(f"{metric_name} requires prediction and target fields")
            pred_encoded, label_mapping = _encode_labels(predictions, metric_name)
            targ_encoded, _ = _encode_labels(targets, metric_name, fallback=label_mapping)
            if key == "macro_f1":
                results[metric_name] = metrics.macro_f1(pred_encoded, targ_encoded)
            else:
                results[metric_name] = metrics.micro_f1(pred_encoded, targ_encoded)
        elif key == "bleu":
            if not all(isinstance(value, str) for value in predictions + targets):
                raise EvaluationError("BLEU requires string predictions and targets")
            bleu_score = metrics.bleu(predictions, targets)
            if bleu_score is None:
                raise EvaluationError("BLEU metric requires sacrebleu or nltk to be installed")
            results[metric_name] = bleu_score
        elif key == "rouge_l":
            if not all(isinstance(value, str) for value in predictions + targets):
                raise EvaluationError("ROUGE-L requires string predictions and targets")
            rouge_score = metrics.rouge_l(predictions, targets)
            if rouge_score is None:
                raise EvaluationError("rouge_score package is required for ROUGE-L")
            results[metric_name] = rouge_score["rougeL_f"]
        else:
            raise EvaluationError(f"Unsupported metric '{metric_name}'")
    return results


def run_evaluation(
    eval_cfg: EvaluationConfig,
    *,
    data_cfg: Optional[DataConfig] = None,
    predictor: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Run evaluation as described by ``eval_cfg``.

    Parameters
    ----------
    eval_cfg:
        Evaluation configuration with dataset details and requested metrics.
    data_cfg:
        Optional data configuration used to annotate the output manifest.
    predictor:
        Optional callable that receives each record and returns additional fields
        (for example model predictions). When omitted, dataset-provided predictions
        are used.
    """

    dataset_path = Path(eval_cfg.dataset_path)
    if not dataset_path.exists():
        raise EvaluationError(f"Dataset not found: {dataset_path}")

    seed_value = int(eval_cfg.seed) if eval_cfg.seed is not None else 0
    set_reproducible(seed_value)

    records = _load_records(
        dataset_path,
        eval_cfg.dataset_format,
        prediction_field=eval_cfg.prediction_field,
        target_field=eval_cfg.target_field,
        text_field=eval_cfg.text_field,
    )

    if eval_cfg.max_samples is not None:
        records = records[: int(eval_cfg.max_samples)]

    if predictor is not None:
        for record in records:
            update = predictor(dict(record))
            if isinstance(update, dict):
                record.update(update)

    metrics_result = _compute_metrics(records, eval_cfg.metrics)

    output_dir = Path(eval_cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    export_environment(
        output_dir / "provenance",
        seed=seed_value,
        command="evaluate",
        extras={"dataset_path": str(dataset_path.resolve())},
    )
    summary_path = output_dir / eval_cfg.report_filename
    ndjson_path = output_dir / eval_cfg.ndjson_filename
    metrics_path = output_dir / eval_cfg.metrics_filename

    summary = {
        "dataset_path": str(dataset_path.resolve()),
        "num_records": len(records),
        "metrics": metrics_result,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    with ndjson_path.open("w", encoding="utf-8") as fh:
        for idx, record in enumerate(records):
            row = {
                "index": idx,
                "text": record.get("text"),
                "prediction": record.get("prediction"),
                "target": record.get("target"),
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    timestamp = datetime.utcnow().isoformat()
    with metrics_path.open("w", encoding="utf-8") as metrics_file:
        for metric_name, metric_value in metrics_result.items():
            if isinstance(metric_value, (int, float)):
                serialised_value: Any = float(metric_value)
            else:
                serialised_value = metric_value
            metric_record = {
                "timestamp": timestamp,
                "dataset_path": str(dataset_path.resolve()),
                "metric": metric_name,
                "value": serialised_value,
                "num_records": len(records),
                "seed": seed_value,
            }
            metrics_file.write(json.dumps(metric_record, ensure_ascii=False) + "\n")

    manifest_params = {
        "evaluation_metrics": eval_cfg.metrics,
        "data_config": asdict(data_cfg) if data_cfg and is_dataclass(data_cfg) else None,
    }

    manifest = CacheManifest(
        source=str(dataset_path.resolve()),
        checksum="",
        encoding="utf-8",
        newline="preserve",
        num_records=len(records),
        params=manifest_params,
    )
    manifest_path = output_dir / "evaluation_manifest.json"
    manifest.write(manifest_path)

    return {
        "summary_path": str(summary_path),
        "records_path": str(ndjson_path),
        "manifest_path": str(manifest_path),
        "metrics": metrics_result,
        "metrics_path": str(metrics_path),
        "num_records": len(records),
    }
