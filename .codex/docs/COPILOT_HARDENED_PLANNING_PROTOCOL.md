# Copilot Hardened Planning Protocol (CHPP) — Session Preload Reference

**Version:** 1.0.0
**Effective Date:** 2026-06-11
**Canonical Source:** `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md`
**Policy Anchor:** `.codex/CODEBASE_AGENCY_POLICY.md` § Custom Agent Delegation Mandate

> This file is the **session-preload-accessible copy** of the CHPP. It is designed
> to be read at the start of every Copilot session via the mandatory pre-load sequence
> in `copilot-setup-steps.yml`. For the full specification, always consult the canonical
> source above.

---

## TL;DR — Three Hard Rules for Every Session

```
Rule 1: Agent-First Delegation (AFD)
  → Before ANY bash/grep/edit, check AGENT_SELECTION_GUIDE.md.
  → If a Custom Agent covers the task, use task(agent_type="...", mode="background").
  → Never bypass a Custom Agent for covered task categories.

Rule 2: Mandatory Session Pre-Load Validation (MSPV)
  → Verify: COPILOT_AGENT_CCA_VERSION_LOCK=stable
  → Read: .codex/CODEBASE_AGENCY_POLICY.md
  → Read: docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
  → Read: last 5 lines of .codex/aftermath/pda_iterations.jsonl
  → Resolve: applicable agents from AGENT_REGISTRY.yaml capability_tags

Rule 3: CTEP-Aligned Plan Structure (CAPS)
  → Every plan MUST bind each task to an agent_type.
  → Format: "- [ ] Task: [desc] → agent_type: `<id>`"
  → Plans without agent bindings are non-compliant.
```

---

## Quick Task → Agent Lookup

```
CI pipeline failing              → ci-testing-agent → ci-auto-healer-agent
CI import error                  → ci-importerror-agent
CI emergency (blocking PR)       → ci-emergency-response-agent
CI workflow YAML broken          → workflow-ci-fixer
Docker build failing             → ci-docker-build-healer
Test coverage below threshold    → unified-coverage-agent
Flaky/intermittent test          → fragile-test-guardian
Test assertions outdated         → test-alignment-fixer-enhanced
New test cases needed            → test-enhancement-agent
CodeQL security alert            → codeql-alert-resolution-agent
Secret detected in code          → unified-security-scanner
Dependency CVE found             → unified-security-scanner
Full security audit              → unified-security-scanner
Doc link broken                  → link-validator-agent
Stale documentation              → doc-freshness-checker
Duplicate documentation          → unified-doc-agent
Post-merge doc drift             → post-merge-doc-alignment-agent
Stale repository files           → repository-hygiene-agent
Dependency version conflict      → dependency-conflict-agent
Python 3.12 type errors          → python-312-type-fixer
mypy type check failures         → mypy-manager-agent
Windows filename incompatibility → cross-platform-filename-validator
RAG index stale                  → rag-freshness-loop-agent
Session memory consolidation     → memory-sync-agent
Session objective tracking       → session-analysis-agent
Agent capability routing         → orchestrator-agent
```

---

## Four-Phase Execution Workflow (Summary)

### Phase 1: Diagnosis & Routing
- Map problem → agent layer via `AGENT_ECOSYSTEM_MAP.md`
- Identify primary + chain agents via `AGENT_SELECTION_GUIDE.md`
- Record binding in the Agent Binding Map table

### Phase 2: Parallel Task Dispatch
- Use `task(agent_type="...", mode="background")` for independent tasks
- Use sequential dispatch only for chained dependencies
- Call `read_agent(agent_id=..., wait=True)` to fetch results

### Phase 3: Automated Quality & Security Validation
- Call `parallel_validation(...)` before PR creation
- Address all valid Code Review + CodeQL findings
- Plan `post-merge-doc-alignment-agent` for post-merge doc sync

### Phase 4: Memory & Accountability Updates
- Call `store_memory()` for new repository conventions
- Append to `.codex/aftermath/pda_iterations.jsonl`
- Delegate: `memory-sync-agent` + `session-analysis-agent`

---

## Agent Ecosystem Layers (Summary)

| Layer | Key Agents |
|-------|-----------|
| Orchestration | `orchestrator-agent`, `skills-master-agent`, `cognitive-ooda-loop-agent` |
| CI/CD & Build | `ci-testing-agent`, `ci-auto-healer-agent`, `artifact-monitor-agent`, `workflow-ci-fixer` |
| Security | `unified-security-scanner`, `codeql-alert-resolution-agent` |
| Testing | `unified-coverage-agent`, `autonomous-test-healer-agent`, `fragile-test-guardian` |
| Documentation | `unified-doc-agent`, `link-validator-agent` |
| Repository Mgmt | `repository-hygiene-agent`, `root-organizer-agent`, `reference-updater-agent` |
| Session / Cognitive | `cognitive-brain-session-injector`, `session-analysis-agent`, `memory-sync-agent` |
| Governance | `unified-governance-gate`, `owner-approval-guard`, `policy-coach-agent` |

---

## CTEP-Compliant Plan Template

```markdown
## 📊 Task Execution Progress

### Phase 1: [Name] — 0% Complete
- [ ] Task 1.1: [Description] → agent_type: `ci-testing-agent` ⏳ PENDING
- [ ] Task 1.2: [Description] → agent_type: `unified-coverage-agent` ⏳ PENDING

## 🔍 Agent Binding Map
| Task | Agent | Mode | Priority |
|------|-------|------|----------|
| Fix CI failure | ci-testing-agent | background | P0 |
| Fill coverage gaps | unified-coverage-agent | background | P1 |

## ✅ Completion Summary
Total Tasks: 2 | Completed: 0 ✅ | Skipped: 0 ❌
CTEP Compliance: ⏳ IN PROGRESS
CAD-Mandate Compliance: ✅ PASS (all tasks have agent bindings)
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md` | Full CHPP specification |
| `.github/agents/AGENT_SELECTION_GUIDE.md` | Quick decision tree by task type |
| `.github/agents/AGENT_ECOSYSTEM_MAP.md` | Topology of all agent interactions |
| `.github/agents/AGENT_REGISTRY.yaml` | Authoritative agent capability registry |
| `.codex/CODEBASE_AGENCY_POLICY.md` | Policy anchor for CAD-Mandate |
| `.codex/docs/COPILOT_AGENT_PROMPT_GUIDE.md` | Per-phase prompt fragments |
| `.codex/docs/AGENTIC_AGENCY_TIPS.md` | Memory system tips and tricks |
