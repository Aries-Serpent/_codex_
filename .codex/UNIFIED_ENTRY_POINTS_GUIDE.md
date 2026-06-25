# 🎯 UNIFIED ENTRY POINTS GUIDE

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:50:36.098694  
**Purpose:** Navigate the 6 unified consolidation points

---

## Overview

The _codex_ ecosystem includes 6 strategic unified consolidation points that aggregate multiple agents:

1. **unified-coverage-agent** - Test coverage management (replaces 5 agents)
2. **unified-doc-agent** - Documentation consolidation (replaces 5 agents)
3. **unified-security-scanner** - Security scanning (replaces 5+ agents)
4. **unified-governance-gate** - Policy enforcement (replaces multiple agents)
5. **cache-management-agent** - 4-layer cache hierarchy
6. **self-healing-orchestrator-agent** - RP-001+ pattern coordination

---

## 1️⃣ unified-coverage-agent

### Purpose
Single entry point for ALL test-coverage work: monitor thresholds, fill gaps, maintain CI enforcement, and drive the incremental coverage roadmap.

### What It Consolidates
- `coverage-gapfill-agent` - Fills gaps in low-coverage modules
- `coverage-maintenance-agent` - Maintains coverage over time
- `coverage-roadmap-agent` - Drives incremental roadmap
- `test-coverage-agent` - Monitors thresholds
- `test-coverage-monitor` - Enforces CI gates

### When to Use
**Use this agent when:**
- Need to improve overall test coverage
- Coverage is below threshold and needs to be increased
- Need to prevent coverage regressions
- Planning multi-phase coverage improvement
- Need gap-filling for specific modules
- Coverage gate is blocking PR merge

**Do NOT use when:**
- Need to fix individual failing tests (→ autonomous-test-healer-agent)
- Need to stabilize flaky tests (→ fragile-test-guardian)
- Need mutation testing analysis (→ mutation-testing-agent)

### Decision Tree

```
"Need to improve test coverage?"
  ├─ "Monitor coverage thresholds?" → unified-coverage-agent (monitor mode)
  ├─ "Fill coverage gaps?" → unified-coverage-agent (gap-fill mode)
  ├─ "Maintain coverage progress?" → unified-coverage-agent (maintenance mode)
  ├─ "Create multi-phase roadmap?" → unified-coverage-agent (roadmap mode)
  └─ "Enforce CI coverage gates?" → unified-coverage-agent (CI gate mode)
```

### Activation
```bash
@copilot use unified-coverage-agent
Task: "Improve test coverage for src/authentication/ module from 42% to 80%"
```

### Performance Characteristics
- **Runtime:** 5-15 minutes (depends on test suite size)
- **Model:** Haiku 4.5 (cost-optimized)
- **Parallelization:** Yes (can run multiple gap-fills in parallel)
- **Token Usage:** ~2000-5000 tokens per coverage report

### Integration Patterns
- **Sequential:** PR check → coverage analysis → gap-fill → verification
- **Conditional:** IF coverage < threshold THEN unified-coverage-agent ELSE pass
- **Aggregation:** Collect coverage metrics from multiple modules

### Use Case Examples

**Example 1: Emergency Coverage Gate Fix**
```
Status: Coverage below 75% threshold
Agent: unified-coverage-agent
Mode: Emergency gap-fill
Target: Increase coverage to 80%
Timeline: 2 hours
```

**Example 2: Incremental Coverage Roadmap**
```
Current: 42% coverage
Target: 80% coverage
Phases:
  - Phase 1 (Week 1): 50% (core auth)
  - Phase 2 (Week 2): 65% (API endpoints)
  - Phase 3 (Week 3): 80% (edge cases)
Agent: unified-coverage-agent (roadmap mode)
```

---

## 2️⃣ unified-doc-agent

### Purpose
Unified documentation management across all documentation types and formats.

### What It Consolidates
- `documentation-consolidator` - Consolidates redundant files
- `documentation-quality-agent` - Improves quality
- `doc-freshness-checker` - Validates link freshness
- `link-validator-agent` - Validates all internal links
- `terminology-consistency-agent` - Enforces terminology

### When to Use
**Use this agent when:**
- Need to improve documentation quality
- Documentation is out of sync with code
- Have redundant documentation files
- Need to validate all links
- Need to enforce terminology consistency
- Post-merge alignment needed

### Decision Tree

```
"Need documentation work?"
  ├─ "Consolidate redundant docs?" → unified-doc-agent (consolidation)
  ├─ "Improve doc quality?" → unified-doc-agent (quality)
  ├─ "Check link freshness?" → unified-doc-agent (freshness)
  ├─ "Enforce terminology?" → unified-doc-agent (terminology)
  └─ "Post-merge alignment?" → unified-doc-agent (alignment)
```

### Activation
```bash
@copilot use unified-doc-agent
Task: "Consolidate duplicate API documentation in docs/ and api-docs/ directories"
```

### Performance Characteristics
- **Runtime:** 10-30 minutes
- **Model:** Sonnet 4.6 (higher reasoning for quality checks)
- **Parallelization:** Limited (sequential link validation)
- **Token Usage:** ~3000-8000 tokens

### Use Case Examples

**Example 1: Post-Merge Documentation Alignment**
```
Merged: Feature branch with new API endpoints
Action: unified-doc-agent (alignment mode)
Scope: Update all API documentation
Timeline: 1 hour
```

**Example 2: Terminology Consistency Pass**
```
Issue: Inconsistent naming across documentation
Action: unified-doc-agent (terminology mode)
Changes: Standardize "model" vs "Model" vs "ML Model"
```

---

## 3️⃣ unified-security-scanner

### Purpose
Comprehensive security scanning combining SAST, dependency checks, and secrets detection.

### What It Consolidates
- `codeql-alert-resolution-agent` - Resolves CodeQL alerts
- `code-scanning-remediation-agent` - Fixes scanning issues
- `secret-detection-agent` - Detects secrets
- `dependency-vulnerability-scanner` - Checks dependencies
- `security-audit-agent` - Full security audits

### When to Use
**Use this agent when:**
- Need comprehensive security scan
- Have CodeQL alerts to resolve
- Need to check dependencies for vulnerabilities
- Need secret scanning before commit
- Need full security audit before release

### Decision Tree

```
"Need security checks?"
  ├─ "Scan code for vulnerabilities?" → unified-security-scanner (SAST)
  ├─ "Check dependencies?" → unified-security-scanner (dependency)
  ├─ "Detect secrets?" → unified-security-scanner (secrets)  # pragma: allowlist secret
  ├─ "Resolve CodeQL alerts?" → unified-security-scanner (CodeQL)
  └─ "Full security audit?" → unified-security-scanner (audit)
```

### Activation
```bash
@copilot use unified-security-scanner
Task: "Full security audit of PR #1234 before merging to main"
```

### Performance Characteristics
- **Runtime:** 15-45 minutes (full scan)
- **Model:** Sonnet 4.6 (detailed analysis)
- **Parallelization:** Yes (4-lane parallel SAST/dependency/secret scans)
- **Token Usage:** ~5000-15000 tokens

---

## 4️⃣ unified-governance-gate

### Purpose
Enforce and auto-heal unified governance policies across all contexts.

### What It Consolidates
- `policy-coach-agent` - Coaches on policies
- `owner-approval-guard` - Enforces approval requirements
- `workflow-compliance-guardian` - Enforces workflow compliance
- Multiple governance enforcement points

### When to Use
**Use this agent when:**
- Need to enforce approval requirements
- Need to validate workflow compliance
- Need to coach contributors on policies
- Need to ensure RBAC enforcement

### Activation
```bash
@copilot use unified-governance-gate
Task: "Validate PR #1234 against organization policies"
```

---

## 5️⃣ cache-management-agent

### Purpose
Manage caching strategies across the 4-layer cache hierarchy.

### 4-Layer Cache Hierarchy

1. **L1: Session Cache** - Per-session ephemeral data
2. **L2: Memory Cache** - Fast in-memory storage
3. **L3: Disk Cache** - Persistent local caching
4. **L4: Remote Cache** - Distributed caching (Redis/Cloud)

### When to Use
**Use this agent when:**
- Need to optimize build performance via caching
- Need to manage cache invalidation strategy
- Need to debug cache hits/misses
- Need to monitor cache health

### Activation
```bash
@copilot use cache-management-agent
Task: "Optimize GitHub Actions cache for Python dependencies"
```

---

## 6️⃣ self-healing-orchestrator-agent

### Purpose
Orchestrates autonomous self-healing loops across all CI failure patterns.

### Handles Patterns
- **RP-001:** Import/module errors
- **RP-002:** Docker build failures
- **RP-003:** Dependency conflicts
- **RP-004:** Parameter mismatches
- **RP-005+:** Custom patterns

### When to Use
**Use this agent when:**
- Need to coordinate multi-agent healing
- Multiple CI failure patterns present
- Need escalation on repeated failures
- Need pattern recognition and learning

### Activation
```bash
@copilot use self-healing-orchestrator-agent
Task: "Diagnose and heal all CI failures in workflow run #12345"
```

---

## Unified Entry Points Decision Matrix

| Scenario | Entry Point | Mode | Timeline |
|----------|------------|------|----------|
| Coverage < threshold | unified-coverage-agent | Emergency | 2h |
| Doc post-merge update | unified-doc-agent | Alignment | 1h |
| Security pre-release | unified-security-scanner | Full audit | 30m |
| Policy enforcement | unified-governance-gate | Validation | 15m |
| Cache optimization | cache-management-agent | Tuning | 1h |
| Multi-failure CI | self-healing-orchestrator-agent | Orchestration | 30m |

---

## Performance Characteristics Summary

| Agent | Runtime | Model | Parallel | Tokens | <!-- pragma: allowlist secret -->
|-------|---------|-------|----------|--------|
| unified-coverage-agent | 5-15m | Haiku | Yes | 2K-5K |
| unified-doc-agent | 10-30m | Sonnet | Limited | 3K-8K |
| unified-security-scanner | 15-45m | Sonnet | Yes | 5K-15K |
| unified-governance-gate | 5-20m | Haiku | No | 1K-3K |
| cache-management-agent | 10-30m | Haiku | Yes | 2K-6K |
| self-healing-orchestrator-agent | 20-60m | Sonnet | Yes | 8K-20K |

---

## Cost Optimization Tips

1. **Use Haiku for simple checks** (policy validation, cache checks)
2. **Use Sonnet for complex analysis** (security audits, doc alignment)
3. **Parallelize independently** (multiple security scans)
4. **Cache reusable outputs** (security baseline, doc structure)
5. **Batch operations** (coverage for multiple modules at once)

---

## Metadata

- **Generated:** 2026-06-20T06:50:36.098704
- **Phase:** D Integration
- **Authority:** @mbaetiong
- **Next Review:** 2026-06-22T12:00Z
