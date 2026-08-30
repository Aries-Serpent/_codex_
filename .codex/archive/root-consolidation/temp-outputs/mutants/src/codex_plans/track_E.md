# Track E: Golden Harness & Tool Truthfulness Plan

This plan defines the implementation tasks for integrating golden harness honesty and tool-truthfulness mechanisms into the Codex environment.

## Honesty Metadata
- Implement an `honesty` module that records every externally visible statement in the workflow. Provide functions like `record_statement(content: str, category: str, verified: bool)` and `flush_honesty_metadata(path: str) -> None` to persist metadata to `artifacts/honesty_metadata.json`.
- Annotate all phases of the workflow (training, evaluation, audit, regression) with calls to record_statement, specifying whether each statement is `VERIFIED`, `INFERRED`, or `PLANNED`.
- Add a self-check that writes an honesty summary to the final report.

## Tool Trace & Truthfulness
- Add a `tool_trace` module to capture every invocation of local tools (pytest, nox, semgrep, etc.). Each call should record the tool name, arguments, exit code, and timestamp in `artifacts/tool_trace.ndjson`.
- Wrap existing calls to subprocesses or custom runners in a `run_local_tool()` helper that records before and after metadata and returns the captured output.
- Add cross-validation that checks consistency between gate results and tool trace, raising an error or warning if mismatched.

## Golden Harness Status & Prompts
- Implement an aggregator that combines RA policy status, honesty metadata, and tool truthfulness into a unified `golden_harness_status.json` with an overall state (green/yellow/red).
- Create prompt templates in `prompts/orchestrator/` for each status. These will drive Codex Orchestrator behaviour when generating responses or tasks.
- Provide a script `scripts/print_golden_harness_snapshot.py` to display the current harness status for operators.

## Tests
- Add tests under `tests/honesty/` verifying that honesty metadata is recorded and flushed correctly. Include cases for verified and inferred statements.
- Add tests under `tests/tool_trace/` ensuring that tool invocation events are captured and that mismatches between gate results and tool trace trigger warnings.
- Ensure all tests run offline within the Codex environment via `nox -s audit` without triggering remote CI.

## Documentation
- Update `docs/explanation/golden_harness.md` to describe honesty labelling and tool trace collection. Provide examples of how to interpret `golden_harness_status.json` and integrate with audit reports.
- Document new CLI commands and modules in `reference` docs.
