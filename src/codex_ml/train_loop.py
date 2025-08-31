# BEGIN: CODEX_TRAIN_LOOP
"""Toy training loop with evaluation hooks and metrics persistence.

Usage::

    python -m codex_ml.train_loop --epochs 3

Metrics are written under ``artifacts/metrics`` where two files are created:

``metrics.json``
    A list containing all metric payloads for easy inspection.

``metrics.ndjson``
    A newline-delimited variant suitable for streaming analytics.

This is a best-effort integration: if your project has an existing trainer,
adapt the callback pattern below and invoke :func:`record_metrics`.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from codex_ml.eval.metrics import perplexity, token_accuracy

ART_DIR = Path("artifacts/metrics")
ART_DIR.mkdir(parents=True, exist_ok=True)


def _ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def record_metrics(
    phase: str,
    epoch: int,
    metrics: Dict[str, Any],
    cfg_hash: str,
    notes: str = "toy-eval",
) -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": _ts(),
        "phase": phase,
        "epoch": epoch,
        "metrics": metrics,
        "config_hash": cfg_hash,
        "notes": notes,
    }
    # write list for back-compat
    out_list = ART_DIR / "metrics.json"
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
    # append NDJSON for streaming analytics
    out_ndjson = ART_DIR / "metrics.ndjson"
    with out_ndjson.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload) + "\n")


def demo_epoch(epoch: int, grad_accum: int = 1) -> Dict[str, float]:
    """Simulate a training epoch with gradient accumulation.

    This toy loop splits the synthetic dataset into ``grad_accum`` micro-batches
    and pretends to step an optimiser once per accumulation cycle. Metrics are
    computed over the full epoch. The number of optimiser steps is returned for
    introspection in tests.
    """

    random.seed(42 + epoch)
    targets = [random.randint(0, 4) for _ in range(100)]
    preds: list[int] = []
    micro = max(1, len(targets) // max(1, grad_accum))
    steps = 0
    for i in range(0, len(targets), micro):
        batch_t = targets[i : i + micro]
        batch_p = [
            t if random.random() < (0.4 + 0.15 * epoch) else random.randint(0, 4) for t in batch_t
        ]
        preds.extend(batch_p)
        steps += 1
    acc = token_accuracy(preds, targets)
    logits = []
    for t in targets:
        base = [0.0] * 5
        base[t] = 1.0 + 0.3 * epoch
        logits.append(base)
    ppl = perplexity(logits, targets, from_logits=True)
    return {"acc": acc, "ppl": ppl, "grad_accum": grad_accum, "steps": steps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument(
        "--grad-accum",
        type=int,
        default=1,
        help="accumulate gradients over N steps",
    )
    args = ap.parse_args()
    cfg_hash = "c898a1161dce426c3f46d5b5f09fd0544abc292a4be5076ecf0d75af2bce2a9c"
    best = {"epoch": -1, "acc": -1.0}
    for ep in range(args.epochs):
        m = demo_epoch(ep, grad_accum=args.grad_accum)
        record_metrics("epoch_end", ep, m, cfg_hash)
        if m["acc"] > best["acc"]:
            best = {"epoch": ep, "acc": m["acc"]}
    # evaluate "best checkpoint" = best epoch metrics
    record_metrics(
        "best_checkpoint",
        best["epoch"],
        {"acc": best["acc"], "ppl": None},
        cfg_hash,
        notes="best-of-toy",
    )
    print(f"Saved metrics.json; best epoch={best['epoch']} acc={best['acc']:.3f}")


if __name__ == "__main__":
    main()
# END: CODEX_TRAIN_LOOP
