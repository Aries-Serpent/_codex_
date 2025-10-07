"""Unified training façade for Codex ML.

WHY:
- Remove drift between multiple training entry points; centralize features (resume, grad clipping, tracking hooks).

RISK:
- Signature differences vs legacy functions. Mitigation: provide thin adapters that raise DeprecationWarning.

ROLLBACK:
- Continue using legacy functions; adapters delegate here, so reverting is localized to this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional
import warnings
import os

try:
    import torch
    from torch.nn.utils import clip_grad_norm_
except Exception:  # pragma: no cover - optional dependency at import time
    torch = None  # type: ignore
    clip_grad_norm_ = None  # type: ignore

# Optional checkpoint core (if present)
try:
    from codex_ml.checkpointing import checkpoint_core  # type: ignore
except Exception:  # pragma: no cover
    checkpoint_core = None  # type: ignore


@dataclass
class UnifiedTrainingConfig:
    epochs: int = 1
    lr: float = 1e-3
    gradient_clip_norm: Optional[float] = None
    resume_from: Optional[str] = None  # path to checkpoint
    deterministic: bool = True
    device: Optional[str] = None  # "cpu" | "cuda" | None (auto)


def _set_determinism(seed: int = 0) -> None:
    if torch is None:
        return
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    # cuDNN determinism (may reduce perf)
    try:
        torch.use_deterministic_algorithms(True)  # PyTorch 2.x
    except Exception:
        pass
    try:
        import torch.backends.cudnn as cudnn

        cudnn.deterministic = True
        cudnn.benchmark = False
    except Exception:
        pass


def _as_device(requested: Optional[str]) -> str:
    if requested is not None:
        return requested
    if torch is not None and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def run_unified_training(
    cfg: UnifiedTrainingConfig,
    *,
    model,
    optimizer,
    loss_fn: Callable[[Any, Any], Any],
    train_loader: Iterable,
    val_loader: Optional[Iterable] = None,
    callbacks: Optional[List[Callable[[Dict[str, Any]], None]]] = None,
    rng_seed: int = 0,
    checkpoint_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Minimal, deterministic-friendly train loop with opt-in grad clipping and resume.
    Returns history: {"loss": [...], "val_loss": [...], "epochs": int}
    """
    if torch is None:
        raise RuntimeError("PyTorch is required for run_unified_training")

    if cfg.deterministic:
        _set_determinism(rng_seed)

    device = _as_device(cfg.device)
    model.to(device)

    # Optional resume
    start_epoch = 0
    if cfg.resume_from and checkpoint_core is not None:
        try:
            state, meta = checkpoint_core.load_checkpoint(  # type: ignore[attr-defined]
                cfg.resume_from, map_location=device
            )
            model.load_state_dict(state["model"])
            optimizer.load_state_dict(state["optimizer"])
            start_epoch = int(meta.get("epoch", 0)) + 1
        except Exception:
            # Soft-fail: continue from scratch if incompatible
            start_epoch = 0

    history_loss: List[float] = []
    history_vloss: List[float] = []

    for epoch in range(start_epoch, cfg.epochs):
        model.train()
        running = 0.0
        n = 0
        for xb, yb in train_loader:
            xb = xb.to(device) if hasattr(xb, "to") else xb
            yb = yb.to(device) if hasattr(yb, "to") else yb
            optimizer.zero_grad(set_to_none=True)
            preds = model(xb)
            loss = loss_fn(preds, yb)
            if hasattr(loss, "backward"):
                loss.backward()
            if cfg.gradient_clip_norm and clip_grad_norm_ is not None:
                clip_grad_norm_(model.parameters(), cfg.gradient_clip_norm)
            optimizer.step()
            val = float(loss.detach().cpu().item() if hasattr(loss, "detach") else float(loss))
            running += val
            n += 1
        epoch_loss = running / max(n, 1)
        history_loss.append(epoch_loss)

        # Simple val pass
        if val_loader is not None:
            model.eval()
            with torch.no_grad():
                vrunning = 0.0
                vn = 0
                for xb, yb in val_loader:
                    xb = xb.to(device) if hasattr(xb, "to") else xb
                    yb = yb.to(device) if hasattr(yb, "to") else yb
                    preds = model(xb)
                    vloss = loss_fn(preds, yb)
                    vval = float(
                        vloss.detach().cpu().item() if hasattr(vloss, "detach") else float(vloss)
                    )
                    vrunning += vval
                    vn += 1
                history_vloss.append(vrunning / max(vn, 1))

        # Optional checkpoint each epoch end
        if checkpoint_dir and checkpoint_core is not None:
            out_dir = os.path.join(checkpoint_dir, f"epoch-{epoch:04d}")
            meta = {"epoch": epoch, "loss": epoch_loss}
            try:
                checkpoint_core.save_checkpoint(  # type: ignore[attr-defined]
                    out_dir,
                    state={"model": model.state_dict(), "optimizer": optimizer.state_dict()},
                    meta=meta,
                    keep_last_k=5,
                )
            except Exception:
                # Non-fatal
                pass

        # Callbacks
        if callbacks:
            payload = {"epoch": epoch, "loss": epoch_loss}
            if history_vloss:
                payload["val_loss"] = history_vloss[-1]
            for cb in callbacks:
                try:
                    cb(payload)
                except Exception:
                    # Non-fatal callback
                    pass

    return {"loss": history_loss, "val_loss": history_vloss, "epochs": cfg.epochs}


# ---- Legacy shims (thin wrappers) ---------------------------------------------------------------
def train_loop(*args, **kwargs):
    warnings.warn(
        "train_loop is deprecated; use run_unified_training(cfg=..., ...)",
        category=DeprecationWarning,
        stacklevel=2,
    )
    return run_unified_training(*args, **kwargs)


def functional_training(*args, **kwargs):
    warnings.warn(
        "functional_training is deprecated; use run_unified_training(cfg=..., ...)",
        category=DeprecationWarning,
        stacklevel=2,
    )
    return run_unified_training(*args, **kwargs)
