"""Evaluate the latest checkpoint saved by the training loop."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

from codex.logging.structured_logger import logger
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.metrics import (
    compute_accuracy,
    compute_f1,
    compute_perplexity,
    compute_token_accuracy,
)
from codex_ml.registry.models import get_model
from codex_ml.utils.checkpoint import load_checkpoint
from codex_ml.utils.optional import optional_import
from codex_ml.utils.yaml_support import MissingPyYAMLError, YAMLErrorType, safe_load

try:
    from codex_ml.safety import SafetyConfig, sanitize_prompt
except (IOError, OSError):  # pragma: no cover - optional dependency
    SafetyConfig = None
    sanitize_prompt = None

hydra, _HAS_HYDRA = optional_import("hydra")
if _HAS_HYDRA:  # pragma: no cover - optional dependency
    try:
        from hydra.utils import to_absolute_path as _hydra_to_absolute_path
    except ImportError:
        logger.warning(
            "Failed to import hydra.utils.to_absolute_path; "
            "falling back to config_legacy.utils.to_absolute_path",
            exc_info=True,
        )
        from config_legacy.utils import (
            to_absolute_path as _hydra_to_absolute_path,
        )

    from omegaconf import OmegaConf


def _cfg_to_container(cfg: Any) -> Any:
    """Normalize config object for downstream mapping-based access.

    When Hydra is available, converts an OmegaConf ``DictConfig`` into a standard
    Python container (dict/list/scalars) with interpolations resolved.
    Otherwise, returns the input object unchanged.
    """
    if _HAS_HYDRA:
        return OmegaConf.to_container(cfg, resolve=True)
    return cfg


torch, _HAS_TORCH = optional_import("torch")
_, _HAS_MLFLOW = optional_import("mlflow")


METRIC_FUNCS = {
    "accuracy": compute_accuracy,
    "token_accuracy": compute_token_accuracy,
    "f1": compute_f1,
    "perplexity": compute_perplexity,
}

_ = run_cmd


def _coerce_sequence(value: Any) -> Optional[list[Any]]:
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str):
        return [value]
    return None


def _sanitize_prompt_list(items: list[Any]) -> tuple[list[Any], bool]:
    if (
        SafetyConfig is None or sanitize_prompt is None
    ):  # pragma: no cover - optional dependency path
        return list(items), False

    cfg = SafetyConfig()
    sanitised: list[Any] = []
    changed = False
    for entry in items:
        if isinstance(entry, str):
            result = sanitize_prompt(entry, cfg)
            text = result.get("text", entry)
            sanitised.append(text)
            if text != entry:
                changed = True
            continue
        if isinstance(entry, dict):
            updated = dict(entry)
            mutated = False
            for key in ("prompt", "input", "text"):
                raw = updated.get(key)
                if isinstance(raw, str):
                    result = sanitize_prompt(raw, cfg)
                    text = result.get("text", raw)
                    if text != raw:
                        updated[key] = text
                        mutated = True
            sanitised.append(updated if mutated else entry)
            if mutated:
                changed = True
            continue
        sanitised.append(entry)
    return sanitised, changed


def _apply_prompt_sanitization(mapping: dict[str, Any], keys: Sequence[str]) -> int:
    total = 0
    for key in keys:
        sequence = _coerce_sequence(mapping.get(key))
        if not sequence:
            continue
        sanitised, changed = _sanitize_prompt_list(sequence)
        if changed:
            mapping[key] = sanitised
            total += 1
    return total


def _sanitize_eval_config(cfg_map: dict[str, Any]) -> int:
    sanitize_flag = cfg_map.get("sanitize_prompts", True)
    if not isinstance(sanitize_flag, bool):
        sanitize_flag = True
    if not sanitize_flag:
        logger.debug("Prompt sanitisation disabled for evaluation config")
        return 0

    total = 0
    dataset_cfg = cfg_map.get("dataset")
    if isinstance(dataset_cfg, dict):
        total += _apply_prompt_sanitization(
            dataset_cfg,
            ("texts", "prompts", "samples", "records"),
        )
    total += _apply_prompt_sanitization(
        cfg_map,
        ("prompts", "inputs", "texts"),
    )
    if total:
        logger.info("Sanitised %d prompt field(s) in evaluation configuration", total)
    return total


def _apply_dotlist_overrides(mapping: dict[str, Any], overrides: Sequence[str]) -> dict[str, Any]:
    """Apply Hydra-style ``key.subkey=value`` overrides to a plain mapping.

    Behavior:
    - Ignores override items that do not contain ``=``.
    - Splits keys by ``.`` and creates missing intermediate dictionaries.
    - Replaces non-dict intermediate values with new dictionaries so nested
      assignment can proceed deterministically.
    - Parses values with YAML-safe semantics (lists, numbers, booleans).
    - Ignores empty/invalid key paths after splitting.
    """
    for item in overrides:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        try:
            parsed: Any = safe_load(value)
        except MissingPyYAMLError:
            # PyYAML not installed — treat as raw string to keep non-Hydra fallback dependency-light
            parsed = value
        except YAMLErrorType:
            # Invalid YAML syntax in override value — treat as raw string
            parsed = value
        target: dict[str, Any] = mapping
        parts = [part for part in key.split(".") if part]
        if not parts:
            continue
        for part in parts[:-1]:
            next_val = target.get(part)
            if not isinstance(next_val, dict):
                next_val = {}
            target[part] = next_val
            target = next_val
        target[parts[-1]] = parsed
    return mapping


def _to_path(value: Optional[str | Path]) -> Optional[Path]:
    if value is None:
        return None
    if isinstance(value, Path):
        return value
    if _HAS_HYDRA:
        return Path(_hydra_to_absolute_path(str(value)))
    return Path(value).expanduser().resolve()


def _resolve_checkpoint_dir(value: Optional[str | Path]) -> Optional[Path]:
    path = _to_path(value)
    if path is None:
        return None
    if not path.exists():
        return None
    return path


def _load_latest_checkpoint_dir(
    checkpoint_dir: Optional[str | Path],
) -> Optional[Path]:
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
        except json.JSONDecodeError as e:
            logger.debug("JSON decode error when parsing checkpoint path: %s", e)

    epoch_dirs = sorted(
        (item for item in root.iterdir() if item.is_dir() and item.name.startswith("epoch-")),
        key=lambda p: p.stat().st_mtime,
    )
    if epoch_dirs:
        return epoch_dirs[-1]

    fallback_dirs = sorted(
        (item for item in root.iterdir() if item.is_dir()),
        key=lambda p: p.stat().st_mtime,
    )
    if fallback_dirs:
        return fallback_dirs[-1]

    if (root / "model.pt").exists():
        return root

    return None


def evaluate(
    checkpoint_dir: Optional[str | Path],
    model_name: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
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
                name=model_name,
                device=device or "cpu",
                dtype=None,
                local_files_only=True,
            )
        except (IOError, OSError) as exc:  # pragma: no cover - defensive
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
        except (ValueError, TypeError) as exc:  # pragma: no cover - defensive
            return {"error": f"Failed to load checkpoint: {exc}"}

    return {
        "evaluated_epoch_dir": str(epoch_dir),
        "model_name": model_name,
        "model_params": model_params,
        "status": "ok",
    }


def _run_dataset_evaluation(
    dataset_path: str,
    output_dir: str,
    metric_names: list[Any],
    limit: Optional[int],
    tokenizer_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Run dataset evaluation pipeline and write output files."""
    import json as _json

    # Load dataset
    records: list[dict[str, Any]] = []
    try:
        with open(dataset_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(_json.loads(line))
    except (IOError, OSError) as exc:
        return {"error": f"Failed to load dataset: {exc}", "status": "error"}

    if limit is not None:
        try:
            records = records[: int(limit)]
        except (TypeError, ValueError):
            # Invalid limit value; proceed without truncating records
            logger.debug("Ignoring invalid limit value %r; using all records", limit)

    # Load vocabulary if tiny-vocab tokenizer
    vocab: Optional[dict[str, Any]] = None
    tok_name = tokenizer_cfg.get("name", "")
    tok_path = (tokenizer_cfg.get("cfg") or {}).get("path")
    if tok_name == "tiny-vocab" and tok_path:
        try:
            vocab = _json.loads(Path(tok_path).read_text(encoding="utf-8"))
        except (IOError, OSError):
            vocab = {}

    def _tokenize(text: str) -> list[Any]:
        if vocab is None:
            return text.split()
        unk = vocab.get("<unk>", 0)
        return [vocab.get(w, unk) for w in text.split()]

    # Generate predictions (trivial: return first token of input as prediction)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    predictions: list[Any] = []
    targets: list[Any] = []
    for rec in records:
        text = rec.get("text") or rec.get("input") or ""
        target = rec.get("target", "")
        toks = _tokenize(text)
        pred_tok = toks[0] if toks else (vocab.get("<unk>", 0) if vocab else 0)
        tgt_toks = _tokenize(str(target))
        tgt_val = tgt_toks[0] if tgt_toks else (vocab.get("<unk>", 0) if vocab else 0)
        predictions.append(pred_tok)
        targets.append(tgt_val)

    # Write predictions.ndjson
    pred_file = out_path / "predictions.ndjson"
    with pred_file.open("w", encoding="utf-8") as fh:
        for i, (pred, tgt) in enumerate(zip(predictions, targets, strict=False)):
            fh.write(_json.dumps({"index": i, "prediction": pred, "target": tgt}) + "\n")

    # Compute metrics
    metric_results: dict[str, Any] = {}
    if "accuracy" in metric_names:
        try:
            metric_results["accuracy"] = compute_accuracy(predictions, targets)
        except (IOError, OSError):
            metric_results["accuracy"] = 0.0

    # Write summary.json
    summary = {"metrics": metric_results, "num_samples": len(records), "status": "ok"}
    (out_path / "summary.json").write_text(_json.dumps(summary, indent=2), encoding="utf-8")

    return summary


# Hydra entry (optional)
if _HAS_HYDRA:

    @hydra.main(version_base=None, config_path="../configs/evaluation", config_name="default")
    def main(cfg: Any) -> None:
        logger = init_json_logging()
        arg_list = sys.argv[1:]
        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
            cfg_map = _cfg_to_container(cfg)
            if isinstance(cfg_map, dict):
                _sanitize_eval_config(cfg_map)
            checkpoint_dir = (
                cfg_map.get("checkpoint", {}).get("dir") if isinstance(cfg_map, dict) else None
            )
            if isinstance(cfg_map, dict) and "checkpoint_dir" in cfg_map and not checkpoint_dir:
                checkpoint_dir = cfg_map.get("checkpoint_dir")
            model_name = cfg_map.get("model_name") if isinstance(cfg_map, dict) else None
            device = cfg_map.get("device") if isinstance(cfg_map, dict) else None

            # Run dataset evaluation pipeline when dataset.path is provided
            dataset_cfg = cfg_map.get("dataset", {}) if isinstance(cfg_map, dict) else {}
            dataset_path = dataset_cfg.get("path") if isinstance(dataset_cfg, dict) else None
            output_dir = (
                cfg_map.get("output_dir", "outputs") if isinstance(cfg_map, dict) else "outputs"
            )
            metric_names = (
                cfg_map.get("metrics", ["accuracy"]) if isinstance(cfg_map, dict) else ["accuracy"]
            )
            limit = cfg_map.get("limit") if isinstance(cfg_map, dict) else None
            tokenizer_cfg = cfg_map.get("tokenizer", {}) if isinstance(cfg_map, dict) else {}

            if dataset_path:
                result = _run_dataset_evaluation(
                    dataset_path=dataset_path,
                    output_dir=output_dir,
                    metric_names=metric_names,
                    limit=limit,
                    tokenizer_cfg=tokenizer_cfg if isinstance(tokenizer_cfg, dict) else {},
                )
            else:
                result = evaluate(
                    checkpoint_dir=checkpoint_dir, model_name=model_name, device=device
                )

            logger.info(json.dumps(result, indent=2))
            status = result.get("status", "error") if isinstance(result, dict) else "error"
            log_event(
                logger,
                "cli.finish",
                prog=sys.argv[0],
                status=status,
                checkpoint_dir=str(checkpoint_dir) if checkpoint_dir else None,
                model_name=model_name,
            )

else:

    def _has_dotlist_args(arg_list: Sequence[str]) -> bool:
        """Detect Hydra-style dotlist args like ``key=value`` or ``a.b=value``.

        Flags that start with ``--`` are excluded from dotlist detection.

        Returns:
            ``True`` when any dotlist-style override is present, else ``False``.
        """
        return any("=" in arg and not arg.startswith("--") for arg in arg_list)

    def _run_non_hydra_main(arg_list: list[str]) -> dict[str, Any]:
        """Run non-Hydra evaluate flow with dotlist fallback support."""
        if _has_dotlist_args(arg_list):
            cfg_map = _apply_dotlist_overrides({}, arg_list)
            _sanitize_eval_config(cfg_map)
            checkpoint_dir = (cfg_map.get("checkpoint") or {}).get("dir")
            if "checkpoint_dir" in cfg_map and not checkpoint_dir:
                checkpoint_dir = cfg_map.get("checkpoint_dir")
            model_name = cfg_map.get("model_name")
            device = cfg_map.get("device")
            dataset_cfg = cfg_map.get("dataset", {})
            dataset_path = dataset_cfg.get("path") if isinstance(dataset_cfg, dict) else None
            output_dir = cfg_map.get("output_dir", "outputs")
            metric_names = cfg_map.get("metrics", ["accuracy"])
            limit = cfg_map.get("limit")
            tokenizer_cfg = cfg_map.get("tokenizer", {})

            if dataset_path:
                return _run_dataset_evaluation(
                    dataset_path=str(dataset_path),
                    output_dir=str(output_dir),
                    metric_names=(
                        list(metric_names) if isinstance(metric_names, list) else ["accuracy"]
                    ),
                    limit=limit,
                    tokenizer_cfg=tokenizer_cfg if isinstance(tokenizer_cfg, dict) else {},
                )
            return evaluate(checkpoint_dir=checkpoint_dir, model_name=model_name, device=device)

        parser = ArgparseJSONParser(description="Evaluate latest checkpoint (skeleton).")
        parser.add_argument("--checkpoint-dir", required=True)
        parser.add_argument("--model-name", default=None)
        parser.add_argument("--device", default=None)
        args = parser.parse_args(arg_list)
        return evaluate(
            checkpoint_dir=args.checkpoint_dir,
            model_name=args.model_name,
            device=args.device,
        )

    def main(argv: Optional[Sequence[str]] = None) -> int:
        logger = init_json_logging()
        arg_list = list(argv) if argv is not None else sys.argv[1:]

        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
            result = _run_non_hydra_main(arg_list)
            logger.info(json.dumps(result, indent=2))
            status = result.get("status", "error") if isinstance(result, dict) else "error"
            log_event(
                logger,
                "cli.finish",
                prog=sys.argv[0],
                status=status,
            )
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
