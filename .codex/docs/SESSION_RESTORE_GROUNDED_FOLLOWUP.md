# HOTFIX Follow-Up Prompt — Agentic GROUNDED System: Remaining Future Scope
> **File**: `.codex/docs/SESSION_RESTORE_GROUNDED_FOLLOWUP.md`
> **Created**: 2026-03-02
> **Purpose**: Chain prompt for the next Copilot session after PR #3447 is merged into `main`.
> **Scope**: Remaining future-scope items from the Soft→GROUNDED conversion (Phases 1–6).
> **Registry**: v1.9.0 · 152 agents · GROUNDED=8 · PARTIAL=142 · SOFT=2 · E→D 5/5 ✅

---

## 🎯 Mission

All Phase 1–6 tasks are complete and merged. This prompt drives the **remaining future-scope** items
that were deferred during the phase implementation. Execute in priority order.

---

## ✅ What Was Already Done (DO NOT RE-DO)

| Phase | Artifact | Status |
|-------|----------|--------|
| Phase 1 | `AGENT_REGISTRY.yaml` v1.9.0 (152 agents, GROUNDED=8, SOFT=2) | ✅ DONE |
| Phase 1 | `CODEX_MANIFEST.json` (SHA-256 integrity, 152 agents / 96 workflows) | ✅ DONE |
| Phase 1 | `.codex/schemas/` (3 JSON Schema draft-07 files) | ✅ DONE |
| Phase 2 | `agent-registry-validation.yml` **Tier-1 GROUNDED** (exit 1) | ✅ DONE |
| Phase 2 | `agent-handoff-gate.yml` **Tier-1 GROUNDED** (exit 1) | ✅ DONE |
| Phase 3 | `build_embeddings.py`, `query_corpus.py`, `prune_corpus.py` | ✅ DONE |
| Phase 3 | `embedding-index-rebuild.yml` (Tier-2 canary — needs Tier-1 promotion) | ✅ Canary |
| Phase 4 | `e-to-d-transition-gate.yml` (5/5 gate, Tier-2 canary — needs Tier-1 promotion) | ✅ Canary |
| Phase 4 | `orchestrator-agent.md` + `orchestrator_routing.py` | ✅ DONE |
| Phase 5 | `auto_promote_tier.py` (CLI only), `auto_append_accountability.py` | ✅ DONE |
| Phase 5 | `enforcement_kpi_dashboard.py` + `ci-health-monitor.yml` step | ✅ DONE |
| Phase 6 | `actionlint-audit.yml` **Tier-1 GROUNDED** | ✅ DONE |
| Phase 6 | `docs/AGENTIC_REPO_SYSTEM_GUIDE.md`, `docs/audits/AGENTIC_FINAL_KPI_REPORT.md` | ✅ DONE |
| Phase 6 | `semgrep/soft_enforcement.yaml` (6 rules), `.github/CODEOWNERS` (12 entries) | ✅ DONE |

---

## 🔴 TASK 1 — Build FAISS Embeddings in CI

**Goal**: Activate semantic routing in `orchestrator_routing.py` by building the FAISS index in CI.

**Problem**: `orchestrator_routing.py` currently falls back to keyword search with the warning:
```
⚠️ FAISS index not found — falling back to SQLite keyword search.
   Run: python scripts/ci/build_embeddings.py  to build the index.
```

**Steps**:

1. **Manually trigger** `embedding-index-rebuild.yml` once to seed the initial index:
   ```bash
   # From GitHub CLI (requires owner token):
   gh workflow run embedding-index-rebuild.yml --ref main
   ```
   Or navigate to: **Actions → Embedding Index Rebuild → Run workflow**

2. **Verify** the index was built:
   ```bash
   python scripts/ci/query_corpus.py "fix failing CI tests"
   # Should now show FAISS semantic results, not keyword fallback
   ls .codex/embeddings/codex_index_meta.json
   ```

3. **Add `embedding-index-rebuild` step to `agent-registry-validation.yml`** — so the index
   stays fresh whenever the registry changes (currently only nightly at 2AM UTC):
   ```yaml
   # In agent-registry-validation.yml, after the "Refresh CODEX_MANIFEST.json" step:
   - name: Trigger embedding index refresh (if registry changed)
     if: github.event_name == 'push' && github.ref == 'refs/heads/main'
     run: |
       python3 scripts/ci/build_embeddings.py || echo "::warning::Embedding rebuild failed — index may be stale"
   ```

**Files to modify**:
- `.github/workflows/agent-registry-validation.yml` — add optional embedding step on push to main
- `.codex/embeddings/codex_index_meta.json` — will be updated by the workflow run

---

## 🔴 TASK 2 — auto_promote_tier.py Integration into chatops_copilot_trigger.yml

**Goal**: Expose `auto_promote_tier.py` as a `/copilot tier-check` slash command in chatops.

**Current state**: `auto_promote_tier.py` works only from the CLI (`python scripts/ci/auto_promote_tier.py`).
The chatops workflow (`.github/workflows/chatops_copilot_trigger.yml`) supports slash commands:
```
/copilot continue <prompt-file>
/copilot run <prompt-file>
/copilot status
/copilot verify
/copilot help
```

**Steps**:

1. **Read the current chatops workflow** to understand the dispatch pattern:
   ```bash
   cat .github/workflows/chatops_copilot_trigger.yml
   ```

2. **Add a new slash command** `tier-check` to the dispatch job:
   - Command: `/copilot tier-check` — runs `auto_promote_tier.py --check-only` and posts results as a PR comment
   - Command: `/copilot tier-promote` — runs `auto_promote_tier.py` (dry-run stub generator) and attaches stubs as artifacts

3. **Add a new job** `tier-enforcement` in `chatops_copilot_trigger.yml`:
   ```yaml
   tier-enforcement:
     name: Tier enforcement check
     runs-on: ubuntu-latest
     timeout-minutes: 5
     if: contains(github.event.comment.body, '/copilot tier-check') || contains(github.event.comment.body, '/copilot tier-promote')
     steps:
       - uses: actions/checkout@v4
       - uses: actions/setup-python@v5
         with: { python-version: '3.11' }
       - run: pip install pyyaml --quiet
       - name: Run tier enforcement scan
         id: tier_scan
         run: |
           python scripts/ci/auto_promote_tier.py --check-only > /tmp/tier_report.txt 2>&1 || true
           cat /tmp/tier_report.txt
       - name: Post tier report as comment
         uses: actions/github-script@v7
         with:
           github-token: ${{ secrets.GITHUB_TOKEN }}
           script: |
             const fs = require('fs');
             const report = fs.readFileSync('/tmp/tier_report.txt', 'utf8');
             await github.rest.issues.createComment({
               owner: context.repo.owner,
               repo: context.repo.repo,
               issue_number: context.issue.number,
               body: '## 🔰 Tier Enforcement Scan\n\n```\n' + report + '\n```\n_[auto_promote_tier.py | dry-run only]_'
             });
   ```

4. **Update the `/copilot help` response** to include the new commands.

**Files to modify**:
- `.github/workflows/chatops_copilot_trigger.yml` — add `tier-enforcement` job + help text

---

## 🟡 TASK 3 — Architecture Decision Records (ADRs) for Each Phase

**Goal**: Create `docs/arch/ADR-20260302-*.md` files documenting the design decisions for each phase.

**Existing ADR template**: `docs/arch/adr-template.md` (already in repo)

**Steps**:

Create one ADR per major phase decision. Use the existing template. Each ADR should be
~100-200 lines. Required ADRs:

### ADR-1: Registry Schema Extension (Phase 1)
```
docs/arch/ADR-20260302-agent-registry-schema-v1.9.md
```
- **Decision**: Extend AGENT_REGISTRY.yaml with 4 new fields (enforcement_tier, autonomy_model, handoff_protocol, accepts_handoff_from)
- **Context**: Pre-extension state had 128 agents with no enforcement metadata
- **Consequences**: All 152 agents now schema-validated; CODEX_MANIFEST.json provides integrity guarantee

### ADR-2: Tier-1 Gate Promotion (Phase 2)
```
docs/arch/ADR-20260302-tier1-gate-promotion.md
```
- **Decision**: Promote agent-registry-validation.yml + agent-handoff-gate.yml from Tier-2 canary to Tier-1 (exit 1)
- **Context**: 2-sprint observation period completed; no false positive gate fires observed
- **Consequences**: PRs with invalid AGENT_REGISTRY.yaml or AgentHandoffManifest are now blocked

### ADR-3: FAISS Memory Corpus (Phase 3)
```
docs/arch/ADR-20260302-faiss-memory-corpus.md
```
- **Decision**: Use all-MiniLM-L6-v2 (offline, Apache 2.0) with 512-word chunks for agent memory corpus
- **Context**: Orchestrator routing needed semantic search; SQLite keyword fallback insufficient
- **Consequences**: FAISS index must be rebuilt after registry changes; 90-day retention policy enforced by prune_corpus.py

### ADR-4: E→D Transition FSM (Phase 4)
```
docs/arch/ADR-20260302-e-to-d-transition-gate.md
```
- **Decision**: 5-condition FSM gate (C1-C5) before any agent promotion to autonomy_model: "D_CAPABLE"
- **Context**: Prevents premature D-mode activation without registry, manifest, tier, and handoff infrastructure
- **Consequences**: Gate score 5/5 satisfied; transition_active: false until first D_CAPABLE agent assigned

### ADR-5: Self-Healing CI Governance (Phases 5-6)
```
docs/arch/ADR-20260302-agentic-governance.md
```
- **Decision**: actionlint-audit.yml (Tier-1) + semgrep/soft_enforcement.yaml (6 rules) as governance backbone
- **Context**: Soft enforcement patterns (::warning:: only) could regress without structural detection
- **Consequences**: All future workflow regressions to Tier-2 will be caught in PRs

**Files to create**:
- `docs/arch/ADR-20260302-agent-registry-schema-v1.9.md`
- `docs/arch/ADR-20260302-tier1-gate-promotion.md`
- `docs/arch/ADR-20260302-faiss-memory-corpus.md`
- `docs/arch/ADR-20260302-e-to-d-transition-gate.md`
- `docs/arch/ADR-20260302-agentic-governance.md`

---

## 🟡 TASK 4 — Promote e-to-d-transition-gate.yml to Tier-1

**Goal**: After 2-sprint observation (no false positives), promote the E→D gate from `core.warning` to `core.setFailed`.

**Current TODO lines** (from `.github/workflows/e-to-d-transition-gate.yml`):
```
Line 5:  # TODO: Promote to Tier-1 (core.setFailed) after 2-sprint observation period.
Line 125: // TODO: Promote to Tier-1 — change `core.warning` to `core.setFailed` after observation period
Line 127: core.warning(`E→D transition not ready: ${score}/5 conditions met`);
Line 153: _[e-to-d-transition-gate.yml] | Phase 4 FSM | Tier-2 canary_
Line 118: _Canary mode: score < 5 emits warning only. Promote to exit(1) after 2-sprint observation._
```

**Steps** (when 2-sprint observation confirms no false positives):
1. Change `core.warning(...)` → `core.setFailed(...)` on line 127
2. Remove `_Canary mode:_` line from the PR comment body (line 118)
3. Update header comment: "Tier-2 canary" → "Tier-1 GROUNDED gate"
4. Remove all `# TODO: Promote to Tier-1` comments
5. Update `docs/audits/AGENTIC_FINAL_KPI_REPORT.md` to reflect Tier-1 status

**Files to modify**:
- `.github/workflows/e-to-d-transition-gate.yml` — change core.warning → core.setFailed
- `docs/audits/AGENTIC_FINAL_KPI_REPORT.md` — update gate promotion status

---

## 🟡 TASK 5 — Promote embedding-index-rebuild.yml to Tier-1

**Goal**: After FAISS index confirmed healthy (TASK 1 done), promote REQ-10 annotation from `::warning::` to `exit 1` on unhealthy index.

**Current TODO** (from `.github/workflows/embedding-index-rebuild.yml`):
```
Line 62: - name: Emit REQ-10 corpus health annotation (Tier-2)
Line 67: echo "::warning::REQ-10 corpus health: chunk count ${CHUNK_COUNT} below threshold"
```

**Steps**:
1. Change `::warning::REQ-10` → `::error::REQ-10` + `exit 1` on chunk count < 100
2. Update step name: "Emit REQ-10 corpus health annotation (Tier-2)" → "(Tier-1 GROUNDED)"
3. Verify build succeeds with healthy index before promoting

**Files to modify**:
- `.github/workflows/embedding-index-rebuild.yml` — REQ-10 warning → exit 1

---

## 📋 Execution Order

```
TASK 1 (FAISS CI activation)     → Run manually first (workflow_dispatch)
TASK 2 (chatops integration)     → Code change (chatops_copilot_trigger.yml)
TASK 3 (ADRs)                    → Documentation (5 new files in docs/arch/)
TASK 4 (e-to-d Tier-1)          → After 2-sprint observation (do NOT rush)
TASK 5 (embedding Tier-1)       → After TASK 1 confirms healthy index
```

---

## 🧪 Verification Commands

```bash
# Verify base state is intact after merge
python3 -c "
import yaml, json, jsonschema
from collections import Counter
schema = json.load(open('.codex/schemas/AgentRegistrySchema.json'))
data = yaml.safe_load(open('.github/agents/AGENT_REGISTRY.yaml'))
jsonschema.validate(data, schema)
tc = Counter(a.get('enforcement_tier','?') for a in data['agents'])
print(f'✅ {len(data[\"agents\"])} agents | Tiers: {dict(tc)}')
print(f'C3={tc.get(\"SOFT\",0)<=2} | C5={tc.get(\"GROUNDED\",0)>=8}')
"

# Verify manifest integrity
python scripts/ci/generate_manifest.py --verify-integrity

# Check FAISS index state
python scripts/ci/query_corpus.py "orchestrator routing" 2>&1 | head -5

# Tier enforcement dry-run
python scripts/ci/auto_promote_tier.py --check-only

# KPI dashboard
python scripts/ci/enforcement_kpi_dashboard.py

# Prune corpus stats
python scripts/ci/prune_corpus.py --stats
```

---

## ⚠️ Critical Technical Rules

1. **YAML embedded Python**: NEVER use `python3 -c "..."` multiline or `<< 'EOF'` in GitHub Actions
   `run: |` blocks. Always encode with: `echo '<b64>' | base64 -d | python3`.
   Prefer extracting to `scripts/ci/*.py` files (as done with `enforcement_kpi_dashboard.py`).

2. **AGENT_REGISTRY.yaml**: Only modify via Python script — never hand-edit large YAML.
   After any change: run `python scripts/ci/generate_manifest.py` to regenerate `CODEX_MANIFEST.json`.

3. **Tier-1 promotions** (TASK 4 + TASK 5): Do NOT promote before 2-sprint observation confirms
   no false positives. Check GitHub Actions run history for `e-to-d-transition-gate` and
   `embedding-index-rebuild` before promoting.

4. **auto_promote_tier.py**: DRY-RUN ONLY per Domain 8. Never add `--apply` to live workflow.

5. **CODEOWNERS**: All new governance artifacts added to `.github/CODEOWNERS` require
   `@Aries-Serpent/owners` review.

---

## 📊 Current State Summary (as of merge)

```
AGENT_REGISTRY.yaml:  v1.9.0 · 152 agents · GROUNDED=8 · PARTIAL=142 · SOFT=2
CODEX_MANIFEST.json:  152 agents / 96 workflows · SHA-256 integrity ✅
E→D FSM gate:         5/5 ✅ (C3: SOFT≤2 ✅ · C5: GROUNDED≥8 ✅)
d_capable_agents:     0 (transition_active: false)
Tier-1 gates:         agent-registry-validation.yml ✅ · agent-handoff-gate.yml ✅ · actionlint-audit.yml ✅
Tier-2 canary:        e-to-d-transition-gate.yml ⏳ · embedding-index-rebuild.yml ⏳
FAISS index:          NOT YET BUILT (keyword fallback active)
```

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `.github/agents/AGENT_REGISTRY.yaml` | Agent registry (v1.9.0) |
| `CODEX_MANIFEST.json` | Root manifest with integrity hash |
| `.codex/schemas/AgentRegistrySchema.json` | Registry JSON Schema |
| `.codex/schemas/AgentHandoffManifest_v1.1.json` | Handoff manifest schema |
| `scripts/ci/build_embeddings.py` | FAISS index builder |
| `scripts/ci/query_corpus.py` | Semantic + keyword search |
| `scripts/ci/prune_corpus.py` | 90-day retention |
| `scripts/ci/orchestrator_routing.py` | 3-strategy routing |
| `scripts/ci/auto_promote_tier.py` | Dry-run tier stub generator |
| `scripts/ci/enforcement_kpi_dashboard.py` | KPI tier table |
| `.github/workflows/e-to-d-transition-gate.yml` | FSM gate (Tier-2 canary) |
| `.github/workflows/embedding-index-rebuild.yml` | Nightly FAISS rebuild (Tier-2 canary) |
| `.github/workflows/chatops_copilot_trigger.yml` | Slash command dispatcher |
| `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` | Canonical 12-section operating reference |
| `docs/audits/AGENTIC_FINAL_KPI_REPORT.md` | Phase KPI report |
| `semgrep/soft_enforcement.yaml` | Regression detection rules |
| `.github/CODEOWNERS` | Ownership enforcement |
| `docs/arch/` | ADR directory (5 ADRs to add) |

---

## 🚀 @copilot Activation Command

After merging this PR, post the following comment on the next PR or as a new issue:

```
@copilot+claude-sonnet-4.6 continue

Load context from `.codex/docs/SESSION_RESTORE_GROUNDED_FOLLOWUP.md` and execute
all tasks in order (TASK 1 → TASK 5). Begin with TASK 2 (chatops integration) since
TASK 1 requires a manual workflow dispatch. Then create the 5 ADRs (TASK 3).
Defer TASK 4 and TASK 5 (Tier-1 promotions) until 2-sprint observation is confirmed.
```

---

*Created: 2026-03-02 | Branch: copilot/extend-agent-registry-schema → main | PR #3447*
*Author: copilot-swe-agent[bot]*
