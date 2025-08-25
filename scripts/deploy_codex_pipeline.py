#!/usr/bin/env python3
"""scripts/deploy_codex_pipeline.py
Run the full symbolic training pipeline from CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RewardModelCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
)


def load_jsonl(path: Path) -> list[Any]:
    """Load newline-delimited JSON objects from ``path``."""

    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--corpus", required=True, type=Path, help="Text corpus, one entry per line"
    )
    p.add_argument(
        "--demos", required=True, type=Path, help="JSONL demonstrations file"
    )
    p.add_argument(
        "--prefs", required=True, type=Path, help="JSONL pairwise preferences file"
    )
    p.add_argument(
        "--output-dir", required=True, type=Path, help="Directory to write artifacts"
    )
    p.add_argument("--alpha", type=float, default=1.0, help="Alpha weight")
    p.add_argument("--beta", type=float, default=1.0, help="Beta weight")
    p.add_argument("--gamma", type=float, default=0.05, help="Gamma weight")
    args = p.parse_args()

    corpus = [
        line.strip() for line in args.corpus.read_text().splitlines() if line.strip()
    ]
    demos = load_jsonl(args.demos)
    prefs = load_jsonl(args.prefs)
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=[tuple(p) for p in prefs],
        w=Weights(alpha=args.alpha, beta=args.beta, gamma=args.gamma),
        pre_cfg=PretrainCfg(),
        sft_cfg=SFTCfg(),
        rm_cfg=RewardModelCfg(),
        rlhf_cfg=RLHFCfg(),
    )

    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
