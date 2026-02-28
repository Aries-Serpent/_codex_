# S99 HOTFIX Continuation Prompt
> **Generated**: 2026-02-28 (S98 close-out)
> **Merged into**: `0D_base_` from `copilot/sub-pr-3389`
> **New PR branch**: `copilot/sub-pr-S99` (or similar)
> **Last AAIS**: 98.6/100 (V4.3, S98)
> **Activation**: Comment `@copilot+claude-sonnet-4.6 continue S99` on the new PR

---

## State After Merge (S98 Terminal)

### Verified Clean ✅
| Gate | Status | Evidence |
|------|--------|----------|
| `ruff check .` | ✅ 0 errors | project config (E,F,W,I / ignore E501) |
| `ruff check src/ --select=F,W,I,E` | ✅ 0 errors | QA walkthrough command (--extend-ignore=E501) |
| `bandit -r src/ --configfile .bandit` | ✅ 0 issues | project config |
| `bandit -r src/ --severity-level medium` | ✅ 0 issues | QA walkthrough command |
| CodeQL alerts | ✅ 0 | GitHub Advanced Security |
| Auto-fixable CI issues | ✅ 0 | auto_fix_common_issues.py --check-only |
| Pattern 6 (informational) | ✅ 77 (≤ 80 target met) | 120 → 77, noqa-aware checker |
| OTel spans (BatchScanRunner) | ✅ Active | lazy no-op when OTel absent |
| SBOM workflow | ✅ Active | sbom.yml on every push/PR |
| OpenVINO Phase B | ✅ Implemented | src/codex_ml/backends/openvino_backend.py |
| OpenVINO smoke tests | ✅ 11/11 pass | tests/smoke/test_openvino_backend_smoke.py |
| AAIS | ✅ 98.6/100 (V4.3) | .github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md |

### Key Deliverable Locations
| Asset | Path |
|-------|------|
| OpenVINO backend | `src/codex_ml/backends/openvino_backend.py` |
| OpenVINO smoke tests | `tests/smoke/test_openvino_backend_smoke.py` |
| Phase 11 plan | `docs/ops/PHASE_11_PLAN.md` |
| Auto-fix patterns (13 total) | `scripts/ci/auto_fix_common_issues.py` |
| QA walkthrough workflow | `.github/workflows/qa-walkthrough.yml` |
| AAIS V4.3 | `.github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md` |

---

## ⚠️ HOTFIX Items — Address First in S99

These items must be fixed before any new feature work:

### HF-01 — Pre-commit `check-yaml` failure (BLOCKING)
**Symptom**: The pre-commit hook `check-yaml` may flag YAML files added in S91–S98.
**Action**:
```bash
pre-commit run check-yaml --all-files 2>&1 | grep -E "Failed|Passed"
```
Fix any flagged YAML files before proceeding.

### HF-02 — `tests/auth/test_exceptions.py` collection error (HIGH)
**Symptom**: `pytest tests/ -x --co` stops at `tests/auth/test_exceptions.py` with import error.
**Action**:
```bash
python -m pytest tests/auth/test_exceptions.py --collect-only 2>&1 | tail -20
```
Fix the import path or add a `try/except ImportError` guard in the file.

### HF-03 — Coverage measurement (BLOCKING for P11-01a)
**Symptom**: `fail_under = 30` but measured coverage is ~27.5%. Must confirm ≥ 33% before raising.
**Action**:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -q 2>&1 | grep "TOTAL"
```
If measured ≥ 33%: raise `fail_under = 35` in `pyproject.toml`. If < 33%: run coverage-gapfill-agent first.

### HF-04 — Workflow `security-alert-notification.yml` consistently fails (MEDIUM)
**Symptom**: Every push triggers a failure in `security-alert-notification.yml` (Dependabot API permissions).
**Action**: Investigate whether the workflow needs `security-events: read` permission or should be disabled.
```bash
# Check the workflow
cat .github/workflows/security-alert-notification.yml | head -30
```

---

## S99 Priority Queue (after HF items)

### 🔴 Priority 1 — Immediate (complete in first session)

#### P1-01: Pattern 6 → 40 (77 → 40)
**Files to target** (run this to get list):
```bash
grep -rn "except Exception:" tests/ --include="*.py" | grep -v "# noqa" \
  | sed 's/:.*//' | sort | uniq -c | sort -rn | head -20
```
**Strategy**:
- `tests/tokenization/test_api_comprehensive.py` (3) → narrow to `(ValueError, TypeError)`
- `tests/cli/test_plugins_cli_comprehensive.py` (3) → narrow or noqa
- `tests/utils/doc_refactor_helpers.py` (2) → narrow to `(OSError, ValueError)`
- Remaining small files (2 each) → `# noqa: BLE001` where intentional

#### P1-02: OpenVINO Phase C CI smoke test
**Action**: Add `@pytest.mark.skipif(not is_available("GPU"), reason="OV GPU not present")` guard to the `infer()` path test in `tests/smoke/test_openvino_backend_smoke.py`. Add a CI job that runs on an Intel Arc runner when available.

### 🟡 Priority 2 — After P1

#### P2-01: Coverage gap-fill (P11-01a)
Use the `coverage-gapfill-agent` to identify 3 lowest-coverage modules in `src/codex_ml/training/` and `src/codex_ml/inference/`. Add targeted tests. Once measured ≥ 33%: raise `fail_under = 35`.

#### P2-02: CI parallel sharding (P11-04 skeleton)
Add a `pytest --split-count=4 --split-index=${{ matrix.shard }}` job in `resilient_validation.yml` using `pytest-split`. Add `pytest-split` to dev dependencies.

#### P2-03: SBOM artifact validation
Confirm the `sbom.yml` workflow artifact contains valid CycloneDX JSON:
```bash
# Trigger manually and check artifact
gh workflow run sbom.yml -R Aries-Serpent/_codex_
```

### 🟢 Priority 3 — Enhancement

- AAIS V4.4: Target 99.0/100 via P11-01a + Pattern 6 → 40 + Phase C OpenVINO
- Update `.github/agents/S100_CONTINUATION_PROMPT.md` for next session
- `0.9.0` stable release preparation (RC → final): bump version in `pyproject.toml`

---

## Quick Context Load (run these first)

```bash
# Verify clean state
python -m ruff check . && echo "ruff: ✅ 0 errors"
python scripts/ci/auto_fix_common_issues.py --check-only
python -m pytest tests/smoke/ -v --tb=short -q

# Count Pattern 6
grep -rn "except Exception:" tests/ --include="*.py" | grep -v "# noqa" | wc -l

# Load context docs
cat docs/ops/PHASE_11_PLAN.md
cat docs/ops/openvino_integration.md
cat .github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md | grep "current\|Score\|Remaining"
```

---

## Environment Notes

| Setting | Value |
|---------|-------|
| Python | 3.12 |
| Primary test machine | Intel Core Ultra 5 135U vPro, 16 GB DDR5-5600, Windows 11 Pro |
| GPU policy | Intel Arc iGPU = Tier 2 optional via OpenVINO; CUDA = Tier 3 deferred |
| Ruff line-length | 100 (both `.ruff.toml` and `pyproject.toml`) |
| Coverage gate | `fail_under = 30` (raise to 35 only when measured ≥ 33%) |
| AAIS current | 98.6/100 (V4.3) |
| Pattern 6 | 77 remaining (target: 0 by S102) |
| Auto-fix patterns | 13 (P1–P13); `--pattern 1-13` |
| Bandit invocation | `bandit -r src/ --configfile .bandit` (YAML config) |

---

## 5-Pass Self-Review Checklist (before closing S99)

- [ ] All HOTFIX items (HF-01–HF-04) resolved
- [ ] `ruff check .` → 0 errors
- [ ] `bandit -r src/ --configfile .bandit` → 0 issues
- [ ] `python scripts/ci/auto_fix_common_issues.py --check-only` → 0 auto-fixable
- [ ] `python -m pytest tests/smoke/ -v` → all pass (except pre-existing torch-absent)
- [ ] Pattern 6 count ≤ 40
- [ ] AAIS updated to V4.4
- [ ] CHANGELOG.md S99 section added
- [ ] `.codex/change_log.md` S99 entry appended
- [ ] `docs/ops/PHASE_11_PLAN.md` S99 row updated
- [ ] `S100_CONTINUATION_PROMPT.md` created

---

*S99 HOTFIX prompt generated post-S98 close-out, 2026-02-28. Pre-merge into `0D_base_`.*
