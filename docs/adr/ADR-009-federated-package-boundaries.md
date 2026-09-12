# ADR-009: Federated Package Boundaries

**Status:** Accepted
**Date:** 2026-09-12

## Context

The monorepo is introducing independently distributable federation primitives while
existing `codex_ml` imports remain in use. Without explicit boundaries, shared contracts
can acquire implementation dependencies, telemetry can become framework-bound, and an
extraction can silently break callers.

The current federated packages are:

- `codex-contracts` (`codex_contracts`), containing dependency-free interoperability
  contracts; and
- `codex-ml-telemetry` (`codex_ml_telemetry`), containing framework-neutral health,
  metrics, and Prometheus export helpers;
- `codex-ml-evaluation` (`codex_evaluation`), containing dependency-free evaluation
  contracts, a scalar runner, and lazy legacy metric adapters; and
- `codex-ml-lora` (`codex_lora`), containing backend-neutral LoRA contracts and lazy
  PEFT and legacy adapters.

## Decision

1. **Keep contracts at the bottom of the dependency graph.** `codex_contracts` has no
   runtime dependencies and must not import `codex_ml`, `codex`,
   `cognitive_brain`, or `aries_serpent_core`.
2. **Keep feature boundaries import-light.** The base installs of
   `codex_ml_telemetry`, `codex_evaluation`, and `codex_lora` have no runtime
   dependencies. Heavy or legacy implementations are resolved only through optional
   extras or lazy adapters.
3. **Keep telemetry framework-neutral.** The base `codex_ml_telemetry` install has no
   runtime dependencies. Prometheus support remains an optional extra; HTTP framework
   response adaptation stays in consumers.
4. **Expose deliberate package roots.** Only names listed in each package's `__all__`
   are the supported public API. Internal modules and implementation types are not
   federation contracts.
5. **Version wire contracts independently.** Package versions follow semantic
   versioning. Serialized envelopes also carry `schema_version`; readers reject
   unsupported versions rather than guessing.
6. **Migrate additively.** Existing `codex_ml` telemetry, metric, evaluation, and PEFT
   entry points remain supported while consumers adopt the standalone packages. Lazy
   adapters provide bounded bridges until their compatibility gates permit removal.
7. **Make ownership explicit.** Custom-agent ownership uses the exact active names
   documented in the repository's `agents/AGENT_MASTER_REFERENCE.md`:
   `orchestrator-agent` for the contract boundary,
   `performance-monitor-agent` for telemetry,
   `ml-validation-suite-agent` for evaluation and LoRA behavior,
   `reference-updater-agent` for compatibility adapters, and
   `unified-doc-agent` for canonical documentation. `security-audit-agent` reviews
   trust-boundary or payload changes.

The canonical dependency graph, public API inventory, compatibility matrix, and
telemetry extraction design are maintained in
[Federated Package Boundaries](../architecture/federated_package_boundaries.md).

## Consequences

### Positive

- Federation consumers can depend on small packages without importing the monolith.
- Wire compatibility and Python import compatibility are evaluated separately.
- Optional observability backends do not become mandatory runtime dependencies.
- Ownership and migration gates remain visible during extraction.

### Negative

- Compatibility tests and adapters must be maintained during the migration window.
- Similar health types may coexist until callers explicitly migrate their semantics.
- Breaking a serialized schema requires a deliberate schema and package-version change.

## Alternatives Considered

### Keep all primitives in `codex_ml`

Rejected because independent consumers would inherit unrelated ML and framework
dependencies.

### Create one shared utilities package

Rejected because it would mix stable wire contracts with operational telemetry and
encourage an unbounded dependency surface.

### Replace legacy imports immediately

Rejected because the existing import path is in active use and an atomic removal would
create avoidable downstream breakage.
