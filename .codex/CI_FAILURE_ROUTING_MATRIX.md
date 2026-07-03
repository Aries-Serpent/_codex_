# CI Failure Routing Matrix v1.0

**Phase 3.6 Audit Deliverable**  
**Authority**: CI/CD & Testing Track — Agent 6 of 7  
**Last Updated**: 2026-07-01

> This matrix is the authoritative routing guide for CI failures. Use this to quickly match error pattern → agent → SLA.

---

## 📊 Quick-Reference Routing Matrix

```
ERROR TYPE                  PRIMARY AGENT              FALLBACK AGENT               P-LVL   SLA     AUTO?
═════════════════════════════════════════════════════════════════════════════════════════════════════════════
Test Assertion Fail         ci-testing-agent           autonomous-test-healer      P1      1h      ✅
API Drift (TypeError)       test-alignment-fixer       autonomous-test-healer      P1      1h      ✅
Import Error                ci-importerror-agent       autonomous-test-healer      P1      1h      ✅
Flaky Test                  fragile-test-guardian      ci-resilience-emergency     P2      4h      ✅
Timeout (6h+ job)           ci-optimization-agent      workflow-optimization       P2      4h      ✅
Build Error (Docker)        ci-docker-build-healer     ci-failure-resolution       P1      2h      ✅
Build Error (Rust)          ci-docker-build-healer     ci-failure-resolution       P1      2h      ✅
Workflow Config (YAML)      workflow-ci-fixer          workflow-compliance-guard    P0      30m     ✅
Merge Gate Broken           ci-emergency-response      self-healing-orchestrator    P0      15m     ✅
Broken Link (Docs)          link-validator-agent       doc-freshness-checker       P2      4h      ✅
Missing Secret/Var          secret-detection-agent     repo-var-sync-agent         P1      2h      ✅
Self-Heal Loop (stuck)      self-healing-orchestrator  ci-failure-resolution       P1      2h      ✅
Pre-existing Failure        [DOCUMENT]                 [SKIP WITH @pytest.mark]    P2      4h      ⚠️
Dep Conflict                dependency-conflict-agent  ci-failure-resolution       P1      1h      ✅
Syntax Error                workflow-ci-fixer          ci-failure-resolution       P0      30m     ✅
Permission/Approval         [HUMAN REVIEW]             [N/A]                       P3      24h     ❌
Scanning Finding            [HUMAN REVIEW]             [N/A]                       P3      24h     ❌
```

---

## 🔍 Decision Tree

```
START: CI run fails
│
├─→ Is it a "failure" conclusion (hard failure)?
│   ├─→ YES: Likely P0/P1
│   │   ├─→ Workflow config error (YAML)? → workflow-ci-fixer (P0, 30m)
│   │   ├─→ Test assertion? → ci-testing-agent (P1, 1h)
│   │   ├─→ Build error? → ci-docker-build-healer (P1, 2h)
│   │   └─→ Other? → ci-testing-agent (P1, 1h)
│   │
│   └─→ NO: "action_required" or "skipped"
│       ├─→ Are there test errors in logs?
│       │   ├─→ YES (assertion/error traceback)
│       │   │   ├─→ TypeError positional args? → test-alignment-fixer (P1, 1h)
│       │   │   ├─→ ImportError? → ci-importerror-agent (P1, 1h)
│       │   │   ├─→ AssertionError? → ci-testing-agent (P1, 1h)
│       │   │   └─→ Other error? → autonomous-test-healer (P1, 1h)
│       │   │
│       │   └─→ NO: Probably scanning/approval gate
│       │       ├─→ Semgrep findings? → [HUMAN] (P3, 24h)
│       │       ├─→ Secrets/scanning results? → [HUMAN] (P3, 24h)
│       │       ├─→ Approval needed? → [HUMAN] (P3, 24h)
│       │       └─→ Doc/link issue? → link-validator-agent (P2, 4h)
│       │
│       └─→ Is it a self-healing loop (multiple failures in sequence)?
│           └─→ YES → self-healing-orchestrator-agent (P1, 2h)
│
└─→ TRIAGE COMPLETE: Route to agent and monitor
```

---

## 💾 Agent Selection Guide (Alphabetical)

### autonomous-test-healer-agent

**When to use**:
- Test assertion failures with unclear root cause
- CLI exit behavior issues (sys.exit vs. return)
- Zero boundary logic errors
- General test repair when pattern is unknown

**Input**: Run ID + test name + error message  
**Output**: Fixed test file(s) + commit  
**P-Level**: P1  
**SLA**: 1 hour  
**Success Rate**: ~70%  

**Example**:
```bash
@copilot Use autonomous-test-healer-agent to fix FAILED tests/ml/test_quantization.py in run #28637875494
```

---

### ci-docker-build-healer

**When to use**:
- Docker build failures in CI
- Multi-stage Dockerfile errors
- Rust compilation issues in CI
- .dockerignore optimization

**Input**: Run ID + build job name  
**Output**: Fixed Dockerfile + rebuild success  
**P-Level**: P1  
**SLA**: 2 hours  
**Success Rate**: ~80%  

**Example**:
```bash
@copilot Use ci-docker-build-healer to debug Docker build failure in run #28637875494
```

---

### ci-emergency-response-agent

**When to use**:
- Merge gate is completely broken (ALL PRs blocked)
- Core CI infrastructure down
- Critical path test suite offline
- P0 merge-blocking issues

**Input**: Run ID + scope of blockage  
**Output**: Hotfix + emergency merge approval  
**P-Level**: P0  
**SLA**: 15 minutes  
**Success Rate**: ~90%  

**Example**:
```bash
@copilot Use ci-emergency-response-agent to restore merge gate (broken since run #28637875494)
```

---

### ci-importerror-agent

**When to use**:
- ImportError / ModuleNotFoundError in tests
- Parent module reload issues (xdist workers)
- sys.path missing directories
- Package initialization problems

**Input**: Run ID + import error message  
**Output**: Fixed imports + conftest.py sys.path updates  
**P-Level**: P1  
**SLA**: 1 hour  
**Success Rate**: ~85%  

**Example**:
```bash
@copilot Use ci-importerror-agent to fix ImportError in run #28637875494
```

---

### ci-optimization-agent

**When to use**:
- Test timeout (job >6 hours)
- Slow build/test suite performance
- Resource bottleneck in CI
- Parallelization opportunity

**Input**: Run ID + job timing profile  
**Output**: Optimized workflow + batch config  
**P-Level**: P2  
**SLA**: 4 hours  
**Success Rate**: ~75%  

**Example**:
```bash
@copilot Use ci-optimization-agent to reduce test suite timeout in run #28637875494
```

---

### ci-resilience-emergency-response-agent

**When to use**:
- Flaky tests that fail intermittently
- Race conditions in parallel tests
- Transient external API failures
- Test isolation issues

**Input**: Run ID + test name + failure frequency  
**Output**: Stabilized test + retry logic / isolation fix  
**P-Level**: P2  
**SLA**: 4 hours  
**Success Rate**: ~65%  

**Example**:
```bash
@copilot Use ci-resilience-emergency-response-agent to stabilize flaky test_network_call in run #28637875494
```

---

### ci-testing-agent

**When to use**:
- General test assertion failures
- Logic errors in test code
- Test setup/teardown issues
- When pattern is unclear

**Input**: Run ID + failing test details  
**Output**: Fixed test + passing run  
**P-Level**: P1  
**SLA**: 1 hour  
**Success Rate**: ~78%  

**Example**:
```bash
@copilot Use ci-testing-agent to debug FAILED test_metric_calculation in run #28637875494
```

---

### dependency-conflict-agent

**When to use**:
- pip dependency resolver conflicts
- Version incompatibility warnings
- Requirements file issues
- Dependency tree resolution

**Input**: Dependency conflict error message  
**Output**: Updated requirements / poetry.lock  
**P-Level**: P1  
**SLA**: 1 hour  
**Success Rate**: ~82%  

**Example**:
```bash
@copilot Use dependency-conflict-agent to resolve version conflict in requirements.txt
```

---

### doc-freshness-checker

**When to use**:
- Documentation is outdated vs. code
- Code examples in docs don't match implementation
- API docs out of sync

**Input**: File path(s) to check  
**Output**: Updated docs + validation  
**P-Level**: P2  
**SLA**: 4 hours  
**Success Rate**: ~85%  

**Example**:
```bash
@copilot Use doc-freshness-checker to validate docs/ against current source
```

---

### fragile-test-guardian

**When to use**:
- Intermittent test failures
- Flaky tests detected by pytest
- Test reliability issues
- Stabilization needed

**Input**: Flaky test node ID(s)  
**Output**: Stabilized test + isolation/timing fixes  
**P-Level**: P2  
**SLA**: 4 hours  
**Success Rate**: ~70%  

**Example**:
```bash
@copilot Use fragile-test-guardian to stabilize flaky tests in run #28637875494
```

---

### link-validator-agent

**When to use**:
- Broken links in documentation
- 404 errors on GitHub Pages
- Markdown reference links broken
- Documentation URL migration

**Input**: Documentation file path(s)  
**Output**: Fixed links + validation report  
**P-Level**: P2  
**SLA**: 4 hours  
**Success Rate**: ~90%  

**Example**:
```bash
@copilot Use link-validator-agent to fix broken links in README.md
```

---

### repo-var-sync-agent

**When to use**:
- GitHub Actions environment variables missing
- Secret not found in workflow
- Variable out of sync with .codex/agent_context.json
- Bootstrap variables incomplete

**Input**: Variable name(s) missing  
**Output**: Synced variables + bootstrap fix  
**P-Level**: P1  
**SLA**: 2 hours  
**Success Rate**: ~88%  

**Example**:
```bash
@copilot Use repo-var-sync-agent to sync missing COPILOT_* variables
```

---

### secret-detection-agent

**When to use**:
- Secret/credential accidentally committed
- API key in env var not set
- .env file missing required secrets
- Secrets baseline enforcement

**Input**: File path(s) suspected to contain secrets  
**Output**: Secrets removed / rotated + remediation guide  
**P-Level**: P1  
**SLA**: 2 hours  
**Success Rate**: ~95%  

**Example**:
```bash
@copilot Use secret-detection-agent to scan and remove secrets from run logs
```

---

### self-healing-orchestrator-agent

**When to use**:
- Iterative self-healing loop is stuck
- Multiple fix attempts failed
- Needs coordination of multiple agents
- Complex multi-step remediation

**Input**: Run ID + failure pattern details  
**Output**: Orchestrated fix sequence + root cause  
**P-Level**: P1  
**SLA**: 2 hours  
**Success Rate**: ~72%  

**Example**:
```bash
@copilot Use self-healing-orchestrator-agent to break out of self-heal loop in run #28637875494
```

---

### test-alignment-fixer

**When to use**:
- TypeError: missing positional argument (dataclass)
- Test calls function with old signature
- API drift: function signature changed, tests not updated
- Constructor argument reorder

**Input**: Run ID + TypeError message  
**Output**: Updated test calls + dataclass migration  
**P-Level**: P1  
**SLA**: 1 hour  
**Success Rate**: ~85%  

**Example**:
```bash
@copilot Use test-alignment-fixer to migrate test calls for reordered dataclass in run #28637875494
```

---

### workflow-ci-fixer

**When to use**:
- GitHub Actions workflow YAML syntax error
- Job definition error (missing field, wrong type)
- Action version mismatch
- Workflow trigger misconfiguration

**Input**: Workflow file path(s) + error message  
**Output**: Fixed YAML + validation  
**P-Level**: P0  
**SLA**: 30 minutes  
**Success Rate**: ~92%  

**Example**:
```bash
@copilot Use workflow-ci-fixer to debug YAML syntax in .github/workflows/ci.yml
```

---

### workflow-compliance-guardian

**When to use**:
- Workflow doesn't follow branch-scoped concurrency rules
- Timeout values non-compliant
- Permission/approval gates misconfigured
- Workflow compliance audit failure

**Input**: Workflow file path(s)  
**Output**: Compliant workflow + enforcement applied  
**P-Level**: P0  
**SLA**: 30 minutes  
**Success Rate**: ~88%  

**Example**:
```bash
@copilot Use workflow-compliance-guardian to auto-heal .github/workflows/ci.yml
```

---

### workflow-optimization-agent

**When to use**:
- Workflow jobs are serial; can be parallelized
- Caching not optimized
- Job dependency graph suboptimal
- Artifact handling inefficient

**Input**: Workflow file + performance profile  
**Output**: Optimized workflow with parallelization  
**P-Level**: P2  
**SLA**: 4 hours  
**Success Rate**: ~78%  

**Example**:
```bash
@copilot Use workflow-optimization-agent to parallelize jobs in .github/workflows/ci.yml
```

---

## 📋 Agent Invocation Template

```bash
# Standard format:
@copilot Use {AGENT_NAME} to {TASK_DESCRIPTION} in run #{RUN_ID}

# Examples:
@copilot Use ci-testing-agent to debug FAILED test_metric_calculation in run #28637875494
@copilot Use test-alignment-fixer to fix TypeError in dataclass construction in run #28637875494
@copilot Use ci-emergency-response-agent to restore merge gate (broken since run #28637875494)
@copilot Use ci-docker-build-healer to fix Docker build failure in rust_swarm_ci.yml run #28637875494
@copilot Use ci-importerror-agent to fix ImportError: parent module not in sys.modules in run #28637875494
@copilot Use fragile-test-guardian to stabilize flaky test_network_call in run #28637875494
@copilot Use link-validator-agent to scan and fix broken links in docs/
@copilot Use secret-detection-agent to scan run logs for accidentally committed secrets
```

---

## 🎯 SLA Performance Targets

| Severity | Current MTTR | 30-Day Target | 90-Day Target |
|----------|---|---|---|
| **P0** | — | <15 min | <10 min |
| **P1** | ~60 min | <45 min | <30 min |
| **P2** | ~240 min | <180 min | <120 min |
| **P3** | Manual | Manual | Manual |

---

## ⚡ Key Performance Indicators (KPIs)

**Track these metrics weekly:**

- [ ] **P0 Response Time**: Avg time to invoke emergency agent (target: <5 min)
- [ ] **P1 Fix Rate**: % of P1 failures auto-fixed by agent (target: 60% → 75%)
- [ ] **MTTR (Mean Time To Resolution)**:
  - P0: (target: 15 min)
  - P1: (target: 45 min)
  - P2: (target: 180 min)
- [ ] **False Positive Rate**: % of agent fixes that require follow-up (target: <20%)
- [ ] **Manual Triage Time**: Hours/week spent manually troubleshooting (target: reduce by 50%)
- [ ] **CI Uptime**: % of time merge gate is passing (target: 95% → 99%)

---

## 🔄 Feedback Loop

After each triage:

1. **Log the outcome**: Which agent was used, did it fix the issue, how long did it take?
2. **Update routing matrix**: If a new pattern emerges, add a row
3. **Contribute to pattern library**: If root cause was novel, document it
4. **Report to memory**: Use `runtime-tools-store_memory` to persist learning

---

## Reference Links

- **Triage Checklist**: `.github/TRIAGE_CHECKLIST.md`
- **Pattern Library**: `.codex/plans/deep_research_ci_failure_patterns_*.md`
- **Full Report**: `.codex/PHASE_3_6_CI_TRIAGE_REPORT.md`
- **Phase 3 Authority**: `.codex/plans/AI_AGENT_TEAM_DEVELOPMENT_PROCESS.md`

---

**Authority**: Phase 3.6 Audit (Agent 6 of 7, D-capable)  
**Last Updated**: 2026-07-01 03:35 UTC  
**Maintained By**: CI/CD & Testing Track Lead  
**Next Review**: Phase 3.7 (Triage Automation)
