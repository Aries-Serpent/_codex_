# Phase 5 Agent Capability Matrix
**Quick Reference Guide for Concurrent Execution**

**Report Date:** 2026-06-15  
**Audience:** DevOps, Orchestration Team, Leadership

---

## Overview

This matrix provides a single-page view of Phase 5 agent capabilities, dependencies, and resource requirements for concurrent execution planning.

---

## Phase 5 Agents - Capability & Resource Matrix

### 5a: Unified Security Scanner

| Category | Details |
|----------|---------|
| **Agent ID** | `unified-security-scanner` |
| **Status** | ✅ Active |
| **Maturity** | 🟢 Production |
| **Autonomy** | E (execute) |
| **Typical Runtime** | 30 seconds |
| **Max Runtime (SLA)** | 5 minutes |

#### Capabilities
- ✅ CVE scanning (NVD + GitHub Advisory DB)
- ✅ Secret detection (GitLeaks patterns)
- ✅ GHAS alert triage (CodeQL + Dependabot)
- ✅ SBOM generation (CycloneDX + SPDX)
- ✅ Auto-remediation (dependency pinning)
- ✅ Dependency drift detection

#### Resource Requirements
| Resource | Usage | Notes |
|----------|-------|-------|
| **Memory** | ~200 MB | Light load |
| **CPU** | ~10% | I/O bound |
| **Network** | 10–20 API calls | GitHub + NVD |
| **Disk** | < 50 MB | Temp files |

#### Dependencies
- GitHub Security Alerts API
- NVD database access
- Cognitive Brain (optional)

#### File Access
- **Read:** requirements*.txt, pyproject.toml, Cargo.toml, package.json
- **Write:** None (read-only mode)
- **Conflict Risk:** ✅ None

---

### 5b: Unified Coverage Agent

| Category | Details |
|----------|---------|
| **Agent ID** | `unified-coverage-agent` |
| **Status** | ✅ Active |
| **Maturity** | 🟡 Beta (stable) |
| **Autonomy** | E (execute w/ constraints) |
| **Typical Runtime** | 90 seconds |
| **Max Runtime (SLA)** | 5 minutes |

#### Capabilities
- ✅ Coverage gap analysis (< 50% modules)
- ✅ Test generation (pytest framework)
- ✅ Threshold enforcement (CI gate)
- ✅ Incremental roadmap (2% monthly)
- ✅ Regression prevention (baseline comparison)
- ✅ Coverage report generation

#### Resource Requirements
| Resource | Usage | Notes |
|----------|-------|-------|
| **Memory** | ~800 MB | Test execution |
| **CPU** | 50–80% | Heavy compute |
| **Network** | < 5 API calls | GitHub API only |
| **Disk** | 100–500 MB | Coverage data |

#### Dependencies
- pytest + coverage.py (pre-installed)
- Python test discovery framework
- Cognitive Brain (optional)

#### File Access
- **Read:** pytest.ini, pyproject.toml, src/, tests/
- **Write:** coverage reports (temporary)
- **Conflict Risk:** ✅ None

---

### 5c: Workflow Compliance Guardian

| Category | Details |
|----------|---------|
| **Agent ID** | `workflow-compliance-guardian` |
| **Status** | ✅ Active |
| **Maturity** | 🟢 Production |
| **Autonomy** | E (execute + repair) |
| **Typical Runtime** | 45 seconds |
| **Max Runtime (SLA)** | 5 minutes |

#### Capabilities
- ✅ YAML syntax validation (full DSL)
- ✅ Concurrency control enforcement (branch-scoped)
- ✅ Timeout rule enforcement (job + workflow)
- ✅ Auto-healing (syntax fixes)
- ✅ Merge gate integration (Workflow Execution Checklist)
- ✅ Policy enforcement reporting

#### Resource Requirements
| Resource | Usage | Notes |
|----------|-------|-------|
| **Memory** | ~50 MB | YAML parsing only |
| **CPU** | ~5% | I/O bound |
| **Network** | 5–10 API calls | GitHub Actions API |
| **Disk** | < 10 MB | Config files |

#### Dependencies
- GitHub Actions API
- YAML parser (built-in)
- Workflow Execution Checklist field

#### File Access
- **Read:** .github/workflows/*.yml, .github/workflows/*.yaml
- **Write:** Repair mode (fixes YAML syntax)
- **Conflict Risk:** ✅ None (exclusive write lock)

---

### 5d: CI Auto-Healer Agent

| Category | Details |
|----------|---------|
| **Agent ID** | `ci-auto-healer-agent` |
| **Status** | ✅ Active |
| **Maturity** | 🟢 Production |
| **Autonomy** | E (execute + heal) |
| **Typical Runtime** | 120 seconds |
| **Max Runtime (SLA)** | 5 minutes |

#### Capabilities
- ✅ Failure pattern recognition (47+ RP patterns)
- ✅ ImportError/AttributeError remediation (sys.path fixes)
- ✅ Dependency resolution (pin drift, transients)
- ✅ Docker build healing (multi-stage editable installs)
- ✅ Self-healing cascade detection (loop prevention)
- ✅ Rollback capability (safe revert)

#### Resource Requirements
| Resource | Usage | Notes |
|----------|-------|-------|
| **Memory** | ~300 MB | Log parsing + remediation |
| **CPU** | 30–50% | Variable load |
| **Network** | 15–25 API calls | GitHub Actions + package managers |
| **Disk** | 200–800 MB | Build artifacts |

#### Dependencies
- GitHub Actions API
- Package managers (pip, cargo, npm)
- Docker daemon (optional)
- Cognitive Brain (pattern recording)

#### File Access
- **Read:** .github/workflows/, logs/, source files
- **Write:** Repair mode (package pins, imports)
- **Conflict Risk:** ✅ None (isolated repairs)

---

## Concurrent Execution Coordination

### Execution Timeline

```
T+00:00 ─── Orchestrator spawns Phase 5 agents
            ├─ [5a] security-scanner ─→ (0s–30s)
            ├─ [5b] coverage-agent ────→ (0s–90s)
            ├─ [5c] compliance-guardian → (0s–45s)
            └─ [5d] ci-healer-agent ───→ (0s–120s)
T+02:00 ─── All agents complete
T+02:30 ─── Results aggregation & grading
T+03:00 ─── PR comment posted
```

**Total Parallelism Gain:** ~36% time reduction (5.5 min → 3.5 min)

---

### Resource Contention Matrix

| Resource | 5a | 5b | 5c | 5d | Contention? |
|----------|:--:|:--:|:--:|:--:|:-----------:|
| **Memory** | 200MB | 800MB | 50MB | 300MB | ✅ No (isolated) |
| **CPU** | 10% | 50–80% | 5% | 30–50% | ✅ No (distributed) |
| **Network** | Light | Light | Medium | Medium | ✅ No (rate-limited) |
| **Disk I/O** | None | Heavy | Light | Heavy | ✅ No (different paths) |

---

## Failure Handling & Escalation

### Per-Agent Failure Modes

#### 5a: Security Scanner

| Failure Mode | Probability | Detection | Recovery |
|-------------|-----------|-----------|----------|
| API rate limit | Low | HTTP 429 | Exponential backoff |
| NVD unavailable | Very low | Connection timeout | Use cached DB |
| Secret pattern false positive | Low | Pattern review | Manual override | <!-- pragma: allowlist secret -->

**Recovery Confidence:** 🟢 High

#### 5b: Coverage Agent

| Failure Mode | Probability | Detection | Recovery |
|-------------|-----------|-----------|----------|
| Test collection error | Low | ImportError | sys.path remediation |
| Coverage regression | Very low | Baseline comparison | Baseline update |
| Test generation timeout | Very low | Async timeout | Partial results |

**Recovery Confidence:** 🟡 Medium (human review recommended)

#### 5c: Compliance Guardian

| Failure Mode | Probability | Detection | Recovery |
|-------------|-----------|-----------|----------|
| YAML parse error | Very low | YAML syntax error | Automatic fix |
| Workflow DSL version | Low | Unsupported construct | Fallback to basic check |
| API permission denied | Very low | 403 Forbidden | Escalate to admin |

**Recovery Confidence:** 🟢 High

#### 5d: CI Auto-Healer

| Failure Mode | Probability | Detection | Recovery |
|-------------|-----------|-----------|----------|
| Healing loop (infinite) | Very low | Loop counter | Max iteration limit |
| Cascading failure | Low | Cross-agent error | Isolated rollback |
| Docker daemon unavailable | Very low | Connection refused | Skip Docker repairs |

**Recovery Confidence:** 🟢 High

---

## Orchestration Grading Rubric

### Phase 5 Results Scoring (0–100)

| Criterion | Points | Threshold | Details |
|-----------|--------|-----------|---------|
| **Failure Reduction** | 40 | ≥ 35/40 | Each fixed failure = 40/N |
| **No Regressions** | 25 | ≥ 25/25 | Full score if clean; -25 if regression |
| **Policy Compliance** | 20 | ≥ 18/20 | No xfail, no bare except, skipif documented |
| **Documentation** | 10 | ≥ 9/10 | Tracking log updated w/ Attempt + SHA |
| **Lint Clean** | 5 | ≥ 4/5 | ruff + import smoke tests pass |

### Score Interpretation

| Score Range | Recommendation | Action |
|-------------|----------------|--------|
| **90–100** | ✅ Auto-approve | Merge immediately |
| **70–89** | ⚠️ Human review | Manual verification required |
| **< 70** | ❌ Escalate | Contact mbaetiong + provide evidence |

---

## Pre-Execution Checklist (T-5 min)

- [ ] All agent containers ready & tagged
- [ ] GitHub API tokens validated (rate limit check)
- [ ] Coverage baseline loaded
- [ ] Workflow compliance rules refreshed
- [ ] CI failure patterns (RP-001–RP-047) up-to-date
- [ ] Orchestrator-agent handoff protocol armed
- [ ] Monitoring dashboards live
- [ ] Escalation contacts on alert

---

## Quick Reference: Agent Handoff Commands

```bash
# Activate Phase 5 orchestration
copilot-invoke orchestrator-agent \
  --phase 5 \
  --agents 5a,5b,5c,5d \
  --concurrent=true \
  --timeout=300s

# Manual agent invocation (fallback)
copilot-invoke unified-security-scanner --trigger-manual
copilot-invoke unified-coverage-agent --trigger-manual
copilot-invoke workflow-compliance-guardian --trigger-manual
copilot-invoke ci-auto-healer-agent --trigger-manual

# Monitor execution
github actions run logs <run_id> --agent=all --follow

# Escalate if score < 70
github issue comment \
  --issue-number <PR> \
  --body "@mbaetiong Phase 5 score: 68/100. See PHASE_4_ORCHESTRATION_REPORT.md"
```

---

## Links & References

- **Master Report:** `.codex/PHASE_4_ORCHESTRATION_REPORT.md`
- **Agent Registry:** `.github/agents/AGENT_REGISTRY.yaml`
- **Policy Document:** `.codex/CODEBASE_AGENCY_POLICY.md`
- **Failure Patterns:** `.github/agents/ci-auto-healer-agent/healing_patterns.md`
- **Orchestrator Agent:** `.github/agents/agent-orchestrator.md`

---

**Last Updated:** 2026-06-15  
**Version:** 1.0.0  
**Status:** Ready for Phase 5 Activation
