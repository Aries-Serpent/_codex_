# Golden Harness Integration, Honesty, and Tool Truthfulness

The Golden Harness remains the contract for tracing and auditing training behaviour, supporting highly auditable offline ML and tool-based workflows. Its latest design ties together experiment tracking, honesty statements, local tool tracing, and RA (Readiness Assessment) policy signals—allowing operators to evaluate the readiness, reproducibility, and integrity of an offline run. Structured NDJSON format is used for traceability, auditability, and downstream scorecards, without requiring third-party platforms like MLflow or W&B.

## Experiment Tracking

- Use `start_run` / `finish_run` to bracket significant phases of your workflow.
- Emit metrics with `log_metric` so downstream auditors can calculate trends and performance metrics.
- Aggregate runs using `scripts/analyze_experiments.py`; the generated JSON feeds directly into the `experiment_summary` detector.
- All artifacts are kept local, enabling harness operation in air-gapped environments, while still retaining reproducibility evidence.

## Honesty Metadata

- Employ `codex_harness.honesty.HonestyRecorder` to capture every externally visible claim or commitment made during the workflow.
- Call `record_statement(content, category, verified)` during key phases (training, evaluation, audit, regression).
- Persist metadata with `flush()` (default location: `artifacts/honesty_metadata.json`). This artifact includes summary counts per category and a simple audit-ready summary.

## Tool Trace and Truthfulness

- Wrap local tool calls using `codex_harness.tool_trace.ToolTraceLogger.run_tool` to automatically capture:
    - tool name
    - arguments
    - stdout/stderr
    - timestamps
    - exit codes
- RA gate expectation results can be loaded from `artifacts/gates/ra_gate_results.json` to help detect mismatches between expected and observed outcomes.
- Tool call logs are stored in `artifacts/tool_trace.ndjson`. Downstream checks can verify coverage for utilities such as pytest, nox, semgrep, etc.

## Golden Harness Status Aggregation

- Use `codex_harness.golden_harness_status.compute_golden_harness_status` to aggregate key signals:
    - RA policy results (from `artifacts/gates/ra_policy.json` if available)
    - Honesty metadata completeness (`artifacts/honesty_metadata.json`)
    - Tool trace coverage and RA gate alignment (`artifacts/tool_trace.ndjson` and `artifacts/gates/ra_gate_results.json`)
- The resulting summary in `golden_harness_status.json` reports the overall state (**green**, **yellow**, or **red**) plus per-signal details:
    - **Green**: All required gates pass, honesty statements recorded, full tool trace present.
    - **Yellow**: Missing data or expected tool runs not yet traced.
    - **Red**: RA failures or explicit gate mismatches detected.

## Workflow Integration

- The `nox -s audit` session records honesty statements, traces tools (such as pytest and space audit make targets), and automatically produces the golden harness status file.
- For extended coverage, load additional RA gate expectations into `artifacts/gates/ra_gate_results.json` before initiating the audit session.

## Operator Guidance

- **Green**: Proceed with standard offline workflows; continue capturing honesty and trace data.
- **Yellow**: Backfill missing statements or tool runs. Re-run the audit before any promotion.
- **Red**: Halt automation. Inspect `golden_harness_status.json`, re-run gates with tracing, and document remediation before proceeding.

## Prompt Templates

- Orchestrator prompts in `prompts/orchestrator/` adapt run behaviour based on harness status:
    - `green.md`: Continues execution with logging.
    - `yellow.md`: Emphasizes mitigation and evidence backfill.
    - `red.md`: Stops promotion until failures are resolved or explicitly waived.