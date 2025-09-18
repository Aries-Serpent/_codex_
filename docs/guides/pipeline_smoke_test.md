# Pipeline Smoke Test

The Codex training pipeline now ships with a deterministic implementation that
runs entirely offline. You can exercise it either through the lightweight
`tools/codex_cli.py` script or via the Hydra-powered CLI.

```bash
python tools/codex_cli.py train-all --no-fallback --print-summary
```

The command emits structured JSON summarising the pretraining, SFT, RLHF and
validation stages. By default the pipeline relies on the built-in
`WhitespaceTokenizer`, `HeuristicRewardModel`, and `BanditRLAgent`. You can swap
any component via environment variables:

```bash
export CODEX_TOKENIZER_PATH="codex_ml.interfaces.tokenizer:WhitespaceTokenizer"
export CODEX_REWARD_PATH="codex_ml.interfaces.reward_model:HeuristicRewardModel"
export CODEX_RL_PATH="codex_ml.interfaces.rl:BanditRLAgent"
```

Setting `CODEX_PIPELINE_SEED` ensures reproducibility when introducing custom
components that use randomness. All stages log to the standard Python logging
system, so `LOG_LEVEL=DEBUG` highlights intermediate metrics when debugging test
failures.

## Hydra integration and configuration

The default Hydra configuration (`configs/config.yaml`) pulls in
`configs/pipeline_inputs/smoke.yaml`. To run the pipeline step through Hydra use:

```bash
python -m codex_ml.cli.main pipeline.steps=[pipeline] hydra.run.dir=.
```

The step reads the following keys from the `pipeline.inputs` block:

| Key | Description | Defaults |
| --- | --- | --- |
| `corpus` | List of documents used in the pretraining stage. Empty entries are removed and an error is raised if no documents remain. | Required |
| `demos` | List of `{prompt, completion}` mappings for supervised fine-tuning. | Required |
| `pairwise` | List of `{label, chosen, rejected, preference}` mappings used for RLHF comparisons. | Required |
| `weights` | Numeric weights for combining stage metrics (`alpha`, `beta`, `gamma`). | `{1.0, 1.1, 0.05}` |
| `pretraining` | `model_size` label and `context_length` integer. | `placeholder`, `2048` |
| `sft` | `batch_size`, `learning_rate`, `epochs` for the SFT stage. | `16`, `1e-4`, `2` |
| `rlhf` | `algorithm`, `kl_penalty`, `ppo_epochs` for the RL agent. | `PPO`, `0.05`, `2` |
| `validation` | Thresholds for `syntax_ok`, `logic_ok`, `security_ok`, `perf_ok`. Values must be between 0 and 1. | `0.8`, `0.8`, `0.9`, `0.6` |
| `synth_prompts` | Optional list of prompts used to produce synthetic follow-up responses. | `[]` |
| `components` | Optional overrides for the tokenizer, reward model, or RL agent using `module:Class` strings and optional kwargs (must be JSON serialisable). | `{}` |
| `seed` | Deterministic seed for synthetic augmentations. | `${CODEX_PIPELINE_SEED:-1337}` |
| `summary_path` | File that receives the JSON summary. | `${CODEX_PIPELINE_SUMMARY:-.codex/pipeline/summary.json}` |
| `log_summary` | When `true`, emits a structured JSON log entry at INFO level. | `true` |

If the configuration is incomplete (for example, missing demonstrations or
negative weights) the pipeline raises a `ValueError` describing the offending
field. Passing `log_summary=false` suppresses the INFO log entry and emits a
DEBUG line instead, which can be useful when keeping logs terse in CI. The
environment overrides applied during execution are scoped to the pipeline run
and automatically restored afterwards, preventing bleed-through to other tests.
