# Copilot Hardened Planning Protocol (CHPP) — Session Preload Reference

**Version:** 2.0.0
**Scope:** Optional session-preload planning reference
**Policy Anchor:** [AI Codebase Agency Policy](../CODEBASE_AGENCY_POLICY.md)
**Related profile reference:** `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md`

This reference replaces the v1 preload mandates below; it is not a new universal
policy. The loader prints bounded context to a step log, not proof of attachment
to a hosted prompt. Related profiles are optional context when accessible and
applicable, not prerequisites to authorized work. Local text cannot override
host-supplied instructions or grant credentials, verification or approval.

---

## Preparation, delegation and planning

- Inspect applicable instructions before affected edits; ordinary authorized
  scoped inspection, edits and tests may proceed directly without a PR.
- Respect explicit read-only tasks: inspection/reporting only, no edits or
  session dispatch. Preserve dirty user work without reset, stash or replacement.
- Delegate when useful, authorized and supported by actual tools; unavailable
  specialists do not prohibit direct execution. Never invent agent invocations.
- Use relevant available memory and historical context. Missing optional memory,
  registry access or runtime flags is not a startup gate. Application version
  flags do not pin the hosted service or establish authority.
- Use task-appropriate planning. Direct execution is a valid assignment; no
  compulsory agent binding, lane count or CTEP format applies to every response.

---

## Optional Task → Agent Lookup

These are routing leads, not proof that a profile is available or activated.
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
Secret detected in code          → unified-security-scanner  # pragma: allowlist secret
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

## Scoped execution workflow

### Phase 1: Inspect and bound
- Establish objective, authority, affected paths and acceptance criteria.
- Reuse existing utilities and inspect relevant source; record inaccessible
  sources honestly. A registry is not a grant of platform capabilities.

### Phase 2: Implement or delegate
- Use direct scoped execution or suitable available specialists.
- Parallelize independent work when useful; serialize shared writes and
  dependent integration. Use the actual available tool schema.

### Phase 3: Validate and preserve controls
- Review correctness, tests, documentation, security and integration according
  to risk; no fixed minimum passes or repeated attempts applies.
- Run existing relevant checks with supported interfaces; missing scanners or
  inaccessible CI remain explicit gaps, not fabricated success.
- Fix introduced/relevant defects. Hand off other findings with evidence,
  impact, mitigation, proposed owner and next action; stop only dependent
  unauthorized or unsafe operations.
- Required security owner/reason classification, credential scopes, reviews,
  branch/environment protections and execution approvals remain binding.
- Missing credentials permit inactive fixture tests, not operational activation.
  Independent verification remains NOT_RUN when no suitable verifier is available;
  technical checks and fixture labels are not approval.

### Phase 4: Evidence and handoff
- Record actual checks, actors, failures, unresolved work and continuation.
- Bookkeeping or memory writes are task-specific, not universal completion gates.
- Public comments, retriggers, package publication, merges, settings changes and
  governance activation require applicable authorization; do not self-dispatch
  another session. A missing approval blocks dependent activation, not local work.

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

## Optional progress example

| Task | Assignment | State | Evidence / next action |
| --- | --- | --- | --- |
| Scoped preparation | Direct execution | Pending | Inspect affected source |
| Independent verification | Not yet available | Blocked | Establish suitable verifier |

Account for every task without claiming incomplete tasks are complete.
CTEP tracking is not authorization, independent approval or acceptance.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md` | Related profile, consult only where accessible and applicable |
| `.github/agents/AGENT_SELECTION_GUIDE.md` | Optional routing reference |
| `.github/agents/AGENT_ECOSYSTEM_MAP.md` | Source-declared topology, not deployment proof |
| `.github/agents/AGENT_REGISTRY.yaml` | Local catalog, not hosted activation or authority |
| `.codex/CODEBASE_AGENCY_POLICY.md` | Canonical scoped execution guidance |
| `.codex/docs/COPILOT_AGENT_PROMPT_GUIDE.md` | Per-phase prompt fragments |
| `.codex/docs/AGENTIC_AGENCY_TIPS.md` | Memory system tips and tricks |
