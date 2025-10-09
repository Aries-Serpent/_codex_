# Hydra sweeps & defaults (Codex)

Codex uses Hydra defaults with `_self_` **first**, which preserves Hydra-1.0 semantics.
This repo’s tests assume that ordering; keep it stable to avoid breakage.

## Quick usage

```bash
# Compose with base config
python -m codex_ml.cli config show

# Example sweep (learning rate x batch size)
python -m codex_ml.cli config sweep \
  --overrides 'train.lr=1e-4,5e-4,1e-3 train.batch_size=16,32'
```

### Notes
- `_self_` ordering: put it **first** to keep current behavior.
- Use environment variables or `--overrides` to vary run-time params.
- See `conf/examples/sweep_offline.yaml` for an offline-friendly template.
