# [Plan]: Complete MLOps Gap Analysis & Implementation Roadmap

**Generated:** 2025-12-07T21:30:00Z  
**Author:** Copilot Autonomous Agent  
**Version:** 2.0.0 - Complete with Deterministic Audit Integration  
**Repository:** Aries-Serpent/_codex_  
**Current Status:** 67/71 Azure MLOps Capabilities (94.4%)  
**Target Status:** 71/71 (100%) - Level 4 MLOps Maturity

---

## 🎯 Executive Summary

This comprehensive roadmap provides a complete path to 100% Azure MLOps Level 4 maturity by addressing:
- **4 Primary Capability Gaps** (Caps 17, 18, 27, 63 - scored 0.5)
- **9 Secondary Hardening Areas** (platform improvements)
- **Total Implementation Effort:** 31-42 developer-days (~6-8 weeks)

### Key Principles
- **Planning Only**: NO code modifications - only planning artifacts
- **Deterministic Validation**: S1-S7 audit pipeline at each checkpoint
- **Incremental**: Small, testable, reversible changes with feature flags
- **Backward Compatible**: All new features opt-in via Hydra configs
- **Self-Healing**: Iterative validation loops with fail-fast policies
- **Mandatory Completion**: DO NOT FINISH until all WPs validated, no regressions

---

## Part 1: MLOps Gap Matrix

### 1.1 Primary Gaps (Score < 1.0)

| ID | Name | Category | Score | Target | Gap Summary | Priority | Complexity | Effort |
|----|------|----------|-------|--------|-------------|----------|-----------|--------|
| 17 | Experiment tracking | Data & Experiments | 0.5 | 1.0 | MLflow stubbed; no central aggregation | HIGH | M | 3d |
| 18 | Experiment results | Data & Experiments | 0.5 | 1.0 | NDJSON only; MLflow/W&B incomplete | HIGH | M | 2d |
| 27 | Feature store | Training & Model Mgmt | 0.5 | 1.0 | Placeholder; no versioning/PoT | HIGH | L | 8-12d |
| 63 | Feature health | Monitoring & Feedback | 0.5 | 1.0 | No SLA/alerting for freshness | HIGH | M | 4-6d |

**Primary Total:** 17-23 developer-days

### 1.2 Secondary Gaps (Hardening)

| Topic | Category | Gap | Priority | Complexity | Effort |
|-------|----------|-----|----------|-----------|--------|
| Config sprawl | Platform | Multiple roots; inconsistent paths | MED | M | 1-2d |
| Evaluation & metrics | Training/Eval | No unified runner/adapters | MED | M | 3d |
| Early stopping & LR | Training | TODO; limited scheduler options | MED | S | 1-2d |
| Data validation | Data | No Great Expectations checks | MED | M | 2-3d |
| Security scans | Governance | pip-audit/gitleaks not enforced | HIGH | S | 1d |
| Checkpoint mgmt | Ops | No listing/retention tooling | LOW | S | 1d |
| Reproducibility | Repro | Missing NumPy seeds, env capture | HIGH | S | 1-2d |
| Prompt safety | Safety | Minimal output sanitization | MED | S | 2d |
| Container opts | Release | Not multi-stage/hardened | MED | M | 2-3d |

**Secondary Total:** 14-19 developer-days  
**Combined Total:** 31-42 developer-days

---

## Part 2: Agent-Ready Implementation Prompts

### WP-A: MLflow Experiment Tracking (Caps 17 & 18)

**Goal:** Offline-first MLflow tracking with NDJSON fallback, artifacts attached

**Repo Areas:**
- `src/codex_ml/utils/mlflow_wrapper.py`
- `src/codex_ml/tracking/writers.py`
- `training/trainer.py`, `configs/base/tracking.yaml`

**Changes:**
1. Implement `MLFlowLogger` context manager
2. Implement `TrackingWriter` interface (NDJSON/MLflow)
3. Add config: `tracking.mlflow_enabled=false`
4. Instrument trainer to log params/metrics/artifacts
5. Add env snapshot (`pip freeze`)
6. Tests: `tests/tracking/test_mlflow_integration.py`

**Validation:**
```bash
pytest tests/tracking/ -v
python cli/train_codex.py +tracking.mlflow_enabled=true
ls mlruns/
```

**DoD:** MLflow run with params/metrics/artifacts when enabled; NDJSON when disabled; Caps 17/18 → 1.0

**Effort:** 3 days

---

### WP-B: Feature Store + Health Monitoring (Caps 27 & 63)

**Goal:** Local feature store (parquet) with versioning + health monitoring

**Repo Areas:**
- `src/codex_ml/features/feature_store.py` (create)
- `src/codex_ml/features/monitor.py` (create)
- `src/codex_ml/cli/feature_store.py` (Typer CLI)

**Changes:**
1. Implement `FeatureStore` class (register/materialize/get)
2. Implement `FeatureHealthMonitor.check_all()`
3. CLI: register, list, materialize, health
4. Integrate into training (opt-in)
5. Tests: registry, PoT retrieval, health
6. Nox session: `feature_health`

**Validation:**
```bash
pytest tests/features/ -v
python -m src.codex_ml.cli.feature_store health
nox -s feature_health
```

**DoD:** Feature store functional; health monitor produces JSON; Caps 27/63 → 1.0

**Effort:** 8-12 days

---

### WP-C: Evaluation Standardization

**Goal:** Unified `EvaluationRunner` with metric adapters

**Repo Areas:**
- `src/codex_ml/evaluation/runner.py` (create)
- `src/codex_ml/evaluation/metrics/*.py`

**Changes:**
1. Add metric adapters (accuracy, BLEU, ROUGE, perplexity)
2. Implement `EvaluationRunner.run()`
3. Log to tracking writer
4. Tests: `tests/evaluation/test_evaluation_runner.py`

**DoD:** Evaluation summary JSON; metrics logged

**Effort:** 3 days

---

### WP-D: Training Enhancements

**Goal:** Early stopping + scheduler selection

**Changes:**
1. Implement early stopping (patience, monitor_metric)
2. Add scheduler factory (cosine, linear, constant)
3. Config: `early_stopping.enabled=false`
4. Tests: `tests/training/test_early_stopping.py`

**DoD:** Early stopping triggers; scheduler selection works

**Effort:** 1-2 days

---

### WP-E: Security Gating

**Goal:** pip-audit & gitleaks in pre-commit + nox

**Changes:**
1. Add hooks to `.pre-commit-config.yaml`
2. Add `nox -s security` session
3. Create `security_allowlist.json`

**Validation:**
```bash
pre-commit run --all-files
nox -s security
```

**DoD:** Security hooks pass; nox session runs

**Effort:** 1 day

---

### WP-F: Config Consolidation

**Goal:** Standardize to `configs/` with legacy aliases

**Changes:**
1. Create `configs/README.md`
2. Update Hydra init for legacy paths
3. Use `nox -s config_index`

**DoD:** Hydra works with new and legacy paths

**Effort:** 1-2 days

---

### WP-G: Reproducibility Hardening

**Goal:** Deterministic seeds + env capture

**Changes:**
1. Add `enable_deterministic_training(seed)`
2. Add `save_env_snapshot()`
3. Tests: `tests/repro/test_seed_consistency.py`

**DoD:** env_snapshot.txt produced; seeds in manifest

**Effort:** 1-2 days

---

### WP-H: Data Validation

**Goal:** Great Expectations validation (opt-in)

**Changes:**
1. Add `validate_dataset()` module
2. Config: `data.validate=false`
3. Tests: `tests/data/test_dataset_validation.py`

**DoD:** Validation runs when enabled

**Effort:** 2-3 days

---

### WP-I: Prompt Safety

**Goal:** Output filter middleware (opt-in blocklist)

**Changes:**
1. Implement `PromptSafetyFilter`
2. Tests: `tests/safety/test_prompt_filter.py`

**DoD:** Blocked terms sanitized when enabled

**Effort:** 2 days

---

### WP-J: Checkpoint Management

**Goal:** Listing CLI + retention policy

**Changes:**
1. Add `scripts/list_checkpoints.py`
2. Tests: `tests/checkpointing/test_checkpoint_listing.py`

**DoD:** CLI lists checkpoints; dry-run deletion

**Effort:** 1 day

---

## Part 3: Execution Strategy

### 3.1 Execution Order

**Phase 1: Foundation (CP1)**
1. WP-F: Config (1-2d)
2. WP-G: Repro (1-2d)

**Phase 2: Tracking & Eval (CP2)**
3. WP-A: MLflow (3d) → Caps 17/18 → 1.0
4. WP-C: Evaluation (3d)

**Phase 3: Training & Security (CP2.5)**
5. WP-D: Training (1-2d)
6. WP-E: Security (1d)

**Phase 4: Feature Store (CP3)**
7. WP-B: Feature Store (8-12d) → Caps 27/63 → 1.0

**Phase 5: Hardening (CP4)**
8. WP-H: Data Validation (2-3d)
9. WP-I: Safety (2d)
10. WP-J: Checkpoint (1d)

### 3.2 Validation Checkpoints

**CP0: Baseline**
```bash
python scripts/space_traversal/audit_runner.py run
cp audit_run_manifest.json baseline_manifest.json
```

**CP1: After WP-F + WP-G**
```bash
make space-audit-fast
python scripts/space_traversal/audit_runner.py diff --old baseline_manifest.json --new audit_run_manifest.json
```

**CP2: After WP-A + WP-C**
```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain 17
python scripts/space_traversal/audit_runner.py explain 18
```
*Expected: Caps 17/18 → 1.0*

**CP3: After WP-B**
```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain 27
python scripts/space_traversal/audit_runner.py explain 63
nox -s feature_health
```
*Expected: Caps 27/63 → 1.0*

**CP4: Final**
```bash
python scripts/space_traversal/audit_runner.py run
# Verify all 71 capabilities at 1.0
```

### 3.3 Fail-Fast Policy

**Config** (`.copilot-space/workflow.yaml`):
```yaml
options:
  fail_on_score_regression: true
  regression_delta_threshold: 0.02
```

**Process:** Run audit after each WP; if regression > 2%: stop, explain, fix, re-audit

### 3.4 Self-Healing Loop

**Per WP:**
1. Implement MVP behind config flags
2. Add tests, run `nox -s tests`
3. Run `make space-audit-fast`
4. If improved → commit
5. If regressed → `explain <cap_id>`, fix, re-audit
6. After merge → full S1-S7 audit

**Self-Review Checklist:**
- [ ] S1-S7 run with changes
- [ ] Determinism confirmed (stable repo_root_sha)
- [ ] No security findings (`nox -s security`)
- [ ] All tests passing
- [ ] Docs updated
- [ ] CHANGELOG entry

### 3.5 Quick Wins vs Heavy Lifts

- **Quick Wins (≤2d):** WP-D, E, F, G, I, J (7-10d)
- **Medium (3d):** WP-A, C, H (8-9d)
- **Heavy Lift:** WP-B (8-12d)

**Strategy:** Quick wins first → high-impact medium → heavy lift → polish

---

## Part 4: Completion Directive

### NOT Complete Until:

1. **All 10 WPs Implemented** (A-J)
2. **All Checkpoints Pass** (CP0-CP4)
3. **71/71 Capabilities at 1.0**
4. **No Regressions** (all `explain` resolved)
5. **Documentation Complete** (WP docs, CHANGELOG, guides)

### Iterative Process

**DO NOT FINISH until:**
- Every WP validated via S1-S7
- No concerns from self-review/self-healing/self-learning cycles
- All capabilities at 1.0

**Exit:** 71/71 capabilities, all checkpoints green, no blocking issues

---

## Part 5: Quick Reference

### Commands

```bash
# Full audit
python scripts/space_traversal/audit_runner.py run

# Fast validation
make space-audit-fast

# Explain score
python scripts/space_traversal/audit_runner.py explain <cap_id>

# Diff manifests
python scripts/space_traversal/audit_runner.py diff --old A --new B

# Tests & security
nox -s tests
nox -s security
nox -s feature_health
```

### Key Files

- Workflow: `.copilot-space/workflow.yaml`
- Audit runner: `scripts/space_traversal/audit_runner.py`
- Template: `templates/audit/capability_matrix.md.j2`
- Make helper: `space.mk`

---

## Conclusion

Complete path from 67/71 (94.4%) to 71/71 (100%) via 10 work packages, 5 checkpoints, deterministic validation.

**Effort:** 31-42 developer-days (~6-8 weeks)  
**Final State:** All 71 capabilities at 1.0, enterprise production ready

---

*End of Complete MLOps Gap Analysis & Implementation Roadmap*
