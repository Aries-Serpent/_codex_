# BEGIN: CODEX_TRAIN_LOOP
"""Minimal training loop with telemetry, LoRA support and checkpoints."""

from __future__ import annotations

import argparse
import contextlib
import json
import logging
import math
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence

import torch
from codex_ml.monitoring.codex_logging import write_ndjson
from codex_ml.registry.models import get_model
from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint
from codex_ml.utils.env import environment_summary
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.repro import record_dataset_checksums, set_reproducible
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset

try:  # optional dependency
    import mlflow

    _HAS_MLFLOW = True
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore
    _HAS_MLFLOW = False

from codex_ml.telemetry.server import start_metrics_server

logger = logging.getLogger("codex_ml.train_loop")

ART_DIR = Path("artifacts/metrics")
CHECKPOINT_ROOT = Path("artifacts/checkpoints")


def _resolve_seed(seed: int | None) -> int:
    """Return a deterministic seed, defaulting to ``1234`` when unset."""

    if seed is None:
        return 1234
    try:
        value = int(seed)
    except (TypeError, ValueError):
        value = 1234
    if value == 0:
        return 1234
    return value


def _ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def record_metrics(
    phase: str,
    epoch: int,
    metrics: Dict[str, Any],
    cfg_hash: str,
    notes: str = "training",
    art_dir: Path | None = None,
) -> None:
    if art_dir is None:
        art_dir = ART_DIR
    art_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": _ts(),
        "phase": phase,
        "epoch": epoch,
        "metrics": metrics,
        "cfg_hash": cfg_hash,
        "notes": notes,
        "git_commit": environment_summary().get("git_commit"),
    }
    out_list = art_dir / "metrics.json"
    prev: List[Dict[str, Any]] = []
    if out_list.exists():
        try:
            prev = json.loads(out_list.read_text(encoding="utf-8"))
            if not isinstance(prev, list):
                prev = []
        except Exception:
            prev = []
    prev.append(payload)
    out_list.write_text(json.dumps(prev, indent=2), encoding="utf-8")
    out_ndjson = art_dir / "metrics.ndjson"
    write_ndjson(out_ndjson, payload)


class ToyDataset(Dataset[torch.Tensor]):
    """A deterministic dataset of token sequences for smoke tests."""

    def __init__(self, *, num_samples: int, seq_len: int, vocab_size: int, seed: int) -> None:
        generator = torch.Generator().manual_seed(seed)
        tokens = torch.randint(0, vocab_size, (num_samples, seq_len), generator=generator)
        self.inputs = tokens
        self.targets = torch.roll(tokens, shifts=-1, dims=1)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return self.inputs.shape[0]

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.inputs[index], self.targets[index]


@dataclass
class TrainingState:
    epoch: int = 0
    global_step: int = 0


def _resolve_device(device: str | None) -> torch.device:
    if device:
        if device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(device)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _resolve_dtype(dtype: Any | None) -> torch.dtype | None:
    if dtype is None:
        return None
    if isinstance(dtype, torch.dtype):
        return dtype
    try:
        return getattr(torch, str(dtype))
    except AttributeError:
        return None


def _autocast(device: torch.device, enabled: bool, dtype: torch.dtype | None):
    if not enabled or not hasattr(torch, "autocast"):
        return contextlib.nullcontext()
    try:
        return torch.autocast(device_type=device.type, dtype=dtype)  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - autocast unavailable
        return contextlib.nullcontext()


def _find_latest_checkpoint(path: Path) -> Path | None:
    if not path.exists():
        return None
    candidates = sorted(path.glob("epoch_*/metadata.json"))
    if not candidates:
        return None
    latest_meta = candidates[-1]
    return latest_meta.parent


def run_training(
    *,
    epochs: int,
    grad_accum: int,
    mlflow_enable: bool = False,
    mlflow_uri: str = "file:./mlruns",
    mlflow_experiment: str = "codex",
    telemetry_enable: bool = False,
    telemetry_port: int = 8001,
    seed: int | None = None,
    art_dir: Path | None = None,
    dataset_sources: Sequence[Path | str] | None = None,
    model_name: str = "MiniLM",
    model_cfg: Dict[str, Any] | None = None,
    lora: bool = False,
    lora_cfg: Dict[str, Any] | None = None,
    learning_rate: float = 5e-4,
    batch_size: int = 8,
    device: str | None = None,
    dtype: Any | None = None,
    amp: bool = False,
    amp_dtype: Any | None = None,
    checkpoint_dir: Path | None = None,
    resume: bool = False,
) -> None:
    """Run a deterministic toy training loop."""

    resolved_seed = _resolve_seed(seed)
    set_reproducible(resolved_seed)
    random.seed(resolved_seed)
    if art_dir is None:
        art_dir = ART_DIR
    export_environment(art_dir, seed=resolved_seed, command="codex_ml.train_loop")
    if dataset_sources:
        paths = [Path(p) for p in dataset_sources]
        record_dataset_checksums(paths, art_dir / "dataset_checksums.json")

    cfg_hash = "toy-train-loop-v2"
    if telemetry_enable:
        start_metrics_server(port=telemetry_port)

    if mlflow_enable and _HAS_MLFLOW:
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment(mlflow_experiment)
        mlflow.start_run()
        mlflow.log_params({"epochs": epochs, "grad_accum": grad_accum, "model": model_name})

    device_obj = _resolve_device(device)
    dtype_obj = _resolve_dtype(dtype)

    model_kwargs: Dict[str, Any] = dict(model_cfg or {})
    model_kwargs.setdefault("device", str(device_obj))
    if dtype_obj is not None:
        model_kwargs.setdefault("dtype", dtype_obj)
    if lora:
        model_kwargs["lora"] = {"enabled": True, **(lora_cfg or {})}
    model = get_model(model_name, model_kwargs)
    model.to(device_obj)
    if dtype_obj is not None:
        model = model.to(dtype=dtype_obj)

    optimiser = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimiser, T_max=max(epochs, 1))
    scaler = torch.cuda.amp.GradScaler(enabled=amp and device_obj.type == "cuda")

    dataset = ToyDataset(
        num_samples=64,
        seq_len=16,
        vocab_size=(getattr(model, "cfg", None).vocab_size if hasattr(model, "cfg") else 128),
        seed=resolved_seed,
    )
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    state = TrainingState(epoch=0, global_step=0)
    if checkpoint_dir is None:
        checkpoint_dir = CHECKPOINT_ROOT / model_name
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    if resume:
        latest = _find_latest_checkpoint(checkpoint_dir)
        if latest is not None:
            metadata = load_checkpoint(
                model=model,
                optimizer=optimiser,
                scheduler=scheduler,
                ckpt_dir=latest,
                map_location=str(device_obj),
            )
            state.epoch = int(metadata.get("epoch", 0)) + 1
            state.global_step = int(metadata.get("global_step", 0))
            logger.info("Resumed from checkpoint %s", latest)

    git_commit = environment_summary().get("git_commit") or "unknown"

    for ep in range(state.epoch, epochs):
        model.train()
        running_loss = 0.0
        running_acc = 0.0
        batches = 0
        optimiser.zero_grad(set_to_none=True)
        for batch_inputs, batch_targets in loader:
            batch_inputs = batch_inputs.to(device_obj)
            batch_targets = batch_targets.to(device_obj)
            batches += 1
            with _autocast(device_obj, amp, _resolve_dtype(amp_dtype)):
                logits = model(batch_inputs)
                loss = F.cross_entropy(logits.view(-1, logits.size(-1)), batch_targets.view(-1))
            loss_to_step = loss / max(1, grad_accum)
            if scaler.is_enabled():
                scaler.scale(loss_to_step).backward()
            else:
                loss_to_step.backward()
            if batches % grad_accum == 0:
                if scaler.is_enabled():
                    scaler.step(optimiser)
                    scaler.update()
                else:
                    optimiser.step()
                optimiser.zero_grad(set_to_none=True)
                scheduler.step()
                state.global_step += 1
            running_loss += loss.detach().item()
            with torch.no_grad():
                preds = logits.argmax(dim=-1)
                running_acc += (preds == batch_targets).float().mean().item()
        epoch_steps = max(1, len(loader))
        metrics = {
            "loss": running_loss / epoch_steps,
            "acc": running_acc / epoch_steps,
            "ppl": math.exp(min(20.0, running_loss / epoch_steps)),
            "grad_accum": grad_accum,
        }
        record_metrics("epoch_end", ep, metrics, cfg_hash, art_dir=art_dir)
        logger.info("epoch %s metrics=%s", ep, metrics)
        if mlflow_enable and _HAS_MLFLOW:
            mlflow.log_metrics(metrics, step=ep)
        ckpt_path = checkpoint_dir / f"epoch_{ep:04d}"
        save_checkpoint(
            model=model,
            optimizer=optimiser,
            scheduler=scheduler,
            out_dir=ckpt_path,
            metadata={
                "epoch": ep,
                "global_step": state.global_step,
                "seed": resolved_seed,
                "git": git_commit[:7] if git_commit else "unknown",
            },
        )

    if mlflow_enable and _HAS_MLFLOW:
        mlflow.end_run()


def main() -> None:  # pragma: no cover - CLI wrapper
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--grad-accum", type=int, default=1)
    ap.add_argument("--model", dest="model_name", default="MiniLM")
    ap.add_argument("--learning-rate", type=float, default=5e-4)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--checkpoint-dir", type=Path, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--lora", action="store_true")
    args = ap.parse_args()
    run_training(
        epochs=args.epochs,
        grad_accum=args.grad_accum,
        model_name=args.model_name,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        seed=args.seed,
        checkpoint_dir=args.checkpoint_dir,
        resume=args.resume,
        lora=args.lora,
    )


if __name__ == "__main__":
    main()
# END: CODEX_TRAIN_LOOP
