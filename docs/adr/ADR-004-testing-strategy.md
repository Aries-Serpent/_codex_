# ADR-004: Multi-Layer Testing: Unit + Integration + Regression + Property + Fuzz + Chaos

**Status:** Accepted
**Date:** 2025-01-15
**Deciders:** codex-ml platform team
**Technical Story:** Gap 45 context — comprehensive testing strategy formalising the existing multi-layer approach

---

## Context

ML codebases present unique testing challenges compared to conventional software:

1. **Statistical correctness** — functions may be deterministically correct but
   statistically wrong (e.g., a metric function that returns a value in range but
   with systematic bias). Unit tests with fixed fixtures do not catch this.
2. **System integration** — model serving, feature pipelines, drift monitors,
   circuit breakers, and CI/CD components interact across multiple process
   boundaries. Failures often manifest only at integration seams.
3. **Regression at the model level** — a code change that is logically correct
   can still cause a measurable accuracy regression on held-out data.
4. **Edge cases and adversarial inputs** — ML models and the pipelines around
   them receive arbitrary external inputs; fuzz testing is needed to find
   unexpected crash paths.
5. **Production resilience** — fault-tolerance code (circuit breakers, retry
   policies, graceful degradation) can only be verified by injecting faults.
   Conventional unit tests cannot exercise this.

A single testing layer cannot provide adequate confidence across all five
dimensions. The _codex_ project had organically accumulated tests in multiple
directories; this ADR formalises and standardises the multi-layer approach.

---

## Decision

We adopt **six explicit test layers**, each in its own `tests/<layer>/`
directory, each with a clearly scoped purpose:

### Layer 1: Unit Tests (`tests/unit/`)

- Tests for individual functions and classes in isolation.
- All external dependencies are mocked.
- Must run in < 5 s per file on developer hardware; entire unit suite < 60 s.
- Enforced by `pytest -m unit` marker and checked in pre-commit.

### Layer 2: Integration Tests (`tests/integration/`)

- Tests for interactions between two or more components across a real or
  lightweight process boundary (e.g., pipeline stage handoffs, database reads,
  HTTP calls to a local test server).
- May use real filesystem, SQLite, or in-process HTTP mocks; no external
  network calls.
- Run in CI on every PR; may be skipped on `--fast` local developer runs.

### Layer 3: Regression Tests (`tests/regression/`)

- Tests that assert model quality metrics (accuracy, F1, AUC) on held-out
  evaluation datasets do not fall below established baselines.
- Baselines are committed to the repository and updated deliberately via
  `make update-regression-baselines`.
- Executed in CI on main branch merges and nightly; not required on feature
  branch PRs unless model code changed.

### Layer 4: Property-Based Tests (`tests/property/`)

- Uses [Hypothesis](https://hypothesis.readthedocs.io/) to generate
  structured random inputs that explore the boundary of invariants.
- Covers statistical properties: PSI/JSD monotonicity, circuit breaker state
  machine transitions for arbitrary failure sequences, serialisation round-trips.
- Hypothesis shrinking produces minimal failing examples that aid debugging.

### Layer 5: Fuzz Tests (`tests/fuzz/`)

- Mutation-based fuzzing of parser and serialisation surfaces that accept
  external input (config parsers, API request deserialisers, log ingestors).
- Uses Hypothesis's `binary()` and `text()` strategies plus structured-input
  fuzzing with `hypothesis-jsonschema`.
- Primary goal: find crashes, not verify correctness.

### Layer 6: Chaos Tests (`tests/chaos/`)

- Fault-injection tests that verify resilience layer behaviour under simulated
  failures: network partition, service timeout, memory pressure.
- Each test in this layer explicitly injects a fault (monkey-patching `socket`,
  raising `TimeoutError`, or using `unittest.mock` to simulate failure sequences)
  and asserts that the system degrades gracefully rather than crashing.
- Required for circuit breaker, retry, and graceful degradation code paths that
  cannot be reached by conventional integration tests.

### Cross-Cutting Tooling

| Concern | Tool |
|---|---|
| Test framework | `pytest` (all layers) |
| Property/fuzz generation | `hypothesis` |
| Type checking (pre-commit) | `mypy --strict` on `src/` |
| Config validation (pre-commit) | `python -m omegaconf.cfg_validator` |
| Mutation testing | `mutmut` — measures suite quality by surviving mutations |
| Coverage enforcement | `pytest-cov` with `--cov-fail-under=80` on unit+integration |

Pre-commit hooks gate `mypy` and config validation on every commit; regression,
property, fuzz, and chaos layers are gated only in CI to keep local iteration
fast.

---

## Consequences

**Positive:**
- ~270+ tests across 6 layers provide defence-in-depth; a failure caught by
  property tests signals a class of bugs, not just one instance.
- Clear layer separation makes test suite navigation predictable; contributors
  know exactly where to add a test for a given concern.
- Mutation testing with `mutmut` identifies tests that pass despite killing a
  mutant — surfacing weak assertions before they miss real bugs in production.
- Chaos tests are the only reliable way to verify resilience code; their
  existence is a direct enabler of ADR-002's guarantees.

**Negative / Trade-offs:**
- Six layers require contributors to learn the purpose and conventions of each
  layer; onboarding documentation is essential.
- Regression test baselines can become stale if updated carelessly; the
  `make update-regression-baselines` workflow must be protected by a pull
  request review requirement.
- Chaos tests are inherently non-deterministic when injecting timing-dependent
  failures; they may produce flaky results on heavily loaded CI runners. The
  `@pytest.mark.flaky(reruns=3)` marker is permitted exclusively for chaos tests.

---

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| **Single flat `tests/` directory** | Files become impossible to navigate beyond ~50 tests; no structural signal about test purpose or execution cost. |
| **BDD-style only (behave/pytest-bdd)** | BDD is excellent for acceptance tests but adds Gherkin overhead inappropriate for unit and property tests; not the right fit for a platform/infrastructure codebase. |
| **Integration-test-only** | Would miss unit-level regressions in statistical functions (drift metrics, EvalGate thresholds) that do not manifest until production traffic is introduced. |
| **No chaos/fault-injection tests** | Resilience code (ADR-002) cannot be verified by black-box integration tests alone; fault injection is the only way to exercise OPEN and HALF-OPEN circuit breaker states in a deterministic test. |
