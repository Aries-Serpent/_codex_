#!/usr/bin/env python
"""
Inference Pipeline

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/inference_pipeline.py [options]

    Examples:
    $ python scripts/inference_pipeline.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Deterministic Inference Pipeline Runner (v1.0.2)
# Production hardening:
#  - Ensure importlib is imported for dynamic preprocessor overrides.
#  - Token cache key includes model_hash, tokenizer identity, max_input_length, and preprocessor override identifier.
#  - Safe tokenizer identity extraction (fallbacks).
#  - Use context["tokenizer"] in inference stage (no NameError).
#  - Keep strict offline default via WANDB_MODE=offline; add --allow-online hidden flag for test harnesses.

import argparse
import hashlib
import importlib
import inspect
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
import yaml

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PIPELINE_VERSION = "1.0.2"
DEFAULT_SEED = 42
MAX_INPUT_LENGTH = 512
SAFEGUARD_KEYWORDS = ["sha256", "checksum", "rng", "seed", "offline", "WANDB_MODE"]

# Caches
MODEL_CACHE: dict[str, tuple[torch.nn.Module, Any, str]] = {}
TOKEN_CACHE: dict[str, dict[str, torch.Tensor]] = {}


@dataclass
class InferenceConfig:
    model_path: Path
    seed: int = DEFAULT_SEED
    deterministic: bool = True
    max_input_length: int = MAX_INPUT_LENGTH
    preprocessor_override: Optional[str] = None


class DeterminismError(RuntimeError):
    pass


# ---- Utilities ----
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(path.rglob("*")):
            if child.is_dir():
                continue
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            with child.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 15), b""):
                    digest.update(chunk)
        return digest.hexdigest()
    raise FileNotFoundError(f"Cannot hash missing path: {path}")


def enforce_offline_mode(allow_online: bool = False) -> None:
    if allow_online:
        return
    if os.environ.get("WANDB_MODE") != "offline":
        raise DeterminismError("Offline mode required: set WANDB_MODE=offline for inference")


def set_deterministic_seeds(seed: int = DEFAULT_SEED, deterministic: bool = True) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        try:
            torch.use_deterministic_algorithms(True, warn_only=False)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            # Older torch versions may not support warn_only
            torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
        torch.backends.cudnn.benchmark = False  # type: ignore[attr-defined]


def _load_callable(path_str: str) -> Callable[[str, Any, int], dict[str, torch.Tensor]]:
    """
    Load a callable given a module.path:callable_name string.
    Raises informative errors on failure.
    """
    try:
        module_path, func_name = path_str.split(":", maxsplit=1)
    except Exception as e:
        logger.debug(f"Exception: {e}")
        raise TypeError(
            f"preprocessor_override must be 'module_path:callable'; got: {path_str}"
        ) from e

    try:
        module = importlib.import_module(module_path)
    except Exception as e:
        logger.debug(f"Exception: {e}")
        raise ImportError(
            f"Failed to import module '{module_path}' for override '{path_str}': {e}"
        ) from e

    fn = getattr(module, func_name, None)
    if not callable(fn):
        raise TypeError(f"Override {path_str} is not callable or not found in module")
    sig = inspect.signature(fn)
    try:
        sig.bind(None, None, None)
    except TypeError as e:
        logger.debug(f"TypeError: {e}")
        raise TypeError(
            "Preprocessor override must accept (text, tokenizer, max_input_length) "
            "as positional arguments"
        ) from e
    return fn


def load_inference_config(config_path: Path) -> InferenceConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    cfg = yaml.safe_load(config_path.read_text())
    inference_cfg = cfg.get("inference", {}) if isinstance(cfg, dict) else {}
    model_path = Path(inference_cfg.get("model_path", ""))
    if not model_path:
        raise ValueError("inference.model_path is required in config")
    seed = int(inference_cfg.get("seed", DEFAULT_SEED))
    deterministic = bool(inference_cfg.get("deterministic", True))
    max_input_length = int(inference_cfg.get("max_input_length", MAX_INPUT_LENGTH))
    preprocessor_override = inference_cfg.get("preprocessor_override")
    return InferenceConfig(
        model_path=model_path,
        seed=seed,
        deterministic=deterministic,
        max_input_length=max_input_length,
        preprocessor_override=preprocessor_override,
    )


# ---- Load model ----
def _load_model_from_directory(model_dir: Path) -> tuple[torch.nn.Module, Any]:
    from codex_ml.utils.hf_pinning import load_from_pretrained
    tokenizer = load_from_pretrained(AutoTokenizer, str(model_dir), local_files_only=True)  # Uses revision pinning for security
    model = load_from_pretrained(AutoModelForCausalLM, str(model_dir), local_files_only=True)  # Uses revision pinning for security
    model.eval()
    return model, tokenizer


def _load_model_from_file(model_path: Path) -> tuple[torch.nn.Module, Any]:
    loaded = torch.load(model_path, map_location="cpu", weights_only=False)  # nosec B614 - Model file may contain custom classes requiring weights_only=False
    if isinstance(loaded, torch.nn.Module):
        model = loaded
    else:
        raise ValueError("Serialized model file must contain a torch.nn.Module")
    model.eval()
    from codex_ml.utils.hf_pinning import load_from_pretrained
    tokenizer = load_from_pretrained(AutoTokenizer, str(model_path.parent), local_files_only=True)  # Uses revision pinning for security
    return model, tokenizer


def stage_i1_load_model(cfg: InferenceConfig) -> dict[str, Any]:
    model_path = cfg.model_path
    if not model_path.exists():
        raise ValueError(f"Model path not found: {model_path}")
    model_hash = sha256_path(model_path)
    cache_key = f"{str(model_path)}:{model_hash}"
    if cache_key in MODEL_CACHE:
        model, tokenizer, _ = MODEL_CACHE[cache_key]
        return {"model": model, "tokenizer": tokenizer, "model_hash": model_hash}
    set_deterministic_seeds(cfg.seed, cfg.deterministic)
    if model_path.is_dir():
        model, tokenizer = _load_model_from_directory(model_path)
    else:
        model, tokenizer = _load_model_from_file(model_path)
    MODEL_CACHE[cache_key] = (model, tokenizer, model_hash)
    return {"model": model, "tokenizer": tokenizer, "model_hash": model_hash}


# ---- Preprocess with scoped token cache ----
def _tokenizer_identity(tokenizer: Any) -> str:
    # Prefer name_or_path or pretrained_model_name_or_path; fallback to class name + repr fragment for uniqueness
    name = getattr(tokenizer, "name_or_path", None) or getattr(
        tokenizer, "pretrained_model_name_or_path", None
    )
    if name:
        return str(name)
    cls = tokenizer.__class__.__name__
    try:
        rep = tokenizer.__repr__()[:64]
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        rep = cls
    return f"{cls}:{rep}"


def stage_i2_preprocess(
    inputs: dict[str, Any],
    context: dict[str, Any],
    cfg: InferenceConfig,
    override: Optional[Callable[[str, Any, int], dict[str, torch.Tensor]]] = None,
) -> dict[str, Any]:
    tokenizer = context["tokenizer"]
    text = inputs.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must contain 'text' field with non-empty string.")
    input_hash = sha256_bytes(json.dumps(inputs, sort_keys=True).encode("utf-8"))
    model_hash = context.get("model_hash", "unknown_model")
    tokenizer_id = _tokenizer_identity(tokenizer)
    override_id = cfg.preprocessor_override or "no_override"
    cache_key = f"{input_hash}|{model_hash}|{tokenizer_id}|{cfg.max_input_length}|{override_id}"
    if cache_key in TOKEN_CACHE:
        cached_tokens = TOKEN_CACHE[cache_key]
        return {
            "tokens": {k: v.clone() for k, v in cached_tokens.items()},
            "input_hash": input_hash,
        }
    tokenizer.model_max_length = min(
        getattr(tokenizer, "model_max_length", cfg.max_input_length), cfg.max_input_length
    )
    if override:
        tokens = override(text, tokenizer, cfg.max_input_length)
    else:
        tokens = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=cfg.max_input_length,
            padding=False,
        )
    if tokens.get("input_ids") is None:
        raise ValueError("Tokenizer must return 'input_ids' for inference")
    if tokens["input_ids"].shape[0] != 1:
        raise ValueError("Batch size must be 1 for deterministic inference")
    TOKEN_CACHE[cache_key] = {k: v.clone() for k, v in tokens.items()}
    return {"tokens": tokens, "input_hash": input_hash}


# ---- Inference ----
def stage_i3_run_inference(
    processed: dict[str, Any], context: dict[str, Any], cfg: InferenceConfig
) -> dict[str, Any]:
    model = context["model"]
    tokenizer = context["tokenizer"]
    tokens = processed["tokens"]
    set_deterministic_seeds(cfg.seed, cfg.deterministic)
    with torch.no_grad():
        if hasattr(model, "generate"):
            generated = model.generate(
                **tokens,
                max_new_tokens=8,
                do_sample=False,
                num_beams=1,
                pad_token_id=getattr(tokenizer, "pad_token_id", 0),
            )
            decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        else:
            outputs = model(**tokens)
            logits = getattr(outputs, "logits", None)
            if logits is None and isinstance(outputs, (list, tuple)):
                logits = outputs[0]
            if logits is None:
                raise ValueError("Model output missing 'logits' for greedy decoding")
            top_ids = logits.argmax(dim=-1)
            decoded = tokenizer.decode(top_ids[0], skip_special_tokens=True)
    return {"predictions": decoded}


# ---- Postprocess ----
def stage_i4_postprocess(
    results: dict[str, Any],
    processed: dict[str, Any],
    context: dict[str, Any],
    cfg: InferenceConfig,
    timings: dict[str, float],
) -> dict[str, Any]:
    payload = {
        "predictions": results["predictions"],
        "input_hash": processed["input_hash"],
        "model_hash": context["model_hash"],
        "seed": cfg.seed,
        "max_input_length": cfg.max_input_length,
        "version": PIPELINE_VERSION,
    }
    output_hash = sha256_bytes(json.dumps(payload, sort_keys=True).encode("utf-8"))
    manifest = {
        "output_hash": output_hash,
        "payload": payload,
        "timings": timings,
        "safeguards": SAFEGUARD_KEYWORDS,
    }
    return manifest


# ---- Runner ----
def run_pipeline(
    config_path: Path,
    input_path: Path,
    output_path: Path,
    manifest_path: Optional[Path] = None,
    explain: bool = False,
    allow_online: bool = False,
) -> dict[str, Any]:
    enforce_offline_mode(allow_online=allow_online)
    cfg = load_inference_config(config_path)
    override = _load_callable(cfg.preprocessor_override) if cfg.preprocessor_override else None
    inputs = json.loads(input_path.read_text())
    timings: dict[str, float] = {}
    start = time.perf_counter()
    context = stage_i1_load_model(cfg)
    timings["I1_load_model_s"] = time.perf_counter() - start
    start = time.perf_counter()
    processed = stage_i2_preprocess(inputs, context, cfg, override)
    timings["I2_preprocess_s"] = time.perf_counter() - start
    start = time.perf_counter()
    results = stage_i3_run_inference(processed, context, cfg)
    timings["I3_infer_s"] = time.perf_counter() - start
    start = time.perf_counter()
    output = stage_i4_postprocess(results, processed, context, cfg, timings)
    timings["I4_postprocess_s"] = time.perf_counter() - start
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))
    if manifest_path:
        manifest = {
            "pipeline_version": PIPELINE_VERSION,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "output_hash": output["output_hash"],
        }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2))
    if explain:
        print(json.dumps({"output_hash": output["output_hash"], "timings": timings}, indent=2))
    return output


# ---- CLI ----
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic Inference Pipeline")
    parser.add_argument("--config", required=True, type=Path, help="Config YAML path")
    parser.add_argument("--input", required=True, type=Path, help="Input JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON path")
    parser.add_argument("--manifest", type=Path, help="Optional manifest output path")
    parser.add_argument("--explain", action="store_true", help="Print stage timings and hashes")
    parser.add_argument("--allow-online", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main():
    args = parse_args()
    run_pipeline(
        args.config,
        args.input,
        args.output,
        manifest_path=args.manifest,
        explain=args.explain,
        allow_online=args.allow_online,
    )


if __name__ == "__main__":
    main()
