## Summary
- add CLI `--engine` option to select Hugging Face Trainer or custom loop
- enforce step-aware MLflow metrics and add batch tokenizer encode
- introduce reproducibility helper, WAL-enabled logging, dataset manifests, telemetry fallback, and checkpoint checksums

## Testing
- `python -m pre_commit run --files <changed>`
- `ruff check` / `black --check` / `isort --check-only`
- `pytest tests/test_tokenizer_batch_encode.py tests/test_mlflow_step_logging.py tests/test_repro_determinism.py tests/test_sqlite_wal.py tests/test_checkpoint_checksum.py tests/test_telemetry_degrade.py -q -p no:cov --override-ini addopts=""`

## Risks
- HF Trainer path minimally wired; further integration may require additional flags
- WAL mode requires short reader transactions to avoid locks

## Rollback
- revert commits `feat: add deterministic utilities and hf trainer option` and `chore: remove old workflows`
