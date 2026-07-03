# 👥 PHASE 8.1 — DOCUMENTATION OWNERSHIP MATRIX (Workstream 8.1.2)

**Track:** 8.1 — Documentation Remediation  
**Track Lead:** unified-doc-agent  
**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE on all gates)  
**Generated:** 2026-07-03T02:20Z  
**Workstream:** 8.1.2 Documentation Ownership & Accountability  
**Scope:** User-facing documentation trees only; excludes immutable archive  

---

## 1. OWNERSHIP MODEL & ACCOUNTABILITY

This matrix establishes **clear ownership and escalation paths** for documentation quality, freshness, and correctness across the Aries-Serpent/_codex_ repository. It operationalizes the audit findings and remediation plan by assigning:

1. **Primary owner** — Responsible for content accuracy, freshness, and consistency within a domain
2. **Fallback owner** — Escalation point if primary is unavailable
3. **Refresh cadence** — How often the docs should be reviewed and updated
4. **SLA thresholds** — Freshness gates (critical vs. general)
5. **Quality checkpoints** — Which agents verify completeness and correctness

---

## 2. DOCUMENTATION OWNERSHIP BY DOMAIN

### 2.1 Core Entrypoints (Root-Level, Canonical)

| Document | Primary Owner | Fallback | Cadence | Freshness SLA | Quality Gate |
|-----------|--------------|----------|---------|---------------|----|
| `README.md` | @unified-doc-agent (coordination) | @skills-master-agent | **30 days (critical)** | Monthly review | doc-quality (C-01), link-validator (C-03) |
| `CONTRIBUTING.md` | @policy-coach-agent | @unified-doc-agent | **30 days (critical)** | Monthly review + before each release | doc-quality, link-validator |
| `SECURITY.md` | @security-audit-agent | @codeql-alert-resolution-agent | **7 days (ultra-critical)** | Continuous (on alert) | doc-quality, security-scanning |
| `CHANGELOG.md` | @pypi-publishing-operations-agent | @orchestrator-agent | **14 days (critical)** | Before release; manual entry | doc-quality |
| `CODE_OF_CONDUCT.md` | @policy-coach-agent | @owner-approval-guard | **90 days** | Quarterly | doc-quality |
| `AGENTS.md` | @skills-master-agent | @orchestrator-agent | **14 days (critical)** | Weekly (agent ecosystem churn) | doc-quality (custom agent inventory) |
| `LICENSE` | @owner-approval-guard | @policy-coach-agent | **N/A (static)** | Governance-triggered only | Policy gate only |

**Notes:**
- **Critical threshold = 30 days:** Core user entrypoints, security, contribution guidance
- All root docs: **0 broken links allowed** (P0 constraint)
- Escalation to @mbaetiong if > 2 missed cadences on critical docs

---

### 2.2 `docs/` Tree (MkDocs canonical site, 1,800 files)

#### 2.2.1 — Top-Level & Index Documents

| Path | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `docs/index.md` | @unified-doc-agent | @post-merge-doc-alignment-agent | **30 days (critical)** | Monthly | Landing page; high visibility |
| `docs/README.md` | @post-merge-doc-alignment-agent | @unified-doc-agent | **30 days** | Monthly | Navigation hub |
| `docs/CHANGELOG.md` | @pypi-publishing-operations-agent | @changelog-agent (N/A; tbd) | **14 days** | Release notes + feature announcements |  Mirrors root CHANGELOG |
| `docs/TERMINOLOGY_GLOSSARY.md` | @terminology-consistency-agent | @policy-coach-agent | **30 days (critical)** | **CREATE in 8.1.3; then quarterly** | P0 missing doc; must exist |

#### 2.2.2 — Guides & Reference (`docs/guides/`, `docs/reference/`, `~145 files)

| Path/Pattern | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `docs/guides/*` (48 files) | @post-merge-doc-alignment-agent | @doc-refactor-test-agent | **60 days** | Quarterly | User onboarding + how-tos |
| `docs/reference/api*.md` (15 files) | @codebase-health-guardian | @python-architect-agent | **30 days** | **Monthly (API churn)** | Code-example validation required |
| `docs/reference/cli*.md` (8 files) | @cognitive-brain-cli-agent | @cli-auto-healer-agent | **30 days** | Monthly | CLI option/subcommand drift |
| `docs/templates/*.md` (61 files) | @unified-doc-agent | @doc-refactor-test-agent | **90 days** | Quarterly | Boilerplate; lower churn expected |

#### 2.2.3 — Administration & Operations (`docs/admin/`, `docs/ops/`, ~103 files)

| Path/Pattern | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `docs/admin/*` (30 files) | @owner-approval-guard | @policy-coach-agent | **60 days** | Quarterly | Access control, governance, org policy |
| `docs/ops/*` (73 files) | @workflow-health-monitor | @artifact-monitor-agent | **30 days** | Monthly | Infrastructure, monitoring, deployment runbooks |
| `docs/security/*` (49 files) | @security-audit-agent | @codeql-alert-resolution-agent | **14 days** | Monthly + alert-triggered | Threat model, vulnerability response |

#### 2.2.4 — Agent & Cognitive Brain Documentation (`docs/agent/`, `docs/cognitive_brain/`, ~144 files)

| Path/Pattern | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `docs/agent/index.md` | @skills-master-agent | @orchestrator-agent | **14 days (critical)** | Weekly | Master agent registry + descriptions |
| `docs/agent/{agent-name}/` (per-agent subdir) | **Per-agent owner** (see below) | @skills-master-agent | **30 days** | Monthly | Individual agent docs maintained by agent author |
| `docs/cognitive_brain/*` (53 files) | @cognitive-brain-session-injector | @skills-master-agent | **30 days** | Monthly | Cognitive brain architecture, skills, OODA loop |

**Per-Agent Ownership Sub-Matrix (high-value agents):**

| Agent Name | Primary Owner | Fallback | Focus Docs |
|-----------|--------------|----------|-----------|
| skills-master-agent | @skills-master-agent | @orchestrator-agent | `docs/agent/skills-master-agent/`, agent lifecycle docs |
| orchestrator-agent | @orchestrator-agent | @agent-iq-scoring-gate | Multi-agent coordination, routing |
| ci-auto-healer-agent | @ci-auto-healer-agent | @ci-testing-agent | CI failure patterns, self-healing loops |
| unified-doc-agent | @unified-doc-agent | @post-merge-doc-alignment-agent | Documentation health, audit, remediation |
| cognitive-brain-session-injector | @cognitive-brain-session-injector | @cognitive-ooda-loop-agent | Session injection, context management |
| autonomous-test-healer-agent | @autonomous-test-healer-agent | @test-failure-analyzer-agent | Test failure diagnosis, remediation patterns |
| security-audit-agent | @security-audit-agent | @codeql-alert-resolution-agent | Security audit procedures, vulnerability response |
| packaging-validation-agent | @packaging-validation-agent | @dependency-security-review-agent | Dependency management, lockfile handling |

#### 2.2.5 — Validation, Testing, & Coverage (`docs/testing/`, `docs/validation/`, ~101 files)

| Path/Pattern | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `docs/testing/*` (32 files) | @test-enhancement-agent | @autonomous-test-healer-agent | **30 days** | Monthly | Test patterns, coverage goals, TDD |
| `docs/validation/*` (69 files) | @qa-walkthrough-agent | @ml-validation-suite-agent | **30 days** | Monthly | QA procedures, acceptance criteria |

#### 2.2.6 — Architecture & Design (`docs/arch/`, ~29 files)

| Path/Pattern | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `docs/arch/*` (29 files) | @codebase-health-guardian | @python-architect-agent | **60 days** | Quarterly | System design, component interaction |

#### 2.2.7 — Archive & Superseded (`docs/archive/`, ~108 files)

| Path | Owner | SLA | Notes |
|------|-------|-----|-------|
| `docs/archive/**` | @unified-doc-agent (inventory) | None (immutable) | Historical docs; do not modify; reference with care in current docs |

---

### 2.3 `.github/agents/` & Copilot Prompt Library (1,188 files, 331 agent specs)

#### 2.3.1 — Custom Agent Specifications (`.github/agents/*.md`, ~331 files)

| Path Pattern | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `.github/agents/{agent-name}.md` (per-agent) | **Per-agent owner** (coordination: @skills-master-agent) | @orchestrator-agent | **30 days** | Monthly | Agent prompt, capabilities, inputs/outputs; mirrors `.github/agents/` YAML spec |
| `.github/agents/AGENT_REGISTRY.yaml` | @skills-master-agent | @orchestrator-agent | **7 days (critical)** | Weekly | Master agent registry; must stay in sync with actual agents |

#### 2.3.2 — Copilot Prompts (`.github/copilot-prompts/`, ~391 files)

| Path Pattern | Owner | Fallback | Cadence | SLA | Notes |
|------|-------|----------|---------|-----|-------|
| `.github/copilot-prompts/**/*.md` | @cognitive-brain-session-injector | @unified-doc-agent | **30 days** | Monthly | Copilot user prompts; update as LLM capabilities shift |

---

### 2.4 Coordination Domains (Cross-Cutting Responsibility)

| Domain | Primary Owner | Stakeholders | Cadence | Focus |
|--------|--------------|-------------|---------|-------|
| **Terminology consistency** | @terminology-consistency-agent | All doc owners | **Continuous** | Glossary updates, terminology audit scores |
| **Link health** | @unified-doc-agent + @doc-refactor-test-agent | All doc owners | **Weekly** (post-CI-gate deploy) | Broken link reports, prioritization |
| **Code-example validation** | @doc-refactor-test-agent | API/reference owners | **Monthly** | Example code runs without error |
| **Freshness gating** | @unified-doc-agent | All doc owners | **Weekly** | SLA monitoring, escalation |
| **Post-merge doc alignment** | @post-merge-doc-alignment-agent | All doc owners | **On release** | Doc ↔ codebase drift detection |

---

## 3. ESCALATION PATHS & RESOLUTION

### 3.1 Escalation Triggers

| Trigger | Action | Escalate To | Timeline |
|---------|--------|-------------|----------|
| **Critical doc stale > 30 days** | PR notification + Slack alert | Primary → Fallback → @mbaetiong | Within 48 h |
| **Broken P0 link detected** | CI gate blocks merge + issue filed | Primary + @doc-refactor-test-agent | Within 24 h fix target |
| **Terminology mismatch across docs** | Report filed by @terminology-consistency-agent | Primary + @terminology-consistency-agent | Within 1 week |
| **Low code-example validation score** | Alert + remediation plan | API owner + @doc-refactor-test-agent | Within 2 weeks |
| **Multiple SLA misses (≥2 in quarter)** | Reassignment review | Primary owner + @mbaetiong | Immediate |
| **Docs conflict with code changes** | Regression detected by @post-merge-doc-alignment-agent | Primary + code author | Within sprint |

### 3.2 Communication Channels

- **Critical escalations (security, API correctness):** GitHub issue + @mention + Slack (#documentation)
- **Freshness alerts:** Automated comment on open PRs (CI gate)
- **Routine updates:** GitHub Discussions "Documentation-Health" category (weekly digest)
- **Ownership disputes or reassignments:** Direct to @mbaetiong

---

## 4. SPECIAL RESPONSIBILITIES

### 4.1 Disambiguation: Multi-Owner Documents

Some docs have multiple owners with distinct responsibilities:

**Example: `docs/reference/api*.md`**
- **Primary owner** (@codebase-health-guardian): Conceptual accuracy, API surface coverage, architecture alignment
- **Code-example validator** (@doc-refactor-test-agent): Examples run without error, imports resolve, outputs match specification
- **Link validator** (@unified-doc-agent): All code cross-refs point to current `.py` locations
- **Freshness owner** (@codebase-health-guardian): API changes require doc updates within 14 days of merge

**Responsibility handoff:** If primary owner misses SLA, fallback takes over. If *both* miss, escalate to @mbaetiong.

### 4.2 Agent Responsibility Expansion (Post-Phase-8.1)

As Phase 8.1 closes and automation wires in:

| Responsibility | Current (Manual) | Post-8.1 (Automated) | Owner |
|---|---|---|---|
| Freshness checking | Manual ad-hoc review | CI gate (nightly + on PR) | unified-doc-agent (gate owner) |
| Broken link detection | Sample-based audit | Full validator pass (weekly CI) | unified-doc-agent (gate owner) |
| Terminology consistency scanning | Manual audit (quarterly) | Automated consistency checker | terminology-consistency-agent |
| Code-example validation | Manual spot-checks | CI test harness (pre-merge) | doc-refactor-test-agent |

---

## 5. ACCOUNTABILITY & DASHBOARDS

### 5.1 Freshness Scorecard (Weekly)

To be generated by unified-doc-agent (post-8.1.5 gate wiring):

```
FRESHNESS SCORECARD — Week of 2026-07-10

Critical Docs (SLA: 30 days max stale)
├─ README.md                          ✅ 3 days old (reviewed 2026-07-07)
├─ CONTRIBUTING.md                    🟡 42 days old (last: 2026-05-27) ⚠️ ALERT
├─ SECURITY.md                        ✅ 2 days old (reviewed 2026-07-08)
├─ docs/index.md                      ✅ 5 days old (reviewed 2026-07-05)
├─ AGENTS.md                          🟡 21 days old (last: 2026-06-19)
└─ CHANGELOG.md                       🟡 35 days old (last: 2026-05-31) ⚠️ ALERT

General Docs (SLA: 90 days max stale)
├─ docs/guides/* (48 files)          ✅ 78/48 compliant; 2 warnings
├─ docs/reference/* (23 files)        ✅ 23/23 compliant
├─ docs/admin/* (30 files)            🟡 24/30 compliant; escalate
├─ docs/ops/* (73 files)              ✅ 71/73 compliant
└─ docs/arch/* (29 files)             ✅ 29/29 compliant

Action Items:
1. @policy-coach-agent: Review CONTRIBUTING.md (42 days, SLA 30)
2. @pypi-publishing-operations-agent: Update CHANGELOG.md (35 days, SLA 14)
3. @owner-approval-guard: Audit docs/admin/* (compliance 80%)

Last Updated: 2026-07-09T23:15Z
```

### 5.2 Link Health Dashboard (Weekly, post-CI gate)

```
LINK VALIDATION REPORT — Week of 2026-07-10

User-Facing Docs Broken Links: 3 / 12,000 relative links (0.025%) ✅

P0 Critical Links (blocking): 0 broken ✅
├─ Code references (src/**/*.py): 0 broken
├─ Terminology glossary links: 0 broken
└─ API cross-refs: 0 broken

P1 Important Links: 2 broken 🟡
├─ docs/guides/deprecated-pattern.md → ./old-api.md (FP: whitelisted 2026-07-08)
└─ docs/ops/runbook.md → ../archived/script.sh (valid; archive path)

P2 Low-Priority Links (waivered): 1 broken
└─ docs/archive/2025-notes/summary.md → htmlcov/index.html (historical; archived)

Escalation: None required
Last Updated: 2026-07-09T23:30Z
```

### 5.3 Ownership Coverage Matrix (Monthly)

| Owner | Primary Docs | Fallback Docs | Escalations (30d) | Freshness Score |
|-------|--------------|-----------|--------|---------|
| @unified-doc-agent | 12 | 18 | 0 | 98% |
| @post-merge-doc-alignment-agent | 96 | 24 | 2 | 87% |
| @security-audit-agent | 49 | 8 | 0 | 100% |
| @policy-coach-agent | 31 | 12 | 1 | 92% |
| @skills-master-agent | 42 | 36 | 0 | 95% |
| @terminology-consistency-agent | 1 | 1 | 0 | New (Phase 8.1) |
| **TOTAL** | **231** | **99** | **3** | **94%** |

---

## 6. ONBOARDING: NEW DOC OWNERSHIP

When a new agent is deployed or a new documentation domain is created:

1. **Owner nomination:** Submit to @mbaetiong with:
   - Primary owner name + contact
   - Fallback owner (or recommend default)
   - Proposed freshness cadence (critical 30d / general 90d)
   - Quality gates (link-validator, code-examples, terminology check, etc.)

2. **Matrix update:** unified-doc-agent updates this document within 1 business day

3. **CI wiring:** unified-doc-agent ensures doc is included in freshness + link gates

4. **Handoff meeting:** 30 min sync between old/new owner (if ownership transfer)

---

## 7. CURRENT STATE → PHASE 8.1 TRANSITION

### 7.1 Temporary Ownership During Remediation (Weeks 1–6)

During Workstreams 8.1.2 through 8.1.5:

| Workstream | Temp Owner | Normal Owner | Revert Date |
|-----------|-----------|-----------|-----------|
| Freshness signal bootstrap | @unified-doc-agent | (Per domain) | 2026-07-17 (Week 2 end) |
| Link fixes | @doc-refactor-test-agent | (Per domain) | 2026-07-24 (Week 3.5 end) |
| Report consolidation | @ci-health-alert-agent | N/A (archive) | 2026-08-07 (Week 5 end) |
| CI gate wiring | @unified-doc-agent + @workflow-compliance-guardian | (Per gate) | 2026-08-14 (Week 6.5 end) |

### 7.2 "Frozen" Docs During Remediation

During 8.1.3–8.1.4, some docs are flagged as "under remediation" and may have:
- **Link changes** (targets updated)
- **Front-matter additions** (new `last_reviewed:` fields)
- **Path moves** (to `.codex/archive/`, affecting cross-refs)

**Stability commitment:** Once a doc is transitioned, it is **not revisited** within the same remediation phase. Only bugs/critical fixes trigger re-opening.

---

## 8. APPENDIX: OWNERSHIP TRANSFER CHECKLIST

**Use this when changing ownership of a documentation domain:**

- [ ] **Outgoing owner:**
  - [ ] Document current state (known issues, pending updates)
  - [ ] List all docs under this domain
  - [ ] Identify any automated tasks/CI hooks
  - [ ] Update `.github/CODEOWNERS` file

- [ ] **Incoming owner:**
  - [ ] Review existing docs + audit findings
  - [ ] Confirm fallback owner agreement
  - [ ] Test CI gates + automation for domain
  - [ ] Schedule 30-min kickoff with outgoing owner

- [ ] **unified-doc-agent:**
  - [ ] Update this ownership matrix (PHASE_8_1_DOC_OWNERSHIP_MATRIX.md)
  - [ ] Update `.github/CODEOWNERS` (primary + fallback)
  - [ ] Test CI gate changes
  - [ ] Announce transfer in GitHub Discussions

---

## 9. SUCCESS CRITERIA FOR PHASE 8.1

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Ownership clarity** | Every user-facing doc has primary + fallback owner | 100% coverage in this matrix |
| **Escalation paths documented** | Clear SLA + escalation thresholds for all levels | This document, section 3 |
| **Automation baseline** | CI gate ready to enforce ownership (Week 6) | `.github/workflows/doc-freshness-gate.yml` deployed |
| **Scorecard published** | Weekly freshness + link dashboards live (Week 7+) | Automated reporting via CI artifacts |

---

**Ownership Matrix Status:** 🟢 COMPLETE — Workstream 8.1.2 planning deliverable  
**Generated:** 2026-07-03T02:20Z  
**Effective Date:** 2026-07-10 (after Phase 8.1.2a completion)  
**Review Cadence:** Monthly (or on agent deployment)  
**Approver:** @mbaetiong (D-tier gate)
