Changes:
- Added engine switch to CLI and HF trainer exposure.
- Enforced MLflow metric steps and added batch tokenizer encode.
- Introduced reproducibility helper and SQLite WAL mode.
- Capability-gated telemetry, dataset manifest writer, checkpoint checksums.
- Restored missing docstrings and __all__ exports; fixed test imports.
Risks:
- Existing formatting and test failures in repository.
Rollback:
- Revert commit.

## Summary
- add CLI `--engine` option to select Hugging Face Trainer or custom loop
- enforce step-aware MLflow metrics and add batch tokenizer encode
- introduce reproducibility helper, WAL-enabled logging, dataset manifests, telemetry fallback, and checkpoint checksums
- restored missing docstrings and __all__ exports; fixed test imports

## Testing
- `python -m pre_commit run --files <changed>`
- `ruff check` / `black --check` / `isort --check-only`
- `pytest tests/test_tokenizer_batch_encode.py tests/test_mlflow_step_logging.py tests/test_repro_determinism.py tests/test_sqlite_wal.py tests/test_checkpoint_checksum.py tests/test_telemetry_degrade.py -q -p no:cov --override-ini addopts=""`

## Risks
- HF Trainer path minimally wired; further integration may require additional flags
- WAL mode requires short reader transactions to avoid locks
- existing formatting and test failures in repository

## Rollback
- revert commits `feat: add deterministic utilities and hf trainer option` and `chore: remove old workflows`
- revert commit
