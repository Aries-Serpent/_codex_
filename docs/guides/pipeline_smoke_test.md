# Pipeline Smoke Test

The Codex training pipeline now ships with a deterministic implementation that
runs entirely offline.  To execute the full flow locally use the provided CLI:

```bash
python tools/codex_cli.py train-all --no-fallback --print-summary
```

The command emits structured JSON summarising the pretraining, SFT, RLHF and
validation stages.  By default the pipeline relies on the built-in
`WhitespaceTokenizer`, `HeuristicRewardModel`, and `BanditRLAgent`.  You can swap
any component via environment variables:

```bash
export CODEX_TOKENIZER_PATH="codex_ml.interfaces.tokenizer:WhitespaceTokenizer"
export CODEX_REWARD_PATH="codex_ml.interfaces.reward_model:HeuristicRewardModel"
export CODEX_RL_PATH="codex_ml.interfaces.rl:BanditRLAgent"
```

Setting `CODEX_PIPELINE_SEED` ensures reproducibility when introducing custom
components that use randomness.  All stages log to the standard Python logging
system, so `LOG_LEVEL=DEBUG` highlights intermediate metrics when debugging test
failures.
