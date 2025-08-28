## $(date -u +%Y-%m-%d) — Codex Run
- Added pad_id and eos_id accessors to HFTokenizerAdapter.
- Surfaced monitoring exceptions in functional_training via stderr logging.
- Introduced --grad-accum support and metric logging in train_loop.
- CheckpointManager now writes system.json for hardware metadata.
- Registered codex-ml-cli entry point in pyproject.
- Updated README with offline CI instructions and codex-ml-cli usage.
- Added tests for tokenizer IDs, grad accumulation, and checkpoint system metadata.
- Added codex_seq_runner and run_codex_sequence utilities.
