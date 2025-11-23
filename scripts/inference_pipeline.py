#!/usr/bin/env python
"""
Deterministic Inference Pipeline Runner (v1.0.1)

Stages:
  - I1: Load Model
  - I2: Preprocess Inputs
  - I3: Run Inference
  - I4: Postprocess & Hash

The pipeline enforces offline execution and deterministic seeds. It emits a
manifest with SHA256 hashes for inputs, model weights, and outputs to ensure
reproducibility and integrity.

Changelog:
- v1.0.1: Fixed token cache scoping to include tokenizer config hash (P1 issue).
"""
from __future__ import annotations

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
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

from scripts.space_traversal.audit_runner import DOMAIN_PATTERNS

PIPELINE_VERSION = "1.0.1"
DEFAULT_SEED = 42
MAX_INPUT_LENGTH = 512
SAFEGUARD_KEYWORDS = ["sha256", "checksum", "rng", "seed", "offline", "WANDB_MODE"]
MODEL_CACHE: Dict[Path, Tuple[torch.nn.Module, Any, str]] = {}
TOKEN_CACHE: Dict[str, Dict[str, torch.Tensor]] = {}


@dataclass
class InferenceConfig:
    """Configuration for deterministic inference. Version: v1.0.1"""

    model_path: Path
    seed: int = DEFAULT_SEED
    deterministic: bool = True
    max_input_length: int = MAX_INPUT_LENGTH
    preprocessor_override: Optional[str] = None


class DeterminismError(RuntimeError):
    """Raised when deterministic constraints are violated."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
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
            with child.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 15), b""):
                    digest.update(chunk)
        return digest.hexdigest()
    raise FileNotFoundError(f"Cannot hash missing path: {path}")


def enforce_offline_mode() -> None:
    if os.environ.get("WANDB_MODE") != "offline":
        raise DeterminismError("Offline mode required: set WANDB_MODE=offline for inference")


def set_deterministic_seeds(seed: int = DEFAULT_SEED, deterministic: bool = True) -> None:
    """
    Set global seeds for Python, NumPy, and torch. Version: v1.0.1

    This function also toggles deterministic algorithms where supported to
    reduce nondeterministic kernel usage.
    """

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        try:
            torch.use_deterministic_algorithms(True, warn_only=False)
        except Exception:
            torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
        torch.backends.cudnn.benchmark = False  # type: ignore[attr-defined]


def _load_callable(path_str: str) -> Callable[[str, Any, int], Dict[str, torch.Tensor]]:
    module_path, func_name = path_str.split(":", maxsplit=1)
    module = importlib.import_module(module_path)
    fn = getattr(module, func_name)
    if not callable(fn):
        raise TypeError(f"Override {path_str} is not callable")
    sig = inspect.signature(fn)
    if len(sig.parameters) < 2:
        raise TypeError("Preprocessor override must accept at least (text, tokenizer, *args)")
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


def _load_model_from_directory(model_dir: Path) -> Tuple[torch.nn.Module, Any]:
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(str(model_dir), local_files_only=True)
    model.eval()
    return model, tokenizer


def _load_model_from_file(model_path: Path) -> Tuple[torch.nn.Module, Any]:
    loaded = torch.load(model_path, map_location="cpu", weights_only=True)
    if isinstance(loaded, torch.nn.Module):
        model = loaded
    else:
        raise ValueError("Expected a torch.nn.Module in the serialized file for deterministic inference")
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(str(model_path.parent), local_files_only=True)
    return model, tokenizer


def stage_i1_load_model(cfg: InferenceConfig) -> Dict[str, Any]:
    """
    Loads model deterministically from path with seeded RNG. Version: v1.0.1

    Cache is keyed by the model hash to avoid repeated loads.
    """

    model_path = cfg.model_path
    if not model_path.exists():
        raise ValueError(f"Model path {model_path} not found. Ensure pre-trained model is available locally.")

    model_hash = sha256_path(model_path)
    cached = MODEL_CACHE.get(model_path)
    if cached and cached[2] == model_hash:
        model, tokenizer, _ = cached
        return {"model": model, "tokenizer": tokenizer, "model_hash": model_hash, "meta": {"source": "cache"}}

    set_deterministic_seeds(cfg.seed, cfg.deterministic)
    if model_path.is_dir():
        model, tokenizer = _load_model_from_directory(model_path)
    else:
        model, tokenizer = _load_model_from_file(model_path)

    MODEL_CACHE[model_path] = (model, tokenizer, model_hash)
    return {"model": model, "tokenizer": tokenizer, "model_hash": model_hash, "meta": {"source": "disk"}}


def stage_i2_preprocess(inputs: Dict[str, Any], context: Dict[str, Any], cfg: InferenceConfig,
                        override: Optional[Callable[[str, Any, int], Dict[str, torch.Tensor]]] = None) -> Dict[str, Any]:
    """Tokenize and batch inputs using fixed tokenization. Version: v1.0.1"""

    tokenizer = context["tokenizer"]
    text = inputs.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must contain 'text' field with non-empty string.")

    input_hash = sha256_bytes(json.dumps(inputs, sort_keys=True).encode("utf-8"))
    # Scope cache by tokenizer config to prevent cross-model reuse (fixes P1 issue)
    tokenizer_hash = sha256_bytes(str(tokenizer.name_or_path).encode("utf-8"))
    cache_key = f"{input_hash}_{tokenizer_hash}"
    if cache_key in TOKEN_CACHE:
        cached_tokens = TOKEN_CACHE[cache_key]
        return {"tokens": {k: v.clone() for k, v in cached_tokens.items()}, "input_hash": input_hash}

    tokenizer.model_max_length = min(getattr(tokenizer, "model_max_length", cfg.max_input_length), cfg.max_input_length)
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


def stage_i3_run_inference(processed: Dict[str, Any], context: Dict[str, Any], cfg: InferenceConfig) -> Dict[str, Any]:
    """
    Execute model prediction with seeded RNG. Version: v1.0.1
    Uses greedy decoding to avoid nondeterministic sampling.
    """

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
    return {"predictions": decoded, "raw": decoded}


def stage_i4_postprocess(results: Dict[str, Any], processed: Dict[str, Any], context: Dict[str, Any],
                         cfg: InferenceConfig, timings: Dict[str, float]) -> Dict[str, Any]:
    """Format outputs and compute SHA256 hashes for integrity. Version: v1.0.1"""

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
        "meta": {"domain_patterns": list(DOMAIN_PATTERNS.keys())},
    }
    return manifest


def build_manifest(output: Dict[str, Any], output_path: Path) -> Dict[str, Any]:
    artifact_hash = sha256_bytes(json.dumps(output, sort_keys=True).encode("utf-8"))
    return {
        "artifacts": {
            "output": {
                "path": str(output_path),
                "hash": artifact_hash,
            }
        },
        "pipeline_version": PIPELINE_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def run_pipeline(config_path: Path, input_path: Path, output_path: Path, manifest_path: Optional[Path] = None,
                 explain: bool = False) -> Dict[str, Any]:
    enforce_offline_mode()
    cfg = load_inference_config(config_path)
    override = _load_callable(cfg.preprocessor_override) if cfg.preprocessor_override else None

    inputs = json.loads(input_path.read_text())

    timings: Dict[str, float] = {}

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
        manifest = build_manifest(output, output_path)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2))
    if explain:
        print(json.dumps({"output_hash": output["output_hash"], "timings": timings}, indent=2))
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic Inference Pipeline")
    parser.add_argument("--config", required=True, type=Path, help="Config YAML path")
    parser.add_argument("--input", required=True, type=Path, help="Input JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON path")
    parser.add_argument("--manifest", type=Path, help="Optional manifest output path")
    parser.add_argument("--explain", action="store_true", help="Print stage timings and hashes")
    return parser.parse_args()


def main():
    args = parse_args()
    run_pipeline(args.config, args.input, args.output, manifest_path=args.manifest, explain=args.explain)


if __name__ == "__main__":
    main()
