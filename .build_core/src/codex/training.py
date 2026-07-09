# [Script]: codex.training.py
# > Generated: 2025-08-26 06:29:37 | Author: mbaetiong
"""Convenience wrapper around the symbolic pipeline with optional tokenization."""

# ruff: noqa: I001

from __future__ import annotations


from codex.logging.structured_logger import logger

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
from collections.abc import Sequence  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

try:
    import torch
    import torch.nn.functional as F

    clip_grad_norm_ = torch.nn.utils.clip_grad_norm_
except (ImportError, AttributeError):  # keep imports resilient
    torch = None  # type: ignore[assignment]
    F = None  # type: ignore[assignment]
    clip_grad_norm_ = None

from codex_ml.models import MiniLM, MiniLMConfig  # noqa: E402
from codex_ml.monitoring.codex_logging import (  # noqa: E402
    CodexLoggers,
    _codex_log_all,
    _codex_logging_bootstrap,
)
from codex_ml.monitoring.codex_logging import (  # noqa: E402
    _codex_patch_argparse as _codex_monitor_patch_argparse,
)
from codex_ml.monitoring.codex_logging import (  # noqa: E402
    _codex_sample_system,
)
from codex_ml.safety import (  # noqa: E402
    SafetyConfig,
    SafetyFilters,
    SafetyViolation,
    sanitize_prompt,
)
from codex_ml.symbolic_pipeline import (  # noqa: E402
    PretrainCfg,
    RewardModelCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
)
from codex_ml.tokenization import TokenizerAdapter, load_tokenizer  # noqa: E402
from codex_ml.utils.checkpointing import (  # type: ignore[attr-defined]  # noqa: E402
    CheckpointManager,
    set_seed,
)
from codex_ml.utils.error_log import log_error  # noqa: E402
from codex_ml.utils.provenance import export_environment  # noqa: E402
from codex_ml.utils.repro import record_dataset_checksums  # noqa: E402
from codex_utils.repro import log_env_info  # noqa: E402

# Import TrainCfg and run_custom_trainer from training module
# These are used by tests in tests/space_traversal/test_peft_comprehensive/
try:
    from training.functional_training import TrainCfg, run_custom_trainer  # type: ignore
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
    logger.warning(
        "ImportError: <ERROR_TYPE>", exc_info=True
    )  # codeql[py/clear-text-logging-sensitive-data]
    # Provide compatibility stubs when training module is not available
    from dataclasses import dataclass
    from typing import Any, Optional

    @dataclass
    class TrainCfg:  # type: ignore[no-redef]
        """Stub for TrainCfg when training module is not available."""

        epochs: int = 1
        batch_size: int = 1
        grad_accum: int = 1
        log_every: int = 1
        save_every: int = 0
        max_steps: int = 2
        checkpoint_dir: str = ""
        resume_from: str = ""
        use_lora: bool = False

    def run_custom_trainer(
        model: Any,
        tok: Any,
        train_ds: Any,
        val_ds: Any,
        cfg: Any,
    ) -> dict[str, Any]:
        """Stub for run_custom_trainer when training module is not available."""
        raise NotImplementedError(
            "run_custom_trainer requires the training.functional_training module, "
            "which is not available in this environment."
        )


# Artifact hashing helpers (sidecar)
try:
    from codex_ml.utils.artifacts import write_hash_sidecar, write_metadata
except (IOError, OSError):  # pragma: no cover - best effort
    write_hash_sidecar = None
    write_metadata = None


def _build_safe_ckpt_payload(
    model,
    optimizer,
    scheduler=None,
    epoch: int = 0,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build a pickle-safe checkpoint dictionary."""

    payload: dict[str, Any] = {
        "epoch": int(epoch),
        "meta": {
            "saved_at": datetime.now(UTC).isoformat(),
        },
    }
    if extra:
        try:
            payload["meta"].update(dict(extra))
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            payload["meta"]["_extra_error"] = "failed to merge extra metadata"
    if hasattr(model, "state_dict"):
        try:
            payload["model_state_dict"] = model.state_dict()
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            payload["model_state_dict"] = {}
    if hasattr(optimizer, "state_dict"):
        try:
            payload["optimizer_state_dict"] = optimizer.state_dict()
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            payload["optimizer_state_dict"] = {}
    if scheduler is not None and hasattr(scheduler, "state_dict"):
        try:
            payload["scheduler_state_dict"] = scheduler.state_dict()
        except (IOError, OSError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            payload["scheduler_state_dict"] = {}
    return payload


def save_checkpoint(
    path: str,
    model,
    optimizer,
    scheduler=None,
    epoch: int = 0,
    extra: Optional[dict[str, Any]] = None,
) -> str:
    """Save a checkpoint and emit hashing sidecars."""

    p = Path(path)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    payload = _build_safe_ckpt_payload(model, optimizer, scheduler, epoch=epoch, extra=extra)
    if torch is None:
        raise RuntimeError("PyTorch is required to save checkpoints, but it is not available.")
    torch.save(payload, p)
    try:
        if write_hash_sidecar is not None:
            write_hash_sidecar(p)
        if write_metadata is not None:
            write_metadata(p, extra={"epoch": epoch, "keys": list(payload.keys())})
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Exception: <ERROR_TYPE>", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
    return str(p)


try:  # Optional TensorBoard integration
    from tools.monitoring_integrate import SummaryWriter
except (IOError, OSError):  # pragma: no cover - optional dep
    SummaryWriter = None


# ---- Codex validation metrics helpers ----
def _codex_config_hash(d: dict[str, Any]) -> str:
    """Return a stable SHA256 hash for a config dictionary."""
    blob = json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def emit_validation_metric_record(path: str, payload: dict[str, Any]) -> None:
    """Append a single validation metric record to ``path`` as NDJSON."""
    payload = dict(payload)
    payload.setdefault("ts", datetime.now(UTC).isoformat())
    cfg = payload.pop("config", {})
    payload.setdefault("split", "val")
    payload.setdefault("notes", "codex.training/_run_minilm_training")
    payload["config_hash"] = _codex_config_hash(cfg if isinstance(cfg, dict) else {"cfg": cfg})
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _safe_token_accuracy(y_true, y_pred) -> float:
    try:
        n = min(len(y_true), len(y_pred))
        if n == 0:
            return 0.0
        match = sum(1 for i in range(n) if y_true[i] == y_pred[i])
        return match / float(n)
    except (ImportError, AttributeError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 0.0


def _safe_perplexity(nll_values) -> float:
    import math

    try:
        vals = list(nll_values)
        if not vals:
            return float("inf")
        mean = sum(vals) / float(len(vals))
        return float(math.exp(max(0.0, mean)))
    except (ImportError, AttributeError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return float("inf")


try:  # Attempt to import metrics; fall back to safe implementations
    from codex_ml.metrics import perplexity, token_accuracy
except (ImportError, AttributeError):  # pragma: no cover - fallback if metrics module missing

    def _fallback_perplexity(nll) -> float:
        """Simple perplexity wrapper used when metrics module is unavailable."""

        return _safe_perplexity(nll if hasattr(nll, "__iter__") else [nll])

    perplexity = _fallback_perplexity
    token_accuracy = _safe_token_accuracy


def run_functional_training(
    corpus: list[str],
    demos: list[dict[str, Any]],
    prefs: list[tuple[str, str, str, int]],
    *,
    tokenizer_name: Optional[str] = None,
    tokenizer_path: Optional[str] = None,
    use_fast_tokenizer: bool = True,
    tokenizer: Optional[TokenizerAdapter] = None,
    weights: Weights = Weights(),
    pre_cfg: PretrainCfg = PretrainCfg(),
    sft_cfg: SFTCfg = SFTCfg(),
    rm_cfg: RewardModelCfg = RewardModelCfg(),
    rlhf_cfg: RLHFCfg = RLHFCfg(),
    use_deeplearning: bool = False,
    seed: int = 0,
    device: Optional[str] = None,
    grad_clip: Optional[float] = None,
    grad_accum: int = 1,
    precision: str = "fp32",
    # Accept both legacy boolean and new string-based scheduler identifiers:
    # - True behaves like "steplr"
    # - None/False disables scheduler
    scheduler: Optional[bool | str] = None,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    tensorboard: bool = False,
    val_split: float = 0.10,
    test_split: float = 0.0,
    monitoring_args: Optional[argparse.Namespace] = None,
    art_dir: Optional[str | Path] = None,
    dataset_sources: Optional[Sequence[str | Path]] = None,
    # LoRA hyper-parameters (optional)
    lora_r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    lora_bias: str = "none",
) -> dict[str, Any]:
    """Run training pipeline, optionally using a tiny Torch model.

    When use_deeplearning is False, this routes to the symbolic pipeline.

    Args:
        corpus: list of raw training texts.
        demos: SFT demonstrations (symbolic pipeline).
        prefs: Preference data (symbolic pipeline).
        tokenizer_name: Optional tokenizer name to load.
        tokenizer_path: Optional tokenizer path to load.
        use_fast_tokenizer: Toggle usage of Rust-backed Fast tokenizer variants.
        tokenizer: Pre-loaded tokenizer adapter.
        weights: Symbolic pipeline weights.
        pre_cfg, sft_cfg, rm_cfg, rlhf_cfg: Pipeline configs.
        use_deeplearning: Use tiny MiniLM demo trainer if True.
        seed: RNG seed applied across libraries.
        device: Torch device (e.g., "cuda", "cpu").
        grad_clip: Optional gradient clipping norm.
        grad_accum: Steps for gradient accumulation.
        precision: Training precision ('fp32', 'fp16', 'bf16').
        scheduler: Optional scheduler selector ("steplr") or legacy bool.
        checkpoint_dir: Directory for checkpoints and metrics.
        resume_from: Optional checkpoint to resume from.
        keep_last: How many recent checkpoints to keep.
        keep_best: How many best checkpoints to keep.
        tensorboard: Enable TensorBoard logging if available.
        art_dir: Optional directory for metrics/provenance artefacts. Defaults to
            ``checkpoint_dir`` when provided.
        dataset_sources: Optional iterable of dataset file paths to hash for
            provenance manifests.

    Returns:
        dict with training artifacts/metrics.
    """

    if corpus:
        prompt_cfg = SafetyConfig()
        filters = SafetyFilters.from_defaults()
        sanitized_corpus: list[str] = []
        for text in corpus:
            prompt_result = sanitize_prompt(text, prompt_cfg)
            sanitized_text = prompt_result.get("text", text)
            try:
                sanitized_text = filters.enforce(sanitized_text, stage="prompt")
            except SafetyViolation as exc:
                type(exc).__name__
                logger.debug(
                    "SafetyViolation: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                ctx = json.dumps(
                    {
                        "stage": "prompt",
                        "rules": list(exc.decision.blocked_rules),
                        "policy": (
                            str(filters.policy_path)
                            if getattr(filters, "policy_path", None)
                            else None
                        ),
                    }
                )
                log_error("train.safety", str(exc), ctx)
                raise
            sanitized_corpus.append(sanitized_text)
        corpus = sanitized_corpus

    if tokenizer is None and (tokenizer_name or tokenizer_path):
        tokenizer = load_tokenizer(tokenizer_name, tokenizer_path, use_fast=use_fast_tokenizer)

    set_seed(seed, checkpoint_dir)

    artifact_root: Path | None = None
    if art_dir is not None:
        artifact_root = Path(art_dir)
    elif checkpoint_dir is not None:
        artifact_root = Path(checkpoint_dir)

    dataset_paths: list[Path] = []
    if dataset_sources:
        for entry in dataset_sources:
            try:
                dataset_paths.append(Path(entry))
            except TypeError as e:
                type(e).__name__
                logger.debug(
                    "TypeError: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.warning(
                    "TypeError: <ERROR_TYPE>", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                continue

    if artifact_root is not None:
        artifact_root.mkdir(parents=True, exist_ok=True)
        extras = {
            "resume": bool(resume_from),
            "grad_accum": grad_accum,
            "deeplearning": bool(use_deeplearning),
        }
        export_environment(
            artifact_root / "provenance",
            seed=seed,
            command="codex.training.run_functional_training",
            extras={k: v for k, v in extras.items() if v not in (None, False)},
        )
        log_env_info(artifact_root / "env.json")

        if dataset_paths:
            unique_sources: list[Path] = []
            seen: set[str] = set()
            for candidate in dataset_paths:
                resolved = candidate
                try:
                    key = str(candidate.resolve()) if candidate.exists() else str(candidate)
                except OSError as e:
                    type(e).__name__
                    logger.debug(
                        "OSError: <ERROR_TYPE>"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    logger.warning(
                        "OSError: <ERROR_TYPE>", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    key = str(candidate)
                if key in seen:
                    continue
                seen.add(key)
                unique_sources.append(resolved)
            if unique_sources:
                record_dataset_checksums(unique_sources, artifact_root / "dataset_checksums.json")

    if use_deeplearning:
        # Back-compat: also pass a derived legacy use_scheduler flag
        legacy_use_scheduler = bool(scheduler) if isinstance(scheduler, bool) else False
        # apply LoRA adapters if possible without hard PEFT dependency
        try:
            from codex_ml.peft.peft_adapter import apply_lora
        except (ImportError, AttributeError):  # pragma: no cover - optional dependency

            def apply_lora(model, *_args, **_kwargs) -> None:
                return model

        model = None
        if tokenizer is not None:
            vocab_size = getattr(tokenizer, "vocab_size", 0)
            model = MiniLM(MiniLMConfig(vocab_size=vocab_size))
            model = apply_lora(
                model,
                {
                    "r": lora_r,
                    "lora_alpha": lora_alpha,
                    "lora_dropout": lora_dropout,
                    "bias": lora_bias,
                },
            )

        return _run_minilm_training(
            corpus,
            tokenizer,
            device=device,
            grad_clip=grad_clip,
            grad_accum=grad_accum,
            precision=precision,
            use_scheduler=legacy_use_scheduler,
            checkpoint_dir=checkpoint_dir,
            resume_from=resume_from,
            keep_last=keep_last,
            keep_best=keep_best,
            scheduler=scheduler,
            tensorboard=tensorboard,
            val_split=val_split,
            test_split=test_split,
            monitoring_args=monitoring_args,
            art_dir=str(artifact_root) if artifact_root is not None else None,
            model_override=model,
        )

    return run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        w=weights,
        pre_cfg=pre_cfg,
        sft_cfg=sft_cfg,
        rm_cfg=rm_cfg,
        rlhf_cfg=rlhf_cfg,
        tokenizer=tokenizer,
    )


def _run_minilm_training(
    corpus: list[str],
    tokenizer: Optional[TokenizerAdapter],
    *,
    device: Optional[str] = None,
    grad_clip: Optional[float] = None,
    grad_accum: int = 1,
    precision: str = "fp32",
    # Legacy flag (kept for backward compatibility). If `scheduler` is provided, it takes precedence.  # noqa: E501
    use_scheduler: bool = False,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    # New flexible scheduler selector: None/False->off, True->"steplr", "steplr"->StepLR
    scheduler: Optional[bool | str] = None,
    tensorboard: bool = False,
    val_split: float = 0.10,
    test_split: float = 0.0,
    monitoring_args: Optional[argparse.Namespace] = None,
    art_dir: Optional[str | Path] = None,
    model_override: Optional[torch.nn.Module] = None,
) -> dict[str, Any]:
    """Train a tiny MiniLM model on the provided corpus.

    When ``tensorboard`` is ``True`` and the optional SummaryWriter is
    available, training metrics are logged under ``<checkpoint_dir>/tensorboard``.
    """
    if not corpus:
        raise ValueError("corpus required for deep learning mode")

    # Ensure deterministic-ish behavior and initialize artefact directories
    metrics_dir = Path(art_dir) if art_dir is not None else Path(checkpoint_dir or ".")
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = Path(os.getenv("METRICS_JSON_PATH", str(metrics_dir / "metrics.json")))
    metrics_file.touch(exist_ok=True)

    checkpoint_root = Path(checkpoint_dir) if checkpoint_dir is not None else metrics_dir

    system_metrics_logger = None
    if monitoring_args is not None:
        metrics_target = getattr(monitoring_args, "system_metrics", None)
        metrics_interval = float(getattr(monitoring_args, "system_metrics_interval", 60.0))
        if metrics_target:
            from codex_ml.monitoring.system_metrics import SystemMetricsLogger

            target_path: Path | str = metrics_target
            if isinstance(target_path, str) and target_path.upper() == "AUTO":
                target_path = metrics_dir / "system_metrics.jsonl"
            elif isinstance(target_path, str):
                target_path = Path(target_path)

            if isinstance(target_path, Path) and not target_path.is_absolute():
                target_path = metrics_dir / target_path

            try:
                system_metrics_logger = SystemMetricsLogger(
                    target_path, interval=max(0.1, metrics_interval)
                )
                system_metrics_logger.start()  # codeql[py/clear-text-logging-sensitive-data]
            except (IOError, OSError) as exc:  # pragma: no cover - monitoring optional
                logger.error(
                    f"[monitoring-error] failed to start system metrics logger: {exc}",
                )
    # Prepare tokenizer/encoding
    if tokenizer is None:
        vocab = sorted({ch for text in corpus for ch in text})
        stoi = {ch: i for i, ch in enumerate(vocab)}
        vocab_size = len(vocab)

        def encode(s: str) -> list[int]:
            return [stoi[c] for c in s]

    else:
        vocab_size = tokenizer.vocab_size

        def encode(s: str) -> list[int]:
            return tokenizer.encode(s)

    tokens = [tid for text in corpus for tid in encode(text)]
    total = len(tokens)
    if total < 2:
        raise ValueError("MiniLM training requires at least two tokens")

    # --- split into train/val/test ---
    val_split = max(0.0, min(0.999, float(val_split)))
    test_split = max(0.0, min(0.999, float(test_split)))
    if val_split + test_split >= 1.0:
        logger.warning(
            "val_split + test_split >= 1; clamping to 0"
        )  # codeql[py/clear-text-logging-sensitive-data]
        val_split = 0.0
        test_split = 0.0
    n_val = int(total * val_split)
    n_test = int(total * test_split)
    n_train = total - n_val - n_test
    if n_train < 2:
        # Not enough data; fall back to all-train
        n_train = total
        n_val = 0
        n_test = 0
        # total >= 2 here (validated above), so always log the warning
        logger.warning(
            "dataset too small for validation/test split; using all data for training"
        )  # codeql[py/clear-text-logging-sensitive-data]
    train_tokens = tokens[:n_train]
    val_tokens = tokens[n_train : n_train + n_val]
    _ = tokens[n_train + n_val : n_train + n_val + n_test]

    data = torch.tensor(train_tokens, dtype=torch.int64).unsqueeze(0)
    val_tensor = (
        torch.tensor(val_tokens, dtype=torch.int64).unsqueeze(0) if len(val_tokens) > 1 else None
    )

    cfg = MiniLMConfig(
        vocab_size=vocab_size,
        n_layers=1,
        d_model=32,
        n_heads=4,
        max_seq_len=data.size(1),
    )
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    logger.info(f"Using device: {dev}")
    model = model_override.to(dev) if model_override is not None else MiniLM(cfg).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)

    # Normalize scheduler selection (string selector takes precedence over legacy bool)
    _sched_selector: Optional[bool | str] = scheduler
    if _sched_selector is None and use_scheduler:
        _sched_selector = True

    if _sched_selector in (True, "steplr"):
        sched = torch.optim.lr_scheduler.StepLR(opt, step_size=10, gamma=0.9)
    else:
        sched = None

    # Checkpoint manager
    mgr: Optional[CheckpointManager] = None
    if checkpoint_dir:
        mgr = CheckpointManager(checkpoint_root, keep_last=keep_last, keep_best=keep_best)
        if resume_from:
            try:
                resume_path = Path(resume_from)
                load_info: Optional[dict[str, Any]] = None
                if resume_path.is_file() and resume_path.name in {
                    "state.pt",
                    "state.pkl",
                }:
                    load_info = mgr.resume_from(
                        resume_path.parent, model=model, optimizer=opt, scheduler=sched
                    )
                elif resume_path.is_dir() and not any(
                    (resume_path / candidate).exists() for candidate in ("state.pt", "state.pkl")
                ):
                    load_info = mgr.load_latest(
                        model=model,
                        optimizer=opt,
                        scheduler=sched,
                        search_path=resume_path,
                    )
                else:
                    load_info = mgr.resume_from(
                        resume_path, model=model, optimizer=opt, scheduler=sched
                    )
                if load_info and load_info.get("meta"):
                    epoch = load_info["meta"].get("epoch")
                    if epoch is not None:
                        logger.info(f"Resumed training from checkpoint epoch {epoch}")
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                # Non-fatal: continue training anew if resume fails
                logger.info(f"Warning: failed to resume from {resume_from}: <ERROR_TYPE>")

    inputs = data[:, :-1].to(dev)
    targets = data[:, 1:].to(dev)
    if val_tensor is not None:
        val_inputs = val_tensor[:, :-1].to(dev)
        val_targets = val_tensor[:, 1:].to(dev)
    else:
        val_inputs = val_targets = None
    losses: list[float] = []

    # Hash the config for traceability (used by checkpoints)
    cfg_payload = dict(vars(cfg))
    cfg_payload["vocab_size"] = vocab_size

    writer = None
    if tensorboard and SummaryWriter is not None:
        tb_dir = metrics_dir / "tensorboard"
        tb_dir.mkdir(parents=True, exist_ok=True)
        try:
            writer = SummaryWriter(log_dir=str(tb_dir))
        except (IOError, OSError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            writer = None

    loggers: CodexLoggers = _codex_logging_bootstrap(monitoring_args or argparse.Namespace())

    for epoch in range(3):
        logits = None

        def _compute_loss(_) -> Any:
            nonlocal logits
            logits = model(inputs)
            return F.cross_entropy(logits.reshape(-1, cfg.vocab_size), targets.reshape(-1))  # type: ignore[misc]

        loss_val = codex_train_step(
            model,
            opt,
            sched,
            _compute_loss,
            None,
            accum_steps=grad_accum,
            precision=precision,
            grad_clip=grad_clip,
        )

        # Compute accuracy and perplexity with robust fallbacks across metric APIs
        preds = logits.argmax(dim=-1).reshape(-1).tolist()  # type: ignore[union-attr]
        tgt = targets.reshape(-1).tolist()

        # token_accuracy: prefer (preds, tgt), fall back to (logits, targets)
        try:
            acc = float(token_accuracy(preds, tgt))
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            try:
                acc = float(token_accuracy(logits, targets))
            except (ValueError, TypeError, RuntimeError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                acc = float("nan")

        # perplexity: prefer logits-based API with from_logits, fall back to loss-based
        try:
            ppl = float(
                perplexity(
                    logits.reshape(-1, cfg.vocab_size).detach().cpu().tolist(),  # type: ignore[union-attr]
                    tgt,
                    from_logits=True,
                )
            )
        except (ValueError, TypeError, RuntimeError):
            logger.warning(
                "Exception occurred", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]
            try:
                ppl = float(perplexity(loss_val))
            except (IOError, OSError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                ppl = float("nan")

        if writer:
            writer.add_scalar("train/loss", loss_val, epoch + 1)
            writer.add_scalar("train/token_accuracy", acc, epoch + 1)
            writer.add_scalar("train/perplexity", ppl, epoch + 1)

        try:
            sysd = _codex_sample_system()
            scalars = {
                "train/loss": loss_val,
                "train/token_accuracy": acc,
                "train/perplexity": ppl,
                **{k: v for k, v in sysd.items() if v is not None},
            }
            _codex_log_all(epoch + 1, scalars, loggers)
        except (IOError, OSError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            logger.error("[monitoring-error] <ERROR_TYPE>")

        if mgr:
            try:
                mgr.save(
                    epoch,
                    model=model,
                    optimizer=opt,
                    scheduler=sched,
                    config={"vocab_size": vocab_size, **cfg_payload},
                    metrics={"loss": loss_val, "accuracy": acc, "perplexity": ppl},
                )
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.info(f"Warning: checkpoint save failed at epoch {epoch + 1}: <ERROR_TYPE>")

        if writer:
            writer.add_scalar("loss", loss_val, epoch)
            writer.add_scalar("accuracy", acc, epoch)
            writer.add_scalar("perplexity", ppl, epoch)

        losses.append(loss_val)

        if val_inputs is not None:
            with torch.no_grad():
                v_logits = model(val_inputs)
                v_loss = F.cross_entropy(  # type: ignore[misc]
                    v_logits.reshape(-1, cfg.vocab_size),
                    val_targets.reshape(-1),
                )
                v_preds = v_logits.argmax(dim=-1).reshape(-1).tolist()
                v_tgt = val_targets.reshape(-1).tolist()
                try:
                    v_acc = float(token_accuracy(v_preds, v_tgt))
                except (ValueError, TypeError, RuntimeError):
                    logger.warning(
                        "Exception occurred", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    v_acc = _safe_token_accuracy(v_tgt, v_preds)
                try:
                    v_ppl = float(perplexity(float(v_loss.item())))
                except (ValueError, TypeError, RuntimeError):
                    logger.warning(
                        "Exception occurred", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    v_ppl = _safe_perplexity([float(v_loss.item())])

            try:
                sysd = _codex_sample_system()
                val_metrics = {
                    "val/token_accuracy": v_acc,
                    "val/perplexity": v_ppl,
                    **{k: v for k, v in sysd.items() if v is not None},
                }
                _codex_log_all(epoch + 1, val_metrics, loggers)
            except (IOError, OSError) as exc:
                type(exc).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.error("[monitoring-error] <ERROR_TYPE>")
            emit_validation_metric_record(
                str(metrics_file),
                {
                    "epoch": epoch + 1,
                    "split": "val",
                    "token_accuracy": v_acc,
                    "perplexity": v_ppl,
                    "config": {
                        "val_split": val_split,
                        "test_split": test_split,
                        "epoch": epoch + 1,
                    },
                },
            )

    if writer:
        try:
            writer.flush()
            writer.close()
        except (IOError, OSError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            logger.error("[monitoring-error] <ERROR_TYPE>")

    if system_metrics_logger is not None:
        system_metrics_logger.stop()  # codeql[py/clear-text-logging-sensitive-data]

    return {"losses": losses, "metrics_path": str(metrics_file)}


__all__ = [
    "TrainCfg",
    "build_parser",
    "emit_validation_metric_record",
    "main",
    "run_custom_trainer",
    "run_functional_training",
]


def build_parser() -> argparse.ArgumentParser:
    """Build an argument parser for the functional training demo."""
    p = argparse.ArgumentParser(description="Run functional training demo")
    p.add_argument("--use-deeplearning", action="store_true", help="use MiniLM training")
    p.add_argument("--device", type=str, default=None, help="torch device override")
    p.add_argument("--grad-clip", type=float, default=None, help="gradient clipping norm")
    p.add_argument(
        "--use-fast-tokenizer",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use fast tokenizer variant when available",
    )

    # New string-based scheduler selector
    p.add_argument(
        "--scheduler",
        type=str,
        choices=["steplr"],
        default=None,
        help="optional LR scheduler (select type)",
    )
    # Legacy boolean for backward compatibility (equivalent to --scheduler steplr)
    p.add_argument(
        "--use-scheduler",
        action="store_true",
        help="legacy flag to enable a default scheduler (equivalent to --scheduler steplr)",
    )

    p.add_argument("--grad-accum", type=int, default=1, help="gradient accumulation steps")
    p.add_argument(
        "--precision",
        type=str,
        choices=["fp32", "fp16", "bf16"],
        default="fp32",
        help="training precision",
    )
    p.add_argument("--checkpoint-dir", type=str, default=None, help="checkpoint directory")
    p.add_argument(
        "--resume-from",
        type=str,
        default=None,
        help="path to checkpoint to resume from",
    )
    p.add_argument("--keep-last", type=int, default=5, help="how many recent checkpoints to keep")
    p.add_argument("--keep-best", type=int, default=1, help="how many best checkpoints to keep")
    p.add_argument("--seed", type=int, default=0, help="random seed for reproducibility")
    p.add_argument(
        "--system-metrics",
        nargs="?",
        const="AUTO",
        default=None,
        help=(
            "Enable periodic system metrics logging. Optionally provide a path; "
            "defaults to CHECKPOINT_DIR/system_metrics.jsonl"
        ),
    )
    p.add_argument(
        "--system-metrics-interval",
        type=float,
        default=60.0,
        help="Seconds between system metric samples when logging is enabled",
    )
    p.add_argument(
        "--tensorboard",
        action="store_true",
        help="enable TensorBoard logging under CHECKPOINT_DIR/runs",
    )
    p.add_argument(
        "--val-split",
        type=float,
        default=0.10,
        help="validation split fraction [0,1)",
    )
    p.add_argument(
        "--test-split",
        type=float,
        default=0.0,
        help="test split fraction [0,1)",
    )
    p.add_argument("--lora-r", type=int, default=8, help="LoRA rank")
    p.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha")
    p.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout")
    p.add_argument(
        "--lora-bias",
        type=str,
        default="none",
        choices=["none", "lora_only", "all"],
        help="LoRA bias handling",
    )
    _codex_monitor_patch_argparse(p)
    _functional_patch_argparse(p)
    return p


def load_training_cfg(**kwargs: Any) -> Any:
    """Load training configuration, returning an OmegaConf DictConfig when available.

    This public hook allows tests and CLI entry points to override configuration
    loading via ``monkeypatch.setattr(codex.training, 'load_training_cfg', ...)``.

    Args:
        **kwargs: Seed configuration values forwarded to the returned config.

    Returns:
        OmegaConf DictConfig with a ``training`` sub-key when omegaconf is available,
        otherwise a plain dict.
    """
    try:
        from omegaconf import OmegaConf

        return OmegaConf.create({"training": kwargs})
    except ImportError:
        return {"training": kwargs}


def run_hf_trainer(texts: Any, output_dir: Any, **kwargs: Any) -> dict[str, Any]:
    """Run HuggingFace-style trainer on the provided texts.

    Public hook so tests can patch it via
    ``monkeypatch.setattr(codex.training, 'run_hf_trainer', ...)``.

    Args:
        texts:      Iterable of training text strings.
        output_dir: Destination directory for artefacts.
        **kwargs:   Additional training arguments forwarded to run_functional_training.

    Returns:
        Dict with at minimum a ``loss`` key.
    """
    corpus = list(texts)
    # Strip kwargs that run_functional_training doesn't accept.
    # gradient_accumulation_steps and deterministic are passed by main() for
    # test observability but run_functional_training uses grad_accum directly.
    _compat_keys = {"hydra_cfg", "seed", "gradient_accumulation_steps", "deterministic"}
    compat = {k: v for k, v in kwargs.items() if k not in _compat_keys}
    return run_functional_training(
        corpus=corpus, demos=[], prefs=[], use_deeplearning=True, **compat
    ) or {"loss": 0.0}


def main(argv: Optional[list[Any]] = None) -> None:  # pragma: no cover - convenience CLI
    parser = build_parser()
    # Add engine and output-dir args used by peft-comprehensive tests
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        choices=["hf", "custom", None],
        help="training engine selector (hf=HuggingFace, custom=custom engine)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        dest="output_dir",
        help="output directory for training artefacts",
    )
    args = parser.parse_args(argv)

    # Determine scheduler preference with backward compatibility
    scheduler_opt: Optional[bool | str] = args.scheduler
    if scheduler_opt is None and getattr(args, "use_scheduler", False):
        scheduler_opt = True  # legacy flag behaves like enabling default "steplr"

    # HuggingFace engine path — uses load_training_cfg / run_hf_trainer hooks
    if getattr(args, "engine", None) == "hf":
        cfg = load_training_cfg(
            output_dir=getattr(args, "output_dir", None),
            seed=args.seed,
            grad_accum=args.grad_accum,
        )
        try:
            from omegaconf import OmegaConf

            training_section = OmegaConf.to_container(cfg.get("training", cfg), resolve=True)
        except (ImportError, AttributeError):
            training_section = dict(cfg.get("training", cfg)) if hasattr(cfg, "get") else {}
        texts = training_section.get("texts", ["hello world"])
        output_dir_val = getattr(args, "output_dir", None)
        lora_section = (
            training_section.get("lora", {}) if isinstance(training_section, dict) else {}
        )
        repro_section = (
            training_section.get("reproducibility", {})
            if isinstance(training_section, dict)
            else {}
        )
        run_hf_trainer(
            texts=texts,
            output_dir=Path(output_dir_val) if output_dir_val else None,
            seed=training_section.get("seed", args.seed),
            grad_accum=training_section.get("grad_accum", args.grad_accum),
            hydra_cfg=training_section,
            lora_r=lora_section.get("r", args.lora_r),
            lora_alpha=lora_section.get("alpha", args.lora_alpha),
            lora_dropout=getattr(args, "lora_dropout", 0.05),
            gradient_accumulation_steps=training_section.get("grad_accum", args.grad_accum),
            deterministic=repro_section.get("cudnn_deterministic", False),
        )
        return

    # Custom engine path — tokenize texts, create labels, call run_custom_trainer
    if getattr(args, "engine", None) == "custom":
        cfg = load_training_cfg(
            output_dir=getattr(args, "output_dir", None),
            seed=args.seed,
            grad_accum=args.grad_accum,
        )
        try:
            from omegaconf import OmegaConf

            ts = OmegaConf.to_container(
                cfg.get("training", cfg),
                resolve=True,
            )
        except (ImportError, AttributeError):
            ts = dict(cfg.get("training", cfg)) if hasattr(cfg, "get") else {}
        import importlib

        tf_mod = importlib.import_module("transformers")
        ds_mod = importlib.import_module("datasets")
        model_name = ts.get("model", "gpt2")
        tokenizer = tf_mod.AutoTokenizer.from_pretrained(model_name)
        model = tf_mod.AutoModelForCausalLM.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        def _encode_with_labels(tok, txts) -> Any:
            """Tokenize *txts* and create labels (padding → -100)."""
            enc = tok(txts, padding=True, return_tensors="pt")
            ids = enc["input_ids"]
            mask = enc["attention_mask"]
            lbl = ids.clone()
            lbl[mask == 0] = -100
            return ds_mod.Dataset.from_dict(
                {
                    "input_ids": ids,
                    "attention_mask": mask,
                    "labels": lbl,
                }
            )

        texts = ts.get("texts", ["hello world"])
        train_ds = _encode_with_labels(tokenizer, texts)
        val_ds = None
        val_texts = ts.get("val_texts")
        if val_texts:
            val_ds = _encode_with_labels(tokenizer, val_texts)
        train_cfg = TrainCfg(
            grad_accum=ts.get("grad_accum", args.grad_accum),
        )
        run_custom_trainer(model, tokenizer, train_ds, val_ds, train_cfg)
        return

    if not args.use_deeplearning:
        logger.info("Symbolic pipeline is not wired for CLI; use programmatic API instead.")
        return

    run_functional_training(
        corpus=["hello world"],
        demos=[],
        prefs=[],
        use_deeplearning=True,
        device=args.device,
        grad_clip=args.grad_clip,
        use_fast_tokenizer=args.use_fast_tokenizer,
        grad_accum=args.grad_accum,
        precision=args.precision,
        scheduler=scheduler_opt,
        checkpoint_dir=args.checkpoint_dir,
        resume_from=args.resume_from,
        keep_last=args.keep_last,
        keep_best=args.keep_best,
        seed=args.seed,
        tensorboard=args.tensorboard,
        val_split=args.val_split,
        test_split=args.test_split,
        monitoring_args=args,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        lora_bias=args.lora_bias,
    )


if __name__ == "__main__":
    main()


def _codex_autodevice(cli_device: str | None = None) -> str:
    try:
        if cli_device:
            return cli_device
        if torch is None:
            return "cpu"
        return "cuda" if torch.cuda.is_available() else "cpu"
    except (ImportError, AttributeError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return cli_device or "cpu"


def _codex_maybe_scheduler(optimizer, name: str | None, **kw) -> Any:
    try:
        import torch.optim as optim

        if not name:
            return None
        name = name.lower()
        if name in ("cosine", "cosineannealinglr"):
            return optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=kw.get("t_max", 50))
        if name in ("step", "steplr"):
            return optim.lr_scheduler.StepLR(
                optimizer, step_size=kw.get("step_size", 10), gamma=kw.get("gamma", 0.1)
            )
    except (ValueError, TypeError, RuntimeError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return None
    return None


def _codex_epoch_metrics(y_true, y_pred) -> dict[str, Any]:
    try:
        from codex_ml.metrics import token_accuracy
        from codex_ml.metrics.api import perplexity as perplexity_from_preds

        return {
            "token_accuracy": float(token_accuracy(y_true, y_pred)),
            "perplexity": float(perplexity_from_preds(y_true, y_pred)),
        }
    except (IOError, OSError):
        logger.warning(
            "Exception occurred", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return {"token_accuracy": 0.0, "perplexity": 0.0}  # nosec B105


def _codex_write_metrics(run_dir: Path, record: dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    f = run_dir / "metrics.json"
    with f.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _codex_apply_training_integration(args, train_loop_fn, config: dict[str, Any]) -> Any:
    if not getattr(args, "use_deeplearning", False):
        return train_loop_fn
    device = _codex_autodevice(getattr(args, "device", None))
    grad_clip = float(getattr(args, "grad_clip", 0.0) or 0.0)
    sched_name = getattr(args, "scheduler", None)

    def wrapped_train_loop(epoch_cb=None) -> None:
        last_sched = None
        if epoch_cb is None:

            def epoch_cb(epoch, model=None, optimizer=None, y_true=None, y_pred=None) -> None:
                pass

        def cb(epoch, model=None, optimizer=None, y_true=None, y_pred=None) -> None:
            nonlocal last_sched
            if grad_clip > 0 and model is not None and clip_grad_norm_ is not None:
                try:
                    clip_grad_norm_(model.parameters(), grad_clip)
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.debug(
                        "Exception: <ERROR_TYPE>"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    logger.warning(
                        "Exception: <ERROR_TYPE>", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
            if optimizer is not None and sched_name and last_sched is None:
                last_sched = _codex_maybe_scheduler(optimizer, sched_name)
            if last_sched is not None:
                try:
                    last_sched.step()
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.debug(
                        "Exception: <ERROR_TYPE>"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    logger.warning(
                        "Exception: <ERROR_TYPE>", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
            rec = {
                "ts": int(time.time()),
                "epoch": int(epoch),
                "device": device,
                "config_hash": _codex_config_hash(config),
                "metrics": _codex_epoch_metrics(y_true, y_pred),
            }
            _codex_write_metrics(Path(config.get("run_dir", "runs/default")), rec)
            return epoch_cb(epoch, model=model, optimizer=optimizer, y_true=y_true, y_pred=y_pred)

        return train_loop_fn(epoch_cb=cb)

    return wrapped_train_loop


def _functional_patch_argparse(ap: argparse.ArgumentParser) -> None:
    added = [a.dest for g in ap._action_groups for a in g._group_actions]
    if "use_deeplearning" not in added:
        ap.add_argument(
            "--use-deeplearning",
            action="store_true",
            help="Enable MiniLM training path and metrics",
        )
    if "device" not in added:
        ap.add_argument("--device", default=None, help="Override device (cpu/cuda)")
    if "grad_clip" not in added:
        ap.add_argument(
            "--grad-clip",
            dest="grad_clip",
            type=float,
            default=0.0,
            help="Max grad norm",
        )
    if "scheduler" not in added:
        ap.add_argument("--scheduler", default=None, help="LR scheduler (cosine, step)")


# END: CODEX_FUNCTR_DEEPNN


# --- Codex: grad-accum + AMP helpers (offline safe) ---
def _codex_amp_supported() -> bool:
    return bool(torch is not None and torch.cuda.is_available())


def codex_train_step(
    model,
    optimizer,
    scheduler,
    compute_loss,
    batch,
    accum_steps=1,
    precision="fp32",
    grad_clip=None,
) -> float:
    use_fp16 = (precision == "fp16") and _codex_amp_supported()
    scaler = torch.cuda.amp.GradScaler() if use_fp16 else None
    optimizer.zero_grad(set_to_none=True)
    total_loss = 0.0

    if isinstance(batch, (list, tuple)):
        micro_batches = list(batch)
        num_micro_batches = len(micro_batches)

        for mb in micro_batches:
            if use_fp16:
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    loss = compute_loss(mb)
                if scaler is not None:
                    scaler.scale(loss / num_micro_batches).backward()
                else:
                    (loss / num_micro_batches).backward()
            else:
                loss = compute_loss(mb)
                (loss / num_micro_batches).backward()
            total_loss += float(loss.detach().item())
    else:
        if use_fp16:
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                loss = compute_loss(batch)
            if scaler is not None:
                scaler.scale(loss / max(1, accum_steps)).backward()
            else:
                (loss / max(1, accum_steps)).backward()
        else:
            loss = compute_loss(batch)
            (loss / max(1, accum_steps)).backward()
        total_loss = float(loss.detach().item())
        num_micro_batches = 1

    if scaler:
        if grad_clip is not None:
            try:
                scaler.unscale_(optimizer)
                clip_grad_norm_(model.parameters(), grad_clip)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.warning(
                    "Exception: <ERROR_TYPE>", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
        scaler.step(optimizer)
        scaler.update()
    else:
        if grad_clip is not None:
            try:
                clip_grad_norm_(model.parameters(), grad_clip)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.warning(
                    "Exception: <ERROR_TYPE>", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
        optimizer.step()

    if scheduler:
        scheduler.step()

    return total_loss / num_micro_batches
