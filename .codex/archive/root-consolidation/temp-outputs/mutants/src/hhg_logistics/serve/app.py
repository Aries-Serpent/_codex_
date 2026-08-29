"""
App Module

This module provides functionality for app.

Usage:
    from serve.app import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import time
from collections.abc import Hashable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import ray
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

serve = ray.serve
logger = logging.getLogger(__name__)

try:
    import hydra
except ImportError as e:
    logger.debug("ImportError: %s", e)
    logger.warning("ImportError: %s", e, exc_info=True)
    import config_legacy as hydra  # type: ignore[no-redef]


from common.ndjson_tools import append_event_ndjson, make_run_metrics_path  # noqa: E402
from hhg_logistics.model.adapters import load_adapters_into  # noqa: E402
from hhg_logistics.model.peft_utils import load_hf_llm  # noqa: E402
from omegaconf import DictConfig, OmegaConf  # noqa: E402

OFFLINE_ENV_VARS: dict[str, str] = {
    "WANDB_MODE": "offline",
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
}


def _ensure_offline_environment() -> dict[str, str]:
    """Set offline-first environment defaults if they are unset."""

    applied: dict[str, str] = {}
    for key, value in OFFLINE_ENV_VARS.items():
        if key not in os.environ:
            os.environ[key] = value
            applied[key] = value
    return applied


def _seed_everything(seed: int) -> dict[str, bool]:
    """Seed common RNG sources to encourage deterministic inference."""

    status = {"python": False, "numpy": False, "torch": False}
    random.seed(seed)
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    status["python"] = True

    try:
        import numpy

        numpy.random.seed(seed)
        status["numpy"] = True
    except (ImportError, AttributeError) as exc:  # pragma: no cover - optional dependency missing
        logger.debug("Failed to seed numpy: %s", exc)

    try:
        import torch

        torch.manual_seed(seed)
        if hasattr(torch, "cuda") and callable(getattr(torch.cuda, "is_available", None)):
            if torch.cuda.is_available():  # pragma: no cover - gpu specific
                torch.cuda.manual_seed_all(seed)
        use_det = getattr(torch, "use_deterministic_algorithms", None)
        if callable(use_det):  # pragma: no cover - optional availability
            try:
                use_det(True)
            except (ValueError, TypeError, RuntimeError):
                logger.warning("Exception occurred", exc_info=True)
                logger.debug("torch.use_deterministic_algorithms unavailable", exc_info=True)
        status["torch"] = True
    except (ValueError, TypeError) as exc:  # pragma: no cover - optional dependency missing
        logger.debug("Failed to seed torch: %s", exc)

    return status


def _normalize_for_hash(value: Any) -> Any:
    """Normalize config values into stable, JSON-serializable structures."""

    if isinstance(value, Mapping):
        return {key: _normalize_for_hash(inner) for key, inner in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_for_hash(item) for item in value]
    if isinstance(value, (set, frozenset)):
        normalized_items = [_normalize_for_hash(item) for item in value]
        normalized_items.sort(key=lambda item: json.dumps(item, sort_keys=True, default=str))
        return normalized_items
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="ignore")
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)


def _config_fingerprint(cfg: DictConfig) -> str:
    """Compute a reproducible SHA-256 fingerprint for the resolved config."""

    resolved = OmegaConf.to_container(cfg, resolve=True)
    normalized = _normalize_for_hash(resolved)
    payload = json.dumps(normalized, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _freeze_override_value(value: Any) -> Hashable:
    if isinstance(value, str):
        return value
    if isinstance(value, bytes | bytearray):
        return bytes(value).decode("utf-8", errors="ignore")
    if value is None or isinstance(value, int | float | bool):
        return value
    if isinstance(value, Mapping):
        return tuple(
            (key, _freeze_override_value(inner))
            for key, inner in sorted(value.items(), key=lambda item: item[0])
        )
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return tuple(_freeze_override_value(item) for item in value)
    if isinstance(value, set | frozenset):
        return tuple(_freeze_override_value(item) for item in sorted(value, key=repr))
    return repr(value)


def _make_override_key(overrides: Mapping[str, Any]) -> Hashable:
    if not overrides:
        return ()
    return tuple(
        (key, _freeze_override_value(value))
        for key, value in sorted(overrides.items(), key=lambda item: item[0])
    )


@dataclass
class GenConfig:
    max_new_tokens: int = 32
    do_sample: bool = False
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int | None = None


api = FastAPI(title="HHG LLM Service")


@serve.deployment(route_prefix="/", num_replicas=1)
@serve.ingress(api)
class LLMService:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.ready = False

        self.seed = int(getattr(cfg, "seed", 0))
        self.offline_env = _ensure_offline_environment()
        self.seed_status = _seed_everything(self.seed)
        self.config_sha256 = _config_fingerprint(cfg)
        self.runtime_metadata = {
            "config_sha256": self.config_sha256,
            "seed": self.seed,
            "offline_env": self.offline_env,
            "seed_status": self.seed_status,
        }
        logger.info(
            "Runtime safeguards established config_sha256=%s seed=%s offline_env=%s",
            self.config_sha256,
            self.seed,
            sorted(self.offline_env.keys()),
        )

        serve_cfg = cfg.serve
        logging_cfg = getattr(serve_cfg, "logging", None)
        metrics_dir = Path(getattr(logging_cfg, "metrics_dir", ".codex/metrics"))
        _ensure_dir(metrics_dir)
        filename_prefix = getattr(logging_cfg, "filename_prefix", "run") or "run"
        raw_metrics_path = make_run_metrics_path(metrics_dir)
        if filename_prefix:
            self.metrics_file = raw_metrics_path.with_name(
                f"{filename_prefix}-{raw_metrics_path.name}"
            )
        else:
            self.metrics_file = raw_metrics_path
        self.enable_req_log = bool(getattr(logging_cfg, "enable_request_log", True))

        bundle = load_hf_llm(
            pretrained=serve_cfg.model.pretrained,
            tokenizer_name=cfg.model.tokenizer,
            dtype=str(cfg.model.dtype),
            trust_remote_code=bool(cfg.model.trust_remote_code),
            low_cpu_mem_usage=bool(cfg.model.low_cpu_mem_usage),
        )
        model = bundle.model
        tokenizer = bundle.tokenizer

        if str(serve_cfg.model.source) == "adapters":
            adapters_dir = Path(serve_cfg.model.adapters_dir)
            if adapters_dir.exists():
                model = load_adapters_into(model, adapter_dir=adapters_dir)
                logger.info("Adapters loaded from %s", adapters_dir)
            else:
                logger.warning("Adapters dir %s not found; using base model.", adapters_dir)

        self.model = model
        self.tokenizer = tokenizer
        self.gen_cfg = GenConfig(
            max_new_tokens=int(serve_cfg.generate.max_new_tokens),
            do_sample=bool(serve_cfg.generate.do_sample),
            temperature=float(serve_cfg.generate.temperature),
            top_p=float(serve_cfg.generate.top_p) if serve_cfg.generate.top_p is not None else 0.95,
            top_k=int(serve_cfg.generate.top_k) if serve_cfg.generate.top_k is not None else None,
        )

        self.batch_enabled = bool(serve_cfg.batching.enabled)
        self.batch_size = int(serve_cfg.batching.max_batch_size)
        self.batch_timeout_s = float(int(serve_cfg.batching.timeout_ms) / 1000.0)

        self.ready = True
        logger.info("LLMService ready. Model=%s", cfg.model.pretrained)

    @api.get("/-/health")
    async def health(self) -> PlainTextResponse:
        return PlainTextResponse("ok")

    @api.get("/-/ready")
    async def readyz(self) -> JSONResponse:
        return JSONResponse({"ready": bool(self.ready)})

    @api.post("/predict")
    async def predict(self, request: Request) -> JSONResponse:
        started = time.perf_counter()
        body = await request.json()
        inputs = body.get("inputs")
        if isinstance(inputs, str):
            prompts = [inputs]
        elif isinstance(inputs, list):
            prompts = [str(item) for item in inputs]
        else:
            return JSONResponse(
                {"error": "inputs must be string or list of strings"}, status_code=400
            )

        overrides = body.get("generate_kwargs") or {}

        if self.batch_enabled and len(prompts) == 1:
            payload = await self._predict_batch({"prompts": prompts, "overrides": overrides})
            outputs = payload["outputs"]
        else:
            outputs = self._generate(prompts, overrides)

        latency_ms = int((time.perf_counter() - started) * 1000)
        response = {
            "outputs": outputs,
            "latency_ms": latency_ms,
            "model": str(self.cfg.model.pretrained),
            "config_sha256": self.config_sha256,
            "seed": self.seed,
        }

        if self.enable_req_log:
            record = {
                "ts": int(time.time()),
                "route": "/predict",
                "n_prompts": len(prompts),
                "prompt_len": sum(len(p) for p in prompts),
                "gen_len": sum(len(o) for o in outputs),
                "latency_ms": latency_ms,
                "model": str(self.cfg.model.pretrained),
                "source": str(self.cfg.serve.model.source),
                "config_sha256": self.config_sha256,
                "seed": self.seed,
                "seed_status": self.seed_status,
            }
            try:
                append_event_ndjson(self.metrics_file, record)
            except (IOError, OSError):  # pragma: no cover - logging best effort
                logger.debug("Failed to append request log", exc_info=True)

        return JSONResponse(response)

    def _collect_generate_kwargs(self, overrides: dict[str, Any]) -> dict[str, Any]:
        base = asdict(self.gen_cfg)
        for key, value in overrides.items():
            if key in base and value is not None:
                base[key] = value
        return base

    def _generate(
        self, prompts: Sequence[str], overrides: dict[str, Any] | None = None
    ) -> list[str]:
        encode = self.tokenizer(
            list(prompts),
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt",
        )
        generate_kwargs = self._collect_generate_kwargs(overrides or {})
        with _TorchInferenceContext():
            output = self.model.generate(
                input_ids=encode["input_ids"],
                attention_mask=encode.get("attention_mask"),
                max_new_tokens=generate_kwargs.get("max_new_tokens", 32),
                do_sample=generate_kwargs.get("do_sample", False),
                temperature=generate_kwargs.get("temperature", 0.7),
                top_p=generate_kwargs.get("top_p", 0.95),
                top_k=generate_kwargs.get("top_k"),
            )
        return self.tokenizer.batch_decode(output, skip_special_tokens=True)

    @serve.batch(max_batch_size=8, batch_wait_timeout_s=0.02)
    async def _predict_batch(self, payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
        payload_infos: list[dict[str, Any]] = []
        flat_prompts: list[str] = []
        for index, payload in enumerate(payloads):
            prompts = list(payload.get("prompts", []))
            overrides = payload.get("overrides") or {}
            payload_infos.append({"index": index, "prompts": prompts, "overrides": overrides})
            flat_prompts.extend(prompts)

        total_prompts = len(flat_prompts)
        if total_prompts > self.batch_size:
            logger.debug(
                "Batch prompt count %s exceeded configured max %s (timeout %.3fs)",
                total_prompts,
                self.batch_size,
                self.batch_timeout_s,
            )

        grouped: dict[Hashable, dict[str, Any]] = {}
        for info in payload_infos:
            key = _make_override_key(info["overrides"])
            if key not in grouped:
                grouped[key] = {
                    "overrides": info["overrides"],
                    "payloads": [],
                }
            grouped[key]["payloads"].append(info)

        result: list[dict[str, Any]] = [{"outputs": []} for _ in payloads]
        for group in grouped.values():
            overrides = group["overrides"]
            group_payloads = group["payloads"]
            group_prompts: list[str] = []
            for payload in group_payloads:
                group_prompts.extend(payload["prompts"])

            if not group_prompts:
                for payload in group_payloads:
                    result[payload["index"]] = {"outputs": []}
                continue

            outputs = self._generate(group_prompts, overrides)

            offset = 0
            for payload in group_payloads:
                count = len(payload["prompts"])
                result[payload["index"]] = {"outputs": outputs[offset : offset + count]}
                offset += count

        return result


class _TorchInferenceContext:
    def __init__(self) -> None:
        try:
            import torch
        except (ImportError, AttributeError):  # pragma: no cover - optional dependency missing
            self._torch = None
            self._inference = None
            self._autocast = None
        else:
            self._torch = torch
            self._inference = torch.inference_mode()
            self._autocast = torch.autocast("cuda") if torch.cuda.is_available() else None

    def __enter__(self) -> None:
        if self._inference is not None:
            self._inference.__enter__()
        if self._autocast is not None:
            self._autocast.__enter__()
        return

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._autocast is not None:
            self._autocast.__exit__(exc_type, exc, tb)
        if self._inference is not None:
            self._inference.__exit__(exc_type, exc, tb)


def _start_serve(cfg: DictConfig) -> None:
    host = str(cfg.serve.host)
    port = int(cfg.serve.port)
    route_prefix = str(cfg.serve.route_prefix)
    num_replicas = int(cfg.serve.num_replicas)

    logger.info(
        "Starting Ray Serve on %s:%s (route_prefix=%s, replicas=%s)",
        host,
        port,
        route_prefix,
        num_replicas,
    )

    ray.init(ignore_reinit_error=True, include_dashboard=False)
    serve.start(http_options={"host": host, "port": port, "location": "HeadOnly"})

    deployment = LLMService.options(num_replicas=num_replicas, route_prefix=route_prefix)  # type: ignore[attr-defined]
    deployment.deploy(cfg)
    logger.info("Serve deployment active at http://%s:%s%s", host, port, route_prefix)

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        logger.info("Shutting down Serve (KeyboardInterrupt).")
    finally:
        serve.shutdown()
        ray.shutdown()


@hydra.main(
    config_path="../../../configs/deployment/hhg_logistics",
    config_name="config",
    version_base="1.3",
)
def main(cfg: DictConfig) -> None:
    if not bool(getattr(cfg.serve, "enabled", False)):
        logger.info("serve.enabled=false; exit.")
        return

    Path(cfg.data.models_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Composed config:\n%s", OmegaConf.to_yaml(cfg))
    _start_serve(cfg)


if __name__ == "__main__":  # pragma: no cover - script entry
    main()
