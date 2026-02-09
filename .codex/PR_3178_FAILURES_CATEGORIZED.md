# Test Failures Categorized (Partial Run)

Log file: `.codex/test_run_complete_20260209_144719.log`

Note: Full test suite run was interrupted early; pytest did not emit detailed tracebacks.
Failure types will be categorized after a full run completes.

Observed failing files: 5 (partial run; one failure resolved)

## AssertionError (resolved)

- `tests/telemetry/test_sample_rate_gate.py`: sample rate zero now suppresses telemetry artifacts.

## Unknown (traceback needed)

- `tests/test_checkpoint_checksum.py`: 6 failure markers
- `tests/test_rag_end_to_end_pipeline.py`: 5 failure markers
- `tests/test_api_secret_filter.py`: 1 failure markers
- `tests/tokenization/test_tokenization_api_and_deprecation.py`: 1 failure markers
- `tests/integration/cli/test_cli_pipeline_integration.py`: 1 failure markers

### Sample lines

- `tests/test_api_secret_filter.py` -> `F`
- `tests/tokenization/test_tokenization_api_and_deprecation.py` -> `F`
- `tests/test_checkpoint_checksum.py` -> `FEFFFF`
- `tests/integration/cli/test_cli_pipeline_integration.py` -> `F`
- `tests/test_rag_end_to_end_pipeline.py` -> `FFFFF`
