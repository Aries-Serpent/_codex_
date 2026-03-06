# 🎯 PR Follow-Up — #3503 — Path to Level 4 MLOps

**PR**: #3503  
**Branch**: `copilot/implement-user-authentication`  
**Owner**: @mbaetiong  
**Date**: 2026-03-06 (W-139)  
**Status**: 🟠 ACTIVE — Level 3.7 → 4.0 gap closure in progress  
**SAR Reference**: `docs/ops/SAR_METHODOLOGY.md`

---

## ⚠️ WHY THIS PROMPT EXISTS

`@copilot continue` and `/copilot continue` on PR #3503 were previously dispatching
with **no scoped Level 4 objective**. The chatops trigger workflow
(`.github/workflows/chatops_copilot_trigger.yml`) posts `@copilot continue <prompt-file>`
using the **latest active prompt**. Without this file, the system falls back to the
most-recently created `*-followup.md`, which has no Level 4 context.

**This file ensures every `@copilot continue` on PR #3503 resumes directly on the SAR
path to Level 4 MLOps certification.**

---

## 📋 PREVIOUS SESSION SUMMARY (W-139)

### Completed Work
- Variable audit CLI (`scripts/tools/variable_audit_cli.py`) — 37 tests passing
- SAR Methodology (`docs/ops/SAR_METHODOLOGY.md`) — 9 Mermaid diagrams, 6 playbooks
- Level 4 MLOps Assessment **corrected**: archive doc 95/100 → **74/100 Level 3.7**
- ROADMAP.md corrected: MLOps Level 4 → Level 3.7 ⚠️; current blockers updated
- `setup-python-cached` L5 SQLite cache layer added
- 3 critical workflows wired to `setup-python-cached` (pre-flight, self-healing, QA)
- `vars-guide-sync.yml` — daily auto-sync workflow created
- CHANGELOG.md + AGENT_ACCOUNTABILITY_REPORT.md updated (pre-flight REQ-4/REQ-5)

### Current Level 4 Score
**3.7 / 4.0** — 3 P1 gaps block full certification (see §10 SAR gap registry)

---

## 🎯 NEXT PHASE — LEVEL 4 CLOSURE SPRINT

### 🔴 Priority 1 — P1 Blockers (agent-executable)

#### P1-A: SAR-G04 — Wire `setup-python-cached` to remaining Python workflows
**Why**: 18+ workflows still use bare `actions/setup-python@v5` + `pip install`.
Each one misses L1–L5 cache, adding ~2–4 min cold-start overhead per run.

```bash
# Find remaining uncached Python workflows
grep -rL "setup-python-cached" .github/workflows/*.yml \
  | xargs grep -l "pip install\|setup-python" 2>/dev/null

# Pattern to apply (replace bare setup-python with):
#   - name: Setup Python (cached)
#     uses: ./.github/actions/setup-python-cached
#     with:
#       python-version: '3.12'
#       cache-tier: common
#       cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v2' }}
```

**Validation**: `grep -rL "setup-python-cached" .github/workflows/*.yml | xargs grep -l "pip install" 2>/dev/null | wc -l` → must reach 0

#### P1-B: SAR-G03 — Wire `check_drift_and_retrain()` to a GitHub Actions trigger
**Why**: Auto-retraining is the highest-impact single gap for Level 4 certification (45/100).
The function exists in `src/codex_ml/training/continuous_learning.py` but no workflow fires it.

```bash
# Verify the function exists
grep -n "check_drift_and_retrain" src/codex_ml/training/continuous_learning.py

# Create: .github/workflows/model-drift-retrain.yml
# Trigger: workflow_dispatch + schedule (daily) + repository_dispatch "model-drift-detected"
# Steps:
#   1. setup-python-cached (cache-tier: common)
#   2. python -c "from codex_ml.training.continuous_learning import ContinuousLearningPipeline; ..."
#   3. On retrain triggered → queue CODEX_RETRAIN_TRIGGER via variable_intent_writer.py
#   4. Post result summary to PR/issue
```

**Success criterion**: `.github/workflows/model-drift-retrain.yml` created and lint-clean;
`docs/archive/LEVEL_4_MLOPS_ASSESSMENT.md` Section 2 score updated from 45/100 → ≥ 75/100.

#### P1-C: SAR-G02 — Feature Store PoC (Feast)
**Why**: Feature store is 1/100 and the only dimension with zero implementation.
A minimal Feast registry wired to one model pipeline moves the score to ~40/100.

```bash
# Evaluate feasibility
pip show feast 2>/dev/null || echo "feast not installed"
ls src/codex_ml/features/ 2>/dev/null || echo "no features dir yet"

# Minimum viable deliverable:
#   src/codex_ml/features/__init__.py
#   src/codex_ml/features/feature_store.py  (Feast FeatureStore wrapper)
#   src/codex_ml/features/feature_views.py  (1–2 feature views)
#   tests/test_feature_store.py              (5 unit tests)
#   docs/ops/FEATURE_STORE_DESIGN.md        (architecture decision record)
```

---

### 🟡 Priority 2 — P2 Improvements (agent-executable)

#### P2-A: SAR-G05 — Add OpenTelemetry distributed tracing stub
```bash
# Add to cognitive_app/src/server/cli_api_server.py:
#   from opentelemetry import trace
#   tracer = trace.get_tracer("codex.cli_api")
#   with tracer.start_as_current_span("webhook_post"): ...
# Wire OTEL_EXPORTER_OTLP_ENDPOINT env var in .devcontainer
```

#### P2-B: Variable Audit CLI — `rotate-check` subcommand
```bash
# Implement: python scripts/tools/variable_audit_cli.py rotate-check --days 90
# Returns secrets last-updated > 90 days ago
# Already documented in GITHUB_VARIABLES_MASTER_GUIDE.md §6
```

#### P2-C: `vars-guide-sync.yml` — wire `variable_audit_cli.py check` exit code to CI gate
```bash
# Currently: audit runs, posts report, but does NOT fail the workflow on absent required vars.
# Add: --fail-on-absent flag to block merge when P1 variables are absent.
```

---

### 🟢 Priority 3 — Lock-in & Certification

#### P3-A: Update Level 4 Assessment after P1 gaps closed
```bash
# After SAR-G02 + SAR-G03 wired:
# docs/archive/LEVEL_4_MLOPS_ASSESSMENT.md:
#   - Section 2 (Auto-Retrain): 45/100 → target ≥ 75/100
#   - Section 7 (Feature Store): 10/100 → target ≥ 40/100
#   - Overall: 74/100 → target ≥ 85/100
#   - Status: "Level 3.7" → "Level 3.9" (path to 4.0)
# docs/ROADMAP.md Infrastructure Maturity table: Level 3.7 → updated
```

#### P3-B: Confirm `process-variable-intents.yml` processed `COPILOT_ACCESS_TEST`
```bash
gh api repos/Aries-Serpent/_codex_/actions/variables/COPILOT_ACCESS_TEST \
  -q '.value' 2>/dev/null || echo "not yet created — check pending_ops/"
```

---

## ✅ Mandatory Pre-Commit Checklist (Cognitive Pre-flight)

Before every `report_progress` call:

- [ ] `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` updated (REQ-4)
- [ ] `CHANGELOG.md` updated with new `## [Unreleased]` entry (REQ-5 / PREFLIGHT_001)
- [ ] `python -m ruff check src/ tests/ scripts/` — 0 errors
- [ ] `python -m pytest tests/tools/test_variable_audit_cli.py tests/utils/test_json_safe.py -q` — all pass
- [ ] `detect-secrets scan --baseline .secrets.baseline` — no new secrets
- [ ] `python scripts/tools/variable_audit_cli.py check` — offline mode OK (no token required for gate)

---

## 🔄 Self-Continuation Protocol

After completing each priority block, post the following comment to continue:

```
/copilot continue .github/copilot-prompts/active/PR-3503-followup.md
```

The chatops trigger workflow will parse this, validate authorization, check for
`SESSION_TIMEBOX_EXPIRED` gate, and post `@copilot continue` with this prompt file —
resuming directly on the Level 4 path.

**Do NOT use bare `@copilot continue`** — the system will fall back to the
most-recent prompt file, losing the Level 4 SAR context.

---

## 📊 Level 4 Progress Tracker

| Gap | ID | Score Before | Score After P1 | Owner |
|-----|-----|-------------|----------------|-------|
| Auto-Retrain wired | SAR-G03 | 45/100 | ≥ 75/100 | @copilot |
| Feature Store PoC | SAR-G02 | 10/100 | ≥ 40/100 | @copilot |
| Distributed Tracing stub | SAR-G05 | 0/100 | ≥ 30/100 | @copilot |
| Cache wiring complete | SAR-G04 | 55/100 | 95/100 | @copilot |
| **Overall** | — | **74/100** | **≥ 85/100** | — |

**Target**: ≥ 85/100 → Level 3.9 → certification sprint begins

---

_Generated W-139 · 2026-03-06 · Use `/copilot continue .github/copilot-prompts/active/PR-3503-followup.md` to resume_
