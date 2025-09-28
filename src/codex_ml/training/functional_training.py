"""Simple fallback training loop for Codex models.

This module implements a minimal causal language model trainer for use
when the HuggingFace Trainer is unavailable or when running in a resource-
constrained environment.  It accepts raw text, tokenizes it using an
``AutoTokenizer``, and trains an ``AutoModelForCausalLM`` (or a provided
``torch.nn.Module``) with a standard cross-entropy loss.  A validation
split is optional, and metrics such as token accuracy and perplexity are
logged at the end of each epoch.

The loop supports gradient accumulation, deterministic seeding and
checkpoint saving via ``codex_ml.utils.checkpointing``.
"""

from __future__ import annotations

import json
import math
import random
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from codex_ml.models.utils.peft import apply_lora_if_available
from codex_ml.monitoring.system_metrics import start_metrics_logger
from codex_ml.monitoring.tb_writer import TBWriter
from codex_ml.utils.checkpointing import save_checkpoint
from codex_ml.utils.experiment_tracking_mlflow import _as_flat_params, maybe_mlflow
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.seeding import set_reproducible
from codex_ml.utils.train_helpers import clip_gradients, get_amp_scaler, maybe_autocast

torch, _HAS_TORCH = optional_import("torch")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if _HAS_TRANSFORMERS:
    AutoModelForCausalLM = transformers.AutoModelForCausalLM  # type: ignore[attr-defined]
    AutoTokenizer = transformers.AutoTokenizer  # type: ignore[attr-defined]
else:  # pragma: no cover - optional dependency
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]


@dataclass
class TrainConfig:
    model_name: str = "sshleifer/tiny-gpt2"
    epochs: int = 1
    batch_size: int = 32
    lr: float = 5e-5
    seed: int = 0
    gradient_accumulation_steps: int = 1
    max_length: int = 512
    checkpoint_dir: Optional[str] = None
    tensorboard: bool = False
    tensorboard_dir: Optional[str] = None
    mlflow_enable: bool = False
    mlflow_tracking_uri: Optional[str] = None
    amp_enable: bool = False
    amp_dtype: Optional[str] = None
    grad_clip_norm: Optional[float] = None
    lora_enable: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    wandb_enable: bool = False
    metrics_out: str = ".codex/metrics.ndjson"
    system_metrics_interval: float = 5.0


def train(
    texts: Iterable[str],
    *,
    config: TrainConfig,
    val_texts: Optional[Iterable[str]] = None,
    model: Optional[torch.nn.Module] = None,
) -> dict[str, float]:
    """Train a causal language model on raw ``texts``.

    Args:
        texts: Iterable of training strings.
        config: Training hyper-parameters.
        val_texts: Optional iterable of validation strings.
        model: Optional ``torch.nn.Module``.  If ``None`` an ``AutoModelForCausalLM``
            is loaded from ``config.model_name``.

    Returns:
        A dictionary of final metrics (token accuracy and perplexity).
    """
    if not (_HAS_TORCH and _HAS_TRANSFORMERS):
        raise ImportError("torch and transformers are required for training")

    # Deterministic seeding
    set_reproducible(config.seed)

    def _append_jsonl(path: Optional[Path], record: Dict[str, Any]) -> None:
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
        except Exception:  # pragma: no cover - best-effort logging
            pass

    # Load tokenizer and model
    tokenizer = load_from_pretrained(
        AutoTokenizer,
        config.model_name,
        revision=get_hf_revision(),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = model or load_from_pretrained(
        AutoModelForCausalLM,
        config.model_name,
        revision=get_hf_revision(),
    )
    model.train()

    if config.lora_enable:
        model = apply_lora_if_available(
            model,
            r=config.lora_r,
            alpha=config.lora_alpha,
            dropout=config.lora_dropout,
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr)

    checkpoint_root: Optional[Path] = None
    env_dir: Optional[Path] = None
    if config.checkpoint_dir:
        checkpoint_root = Path(config.checkpoint_dir)
        checkpoint_root.mkdir(parents=True, exist_ok=True)
        env_dir = checkpoint_root / "provenance"
        export_environment(env_dir, seed=config.seed, command="train.functional")

    base_metrics_dir = checkpoint_root or Path(".")

    metrics_path: Optional[Path]
    if config.metrics_out:
        metrics_path_candidate = Path(config.metrics_out)
        if not metrics_path_candidate.is_absolute():
            metrics_path = base_metrics_dir / metrics_path_candidate
        else:
            metrics_path = metrics_path_candidate
    else:
        metrics_path = None

    if config.tensorboard_dir:
        tb_path = Path(config.tensorboard_dir)
        if not tb_path.is_absolute():
            tb_path = base_metrics_dir / tb_path
    else:
        tb_path = (
            checkpoint_root / "tensorboard"
            if checkpoint_root is not None
            else base_metrics_dir / "tensorboard"
        )
    writer = TBWriter(config.tensorboard, str(tb_path))

    scaler = get_amp_scaler(config.amp_enable)

    # Tokenize the entire dataset once for simplicity
    def _prepare(batch_texts: Iterable[str]):
        enc = tokenizer(
            list(batch_texts),
            padding="max_length",
            truncation=True,
            max_length=config.max_length,
            return_tensors="pt",
        )
        return enc["input_ids"], enc["attention_mask"]

    train_ids, _ = _prepare(texts)
    val_ids, _ = _prepare(val_texts) if val_texts is not None else (None, None)

    optimizer.zero_grad(set_to_none=True)

    configured_metrics_path: Optional[Path] = metrics_path
    config_snapshot: Optional[Path] = None
    if config.mlflow_enable:
        base_dir = checkpoint_root if checkpoint_root is not None else Path(".codex")
        artifact_root = base_dir / "mlflow"
        artifact_root.mkdir(parents=True, exist_ok=True)
        metrics_path = artifact_root / "metrics.ndjson"
        if metrics_path.exists():
            try:
                metrics_path.unlink()
            except Exception:
                pass
        try:
            config_snapshot = artifact_root / "config.json"
            config_snapshot.write_text(
                json.dumps(asdict(config), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except Exception:
            config_snapshot = None
    else:
        metrics_path = configured_metrics_path

    def _append_metric(record: Dict[str, object]) -> None:
        if metrics_path is None:
            return
        try:
            with metrics_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, sort_keys=True) + "\n")
        except Exception:
            pass

    global_step = 0
    num_batches = math.ceil(len(train_ids) / config.batch_size)
    system_metrics_path = base_metrics_dir / "system_metrics.ndjson"
    stop_event = threading.Event()
    system_thread: Optional[threading.Thread] = None

    if config.system_metrics_interval > 0:
        try:
            system_thread = start_metrics_logger(
                interval_s=float(config.system_metrics_interval),
                write_fn=lambda payload: _append_jsonl(
                    system_metrics_path,
                    {"event": "system", **payload},
                ),
                stop_event=stop_event,
            )
        except Exception:
            system_thread = None

    run_name = f"run-{config.seed}"
    metrics: Dict[str, float] = {}
    with maybe_mlflow(
        enable=bool(config.mlflow_enable),
        run_name=run_name,
        tracking_uri=config.mlflow_tracking_uri,
    ) as mlf:
        if config.mlflow_enable:
            try:
                params = {
                    "model.name": config.model_name,
                    "training.lr": config.lr,
                    "training.batch_size": config.batch_size,
                    "training.epochs": config.epochs,
                    "training.grad_accum": config.gradient_accumulation_steps,
                    "training.amp": config.amp_enable,
                    "training.lora": config.lora_enable,
                }
                mlf.log_params(_as_flat_params(params))
            except Exception:
                pass

        grad_accum = max(int(config.gradient_accumulation_steps), 1)

        def _optimizer_step() -> None:
            scaler.unscale_(optimizer)
            if config.grad_clip_norm:
                clip_gradients(model.parameters(), float(config.grad_clip_norm))
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)

        for epoch in range(config.epochs):
            perm = list(range(len(train_ids)))
            random.shuffle(perm)
            step_since_update = 0
            for b in range(num_batches):
                start = b * config.batch_size
                end = start + config.batch_size
                idx = perm[start:end]
                batch = train_ids[idx].to(device)
                labels = batch.clone()
                with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                    outputs = model(batch, labels=labels)
                    raw_loss = outputs.loss
                    loss = raw_loss / grad_accum
                scaled_loss = scaler.scale(loss)
                scaled_loss.backward()
                step_since_update += 1

                if step_since_update % grad_accum == 0:
                    _optimizer_step()
                    step_since_update = 0

                global_step += 1
                if writer is not None or config.mlflow_enable:
                    try:
                        loss_value = float(raw_loss.detach().cpu().item())
                    except Exception:
                        try:
                            loss_value = float(loss.detach().cpu().item())
                        except Exception:
                            loss_value = None
                    if loss_value is not None:
                        if writer is not None:
                            try:
                                writer.add_scalar("train/loss", loss_value, global_step)
                            except Exception:
                                pass
                        if config.mlflow_enable:
                            try:
                                mlf.log_metrics({"train/loss": loss_value}, step=global_step)
                            except Exception:
                                pass
                            _append_metric(
                                {
                                    "phase": "train",
                                    "epoch": epoch + 1,
                                    "step": global_step,
                                    "loss": loss_value,
                                }
                            )

            if step_since_update != 0:
                _optimizer_step()

            if checkpoint_root is not None:
                ckpt_path = checkpoint_root / f"epoch-{epoch}.pt"
                save_checkpoint(str(ckpt_path), model, optimizer, None, epoch, {})

        with torch.no_grad():
            model.eval()
            train_tensor = train_ids.to(device)
            with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                logits = model(train_tensor).logits
            preds = logits.argmax(dim=-1)
            mask = train_tensor != tokenizer.pad_token_id
            acc = (preds[mask] == train_tensor[mask]).float().mean().item()
            loss_fn = torch.nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
            with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                train_loss_tensor = loss_fn(
                    logits.view(-1, model.config.vocab_size),
                    train_tensor.view(-1),
                )
            loss_val = float(train_loss_tensor.detach().cpu().item())
            ppl = math.exp(loss_val) if loss_val > 0 else float("inf")
            metrics = {"token_accuracy": acc, "perplexity": ppl}
            if val_ids is not None:
                val_tensor = val_ids.to(device)
                with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                    val_logits = model(val_tensor).logits
                val_preds = val_logits.argmax(dim=-1)
                val_mask = val_tensor != tokenizer.pad_token_id
                metrics["val_token_accuracy"] = (
                    (val_preds[val_mask] == val_tensor[val_mask]).float().mean().item()
                )
                with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                    val_loss_tensor = loss_fn(
                        val_logits.view(-1, model.config.vocab_size),
                        val_tensor.view(-1),
                    )
                val_loss = float(val_loss_tensor.detach().cpu().item())
                metrics["val_perplexity"] = math.exp(val_loss) if val_loss > 0 else float("inf")
                if writer is not None:
                    try:
                        writer.add_scalar(
                            "val/perplexity", float(metrics["val_perplexity"]), global_step
                        )
                    except Exception:
                        pass
                if config.mlflow_enable:
                    try:
                        mlf.log_metrics(
                            {
                                "eval/perplexity": float(metrics["val_perplexity"]),
                                "eval/token_accuracy": float(metrics["val_token_accuracy"]),
                            },
                            step=global_step,
                        )
                    except Exception:
                        pass
                    _append_metric(
                        {
                            "phase": "eval",
                            "epoch": config.epochs,
                            "step": global_step,
                            "perplexity": float(metrics["val_perplexity"]),
                            "token_accuracy": float(metrics["val_token_accuracy"]),
                        }
                    )

        if config.mlflow_enable:
            try:
                final_payload = {
                    f"final/{k}": float(v)
                    for k, v in metrics.items()
                    if isinstance(v, (int, float))
                }
                if final_payload:
                    mlf.log_metrics(final_payload, step=global_step)
                    for key, value in final_payload.items():
                        _append_metric(
                            {
                                "phase": "final",
                                "metric": key,
                                "value": value,
                                "step": global_step,
                            }
                        )
                artifacts: list[Path] = []
                if metrics_path and metrics_path.exists():
                    artifacts.append(metrics_path)
                if config_snapshot and config_snapshot.exists():
                    artifacts.append(config_snapshot)
                if env_dir and env_dir.exists():
                    artifacts.append(env_dir)
                for artifact in artifacts:
                    try:
                        mlf.log_artifact(str(artifact))
                    except Exception:
                        continue
            except Exception:
                pass

    if stop_event is not None and system_thread is not None:
        try:
            stop_event.set()
            system_thread.join(timeout=5.0)
        except Exception:
            pass

    if writer is not None:
        try:
            writer.flush()
            writer.close()
        except Exception:
            pass

    return metrics
