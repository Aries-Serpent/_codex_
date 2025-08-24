#!/usr/bin/env python3
"""
scripts/deploy_codex_pipeline.py
Run the full symbolic training pipeline from CLI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RewardModelCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
)


def load_jsonl(path: Path):
    with path.open() as f:
        return [json.loads(line) for line in f]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", required=True, type=Path)
    p.add_argument("--demos", required=True, type=Path)
    p.add_argument("--prefs", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
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
        w=Weights(alpha=1.0, beta=1.0, gamma=0.05),
        pre_cfg=PretrainCfg(),
        sft_cfg=SFTCfg(),
        rm_cfg=RewardModelCfg(),
        rlhf_cfg=RLHFCfg(),
    )

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
