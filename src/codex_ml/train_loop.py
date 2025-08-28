# BEGIN: CODEX_TRAIN_LOOP
"""Toy training loop with evaluation hooks and metrics persistence.

Usage:
    python -m codex_ml.train_loop --epochs 3

This is a best-effort integration: if your project has an existing trainer,
adapt the callback pattern below and invoke `record_metrics(...)`.
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


def demo_epoch(epoch: int) -> Dict[str, float]:
    # Create a toy prediction/target scenario where accuracy and ppl can improve
    random.seed(42 + epoch)
    targets = [random.randint(0, 4) for _ in range(100)]
    preds = [
        t if random.random() < (0.4 + 0.15 * epoch) else random.randint(0, 4)
        for t in targets
    ]
    acc = token_accuracy(preds, targets)
    # Build logits such that correct class probability improves per epoch
    logits = []
    for t in targets:
        base = [0.0] * 5
        base[t] = 1.0 + 0.3 * epoch
        logits.append(base)
    ppl = perplexity(logits, targets, from_logits=True)
    return {"acc": acc, "ppl": ppl}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=3)
    args = ap.parse_args()
    cfg_hash = "c898a1161dce426c3f46d5b5f09fd0544abc292a4be5076ecf0d75af2bce2a9c"
    best = {"epoch": -1, "acc": -1.0}
    for ep in range(args.epochs):
        m = demo_epoch(ep)
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
