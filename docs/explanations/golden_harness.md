# Golden Harness, Honesty, and Tool Truthfulness

The golden harness ties together honesty statements, local tool tracing, and RA policy signals so operators can understand the readiness of an offline run.

## Honesty metadata
- Use `codex_harness.honesty.HonestyRecorder` to capture every externally visible claim or commitment.
- Call `record_statement(content, category, verified)` during each workflow phase (training, evaluation, audit, regression).
- Persist metadata with `flush()` (default: `artifacts/honesty_metadata.json`). The file includes per-category counts and a simple summary for audits.

## Tool trace and truthfulness
- Wrap local tool calls with `codex_harness.tool_trace.ToolTraceLogger.run_tool` to automatically capture the tool name, arguments, stdout/stderr, timestamps, and exit codes.
- Optional RA gate expectations can be loaded from `artifacts/gates/ra_gate_results.json` to detect mismatches between expected and observed outcomes.
- Logs are appended to `artifacts/tool_trace.ndjson` so downstream checks can confirm coverage for pytest, nox, semgrep, and other utilities.

## Golden harness status aggregation
- `codex_harness.golden_harness_status.compute_golden_harness_status` combines:
  - RA policy results (from `artifacts/gates/ra_policy.json` when available)
  - Honesty metadata completeness (`artifacts/honesty_metadata.json`)
  - Tool trace coverage and RA gate alignment (`artifacts/tool_trace.ndjson` and `artifacts/gates/ra_gate_results.json`)
- The function emits `golden_harness_status.json` with an overall state (**green**, **yellow**, or **red**) plus per-signal details.
- **Green** requires passing RA gates, recorded honesty statements, and complete tool traces. **Yellow** indicates missing data or expected tool runs not yet traced. **Red** is raised for RA failures or explicit gate mismatches.

## Workflow integration
- The `nox -s audit` session now records honesty statements, traces pytest and the space audit make target, and writes a golden harness status file automatically.
- To extend coverage, load additional RA gate expectations into `artifacts/gates/ra_gate_results.json` before running the session.

## Operator guidance
- When the status is **green**, proceed with standard offline workflows but continue capturing honesty and trace data.
- If the status is **yellow**, backfill missing statements or tool runs and re-run the audit before promotion.
- On **red**, stop automation, inspect `golden_harness_status.json`, re-run gates with tracing enabled, and document remediation before proceeding.

## Prompt templates
- Status-aware orchestrator prompts live under `prompts/orchestrator/`:
  - `green.md` continues standard execution with logging intact.
  - `yellow.md` emphasizes mitigation and evidence backfill.
  - `red.md` halts promotion until failures are resolved or waived.
