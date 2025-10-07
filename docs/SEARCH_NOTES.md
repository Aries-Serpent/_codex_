# Comparative Pattern Search Notes

**Scope:** Public documentation and widely cited discussions only. No cost-incurring or account-gated services were accessed.

## Sources Consulted (examples)
- PyTorch reproducibility and DataLoader determinism:
  - https://docs.pytorch.org/docs/stable/notes/randomness.html
  - https://docs.pytorch.org/docs/stable/data.html
- PyTorch checkpoint patterns:
  - https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html
- MLflow tracking / URIs:
  - https://mlflow.org/docs/latest/ml/tracking/
  - https://mlflow.org/docs/3.1.3/ml/tracking/server/
- Weights & Biases offline environment variables:
  - https://docs.wandb.ai/guides/track/environment-variables/
  - https://docs.wandb.ai/support/run_wandb_offline/
- Pytest warning capture (for deprecations):
  - https://docs.pytest.org/en/stable/how-to/capture-warnings.html

## Notes on Constraints
- External search used only to confirm **patterns** (not to import code).
- Where project expectations differed (e.g., `WANDB_ENABLE`), we aligned with documented envs:
  - Prefer `WANDB_MODE=offline` or `WANDB_DISABLED=true` for explicit offline behavior.
- All references are mirrored in docs for offline reading later.
