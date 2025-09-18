<!-- BEGIN: CODEX_IFACE_DOCS -->

# Interfaces & Extensibility

This project defines abstract interfaces to allow **swappable implementations** without code changes.

## Interfaces

- `TokenizerAdapter` — encode/decode, vocab_size/pad_id/eos_id, optional batch_encode.
- `RewardModel` — evaluate(prompt, completion, metadata?), learn(data)->metrics, optional batch_evaluate.
- `RLAgent` — act, update(trajectory)->metrics, save/load.

## Swapping Implementations

1. Provide implementation import paths (e.g., `pkg.module:Class`) via environment:
   - `CODEX_TOKENIZER_PATH`, `CODEX_REWARD_PATH`, `CODEX_RL_PATH`
   - Example:

     ```bash
     export CODEX_TOKENIZER_PATH="codex_ml.interfaces.tokenizer:WhitespaceTokenizer"
     export CODEX_REWARD_PATH="codex_ml.interfaces.reward_model:HeuristicRewardModel"
     export CODEX_RL_PATH="codex_ml.interfaces.rl:BanditRLAgent"
     ```

     The helper :func:`codex_ml.interfaces.get_component` reads these variables
     and instantiates the referenced classes.
1. Or maintain a config like `configs/interfaces.yaml` and load them at runtime.

   The repository ships with a default mapping in `configs/interfaces.example.yaml`
   that wires built‑in components suitable for offline CI:

   ```yaml
   tokenizer:
     path: codex_ml.interfaces.tokenizer:WhitespaceTokenizer
     kwargs:
       lowercase: false
   reward_model:
     path: codex_ml.interfaces.reward_model:HeuristicRewardModel
     kwargs: {}
   rl_agent:
     path: codex_ml.interfaces.rl:BanditRLAgent
     kwargs: {}
   ```

   To register your own components, either edit this file or override the
   corresponding `CODEX_*` environment variables with `module:Class` paths and
   optional JSON‑encoded kwargs.

## Optional Plugins (entry points)

Projects can expose entry points under:

- `codex_ml.tokenizers`, `codex_ml.reward_models`, `codex_ml.rl_agents`

> Entry-point stubs are commented in `pyproject.toml` to avoid unintended side effects. Enable explicitly if desired.

## Testing Compatibility

- Run `pytest -q -k interfaces` after setting env vars to your implementations.
- Tests assert basic contract compliance.

> **Policy:** DO NOT ACTIVATE ANY GitHub Actions Online files. All validations run locally in the Codex environment.
