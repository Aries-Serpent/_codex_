# Track C Workflow Orchestrator

This guide documents the offline Track C workflow that now drives capability execution in Codex. The workflow is designed to be deterministic, auditable, and reversible (each phase registers a rollback action).

## Six-Phase Workflow

1. **Preparation** – initialize offline context, seed phase notes, and register rollback hooks.
2. **Search & Mapping** – bind the capability to its search targets and task map.
3. **Best-Effort Construction** – build artifacts for the capability using offline-safe steps.
4. **Controlled Pruning** – prune duplicate or rule-violating artifacts without touching external systems.
5. **Error Capture** – consolidate the error taxonomy, invoke rollbacks, and mark the review checkpoint.
6. **Finalization** – emit a structured summary for downstream tooling and reports.

Each phase stores its rollback in the workflow context so that failures can be safely reverted.

## Capability Routing

The router maps capabilities and aliases to their phase configuration. Default mappings include:

- `tokenization` (aliases: `token`, `bpe`)
- `training` (alias: `train`)
- `evaluation` (alias: `eval`)

Use `run_capability("tokenization")` to execute all six phases with routing and rollback support. The router can be extended by registering a new `CapabilityPlan` with custom search targets, construction steps, and per-phase overrides.

## Error Taxonomy and Capture

- **ErrorRecord** – captures timestamp, phase, capability, step, exception type, message, and extra context.
- **record_error** – appends an `ErrorRecord` to the workflow context and tracks failing phases.
- **step_context** – context manager that records errors and optionally triggers rollback callbacks.

The **Error Capture** phase automatically runs queued rollbacks when errors are present so state is restored before finalization.

## CLI Entry Point

The offline CLI wrapper orchestrates the phases and applies gating:

```bash
python scripts/run_codex_workflow.py \
  --capability tokenization \
  --summary artifacts/workflow-summary.json \
  --require-phase-order
```

Flags:

- `--capability/-c` – capability to execute (can be passed multiple times).
- `--online` – opt out of offline mode (defaults to offline; not recommended).
- `--summary` – path to write a JSON summary of executed phases, artifacts, and errors.
- `--require-phase-order` – fails if phases did not complete in the canonical order.
- `--fail-on-error` – returns non-zero if any errors were recorded.

## Offline-First Expectations

- No external network calls are performed; `_gate_offline_mode` must succeed before execution.
- Tests under `tests/workflow/` validate phase ordering, routing, and error capture in offline mode.
- Rollback hooks ensure the workflow leaves no residual state when failures occur.
