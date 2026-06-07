# Wave 3 / Wave 4 — Workflow-Dispatch Matrix

**Generated:** 2026-06-06T05:49:59Z  
**Mode:** workflow-dispatch only — NO in-session implementation  
**Context lock snapshot:**

| Field | Value |
|---|---|
| Wave 3 queued | 17, 18, 20, 21, 22, 23, 24, 28, 29, 30, 31 |
| Wave 4 queued | 32–45 |
| gap_id 19 | ✅ completed |
| gap_id 20 | ✅ completed (Wave 3) |
| gap_id 26 | ✅ completed |
| special_flags.needs_verification | [14, 27] |
| Mandatory dispatch (Wave 3) | 17, 18, 21, 23 |
| Optional dispatch (Wave 3) | 22, 24, 28, 29, 30, 31 |
| Mandatory dispatch (Wave 4) | 32–45 (full set) |

---

## Dispatch Matrix

> Legend — Effort: **S**=Small ≤1 hr · **M**=Medium 1-4 hr · **L**=Large 5-10 hr · **XL**=XLarge 10+ hr  
> Dispatch type: **WF**=workflow_dispatch · **AG**=custom-agent  
> Batch: tasks in the same batch may run in parallel.

### Wave 3 — P2 Items

| gap_id | Title | Effort | Dispatch type | Workflow / Agent | Objective | Expected Artifacts | Success Criteria | Batch |
|--------|-------|--------|---------------|------------------|-----------|--------------------|-----------------|-------|
| 17 | Implement data drift monitoring | L | AG | `ml-validation-suite-agent` | Implement `src/codex_ml/monitoring/data_drift.py` using PSI/KL-divergence metrics; wire into `train_loop.py`; add CI job | `workbench/evidence/gap17_data_drift.md` · CI run log · drift detector unit tests (≥5) passing | Evidence file present; drift detector importable; ≥5 tests green | A |
| 18 | Add model drift detection | L | WF+AG | `model-drift-retrain.yml` (`dry_run:true`) + `ml-validation-suite-agent` | Verify existing drift-score pipeline covers concept-drift; extend if needed; CI evidence | `workbench/evidence/gap18_model_drift.md` · workflow run artifact | `model-drift-retrain.yml` run concludes success with drift score logged; gap18 evidence file present | A |
| 21 | Build comprehensive regression test suite | L | AG | `test-enhancement-agent` | Create `tests/regression/` with ≥20 regression scenarios covering model outputs, API contracts, data pipeline | `tests/regression/` directory committed · `workbench/evidence/gap21_regression_suite.md` · CI run log | `pytest tests/regression/` exits 0; ≥20 test functions; evidence file present | A |
| 22 | Add mutation testing with mutmut | M | WF | `mutation-testing.yml` (workflow_dispatch) | Run mutation testing workflow; capture mutation score; target ≥50% | `workbench/evidence/gap22_mutation_testing.md` · CI artifact `mutation-report-*` | Workflow run conclusion=success; mutation score ≥50%; evidence file present | A |
| 23 | Implement automated integration tests | L | AG | `integration-test-runner` | Create `tests/integration/` suite covering inter-service boundaries (API↔model, monitoring↔alerting); wire into CI | `tests/integration/` directory · `workbench/evidence/gap23_integration_tests.md` · CI run log | `pytest tests/integration/` exits 0; ≥10 integration test functions; evidence file present | A |
| 24 | Add performance benchmarking suite | M | AG | `performance-monitor-agent` | Create `benchmarks/` directory with benchmark harness (training throughput, inference latency, memory); CI job producing JSON report | `benchmarks/` dir · benchmark JSON report artifact · `workbench/evidence/gap24_benchmarks.md` | Benchmarks run to completion; report artifact uploaded; evidence file present | B |
| 28 | Add Sigstore verification for critical dependencies | M | AG | `security-audit-agent` | Implement `scripts/security/sigstore_verify.py`; add CI job to verify Sigstore signatures on release artifacts | `scripts/security/sigstore_verify.py` · `workbench/evidence/gap28_sigstore.md` · CI run log | Sigstore check script present; CI job green; evidence file present | B |
| 29 | Implement circuit breakers for external services | M | AG | `ci-resilience-emergency-response-agent` | Implement `src/codex/resilience/circuit_breaker.py` (half-open/closed/open states); unit tests; integrate with external service calls | `src/codex/resilience/circuit_breaker.py` · `tests/unit/test_circuit_breaker.py` · `workbench/evidence/gap29_circuit_breaker.md` | Circuit breaker importable; ≥8 unit tests green; evidence file present | B |
| 30 | Add exponential backoff retry logic | S | AG | `ci-auto-healer-agent` | Implement `src/codex/resilience/retry.py` with exponential backoff + jitter; wire into HTTP clients; unit tests | `src/codex/resilience/retry.py` · `tests/unit/test_retry.py` · `workbench/evidence/gap30_retry.md` | Retry module importable; ≥5 unit tests green; evidence file present | B |
| 31 | Build graceful degradation mechanisms | M | AG | `ci-resilience-emergency-response-agent` | Implement `src/codex/resilience/degradation.py` with fallback chains; integrate with alerting + monitoring; unit tests | `src/codex/resilience/degradation.py` · `tests/unit/test_degradation.py` · `workbench/evidence/gap31_degradation.md` | Degradation module importable; ≥6 unit tests green; evidence file present | B |

### Wave 4 — P3 Items

| gap_id | Title | Effort | Dispatch type | Workflow / Agent | Objective | Expected Artifacts | Success Criteria | Batch |
|--------|-------|--------|---------------|------------------|-----------|--------------------|-----------------|-------|
| 32 | Clean up 1,152 TODOs/FIXMEs/stubs | XL | AG | `repository-hygiene-agent` | Systematically resolve or document all TODO/FIXME/stub annotations; produce cleanup report | `workbench/evidence/gap32_todo_cleanup.md` · diff summary · TODO count before/after | TODO count reduced by ≥50% (≤576); no new TODOs introduced; evidence file present | C |
| 33 | Add mypy to pre-commit hooks | S | WF | `mypy-baseline.yml` (workflow_dispatch) + `mypy-manager-agent` | Add mypy pre-commit hook in `.pre-commit-config.yaml`; ensure baseline passes | `.pre-commit-config.yaml` updated · `workbench/evidence/gap33_mypy_precommit.md` | `pre-commit run mypy` exits 0; mypy-baseline.yml workflow green; evidence file present | C |
| 34 | Implement automated docstring generation | M | AG | `documentation-quality-agent` | Configure `pydocstyle`/`darglint` + docstring generator (e.g. `autoDocstring` pattern); wire into CI | `workbench/evidence/gap34_docstrings.md` · CI run log | Docstring coverage > 60% on `src/`; CI docstring check green; evidence file present | C |
| 35 | Add schema validation to pre-commit | S | AG | `config-validator` | Add `check-jsonschema` / `pydantic` schema validation hook for YAML/JSON configs in `.pre-commit-config.yaml` | `.pre-commit-config.yaml` updated · `workbench/evidence/gap35_schema_validation.md` | `pre-commit run schema-validation` exits 0; evidence file present | C |
| 36 | Build continuous learning pipeline | XL | AG | `ml-validation-suite-agent` | Design and implement `src/codex_ml/continuous_learning/` pipeline: trigger on new data, retrain, eval gate, auto-promote | `src/codex_ml/continuous_learning/` package · `workbench/evidence/gap36_continuous_learning.md` · CI run log | Pipeline importable; ≥10 unit tests green; evidence file present | D |
| 37 | Implement A/B testing framework | L | AG | `ml-validation-suite-agent` | Implement `src/codex_ml/experiments/ab_testing.py` with statistical significance testing; integrate with model serving | `src/codex_ml/experiments/ab_testing.py` · `tests/unit/test_ab_testing.py` · `workbench/evidence/gap37_ab_testing.md` | A/B framework importable; ≥6 unit tests green; evidence file present | D |
| 38 | Add automated model retraining | L | WF+AG | `model-drift-retrain.yml` (`dry_run:false`, `force_retrain:true`) + `ml-validation-suite-agent` | Wire drift-triggered retraining into CI pipeline; validate retrain pipeline e2e (dry run first) | `workbench/evidence/gap38_auto_retrain.md` · workflow run artifact | `model-drift-retrain.yml` full run conclusion=success; retrain pipeline validated; evidence file present | D |
| 39 | Build feedback loop integration | L | AG | `cognitive-ooda-loop-agent` | Implement feedback ingestion (`src/codex_ml/feedback/`) wired to OODA loop; integrate with monitoring alerts | `src/codex_ml/feedback/` package · `workbench/evidence/gap39_feedback_loop.md` · CI run log | Feedback module importable; ≥6 unit tests green; evidence file present | D |
| 40 | Add fuzzing for critical code paths | L | AG | `test-enhancement-agent` | Integrate `atheris` or `hypothesis` fuzzing for tokenizer, config parser, API handlers; add CI job | `tests/fuzz/` directory · `workbench/evidence/gap40_fuzzing.md` · CI run log | Fuzz tests run to completion; no crashes on 10k iterations; evidence file present | E |
| 41 | Implement property-based testing expansion | M | AG | `test-enhancement-agent` | Expand `hypothesis` property-based tests across data transforms, model utilities; target ≥15 new property tests | `tests/property/` directory · `workbench/evidence/gap41_property_tests.md` | ≥15 property-based tests green; evidence file present | E |
| 42 | Add chaos engineering tests | L | AG | `integration-test-runner` | Implement `tests/chaos/` using `chaostoolkit` or custom fault injection; cover network/disk/memory failures | `tests/chaos/` directory · `workbench/evidence/gap42_chaos.md` · CI run log | Chaos tests run to completion; system recovers gracefully; evidence file present | E |
| 43 | Create video tutorials for key workflows | M | AG | `unified-doc-agent` | Create scripted tutorial outlines and accompanying docs for 5 key workflows; deposit in `docs/tutorials/` | `docs/tutorials/` directory (≥5 guides) · `workbench/evidence/gap43_tutorials.md` | ≥5 tutorial docs present in `docs/tutorials/`; evidence file present | F |
| 44 | Build interactive documentation with examples | L | AG | `unified-doc-agent` | Add runnable code examples to `docs/` (Jupyter-style or doctest blocks); set up MkDocs live examples | `docs/examples/` directory · `workbench/evidence/gap44_interactive_docs.md` | ≥10 runnable examples pass `doctest`/`pytest --doctest-glob`; evidence file present | F |
| 45 | Add architecture decision records (ADRs) | M | AG | `unified-doc-agent` | Create `docs/adr/` with ADRs covering 10 key architecture decisions; template + index | `docs/adr/` with ≥10 ADR files · `workbench/evidence/gap45_adrs.md` | ≥10 ADR files present; ADR index exists; evidence file present | F |

---

## Ordered Execution Batches

Batch ordering maximizes parallelism within lanes while respecting the dependency: Wave 3 must all be dispatched before Wave 4 batches may start (though Wave 4 C batches are independent of Wave 3 and can overlap).

```
BATCH A — Wave 3 Core (mandatory + adjacent; all independent — run in parallel)
  ├── gap 17  →  ml-validation-suite-agent         [Lane E]
  ├── gap 18  →  model-drift-retrain.yml + ml-validation-suite-agent  [Lane E]
  ├── gap 21  →  test-enhancement-agent             [Lane D]
  ├── gap 22  →  mutation-testing.yml               [Lane D]
  └── gap 23  →  integration-test-runner            [Lane D]

BATCH B — Wave 3 Resilience/Security (optional dispatch; all independent — run in parallel after Batch A dispatched)
  ├── gap 24  →  performance-monitor-agent          [Lane E]
  ├── gap 28  →  security-audit-agent               [Lane A]
  ├── gap 29  →  ci-resilience-emergency-response-agent  [Lane B/C]
  ├── gap 30  →  ci-auto-healer-agent               [Lane B/C]
  └── gap 31  →  ci-resilience-emergency-response-agent  [Lane B/C]

BATCH C — Wave 4 Code Quality (independent of Wave 3 results; run in parallel)
  ├── gap 33  →  mypy-baseline.yml + mypy-manager-agent  [Shared/Lane D]
  ├── gap 34  →  documentation-quality-agent        [Docs]
  └── gap 35  →  config-validator                   [Shared]

BATCH D — Wave 4 ML Advanced (after Batch A completes for dependency safety)
  ├── gap 36  →  ml-validation-suite-agent          [Lane E]
  ├── gap 37  →  ml-validation-suite-agent          [Lane E]
  ├── gap 38  →  model-drift-retrain.yml + ml-validation-suite-agent  [Lane E]
  └── gap 39  →  cognitive-ooda-loop-agent          [Lane E]

BATCH E — Wave 4 Testing (parallel with D)
  ├── gap 40  →  test-enhancement-agent             [Lane D]
  ├── gap 41  →  test-enhancement-agent             [Lane D]
  └── gap 42  →  integration-test-runner            [Lane D]

BATCH F — Wave 4 Documentation (parallel with D, E)
  ├── gap 43  →  unified-doc-agent                  [Docs]
  ├── gap 44  →  unified-doc-agent                  [Docs]
  └── gap 45  →  unified-doc-agent                  [Docs]

BATCH G — Wave 4 XL Maintenance (long-running background; start with Batch C)
  └── gap 32  →  repository-hygiene-agent           [Shared]
```

### Batch dependency graph

```
Batch A  ──┬──────────────────────────────► Batch D (after A dispatched)
            └──► Batch B (after A dispatched)

Batch C  ──────────────────────────────────► immediately (Wave 4 P3, independent)
Batch G  ──────────────────────────────────► immediately (long background)

Batch D  ──┬──────────────────────────────► (Wave 4 ML, after Batch A complete)
Batch E  ──┤
Batch F  ──┘  (D/E/F all run in parallel after their start condition met)
```

---

## Special Flag Handling

| gap_id | Flag | Required action |
|--------|------|-----------------|
| 14 | `needs_verification` | Dispatch `ml-validation-suite-agent` to verify Prometheus wiring against current codebase; produce `workbench/evidence/gap14_prometheus_verification_v2.md` |
| 27 | `needs_verification` | Dispatch `security-audit-agent` to re-verify ModerationAdapter wiring on all 7 LLM entry points; produce `workbench/evidence/gap27_moderation_verification_v2.md` |

---

## Ready-to-Run Handoff Block

```yaml
# ─────────────────────────────────────────────────────────────
# READY-TO-RUN HANDOFF — Wave 3/4 Dispatch
# Operator: paste each block into the appropriate dispatch UI
# Session rule: NO in-session implementation. Dispatch only.
# ─────────────────────────────────────────────────────────────

dispatch_session:
  context_lock:
    wave_3_queued:  [17, 18, 21, 22, 23, 24, 28, 29, 30, 31]   # 20 already completed
    wave_4_queued:  [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
    completed:      [19, 20, 26]
    needs_verification: [14, 27]

  batch_A:
    start_condition: immediate
    parallelism: all_parallel
    dispatches:
      - gap_id: 17
        type: custom_agent
        agent: ml-validation-suite-agent
        prompt: |
          Implement gap 17: data drift monitoring.
          Create src/codex_ml/monitoring/data_drift.py with PSI and KL-divergence
          drift detectors. Wire into train_loop.py. Add ≥5 unit tests.
          Store evidence in workbench/evidence/gap17_data_drift.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap17_data_drift.md]

      - gap_id: 18
        type: workflow_dispatch + custom_agent
        workflow: model-drift-retrain.yml
        workflow_inputs:
          drift_score: ""
          dry_run: "true"
          force_retrain: "false"
        agent: ml-validation-suite-agent
        agent_prompt: |
          Implement gap 18: model drift detection.
          Extend model-drift-retrain.yml to cover concept drift (output distribution shift).
          Store evidence in workbench/evidence/gap18_model_drift.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap18_model_drift.md]

      - gap_id: 21
        type: custom_agent
        agent: test-enhancement-agent
        prompt: |
          Implement gap 21: comprehensive regression test suite.
          Create tests/regression/ with ≥20 regression scenarios covering model outputs,
          API contracts, and data pipeline. Wire pytest in CI.
          Store evidence in workbench/evidence/gap21_regression_suite.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap21_regression_suite.md]

      - gap_id: 22
        type: workflow_dispatch
        workflow: mutation-testing.yml
        workflow_inputs: {}
        artifacts: [workbench/evidence/gap22_mutation_testing.md]
        post_dispatch_agent: mutation-testing-agent
        post_dispatch_prompt: |
          Capture mutation testing results from the latest mutation-testing.yml run.
          Store evidence in workbench/evidence/gap22_mutation_testing.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented (or 🟡 In Progress if score <50%).

      - gap_id: 23
        type: custom_agent
        agent: integration-test-runner
        prompt: |
          Implement gap 23: automated integration tests.
          Create tests/integration/ with ≥10 integration tests covering
          API↔model and monitoring↔alerting boundaries. Wire into CI.
          Store evidence in workbench/evidence/gap23_integration_tests.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap23_integration_tests.md]

  batch_B:
    start_condition: after_batch_A_dispatched
    parallelism: all_parallel
    dispatches:
      - gap_id: 24
        type: custom_agent
        agent: performance-monitor-agent
        prompt: |
          Implement gap 24: performance benchmarking suite.
          Create benchmarks/ directory with harness for training throughput,
          inference latency, and memory benchmarks. Add CI job producing JSON report.
          Store evidence in workbench/evidence/gap24_benchmarks.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap24_benchmarks.md]

      - gap_id: 28
        type: custom_agent
        agent: security-audit-agent
        prompt: |
          Implement gap 28: Sigstore verification for critical dependencies.
          Create scripts/security/sigstore_verify.py and add CI job.
          Store evidence in workbench/evidence/gap28_sigstore.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap28_sigstore.md]

      - gap_id: 29
        type: custom_agent
        agent: ci-resilience-emergency-response-agent
        prompt: |
          Implement gap 29: circuit breakers for external services.
          Create src/codex/resilience/circuit_breaker.py (half-open/closed/open states).
          Add ≥8 unit tests. Store evidence in workbench/evidence/gap29_circuit_breaker.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap29_circuit_breaker.md]

      - gap_id: 30
        type: custom_agent
        agent: ci-auto-healer-agent
        prompt: |
          Implement gap 30: exponential backoff retry logic.
          Create src/codex/resilience/retry.py with exponential backoff + jitter.
          Wire into HTTP clients. Add ≥5 unit tests.
          Store evidence in workbench/evidence/gap30_retry.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap30_retry.md]

      - gap_id: 31
        type: custom_agent
        agent: ci-resilience-emergency-response-agent
        prompt: |
          Implement gap 31: graceful degradation mechanisms.
          Create src/codex/resilience/degradation.py with fallback chains.
          Add ≥6 unit tests. Store evidence in workbench/evidence/gap31_degradation.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap31_degradation.md]

  batch_C:
    start_condition: immediate   # Wave 4 P3 quality, independent
    parallelism: all_parallel
    dispatches:
      - gap_id: 33
        type: workflow_dispatch + custom_agent
        workflow: mypy-baseline.yml
        workflow_inputs: {}
        agent: mypy-manager-agent
        agent_prompt: |
          Implement gap 33: add mypy to pre-commit hooks.
          Add mypy hook to .pre-commit-config.yaml (uses .mypy_baseline for ratchet).
          Store evidence in workbench/evidence/gap33_mypy_precommit.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap33_mypy_precommit.md]

      - gap_id: 34
        type: custom_agent
        agent: documentation-quality-agent
        prompt: |
          Implement gap 34: automated docstring generation.
          Configure pydocstyle/darglint CI check and docstring generation tooling.
          Wire into CI. Store evidence in workbench/evidence/gap34_docstrings.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap34_docstrings.md]

      - gap_id: 35
        type: custom_agent
        agent: config-validator
        prompt: |
          Implement gap 35: schema validation in pre-commit.
          Add check-jsonschema/pydantic schema validation pre-commit hooks for YAML/JSON configs.
          Store evidence in workbench/evidence/gap35_schema_validation.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap35_schema_validation.md]

  batch_G:
    start_condition: immediate   # long-running background
    parallelism: single
    dispatches:
      - gap_id: 32
        type: custom_agent
        agent: repository-hygiene-agent
        prompt: |
          Implement gap 32: clean up 1,152 TODOs/FIXMEs/stubs.
          Systematically resolve or document all TODO/FIXME/stub annotations.
          Produce cleanup report with before/after counts.
          Target: reduce by ≥50% (≤576 remaining).
          Store evidence in workbench/evidence/gap32_todo_cleanup.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented or 🟡 In Progress.
        artifacts: [workbench/evidence/gap32_todo_cleanup.md]

  batch_D:
    start_condition: after_batch_A_complete
    parallelism: all_parallel
    dispatches:
      - gap_id: 36
        type: custom_agent
        agent: ml-validation-suite-agent
        prompt: |
          Implement gap 36: continuous learning pipeline.
          Create src/codex_ml/continuous_learning/ package with trigger, retrain, eval-gate, promote logic.
          Add ≥10 unit tests. Store evidence in workbench/evidence/gap36_continuous_learning.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap36_continuous_learning.md]

      - gap_id: 37
        type: custom_agent
        agent: ml-validation-suite-agent
        prompt: |
          Implement gap 37: A/B testing framework.
          Create src/codex_ml/experiments/ab_testing.py with statistical significance testing.
          Add ≥6 unit tests. Store evidence in workbench/evidence/gap37_ab_testing.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap37_ab_testing.md]

      - gap_id: 38
        type: workflow_dispatch + custom_agent
        workflow: model-drift-retrain.yml
        workflow_inputs:
          force_retrain: "true"
          dry_run: "false"
        agent: ml-validation-suite-agent
        agent_prompt: |
          Implement gap 38: automated model retraining pipeline.
          Validate model-drift-retrain.yml e2e (dry_run first, then live).
          Store evidence in workbench/evidence/gap38_auto_retrain.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap38_auto_retrain.md]

      - gap_id: 39
        type: custom_agent
        agent: cognitive-ooda-loop-agent
        prompt: |
          Implement gap 39: feedback loop integration.
          Create src/codex_ml/feedback/ package wired to OODA loop and monitoring alerts.
          Add ≥6 unit tests. Store evidence in workbench/evidence/gap39_feedback_loop.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap39_feedback_loop.md]

  batch_E:
    start_condition: after_batch_A_complete
    parallelism: all_parallel
    dispatches:
      - gap_id: 40
        type: custom_agent
        agent: test-enhancement-agent
        prompt: |
          Implement gap 40: fuzzing for critical code paths.
          Integrate atheris/hypothesis fuzzing for tokenizer, config parser, API handlers.
          Create tests/fuzz/ directory and CI job.
          Store evidence in workbench/evidence/gap40_fuzzing.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap40_fuzzing.md]

      - gap_id: 41
        type: custom_agent
        agent: test-enhancement-agent
        prompt: |
          Implement gap 41: property-based testing expansion.
          Expand hypothesis tests across data transforms and model utilities.
          Target ≥15 new property-based test functions in tests/property/.
          Store evidence in workbench/evidence/gap41_property_tests.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap41_property_tests.md]

      - gap_id: 42
        type: custom_agent
        agent: integration-test-runner
        prompt: |
          Implement gap 42: chaos engineering tests.
          Create tests/chaos/ using chaostoolkit or custom fault injection.
          Cover network/disk/memory failures; ensure system recovers.
          Store evidence in workbench/evidence/gap42_chaos.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap42_chaos.md]

  batch_F:
    start_condition: after_batch_A_complete
    parallelism: all_parallel
    dispatches:
      - gap_id: 43
        type: custom_agent
        agent: unified-doc-agent
        prompt: |
          Implement gap 43: video tutorial scripts/documentation.
          Create docs/tutorials/ with ≥5 scripted tutorial guides for key workflows.
          Store evidence in workbench/evidence/gap43_tutorials.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap43_tutorials.md]

      - gap_id: 44
        type: custom_agent
        agent: unified-doc-agent
        prompt: |
          Implement gap 44: interactive documentation with examples.
          Create docs/examples/ with ≥10 runnable code examples (doctest/pytest-doctest).
          Store evidence in workbench/evidence/gap44_interactive_docs.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap44_interactive_docs.md]

      - gap_id: 45
        type: custom_agent
        agent: unified-doc-agent
        prompt: |
          Implement gap 45: architecture decision records (ADRs).
          Create docs/adr/ with ≥10 ADR files covering key architecture decisions.
          Include ADR template and index.
          Store evidence in workbench/evidence/gap45_adrs.md.
          Update gap_backlog_prioritized.md status to ✅ Implemented.
        artifacts: [workbench/evidence/gap45_adrs.md]

  verification_dispatches:
    - gap_id: 14
      flag: needs_verification
      type: custom_agent
      agent: ml-validation-suite-agent
      prompt: |
        Re-verify gap 14: Prometheus metrics collection.
        Confirm CodexMetricsRegistry and start_metrics_server() are correctly wired in
        train_loop.py and CLI. Run existing tests. Produce updated evidence.
        Store in workbench/evidence/gap14_prometheus_verification_v2.md.
      artifacts: [workbench/evidence/gap14_prometheus_verification_v2.md]

    - gap_id: 27
      flag: needs_verification
      type: custom_agent
      agent: security-audit-agent
      prompt: |
        Re-verify gap 27: input sanitization for LLM prompts.
        Confirm ModerationAdapter is wired to all 7 LLM entry points with fail_open=False.
        Run existing 18 integration tests. Produce updated evidence.
        Store in workbench/evidence/gap27_moderation_verification_v2.md.
      artifacts: [workbench/evidence/gap27_moderation_verification_v2.md]

done_criteria:
  per_gap: |
    - evidence file present at workbench/evidence/gap{N}_*.md
    - gap_backlog_prioritized.md status updated to ✅ Implemented
    - wave_execution_control.md lane/wave summary updated
    - CI evidence (run log URL or artifact name) recorded in evidence file
  wave_complete: |
    All gaps in wave show ✅ in gap_backlog_prioritized.md AND
    wave_execution_control.md wave row shows: gap_status_updates=✅, evidence_links=✅,
    lane_summary=✅, escalations=✅
```

---

## Operator Notes

1. **Start Batch A + Batch C + Batch G simultaneously** — these are all independent.
2. **Batch B** may be dispatched immediately after Batch A dispatches are issued (no need to wait for completion).
3. **Batches D, E, F** should wait for Batch A to *complete* (not just dispatch) to avoid ML pipeline conflicts.
4. **All evidence files must be stored under `workbench/evidence/`** — never in `/tmp` (per repo policy).
5. **Update `workbench/wave_execution_control.md`** wave row after each batch completes.
6. **Approval workflow** — this PR carries the `wec:auto-approve-once` label for CI continuation.
