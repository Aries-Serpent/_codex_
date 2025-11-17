# Serving Reproducibility Playbook

The HHG logistics serving stack prioritizes deterministic inference and offline safety. Use this checklist whenever deploying or troubleshooting the Ray Serve application.

## Runtime Guardrails

1. **Deterministic seeds** – the service seeds Python, NumPy, and PyTorch (if available) from `cfg.seed`. Keep this value stable to reproduce metrics.  
2. **Offline-first defaults** – environment variables (`WANDB_MODE=offline`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`) are injected automatically when missing. Override explicitly only if you understand the downstream effects.  
3. **Configuration fingerprint** – each boot computes a SHA-256 hash of the fully resolved Hydra config. Persist this value alongside logs to confirm runs share the same topology.

## Suggested Workflow

```bash
# 1. Resolve the Hydra config (dry run)
python -m hhg_logistics.serve.app --cfg job.print_config=true

# 2. Launch Ray Serve locally (offline)
WANDB_MODE=offline TRANSFORMERS_OFFLINE=1 python -m hhg_logistics.serve.app serve.enabled=true

# 3. Tail request metrics (shared NDJSON + CSV formats)
tail -f .codex/metrics/serve-run-*.ndjson
```text

## Troubleshooting

- **Hash drift** – compare `config_sha256` between nodes. Mismatches usually mean diverging overrides or environment differences.  
- **Unexpected remote calls** – ensure `HF_HUB_OFFLINE` and `TRANSFORMERS_OFFLINE` remain set to "1". Hugging Face transformers fall back to cached artifacts under these flags.  
- **Seed coverage** – inspect the `seed_status` field in request logs; `False` values indicate a missing optional dependency. Install the library locally or accept nondeterministic paths with caution.

## Related References

- `src/hhg_logistics/serve/app.py` – runtime safeguards implementation.  
- `tests/hhg_logistics/serve/test_app.py` – guardrail regression tests.  
- `codex_ml/tracking/writers.py` – shared telemetry writers with deterministic schema ordering.
