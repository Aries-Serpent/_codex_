# 🗺️ Agent Ecosystem Map

**Version**: 1.0.0
**Last Updated**: 2026-03-24
**Repository**: Aries-Serpent/_codex_
**Total Agents**: 153 active

---

## Overview

This map provides a high-level topology of the agent ecosystem in this repository, showing how specialized agents interact, chain, and coordinate to deliver autonomous operations.

---

## Ecosystem Topology

```
Orchestration Layer
├── orchestrator-agent          — Routes tasks to specialist agents via FAISS/AGENT_REGISTRY.yaml
├── agent-orchestrator          — Coordinates multi-agent workflows
└── cognitive-ooda-loop-agent   — Full OODA loop execution (Observe→Orient→Decide→Act)

CI/CD Layer
├── ci-testing-agent            — Debug CI pipelines, test failures, import errors
├── ci-auto-healer-agent        — Detect and heal CI failures (embedded fix patterns)
├── ci-failure-resolution-agent — Diagnose and resolve CI/CD pipeline failures
├── ci-emergency-response-agent — Emergency fixes for blocking failures
├── ci-triage-pipeline-agent    — Triage CI failures by severity
├── iterative-self-healing-ci   — (workflow) Auto-fix + Copilot escalation
└── artifact-monitor-agent      — CI/CD artifact health monitoring

Security Layer
├── security-audit-agent        — SAST, dependency vulnerabilities, compliance
├── code-scanning-remediation-agent — Fix code scanning alerts
├── codeql-alert-resolution-agent   — Resolve CodeQL security alerts
├── secret-detection-agent      — Detect committed secrets/tokens
└── dependency-vulnerability-scanner — Scan deps for CVEs

Documentation Layer
├── documentation-consolidator  — Eliminate documentation duplication
├── documentation-quality-agent — Assess and improve doc quality
├── link-validator-agent        — Validate internal/external links
└── unified-doc-agent           — Unified documentation management

Testing Layer
├── autonomous-test-healer-agent — Auto-fix failing tests
├── unified-coverage-agent       — Monitor thresholds, fill gaps
├── test-enhancement-agent       — Improve test quality/assertions
├── fragile-test-guardian        — Detect and stabilize flaky tests
└── mutation-testing-agent       — Assess test suite effectiveness

Repository Management
├── repository-hygiene-agent    — Clean up stale files, maintain hygiene
├── repository-organization-agent — Restructure repository layout
└── root-organizer-agent        — Safe incremental root reorganization

Session / Cognitive Layer
├── cognitive-brain-manager     — Manage memory, topology, pattern libraries
├── cognitive-brain-session-injector — Inject session context at start
├── memory-sync-agent           — Consolidate STM→LTM, prune stale entries
└── session-analysis-agent      — Analyze sessions, verify commits, track objectives
```

---

## Agent Interaction Patterns

### Pattern 1: CI Self-Healing Cascade
```
iterative-self-healing-ci.yml
  → ci-auto-healer-agent (apply known fix patterns)
  → [if exhausted] → copilot-escalation job → @copilot
  → ci-failure-resolution-agent (deep diagnosis)
```

### Pattern 2: PR Quality Gate
```
agent-auth-delegation.yml
  → cognitive-preflight (REQ checks)
  → pr-body-checkpoint-guardian
  → session concurrency gate (COPILOT_ACTIVE_SESSION)
  → activate-delegation → Copilot agent session
```

### Pattern 3: Security Scan Pipeline
```
PR push event
  → code-scanning-remediation-agent (CodeQL alerts)
  → codeql-alert-resolution-agent (targeted fixes)
  → dependency-vulnerability-scanner (CVE check)
  → security-audit-agent (full SAST)
```

### Pattern 4: Documentation Freshness
```
doc-freshness-checker → link-validator-agent
  → documentation-quality-agent
  → documentation-consolidator (if duplicates found)
```

---

## Governance

- **Authority Model**: Pre-Genesis (Phase 1 complete) — agents operate in advisory mode
- **Safe Mode**: `autonomous_actions_enabled: false`
- **Escalation Path**: Agents → create GitHub issue → @mbaetiong
- **Policy**: See `.codex/CODEBASE_AGENCY_POLICY.md`

---

## Registry References

- **YAML Registry**: `.github/agents/AGENT_REGISTRY.yaml`
- **Markdown Registry**: `.github/agents/AGENT_REGISTRY.md`
- **Selection Guide**: `.github/agents/AGENT_SELECTION_GUIDE.md`
- **Architecture**: `.github/agents/ARCHITECTURE.md`
