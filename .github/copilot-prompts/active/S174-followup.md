# 🎯 Follow-Up Prompt — S174 Session
# PR: copilot/update-ci-failure-rate-and-confirm-transition
# Branch: copilot/update-ci-failure-rate-and-confirm-transition → 0D_base_ → main
# Generated: 2026-03-22T03:13Z | Agent: copilot-swe-agent[bot]
# Status: 🟡 AWAITING OWNER ACTION (sub-PR creation requires CODEX_MASTER_KEY)

---

## 📋 Session S174 — Completed Work

### ✅ All Completed (this session)

| # | Commit | Description |
|---|--------|-------------|
| 1 | `cf0d2f2` | feat(S174): execute consolidation planset — archive workflows, deprecate agents, remove Art_ prefix |
| 2 | `9fea48d` | docs: update INTEGRATION_BRANCH_MODEL.md |
| 3 | `e79aef5` | feat(S174+delegation): extend GitHubMCPPoster + MCP improvements doc + fix INDEX.md |
| 4 | `d4bb011` | feat(S174): add promote-integration-branch.yml |
| 5 | `c561db7` | fix(security): pr_title via env var |
| 6 | `c0095ce` | feat: energy-conversion-agent (cherry-pick) |
| 7 | `6b2247e` | chore: plan Claudeclaw autonomous management (cherry-pick) |
| 8 | `7c75962` | chore: plan abbreviation pass (cherry-pick) |
| 9 | `237febd` | feat: energy-conversion-agent v1.2.0 (cherry-pick) |
| 10 | `b988f2d` | fix(docs): accountability + CHANGELOG conflict resolved |
| 11 | `2c83149` | chore: follow-up prompt PR #3664 |
| 12 | `bd98345` | fix(docs): CHANGELOG auto-update |
| 13 | `f80b395` | feat(migration): cherry-pick complete, total_agents 157 |
| 14 | (this) | fix(gates): archive 2 oversized agent files + cognitive brain S174 status + create-sub-pr workflow |

---

## 🎯 Owner Actions Required (before next @copilot session)

### Action 1: Approve `agent-auth-delegation` environment gate

The `agent-auth-delegation.yml` workflow is waiting for approval at the
`agent-auth-delegation` environment gate.

1. Go to: https://github.com/Aries-Serpent/_codex_/actions
2. Find the run titled "Agent Auth Delegation" or "Token Delegation"
3. Click "Review pending deployments"
4. Approve → this sets `COPILOT_AGENT_AUTH_ENABLED=true` and posts `@copilot continue`

### Action 2: Create sub-PR → 0D_base_ (once this PR is merged to its target)

Once this PR's CI passes, trigger the new `create-sub-pr-to-0D_base_.yml` workflow:

```bash
# After merging to target, or directly:
gh workflow run create-sub-pr-to-0D_base_.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  -f session_branch=copilot/update-ci-failure-rate-and-confirm-transition
```

**Or via GitHub Actions UI:**
Actions → "🔀 Create Sub-PR: Session Branch → 0D_base_" → Run workflow

### Action 3: Promote 0D_base_ → main

After the sub-PR is merged into `0D_base_`, trigger the promotion:

```bash
gh workflow run promote-integration-branch.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  -f source_branch=0D_base_
```

---

## 🚀 Next @copilot Session — Priority Tasks

### 🔴 Priority 1 — Unblocked NOW

```markdown
@copilot
## S175 Session Task

### Context
- Session S174 completed: consolidation + MCP write methods + energy-conversion migration
- Branch model: copilot/session-* → 0D_base_ → main
- AAIS score: ~82.5 (A−), target 90 (A)

### Priority 1 Tasks (complete ALL)

**P1.1: Implement MCP real-mode JSON-RPC 2.0 transport (IMP-004)**
File: `src/codex/github/mcp_poster.py`
Replace the `_execute_real()` placeholder stub with actual JSON-RPC 2.0 transport:
- POST to `https://api.githubcopilot.com/mcp/`
- Handle `id`, `method`, `params`, `result`, `error` fields per JSON-RPC spec
- Add `CODEX_MCP_ENDPOINT` env var override for staging

**P1.2: Playwright storage-state auth (IMP-006)**
File: `tests/playwright/conftest.py` (create if absent)
- Global setup: save GitHub OAuth session to `playwright/.auth/user.json`
- All test fixtures use stored state (no re-login per test)
- Add `tests/playwright/test_github_mcp_e2e.py` — E2E delegation activation test

**P1.3: Test coverage 72% → 80%**
- Run `pytest --cov=codex --cov-report=term-missing`
- Identify lowest-coverage modules
- Add targeted tests until `fail_under=80` passes

### Validation
```bash
python -m pytest tests/github/ tests/playwright/ -v
python scripts/ci/check_cross_references.py
python -c "import yaml; r=yaml.safe_load(open('.github/agents/AGENT_REGISTRY.yaml')); assert r['total_agents']==len(r['agents'])"
```

### Required PR Body (EVERY commit)
- Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- Update `CHANGELOG.md [Unreleased]`
- `[x] Enable Agent Token Delegation`
- `[x] 💰 Cost Proposal Approved`
```

### 🟡 Priority 2 — Next 2 sessions

```markdown
**P2.1: Cognitive brain lifecycle hooks (IMP-012)**
- On `create_ref()` → record pattern `CB-branch-create` in cognitive_brain
- On `create_pull_request()` → record pattern `CB-pr-open`
- On `merge_branch()` → record pattern `CB-merge` with outcome

**P2.2: energy-conversion-agent simulation unit tests**
- Create `tests/agents/test_energy_conversion.py`
- Test G2E conversion calculation functions
- Test RPi/SBC pattern logic
```

---

## 📐 Production-Ready Agent Designs — S174

### Agent: `promote-integration-branch` (NEW ✅)

```yaml
id: promote-integration-branch
name: Promote Integration Branch
version: 1.0.0
file: .github/workflows/promote-integration-branch.yml
status: active
description: >
  Autonomously creates 0D_base_ branch from a given SHA using
  GitHubMCPPoster.create_ref() and opens the 0D_base_ → main
  promotion PR using create_pull_request(). Requires CODEX_MASTER_KEY.
  workflow_dispatch only (must be on main branch to run).
capability_tags:
  - branch_creation
  - pr_lifecycle
  - integration_branch_management
  - promotion_workflow
```

### Agent: `create-sub-pr-to-0D_base_` (NEW ✅)

```yaml
id: create-sub-pr-to-0D_base_
name: Create Sub-PR to 0D_base_
version: 1.0.0
file: .github/workflows/create-sub-pr-to-0D_base_.yml
status: active
description: >
  Creates a pull request from any session branch into 0D_base_
  (the staging integration branch). Verifies 0D_base_ exists,
  checks for existing PRs (idempotent), and uses mcp_poster create-pr.
  Requires CODEX_MASTER_KEY (pull-requests:write).
capability_tags:
  - sub_pr_creation
  - session_branch_management
  - 0D_base_routing
```

### Agent: `energy-conversion-agent` (MIGRATED v1.2.0 ✅)

```yaml
id: energy-conversion-agent
name: Energy Conversion Agent
version: 1.2.0
file: .github/agents/energy-conversion-agent.md
status: active
description: >
  AI-enhanced agent for G2E (gas-to-electric) energy conversion simulation.
  RPi/SBC patterns, Claudeclaw autonomous management, APA citations,
  thermodynamic modeling, grid stability, AI-driven PD optimization.
capability_tags:
  - energy_conversion_simulation
  - gas_to_electric
  - power_distribution
  - thermodynamic_modeling
  - rpi_sbc_patterns
  - claudeclaw_autonomous_mgmt
```

---

## ✅ Validation Gate Results

| Gate | Status | Details |
|------|--------|---------|
| Cross-reference gate | ✅ PASS | 4 files, 0 broken refs |
| Workflow YAML | ✅ PASS | 128 files parse OK |
| AGENT_REGISTRY count | ✅ PASS | total_agents=157, actual=157 |
| Agent file size gate | ✅ PASS | all ≤30,000 chars (2 archived: QA_AGENT, INFRA_LINTER) |
| mcp_poster tests | ✅ PASS | 22/22 |
| Deferral language | ✅ PASS | 0 violations |
| Python compile | ✅ PASS | src/codex/github/mcp_poster.py |

---

## 🔐 Agent Token Delegation Status

- [x] `COPILOT_AGENT_AUTH_ENABLED` checkbox checked in PR body
- [ ] Owner approval pending in GitHub Actions UI
- [ ] `COGNITIVE_BRAIN_ALLOWED_ACTORS` updated (post-approval)
- [ ] `@copilot continue` auto-posted (post-approval)

---

*This prompt was auto-generated by S174 session — 2026-03-22T03:13Z*
*Post as PR comment and save to `.github/copilot-prompts/active/S174-followup.md`*
