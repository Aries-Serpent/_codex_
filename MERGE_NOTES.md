Changes:
- Added engine switch to CLI and HF trainer exposure.
- Enforced MLflow metric steps and added batch tokenizer encode.
- Introduced reproducibility helper and SQLite WAL mode.
- Capability-gated telemetry, dataset manifest writer, checkpoint checksums.
Risks:
- Existing formatting and test failures in repository.
Rollback:
- Revert commit.
