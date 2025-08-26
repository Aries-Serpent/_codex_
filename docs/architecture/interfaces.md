<!-- BEGIN: CODEX_IFACE_DOCS -->
# Interfaces & Extensibility

This project defines abstract interfaces to allow **swappable implementations** without code changes.

## Interfaces
- `TokenizerAdapter` — encode/decode, vocab_size/pad_id/eos_id, optional batch_encode.
- `RewardModel` — score(prompt, completion, metadata?), optional batch_score.
- `RLAgent` — select_action, update(trajectory)->metrics, save/load.

## Swapping Implementations
1. Provide implementation import paths (e.g., `pkg.module:Class`) via environment:
   - `CODEX_TOKENIZER_PATH`, `CODEX_REWARD_PATH`, `CODEX_RL_PATH`
2. Or maintain a config like `configs/interfaces.yaml` and load them at runtime.

## Optional Plugins (entry points)
Projects can expose entry points under:
- `codex_ml.tokenizers`, `codex_ml.reward_models`, `codex_ml.rl_agents`

> Entry-point stubs are commented in `pyproject.toml` to avoid unintended side effects. Enable explicitly if desired.

## Testing Compatibility
- Run `pytest -q -k interfaces` after setting env vars to your implementations.
- Tests assert basic contract compliance.

> **Policy:** DO NOT ACTIVATE ANY GitHub Actions Online files. All validations run locally in the Codex environment.
