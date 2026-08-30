"""Evaluation runner orchestrating metric computation and report generation."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import uuid  # noqa: E402
from collections.abc import Callable, Sequence  # noqa: E402
from contextlib import ExitStack  # noqa: E402
from dataclasses import asdict, is_dataclass  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional, TypeVar  # noqa: E402

from codex_ml.config import DataConfig, EvaluationConfig  # noqa: E402
from codex_ml.data.loader import CacheManifest  # noqa: E402
from codex_ml.metrics import (  # noqa: E402
    compute_accuracy,
    compute_bleu,
    compute_f1,
    compute_perplexity,
    compute_rouge_l,
    compute_token_accuracy,
)
from codex_ml.metrics.registry import (
    append_error_entry,  # noqa: E402
    list_metrics,  # noqa: E402
)
from codex_ml.metrics.registry import get as get_registered_metric  # noqa: E402
from codex_ml.metrics.sinks import create_sink  # noqa: E402
from codex_ml.registry.base import RegistryNotFoundError  # noqa: E402
from codex_ml.tracking.writers import NdjsonWriter  # type: ignore  # noqa: E402
from codex_ml.utils.provenance import export_environment  # noqa: E402
from codex_ml.utils.seeding import set_reproducible  # noqa: E402

__all__ = ["EvaluationError", "run_evaluation"]


class EvaluationError(RuntimeError):
    """Raised when evaluation cannot be completed."""


_T = TypeVar("_T")


def _append_error_report(
    step_name: str,
    message: str,
    context: Optional[dict[str, Any]] = None,
) -> None:
    """Append an error entry to the daily Codex report."""

    timestamp = datetime.now(timezone.utc)
    reports_dir = Path(os.environ.get("CODEX_ERROR_REPORTS_DIR", ".codex/reports"))
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
        # If error reporting fails we swallow the exception to avoid cascading failures.
        return

    error_file = reports_dir / f"errors_{timestamp.date().isoformat()}.md"
    try:
        context_payload = context or {}
        context_str = json.dumps(context_payload, sort_keys=True, default=str)
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
        context_str = repr(context)

    block_lines = [
        ":::",
        f"Question for ChatGPT @codex {timestamp.isoformat()}:",
        f"While performing {step_name}, encountered the following error:",
        message,
        f"Context: {context_str}",
        "What additional information would help clarify or resolve this issue?",
        ":::",
        "",
    ]

    try:
        with error_file.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(block_lines))
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
        # Suppress logging failures to keep evaluation running.
        return


def _safe_operation(
    step_name: str,
    operation: Callable[[], _T],
    *,
    context: Optional[dict[str, Any]] = None,
) -> Optional[_T]:
    """Execute ``operation`` while capturing and reporting errors."""

    try:
        return operation()
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - defensive logging path
        message = f"{exc.__class__.__name__}: {exc}"
        _append_error_report(step_name, message, context)
        raise


def _normalise_metrics_sink(value: Any) -> list[str]:
    allowed = {"ndjson", "csv", "none"}
    tokens: list[str]
    if isinstance(value, str):
        tokens = [token.strip().lower() for token in value.split(",") if token.strip()]
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        tokens = [str(item).strip().lower() for item in value if str(item).strip()]
    else:
        tokens = []
    if not tokens:
        tokens = ["ndjson"]
    invalid = [token for token in tokens if token not in allowed]
    if invalid:
        raise EvaluationError(f"Unsupported metrics sink(s): {sorted(set(invalid))}")
    seen: list[str] = []
    for token in tokens:
        if token not in seen:
            seen.append(token)
    return seen


def _load_records(
    dataset_path: Path,
    fmt: str,
    *,
    prediction_field: str,
    target_field: str,
    text_field: str,
) -> list[dict[str, Any]]:
    fmt = fmt.lower()
    records: list[dict[str, Any]] = []
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
    values: Sequence[Any],
    metric_name: str,
    *,
    fallback: Optional[dict[Any, int]] = None,
) -> tuple[list[int], dict[Any, int]]:
    ints: list[int] = []
    mapping: dict[Any, int]
    mapping = {} if fallback is None else fallback
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
        except (TypeError, ValueError) as e:
            logger.debug("Type conversion failed for value '%s': %s", value, e)
        if value not in mapping:
            mapping[value] = len(mapping)
        ints.append(mapping[value])
    return ints, mapping


def _coerce_token_sequence(record: dict[str, Any], key: str, index: int) -> list[int]:
    tokens = record.get(key)
    if tokens is None:
        raise EvaluationError(f"Record {index} missing '{key}' field")
    try:
        coerced = [int(token) for token in tokens]
    except (TypeError, ValueError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        raise EvaluationError(f"Record {index} has invalid '{key}' values: {exc}") from exc
    return coerced


def _collect_perplexity_inputs(
    records: Sequence[dict[str, Any]],
) -> tuple[list[Any], list[int], bool]:
    logits: list[Any] = []
    nll: list[float] = []
    targets: list[int] = []
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
                    f"Record {idx} logits length {len(record_logits)} != target length {len(tokens)}"  # noqa: E501
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


def _invoke_registry_metric(
    metric_name: str,
    metric_fn: Callable[..., Any],
    predictions: Sequence[Any],
    targets: Sequence[Any],
    records: Sequence[dict[str, Any]],
) -> Any:
    """Execute a registry metric supporting multiple calling conventions."""

    attempts = [
        lambda: metric_fn(predictions, targets),
        lambda: metric_fn(predictions=predictions, targets=targets, records=records),
        lambda: metric_fn(predictions=predictions, targets=targets),
        lambda: metric_fn(records),
    ]
    last_type_error: Exception | None = None
    for attempt in attempts:
        try:
            return attempt()
        except TypeError as exc:
            type(exc).__name__
            logger.debug("TypeError: <ERROR_TYPE>")
            last_type_error = exc
            continue
        except (ValueError, RuntimeError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            append_error_entry(
                "metric.execute",
                str(exc),
                f"metric={metric_name}",
                "Does the metric implementation handle the provided inputs?",
            )
            raise EvaluationError(f"Metric '{metric_name}' failed: {exc}") from exc

    detail = f": {last_type_error}" if last_type_error else ""
    append_error_entry(
        "metric.execute",
        f"Metric '{metric_name}' has incompatible signature{detail}",
        f"metric={metric_name}",
        "Can the metric accept (predictions, targets) or (records) arguments?",
    )
    raise EvaluationError(f"Metric '{metric_name}' has incompatible signature")


def _compute_metrics(
    records: Sequence[dict[str, Any]], metric_names: Sequence[str]
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    predictions = [rec.get("prediction") for rec in records]
    targets = [rec.get("target") for rec in records]

    registry_metrics: dict[str, tuple[str, Callable[..., Any]]] = {}
    try:
        for registered_name in list_metrics():
            key = registered_name.lower()
            if key in registry_metrics:
                continue
            try:
                registry_metrics[key] = (
                    registered_name,
                    get_registered_metric(registered_name),
                )
            except (ValueError, TypeError, RuntimeError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                append_error_entry(
                    "metric-registry.load",
                    str(exc),
                    f"metric={registered_name}",
                    "Should this registry metric be reviewed or disabled?",
                )
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        append_error_entry(
            "metric-registry.enumerate",
            str(exc),
            "list_metrics()",
            "Is the metric registry initialised correctly?",
        )
        registry_metrics = {}

    for metric_name in metric_names:
        if key == "perplexity":
            values, targs, from_logits = _collect_perplexity_inputs(records)
            results[metric_name] = compute_perplexity(values, targs, from_logits=from_logits)
        elif key == "accuracy":
            if not all(value is not None for value in predictions + targets):
                raise EvaluationError("accuracy requires prediction and target fields")
            results[metric_name] = compute_accuracy(predictions, targets)
        elif key in {"token_accuracy", "accuracy@token"}:
            pred_tokens: list[int] = []
            target_tokens: list[int] = []
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
            results[metric_name] = compute_token_accuracy(pred_tokens, target_tokens)
        elif key in {"micro_f1", "macro_f1", "f1"}:
            if not all(value is not None for value in predictions + targets):
                raise EvaluationError(f"{metric_name} requires prediction and target fields")
            pred_encoded, label_mapping = _encode_labels(predictions, metric_name)
            targ_encoded, _ = _encode_labels(targets, metric_name, fallback=label_mapping)
            if key == "macro_f1":
                results[metric_name] = compute_f1(pred_encoded, targ_encoded, average="macro")
            else:
                results[metric_name] = compute_f1(pred_encoded, targ_encoded, average="micro")
        elif key == "bleu":
            if not all(isinstance(value, str) for value in predictions + targets):
                raise EvaluationError("BLEU requires string predictions and targets")
            bleu_score = compute_bleu(predictions, targets)
            results[metric_name] = bleu_score
        elif key == "rouge_l":
            if not all(isinstance(value, str) for value in predictions + targets):
                raise EvaluationError("ROUGE-L requires string predictions and targets")
            rouge_score = compute_rouge_l(predictions, targets)
            # Unified API always returns float
            results[metric_name] = rouge_score
        else:
            if key in registry_metrics:
                _, metric_fn = registry_metrics[key]
            else:
                try:
                    metric_fn = get_registered_metric(metric_name)
                except RegistryNotFoundError as exc:  # pragma: no cover - defensive guard
                    append_error_entry(
                        "metric.resolve",
                        str(exc),
                        f"metric={metric_name}",
                        "Should this metric be registered before evaluation?",
                    )
                    raise EvaluationError(f"Unsupported metric '{metric_name}'") from exc
                except Exception as exc:  # pragma: no cover - defensive guard
                    append_error_entry(
                        "metric.resolve",
                        str(exc),
                        f"metric={metric_name}",
                        "Is the metric registry configured correctly?",
                    )
                    raise EvaluationError(
                        f"Metric '{metric_name}' failed to resolve: {exc}"
                    ) from exc

            result = _invoke_registry_metric(
                metric_name,
                metric_fn,
                predictions,
                targets,
                records,
            )
            results[metric_name] = result

    return results


_EVAL_RUN_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "codex_ml/eval_runner")


def _derive_run_id(cfg: EvaluationConfig, dataset_path: Path) -> str:
    if getattr(cfg, "run_id", None):
        return str(cfg.run_id)
    seed_component = cfg.seed if cfg.seed is not None else 0
    metrics_component = ",".join(sorted(cfg.metrics))
    split_component = getattr(cfg, "split", "eval")
    payload = f"{dataset_path.resolve()}|{metrics_component}|{seed_component}|{split_component}"
    return uuid.uuid5(_EVAL_RUN_NAMESPACE, payload).hex


def _write_dataset_manifest(
    output_dir: Path,
    *,
    dataset_name: str,
    dataset_path: Path,
    split: str,
    num_rows: int,
    seed: int,
) -> Optional[Path]:
    dataset_manifest_path = output_dir / "dataset_manifest.json"
    payload = {
        "dataset_name": dataset_name,
        "dataset_path": str(dataset_path),
        "split": split,
        "num_rows": num_rows,
        "seed": seed,
    }

    def _writer() -> Path:
        dataset_manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return dataset_manifest_path

    result = _safe_operation(
        "Step: write dataset manifest",
        _writer,
        context={"path": str(dataset_manifest_path), "payload": payload},
    )
    if isinstance(result, Path):
        return result
    return dataset_manifest_path if dataset_manifest_path.exists() else None


def run_evaluation(
    eval_cfg: EvaluationConfig,
    *,
    data_cfg: Optional[DataConfig] = None,
    predictor: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None,
) -> dict[str, Any]:
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

    output_dir = Path(eval_cfg.output_dir)
    _safe_operation(
        "Step: ensure evaluation output directory",
        lambda: output_dir.mkdir(parents=True, exist_ok=True),
        context={"output_dir": str(output_dir)},
    )

    split_name = getattr(eval_cfg, "split", "eval")
    dataset_manifest_path: Path | None = None
    dataset_display_name = eval_cfg.dataset_name or dataset_path.stem
    num_records = len(records)
    if getattr(eval_cfg, "write_dataset_manifest", True):
        dataset_manifest_path = _write_dataset_manifest(
            output_dir,
            dataset_name=dataset_display_name,
            dataset_path=dataset_path,
            split=split_name,
            num_rows=num_records,
            seed=seed_value,
        )

    if predictor is not None:
        for record in records:
            update = predictor(dict(record))
            if isinstance(update, dict):
                record.update(update)

    metrics_result = _compute_metrics(records, eval_cfg.metrics)

    _safe_operation(
        "Step: export evaluation environment",
        lambda: export_environment(
            output_dir / "provenance",
            seed=seed_value,
            command="evaluate",
            extras={"dataset_path": str(dataset_path.resolve())},
        ),
        context={"output_dir": str(output_dir)},
    )
    summary_path = output_dir / eval_cfg.report_filename
    ndjson_path = output_dir / eval_cfg.ndjson_filename
    metrics_path = output_dir / eval_cfg.metrics_filename
    metrics_csv_filename = getattr(eval_cfg, "metrics_csv_filename", "metrics.csv")
    metrics_csv_path = output_dir / metrics_csv_filename
    metrics_sinks = _normalise_metrics_sink(getattr(eval_cfg, "metrics_sink", "ndjson"))

    # Optional MLflow (offline) init - only when explicitly enabled
    import os

    if os.getenv("CODEX_ENABLE_MLFLOW") == "1":
        try:
            import mlflow

            mlflow.set_tracking_uri("file:artifacts/mlruns")
            mlflow.set_experiment("codex_offline")
            mlflow.start_run()

            # Best-effort: log enriched run metadata (guarded)
            try:
                # Git commit
                git_commit = os.getenv("CODEX_GIT_COMMIT", "")
                if git_commit:
                    mlflow.log_param("codex_git_commit", git_commit)

                # Conda environment
                conda_env = os.getenv("CONDA_DEFAULT_ENV", "")
                if conda_env:
                    mlflow.log_param("conda_env", conda_env)

                # Seed
                mlflow.log_param("seed", seed_value)

                # Dataset path (absolute)
                mlflow.log_param("dataset_path", str(dataset_path.resolve()))
            except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning(
                    f"Exception: {e}", exc_info=True
                )  # Silently ignore param logging errors
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning(
                "Exception: <ERROR_TYPE>", exc_info=True
            )  # Silently ignore MLflow errors

    # For the pluggable sink feature, use the first sink if multiple are specified
    # The remaining sinks will be handled by the dedicated writers later
    sink_kind = metrics_sinks[0] if metrics_sinks else "none"
    sink_target_path: Path | None = None
    sink_stack = ExitStack()
    try:
        if sink_kind not in {"none", "csv", "ndjson"}:
            raise EvaluationError(f"Unsupported metrics sink: {sink_kind}")
        if sink_kind != "none":
            sink_path_value = getattr(eval_cfg, "metrics_sink_path", None)
            if not sink_path_value:
                # Use default path based on sink kind
                if sink_kind == "csv":
                    sink_target_path = metrics_csv_path
                else:  # ndjson
                    sink_target_path = metrics_path
            else:
                sink_target_path = Path(sink_path_value)
            sink_target_path.parent.mkdir(parents=True, exist_ok=True)
            newline = "" if sink_kind == "csv" else None
            sink_fp = sink_stack.enter_context(
                sink_target_path.open("w", encoding="utf-8", newline=newline)
            )
            fieldnames = [
                "run_id",
                "metric",
                "value",
                "split",
                "dataset",
                "dataset_path",
                "num_records",
                "step",
                "timestamp",
            ]
            create_sink(
                sink_kind,
                sink_fp,
                fieldnames=fieldnames if sink_kind == "csv" else None,
            )
    except (ImportError, AttributeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        sink_stack.close()
        raise EvaluationError(f"Failed to initialise metrics sink: {exc}") from exc

    # Optional determinism hint (no-op if libs missing)
    try:
        from codex_ml.utils.determinism import set_global_determinism

        set_global_determinism(1337)
    except (ValueError, TypeError):
        logger.warning("Exception occurred", exc_info=True)
        # Determinism module not available or failed to initialize

    # Structured log (append-only)
    try:
        from tools.logging.structured_logger import JsonLogger

        _jl = JsonLogger("artifacts/logs/eval.ndjson")
        _jl.write(event="eval_start", metrics_sink=sink_kind)
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("Exception occurred", exc_info=True)
        # Logging module not available or failed to initialize

    # Optional perf sampling
    if os.getenv("CODEX_ENABLE_PERF_SAMPLER") == "1":
        try:
            from tools.perf.sampler import PerfSampler

            PerfSampler().run(steps=3)
        except (IOError, OSError, ModuleNotFoundError, ImportError):
            logger.warning("Exception occurred", exc_info=True)
            # Performance sampler not available or failed

    run_id = _derive_run_id(eval_cfg, dataset_path)
    # Convert run_id to integer using hash for arbitrary strings
    try:
        run_int = int(run_id, 16)
    except ValueError as e:
        type(e).__name__
        logger.debug("ValueError: <ERROR_TYPE>")
        logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
        # Fall back to hashing for non-hexadecimal run_ids
        run_int = int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:16], 16)
    seconds_range = 3153600000  # ~100 years in seconds
    seconds = run_int % seconds_range
    micros = (run_int // seconds_range) % 1_000_000
    deterministic_timestamp = (
        datetime.fromtimestamp(seconds, timezone.utc)
        .replace(microsecond=micros)
        .isoformat()
        .replace("+00:00", "Z")
    )
    summary = {
        "dataset_path": str(dataset_path.resolve()),
        "num_records": num_records,
        "metrics": metrics_result,
        "run_id": run_id,
        "dataset_name": dataset_display_name,
    }
    _safe_operation(
        "Step: write evaluation summary",
        lambda: summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True),
            encoding="utf-8",
        ),
        context={"path": str(summary_path)},
    )

    def _write_records_file() -> Path:
        with ndjson_path.open("w", encoding="utf-8") as fh:
            for idx, record in enumerate(records):
                row = {
                    "index": idx,
                    "text": record.get("text"),
                    "prediction": record.get("prediction"),
                    "target": record.get("target"),
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return ndjson_path

    _safe_operation(
        "Step: write evaluation records",
        _write_records_file,
        context={"path": str(ndjson_path), "num_records": num_records},
    )

    metrics_outputs: dict[str, Path] = {}

    if "ndjson" in metrics_sinks:

        def _write_metrics_ndjson() -> Path:
            # Use sink_target_path if ndjson is the primary sink, otherwise use default metrics_path
            ndjson_target = (
                sink_target_path if sink_kind == "ndjson" and sink_target_path else metrics_path
            )
            ndjson_writer = NdjsonWriter(ndjson_target, run_id=run_id)
            try:
                for idx, (metric_name, metric_value) in enumerate(metrics_result.items()):
                    if isinstance(metric_value, (int, float)):
                        serialised_value: Any = float(metric_value)
                    else:
                        serialised_value = metric_value
                    ndjson_writer.log(
                        {
                            "step": idx,
                            "split": split_name,
                            "metric": metric_name,
                            "value": serialised_value,
                            "dataset": str(dataset_path.resolve()),
                            "dataset_path": str(dataset_path.resolve()),
                            "num_records": num_records,
                            "timestamp": deterministic_timestamp,
                            "tags": {
                                "phase": "evaluation",
                                "source": "run_evaluation",
                                "num_records": num_records,
                                "seed": seed_value,
                            },
                        }
                    )
            finally:
                ndjson_writer.close()
            return ndjson_target

        ndjson_result = _safe_operation(
            "Step: write evaluation metrics log (ndjson)",
            _write_metrics_ndjson,
            context={
                "path": str(
                    sink_target_path if sink_kind == "ndjson" and sink_target_path else metrics_path
                ),
                "num_metrics": len(metrics_result),
            },
        )
        if isinstance(ndjson_result, Path):
            metrics_outputs["ndjson"] = ndjson_result
        else:
            ndjson_target = (
                sink_target_path if sink_kind == "ndjson" and sink_target_path else metrics_path
            )
            if ndjson_target.exists():
                metrics_outputs["ndjson"] = ndjson_target

    if "csv" in metrics_sinks:

        def _write_metrics_csv() -> Path:
            # Use sink_target_path if csv is the primary sink, otherwise use default metrics_csv_path  # noqa: E501
            csv_target = (
                sink_target_path if sink_kind == "csv" and sink_target_path else metrics_csv_path
            )
            fieldnames = [
                "metric",
                "value",
                "step",
                "split",
                "dataset",
                "dataset_path",
                "num_records",
                "run_id",
                "seed",
                "timestamp",
            ]
            with csv_target.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for idx, (metric_name, metric_value) in enumerate(metrics_result.items()):
                    if isinstance(metric_value, (int, float)):
                        serialised_value = float(metric_value)
                    else:
                        serialised_value = metric_value
                    writer.writerow(
                        {
                            "metric": metric_name,
                            "value": serialised_value,
                            "step": idx,
                            "split": split_name,
                            "dataset": str(dataset_path.resolve()),
                            "dataset_path": str(dataset_path.resolve()),
                            "num_records": num_records,
                            "run_id": run_id,
                            "seed": seed_value,
                            "timestamp": deterministic_timestamp,
                        }
                    )
            return csv_target

        csv_result = _safe_operation(
            "Step: write evaluation metrics log (csv)",
            _write_metrics_csv,
            context={
                "path": str(
                    sink_target_path
                    if sink_kind == "csv" and sink_target_path
                    else metrics_csv_path
                ),
                "num_metrics": len(metrics_result),
            },
        )
        if isinstance(csv_result, Path):
            metrics_outputs["csv"] = csv_result
        else:
            csv_target = (
                sink_target_path if sink_kind == "csv" and sink_target_path else metrics_csv_path
            )
            if csv_target.exists():
                metrics_outputs["csv"] = csv_target

    manifest_params = {
        "evaluation_metrics": eval_cfg.metrics,
        "data_config": asdict(data_cfg) if data_cfg and is_dataclass(data_cfg) else None,  # type: ignore[arg-type]
    }

    manifest = CacheManifest(
        source=str(dataset_path.resolve()),
        checksum="",
        encoding="utf-8",
        newline="preserve",
        num_records=num_records,
        params=manifest_params,
    )
    manifest_path = output_dir / "evaluation_manifest.json"

    _safe_operation(
        "Step: write evaluation manifest",
        lambda: manifest.write(manifest_path),
        context={"path": str(manifest_path), "num_records": num_records},
    )

    # Close the metrics sink file handles to prevent descriptor leaks
    sink_stack.close()

    return {
        "summary_path": str(summary_path),
        "records_path": str(ndjson_path),
        "manifest_path": str(manifest_path),
        "metrics": metrics_result,
        "metrics_path": str(
            metrics_outputs.get("ndjson") or metrics_outputs.get("csv") or metrics_path
        ),
        "metrics_csv_path": (str(metrics_outputs["csv"]) if "csv" in metrics_outputs else None),
        "metrics_sink": sink_kind,
        "metrics_sink_path": str(sink_target_path) if sink_target_path else None,
        "num_records": num_records,
        "run_id": run_id,
        "dataset_manifest_path": (
            str(dataset_manifest_path) if dataset_manifest_path is not None else None
        ),
    }
