# S98 Follow-Up Prompt — Phase 11: Quality Hardening & Coverage Growth

> **Generated**: 2026-02-28 (S97)
> **Branch**: `copilot/sub-pr-3389`
> **Last AAIS**: 98.0/100 (V4.2)
> **Activation**: Comment `@copilot continue` on PR #3397

---

## Context (load before acting)

- `docs/ops/hardware_compatibility_matrix.md` — Tier 1/2/3 policy
- `docs/ops/PHASE_11_PLAN.md` — Phase 11 objectives + session map
- `docs/ops/openvino_integration.md` — P10-05 OpenVINO plan (Phase B+C pending)
- `docs/ops/DEPLOYMENT_READINESS_S92.md` — all B-01–B-07 resolved
- `.github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md` — AAIS V4.2 98.0/100
- `scripts/benchmark/cpu_baseline.py` — CPU baseline runner
- `scripts/ci/batch_scan_integration.py` — BatchScanRunner + OTel spans
- `.codex/change_log.md` — S91–S97 audit trail

---

## Phase 10 Status (S97 terminal — ALL COMPLETE)

| Objective | ID | Status |
|-----------|-----|--------|
| Hardware-first policy enforced | P10-01 | ✅ DONE (S95) |
| All GPU optional/deferred | P10-02 | ✅ DONE (S92–S95) |
| 0.9.0-rc1 publishable | P10-03 | ✅ DONE (S94) |
| CPU performance baseline | P10-04 | ✅ DONE (S96) |
| Intel OpenVINO path (optional) | P10-05 | ✅ DONE (S97 — doc + Phase A plan) |
| Secrets rotation runbook | P10-06 | ✅ DONE (S96) |
| SBOM scan in CI | P10-07 | ✅ DONE (S96) |
| Pattern 6 catch-all systematic fix | P10-08 | ✅ DONE (S97 — 222→118) |
| Coverage threshold raise | P10-09 | ✅ DONE (S96, 30% active) |
| OTel spans on BatchScanRunner | P10-10 | ✅ DONE (S96) |

**Phase 10: 10/10 complete ✅**

---

## S97 Completed Deliverables

| Deliverable | Status |
|-------------|--------|
| Pattern 6: 222→118 (import guards + file-read guards + trivial assertion cleanup) | ✅ |
| CodeQL alerts: all 6 resolved (rvs_preflight, auto_fix_common_issues, test files) | ✅ |
| Ruff F401/F841: 0 errors (unused pytest import + unused content var) | ✅ |
| `docs/ops/openvino_integration.md` (P10-05) | ✅ |
| `docs/ops/PHASE_11_PLAN.md` | ✅ |
| AAIS V4.2: 97.5→98.0/100 (+0.5) | ✅ |
| S98 continuation prompt | ✅ (this file) |

---

## Phase 11 Status

| Objective | ID | Status |
|-----------|-----|--------|
| Coverage 30%→50% | P11-01 | 🔶 IN PROGRESS (30% baseline) |
| Pattern 6 → 0 | P11-02 | 🔶 IN PROGRESS (118 remaining) |
| OpenVINO backend (Phase B+C) | P11-03 | ⏳ S99 |
| CI parallel sharding | P11-04 | ⏳ S101 |
| AAIS V5.0 | P11-05 | ⏳ S103 |

---

## S98 Priority 1 — Immediate

1. **Pattern 6 continuation**: 118→60
   - Target: `tests/rag/` broad retrieval guards → narrow to `(ValueError, RuntimeError)`
   - Target: `tests/branch_coverage/` intentional testing catches → add `# noqa: BLE001` comment
   - Target: `tests/conftest.py` best-effort cleanup handlers → add rationale comments
   - Skip: `tests/capabilities/error_handling/` — intentionally broad, leave as-is

2. **Coverage gap-fill P11-01a** (raise `fail_under` 30→35):
   - Run: `python -m pytest --cov=src --cov-report=term-missing 2>&1 | grep TOTAL`
   - Identify 3 lowest-coverage modules in `src/codex_ml/training/` and `src/codex_ml/inference/`
   - Add targeted tests (use `coverage-gapfill-agent`)
   - Once measured ≥ 33%: raise `fail_under = 35` in `pyproject.toml`

3. **Validate S97 CI**: Confirm new CI run shows:
   - 0 auto-fixable issues (P1–P11)
   - 0 CodeQL alerts
   - Fast Validation: PASS

---

## S98 Priority 2 — Validation

- Validate `docs/ops/openvino_integration.md` content vs Intel OpenVINO 2024.x API
- Verify `tests/monitoring/test_nvml_optional.py` pynvml detection fix
- Confirm SBOM artifact (CycloneDX JSON) is valid in latest CI run

---

## S98 Priority 3 — Enhancement

- OpenVINO backend Phase B: `src/codex_ml/backends/openvino_backend.py`
- CI parallel sharding initial scaffold (P11-04)

---

## Execution Instructions

1. Comment `@copilot continue` on this PR
2. Copilot loads this prompt and executes in priority order
3. Update this file (rename to S99_CONTINUATION_PROMPT.md) with progress
4. 5-pass self-review before concluding

---

## Verification Commands

```bash
# Pattern 6 check
python scripts/ci/auto_fix_common_issues.py --check-only 2>&1 | grep "Pattern 6"

# Ruff clean
ruff check --select F401,F841 .

# CodeQL / security
bandit -r src/ --configfile .bandit

# Coverage measurement
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=30 tests/ -q 2>&1 | tail -5

# Full auto-fix check
python scripts/ci/auto_fix_common_issues.py --check-only
```
