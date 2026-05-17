# Next Expected Codebase Change (48-Hour Alignment)

Generated: 2026-05-17T07:39:30Z  
Repository: `Aries-Serpent/_codex_`  
Window reviewed: last 48 hours

## 1) Recent Change Alignment Summary

The most recent sessions concentrated on:
- GitHub Pages reliability hardening (`pages-mkdocs.yml` deploy action fix, `pages-health-guard.yml` telemetry directory creation).
- WEC/workflow governance tightening (`wec_enforcer.py` active-state validation, token-chain usage hardening).
- Reporting expansion (`workflow_portfolio_7d_{table,analysis}` and session SOP updates with tokenized mapping and mermaid flows).
- Persistent baseline test instability (`nox -s tests` collection failures centered on `codex_ml.data._core_loaders.stream_paths`).

## 2) Next Expected Codebase Change

**Expected next change:** implement and validate a focused remediation path for the recurring `stream_paths` collection failure class, then reflect the fix status in workflow/reporting docs so WEC validation and session handoffs operate on cleaner CI signals.

## 3) Mermaid Mapping Outline

```mermaid
flowchart TD
  A[Session Start + Preload] --> B[Baseline checks: precommit + nox tests]
  B --> C{Collection failures include stream_paths?}
  C -->|Yes| D[Remediate loader API/export contract]
  C -->|No| E[Proceed to workflow/pages governance updates]
  D --> F[Targeted regression tests]
  F --> G[Re-run nox tests sample/full gate]
  G --> H[Update accountability + workflow reporting]
  E --> H
  H --> I[Next-session prompt handoff]
```

## 4) Expected Results

- Reduced or eliminated `stream_paths`-driven pytest collection errors.
- Cleaner differentiation between infra/workflow issues vs. Python runtime/import issues.
- More reliable signal for WEC merge-required workflow selection and session planning.
- Updated reporting artifacts capturing post-fix risk posture and next operational priorities.

## 5) Quantum-Inspired Formulation (Tokenized Variables)

\[
\Psi_{CI} = \alpha_1 \cdot TVAR\_CODEX\_CI\_FAILURE\_RATE
          + \alpha_2 \cdot \mathbb{I}(ERR\_STREAM\_PATHS)
          + \alpha_3 \cdot METRIC\_COMMITS\_SINCE\_LAST\_GREEN
\]

\[
R_{session} = \beta_1 \cdot DRIFT_{branch}
            + \beta_2 \cdot \mathbb{I}(TVAR\_CODEX\_SWEEP\_SKIP\_MAIN=0)
            + \beta_3 \cdot \mathbb{I}(WEC_{nonactive}>0)
\]

\[
U_{next} = \gamma_1 \cdot FIX_{stream\_paths}
         + \gamma_2 \cdot PASS_{targeted\_tests}
         - \gamma_3 \cdot \Psi_{CI}
         - \gamma_4 \cdot R_{session}
\]

Coefficient interpretation (normalized scoring model):
- \(\alpha_1,\alpha_2,\alpha_3 \in [0,1]\), \(\sum \alpha_i = 1\): CI instability weighting.
- \(\beta_1,\beta_2,\beta_3 \in [0,1]\), \(\sum \beta_i = 1\): session risk weighting.
- \(\gamma_1,\gamma_2,\gamma_3,\gamma_4 \in [0,1]\), \(\sum \gamma_i = 1\): utility tradeoff weighting.
- If no calibrated data is available, initialize as uniform weights and tune per session evidence.

### Token/Variable Descriptions

| Token | Meaning |
|---|---|
| `TVAR_CODEX_CI_FAILURE_RATE` | Current CI instability pressure signal |
| `ERR_STREAM_PATHS` | Indicator that collection failures contain `stream_paths` attribute errors |
| `METRIC_COMMITS_SINCE_LAST_GREEN` | Numeric distance from latest commit to `TVAR_CODEX_CI_LAST_GREEN_SHA` baseline |
| `DRIFT_branch` | Branch divergence pressure from moving base |
| `TVAR_CODEX_SWEEP_SKIP_MAIN` | Main-branch sweep conflict mitigation switch |
| `WEC_nonactive` | Count of WEC-checked workflows in non-active states |
| `FIX_stream_paths` | Binary/score signal for remediation completion |
| `PASS_targeted_tests` | Targeted regression validation success signal |

## 6) Iterative Expected Session Promptset (Outline)

1. **Session A — Loader Contract Remediation** ✅ COMPLETE (S1042-2026-05-17)
   - Root cause confirmed: `pytest_plugins` in non-root `tests/quantum/conftest.py` caused a hard pytest collection interrupt blocking all 16,373 tests.
   - Fix applied: removed deprecated `pytest_plugins`, directly imported `quantum_plugin_fixture` in conftest.
   - Before: `Interrupted: 1 error during collection` — 0 tests collected.
   - After: **0 collection errors — 16,373 tests collected**.
   - Targeted suite: 95/95 quantum tests pass; 105/106 in broader targeted set (1 pre-existing flaky isolation-dependent test unrelated to this fix).

2. **Session B — CI Signal Stabilization**
   - Re-run `nox -s tests` full suite and confirm zero collection errors in CI.
   - Characterize any remaining runtime test failures separate from collection gate.
   - Update accountability + reporting with measured outcomes.

3. **Session C — Workflow/WEC Follow-Through**
   - Reassess merge-required workflow set post-stabilization.
   - Validate active-state and token-chain assumptions.
   - Refresh handoff prompt and next priority matrix.

4. **Session D — Pages + Reporting Reliability Confirmation**
   - Verify Pages deploy/health telemetry remains stable with latest changes.
   - Confirm reporting docs/nav reflect current operational status.
   - Publish final continuation prompt for the next 48-hour cycle.

## 7) Groundwork Package for the Next Session

### A. Startup Checklist (Ready-to-Run)

1. Load policy/accountability/session context packet.
2. Run `nox -s precommit` and `nox -s tests` to capture current baseline.
3. Confirm zero collection errors — quantum conftest fix in `tests/quantum/conftest.py` is applied.
4. If any new collection errors surface, identify impacted modules and scope minimal fix.
5. Run targeted test set for any changed area.
6. Refresh accountability/changelog/reporting artifacts with measured deltas.

### B. Execution Guardrails

- Keep remediation scoped to loader contract compatibility and direct downstream callsites.
- Prefer additive/backward-compatible fixes over broad refactors.
- Re-check WEC non-active workflow state before final handoff notes.
- Preserve token-chain assumptions (`CODEX_MASTER_KEY || CODEX_BACKUP_KEY || github.token`) in workflow-related commentary.

### C. Promptset Pack (Iterative)

**Prompt 1 — Baseline Capture** ✅ DONE
> Baseline captured: `pytest_plugins` in `tests/quantum/conftest.py` caused hard collection interrupt (0/16,373 tests collected).

**Prompt 2 — Minimal Remediation** ✅ DONE
> Fix applied: replaced `pytest_plugins` with direct import. After: 0 errors, 16,373 collected. 95/95 quantum pass.

**Prompt 3 — Stability Verification**
> “Re-run broad validation, separate remaining pre-existing failures from fixed signatures, and update reporting/accountability artifacts with evidence.”

**Prompt 4 — Handoff Closure**
> “Produce next-session continuation notes: unresolved risks, required workflow checks, and a prioritized follow-up matrix for the next 48-hour window.”
