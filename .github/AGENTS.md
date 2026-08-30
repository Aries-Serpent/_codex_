# AGENTS.md - Repository Conventions for Autonomous AI Agents

> **Generated:** 2026-01-03T21:34:00Z
> **Author:** mbaetiong
> **Repository:** Aries-Serpent/_codex_
> **Protocol:** CTEP-Compliant

Guidelines for contributors and Codex automation. Keep this file updated as conventions change.

---

## 📋 Table of Contents

1. [Repository Overview](#repository-overview)
2. [Environment Variables](#environment-variables)
3. [Logging Roles](#logging-roles)
4. [Tooling & Testing](#tooling-testing)
5. [Useful Commands](#useful-commands)
6. [Prohibited Actions](#prohibited-actions)
7. [Copilot Task Execution Protocol (CTEP)](#copilot-task-execution-protocol-ctep)
8. [Log Directory & Retention](#log-directory-retention)
9. [Error Handling & Backward Compatibility](#️-error-handling--backward-compatibility)
10. [Configuration Management (Hydra)](#configuration-management-hydra)
11. [Next Steps & Production Readiness](#next-steps-production-readiness)
12. [Troubleshooting Checklist](#troubleshooting-checklist)
13. [Contact & Maintainers](#contact-maintainers)

---

## 📦 Repository Overview

### Packaging & Installation
- **Configuration:** Defined in `pyproject.toml`
- **Installation:** `pip install -e .` (editable mode for development)
- **Production Install:** `pip install --no-cache-dir .` (CI/Docker parity)
- **CLI Entry Point:** `src/codex/cli.py`
- **Invocation:** `python -m codex.cli <task>`

### Base Configuration
- **Location:** `configs/` directory (NOT `conf/` - deprecated, removal scheduled Phase 2 (Current Cycle))
- **Format:** Hydra-compatible YAML
- **Purpose:** Runtime configuration management
- **Migration Guide:** `.codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/README.md` (legacy root alias kept only for compatibility)

### Language Composition
| Language | Percentage | Focus Area |
|----------|-----------|------------|
| Python | 77.3% | Core Implementation |
| Markdown | 19.2% | Documentation |
| Shell | 2.4% | Automation Scripts |
| HTML | 0.9% | Web Interface |
| Makefile | 0.1% | Build System |
| JavaScript | 0.1% | Frontend Components |

---

## 🌍 Environment Variables

### Core Environment Variables

| Variable | Purpose | Default / Notes |
|----------|---------|-----------------|
| `CODEX_ENV_PYTHON_VERSION` | Python version selection | Detected from system |
| `CODEX_ENV_NODE_VERSION` | Node.js version selection | Detected from system |
| `CODEX_ENV_RUST_VERSION` | Rust version selection | Detected from system |
| `CODEX_ENV_GO_VERSION` | Go version selection | Detected from system |
| `CODEX_ENV_SWIFT_VERSION` | Swift version selection | Detected from system |
| `CODEX_SESSION_ID` | Logical session identifier | Auto-generated UUID |
| `CODEX_SESSION_LOG_DIR` | Session log directory | `.codex/sessions` |
| `CODEX_LOG_DB_PATH` | SQLite database path | `.codex/logs.db` |
| `CODEX_DB_PATH` | Alias for CODEX_LOG_DB_PATH | `.codex/logs.db` |
| `CODEX_SQLITE_POOL` | Enable SQLite connection pooling | Set to `1` to enable |
| `WANDB_MODE` | Weights & Biases mode | `offline` (recommended for determinism) |

### V10 Agent Seeds (Deterministic Execution)

| Variable | Agent | Purpose | Default |
|----------|-------|---------|---------|
| `EMERGENT_AGENT_SEED` | Emergent Intelligence | Pattern detection reproducibility | `46` |
| `PERF_MONITOR_SEED` | Performance Monitor | Latency/throughput determinism | `47` |
| `DOC_AGENT_SEED` | Documentation | Doc generation consistency | `48` |
| `CI_OPTIMIZER_SEED` | CI Optimizer | Test prioritization reproducibility | `49` |
| `REASONING_SEED` | Reasoning Advisor | Causal inference determinism | `50` |
| `ECOSYSTEM_SEED` | Ecosystem Coordinator | Coalition formation reproducibility | `51` |
| `VALIDATION_SEED` | General validation | Cross-agent validation | `42` |

### Audit Infrastructure Variables

| Variable | Purpose | Default | Type |
|----------|---------|---------|------|
| `AUDIT_SAFEGUARD_KEYWORDS` | Offline/integrity signal keywords | `["sha256","checksum","rng","seed","offline","WANDB_MODE"]` | JSON/CSV |
| `AUDIT_MAX_READ_BYTES` | Deterministic file read truncation | `200000` | int |
| `AUDIT_DOMAIN_PATTERNS` | Facet clustering regex patterns | See audit_runner.py | JSON |
| `AUDIT_WEIGHTS` | Component scoring weights | `{0.25,0.20,0.25,0.15,0.15}` | JSON |
| `AUDIT_LOW_THRESHOLD` | Low maturity gate | `0.70` | float |
| `AUDIT_REGRESSION_DELTA` | Regression failure threshold | `0.02` | float |

### CI/CD & Workflow Variables

| Variable | Purpose | Type |
|----------|---------|------|
| `CI_DURATION_MS` | CI timing normalization baseline | int (default: 1000) |
| `PREDEPLOY_ENABLED` | Enable pre-deploy gates | bool (`true`/`false`) |
| `PREDEPLOY_COMMAND` | Shared pre-deploy CLI command | string |
| `PREDEPLOY_SCRIPT` | Multi-line pre-deploy script | string |

---

## 📝 Logging Roles

Use one of the following roles when recording conversation or session events:

| Role | Purpose | Usage |
|------|---------|-------|
| `system` | System-generated messages | Configuration, initialization |
| `user` | Human input | User queries, commands |
| `assistant` | AI agent responses | Codex/Copilot output |
| `tool` | Tool execution results | Command outputs, API responses |

---

## 🔧 Tooling & Testing

### Code Quality Tools

**Formatting & Linting:**
- **Black**: Python code formatter
- **Ruff**: Fast Python linter
- **isort**: Import statement sorter
- **mypy**: Static type checker (optional, recommended for type-heavy modules)

**Pre-commit Hooks:**
```bash
# Run on specific files before committing
pre-commit run --files <changed_files>

# Run all hooks on all files
pre-commit run --all-files
```

### Testing Infrastructure

**Test Execution:**
```bash
# Full test suite with nox
nox -s tests

# Docker test environment (CI parity)
make docker-test
# OR
./docker/ci_run.sh

# Quick pytest run
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

**Test Dependencies:**
- Core dependencies: `requirements.txt`
- Test dependencies: `requirements-test.txt`
- Optional test deps (e.g., `hydra-core`, `mlflow`) should be installed or appropriately mocked

**Docker Testing:**
- Use `pip install --no-cache-dir .` (NOT `-e`) for CI/Docker parity
- Test files: 32 base + 3 V10 agent test suites
- Current test count: 639 tests (107% of target)

---

## 💻 Useful Commands

### Session & Log Management
```bash
# Record session events
python -m codex.logging.session_logger

# View session logs
python -m codex.logging.viewer

# Search conversation transcripts
python -m codex.logging.query_logs
```

### Audit & Analysis
```bash
# Run space traversal audit (fast)
make space-audit-fast

# Full audit with all stages
python scripts/space_traversal/audit_runner.py run

# Specific stage
python scripts/space_traversal/audit_runner.py stage S4
```

### V10 Agent Management
```bash
# Initialize GitHub Variables for V10 agents
python .codex/scripts/manage_github_variables.py init-v10

# Run specific agent
python -m .github.agents.emergent-intelligence-agent.src <args>

# Run agent tests
pytest .github/agents/emergent-intelligence-agent/tests/ -v
```

### Code Compilation & Validation
```bash
# Compile specific agent
python3 -m py_compile .github/agents/*/src/*.py

# Validate workflow YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/example.yml'))"

# Check for issues
ruff check src/ tests/
black --check src/ tests/
```

---

## 🚫 Prohibited Actions

### Strictly Forbidden

**Do NOT:**
1. Create or activate any GitHub Actions workflow files without explicit approval
2. Commit secrets, API keys, or PII to the repository
3. Use `git reset` or `git rebase` (force push not available)
4. Push changes to repos other than the working repository
5. Access files in `.github/agents/` directory (agent-specific instructions)
6. Archive critical paths: `.codex/change_log.md`, `.codex/results.md`, `_codex_reports/`, `patches/`, `archive/removed/`

**Before Archiving Files:**
```bash
# Verify no active references
grep -rn "filename" --include="*.py" --include="*.yaml" --include="*.sh" .
```

### Automation Constraints

- Keep automation artifacts confined to `.codex/` directory
- Use `.gitignore` to exclude build artifacts, dependencies (e.g., `node_modules`, `dist`)
- Always validate changes with `git diff` before committing

---

## ⚡ Copilot Task Execution Protocol (CTEP)

### Activation Commands

**Enable:**
- `Enable CTEP`
- `CTEP Mode: ON`
- `Task mode: ON`

**Disable:**
- `Disable CTEP`
- `CTEP Mode: OFF`
- `Exit Task mode`

### Protocol Behavior (When Active)

1. **Complete ALL tasks** - Zero omissions allowed
2. **Maintain progress tracker** - Live status updates for each task
3. **Codebase-first approach** - Search existing utilities before creating new ones
4. **Document new utilities** - Include integration plans for any new code
5. **Verify completion** - Final check: `Completed = Total, Skipped = 0`

### Response Structure

```markdown
## 📊 Task Execution Progress
### Phase 1: [Name] - X% Complete
- [ ] Task 1.1: [Description] ⏳ PENDING
- [x] Task 1.2: [Description] ✅ COMPLETE

## 🔍 Codebase Integration Analysis
[Search results for existing utilities]

## ✅ Completion Summary
Total Tasks: X | Completed: X ✅ | Skipped: 0 ❌
CTEP Compliance: ✅ PASS
```

### Documentation Links


---

## 📂 Log Directory & Retention

### Directory Structure

```
.codex/
├── sessions/          # Session logs (rotated)
├── logs.db            # SQLite database
├── results.md         # Results tracking (DO NOT ARCHIVE)
├── change_log.md      # Change tracking (DO NOT ARCHIVE)
├── reports/           # Status reports
│   ├── pr_2685_status_report.md
│   ├── pr_2685_status.json
│   └── v10_agents_capabilities_and_research_roadmap.md
├── plans/             # Implementation plans
│   ├── github_variables_implementation_plan.md
│   ├── github_variables_advanced_patterns.md
│   ├── v10_agent_development_plansets.md
│   ├── autonomous_implementation_master_plan.md
│   └── integration_verification_complete.md
└── scripts/           # Utility scripts
    ├── manage_github_variables.py
    └── pr_2685_status_analyzer.py
```

### Retention Policy

- Session logs: Rotate after 30 iterations
- Database: Compact per phase
- Reports: Archive after 90 iterations
- Plans: Retain indefinitely (version controlled)

---

## 🛠️ Error Handling & Backward Compatibility

### Graceful Degradation Patterns

```python
# Check for optional methods before calling
if hasattr(navigator, 'create_workflow'):
    workflow_id = navigator.create_workflow(id, steps)
else:
    # Fallback or skip
    pass
```

### Clock Abstraction (Deterministic Timestamps)

```python
from agents.mental_mapping import get_timestamp, set_clock, reset_clock

# Use in tests for deterministic timestamps
set_clock(1234567890)
timestamp = get_timestamp()
reset_clock()
```

### Exception Handling Best Practices

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # Silently skip files that cannot be processed
    pass
```

---

## ⚙️ Configuration Management (Hydra)

### Using Hydra Configuration

```python
import hydra
from omegaconf import DictConfig

@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):
    print(cfg.param)
```

### Configuration Files

**Location:** `configs/` directory

**Structure:**
```yaml
# configs/config.yaml
param: value
nested:
  param: value
```

**Override at Runtime:**
```bash
python script.py param=new_value nested.param=new_value
```

---

## 🚀 Next Steps & Production Readiness

### V10 Agent Deployment Checklist

- [ ] Create GitHub Variables (19 vars): `python .codex/scripts/manage_github_variables.py init-v10`
- [ ] Deploy workflows from `.codex/plans/github_variables_advanced_patterns.md`
- [ ] Run integration tests on all 6 agents
- [ ] Set up monitoring dashboards (Prometheus, Grafana)
- [ ] Begin Phase 1 research (R4: Predictive Resource Modeling, R10: Test Prioritization)
- [ ] Establish data collection infrastructure (1.65TB total)
- [ ] Form research team (3-5 ML/AI researchers)

### Production Monitoring

**Key Metrics:**
- Agent performance (latency, throughput, accuracy)
- Test execution optimization (CI Agent)
- Documentation generation quality (Doc Agent)
- Pattern detection accuracy (Emergent Intelligence Agent)
- Resource utilization (Performance Monitor Agent)

**Alerting Thresholds:**
- Latency p95 > 100ms
- Throughput < 1000 req/s
- Pattern detection accuracy < 85%
- Test execution time increase > 10%

---

## 🔍 Troubleshooting Checklist

### Common Issues

**Import Errors:**
```bash
# Ensure package is installed in editable mode
pip install -e .

# Check for missing test dependencies
pip install -r requirements-test.txt
```

**Test Failures:**
```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test file
pytest tests/test_specific.py -v

# Check for non-deterministic issues (run multiple times)
pytest tests/ --count=5
```

**Audit Issues:**
```bash
# Verify environment variables
echo $AUDIT_SAFEGUARD_KEYWORDS
echo $AUDIT_MAX_READ_BYTES

# Run audit with debug output
python scripts/space_traversal/audit_runner.py run --debug
```

**Agent Issues:**
```bash
# Verify agent seeds
echo $EMERGENT_AGENT_SEED
echo $PERF_MONITOR_SEED

# Run agent tests with verbose output
pytest .github/agents/emergent-intelligence-agent/tests/ -v -s

# Check agent compilation
python3 -m py_compile .github/agents/emergent-intelligence-agent/src/__init__.py
```

---

## 📞 Contact & Maintainers

### Primary Maintainer

- **Name:** mbaetiong
- **GitHub:** @mbaetiong
- **Role:** Audit Orchestrator, Capability Cartographer

### Repository Information

- **Organization:** Aries-Serpent
- **Repository:** _codex_
- **Branch:** copilot/sub-pr-2682
- **PR:** #2685

### Support Resources

- **Issues:** https://github.com/Aries-Serpent/_codex_/issues
- **Discussions:** https://github.com/Aries-Serpent/_codex_/discussions
- **Documentation:** `.codex/plans/` and `.codex/reports/`
- **Research Roadmap:** `.codex/reports/v10_agents_capabilities_and_research_roadmap.md`

---

## 📊 Current Repository Status

### Session Metrics (2026-01-03)

- **Commits:** 22 total
- **Test Coverage:** 639/597 (107%)
- **CodeQL Alerts:** 0/26 (100% resolved)
- **V10 Agents:** 6/6 complete (100%)
- **Security Score:** 100/100
- **Code Quality:** 5/5 stars ⭐⭐⭐⭐⭐

### Agent Status

| Agent | Tests | Seed | Size | Maturity | Status |
|-------|-------|------|------|----------|--------|
| Emergent Intelligence | 34 | 46 | 120KB | 85% | ✅ Production |
| Performance Monitor | 32 | 47 | 84KB | 85% | ✅ Production |
| Documentation | 30 | 48 | 72KB | 80% | ✅ Production |
| CI Optimizer | 21 | 49 | 40KB | 85% | ✅ Production |
| Reasoning Advisor | 17 | 50 | 30KB | 80% | ✅ Production |
| Ecosystem Coordinator | 18 | 51 | 30KB | 80% | ✅ Production |

---

**Last Updated:** 2026-01-03T21:34:00Z
**Document Version:** 1.0.0
**Status:** ✅ Production Ready

---

## 🚀 Multi-Lane Custom Agent Delegation Framework

> **MANDATORY DEFAULT for ALL Copilot Agent Sessions — effective immediately.**
> Every session MUST launch independent agents in parallel using `task(mode="background")`.

### Why Multi-Lane

| Metric | Serial Execution | Multi-Lane Execution |
|--------|-----------------|---------------------|
| Session Duration | 20-30 minutes | 8-12 minutes |
| Parallelism | 1 agent at a time | 3-5 agents simultaneously |
| Coverage | Sequential scope | Concurrent scope (CI + Security + Docs) |
| Failure Rate | Higher (one miss = block) | Lower (parallel validation) |
| Time Savings | Baseline | **60-80% reduction** |

### Lane Types

| Type | `mode` | Purpose |
|------|--------|---------|
| **Primary (P1, P2...)** | `background` | Core task — launch immediately |
| **Support (S1, S2...)** | `background` | Complementary — launch same time as Primary |
| **Sequential (Seq1...)** | `sync` | Depends on prior lane output |

### Task → Lane Quick Reference

| Task Category | P1 Agent | P2 Agent | S1 Agent |
|---------------|----------|----------|----------|
| CI import error | `ci-importerror-agent` | `ci-testing-agent` | `unified-coverage-agent` |
| CodeQL alert | `codeql-alert-resolution-agent` | `security-audit-agent` | `dependency-vulnerability-scanner` |
| Workflow YAML | `workflow-ci-fixer` | `ci-log-retrieval-agent` | `workflow-compliance-guardian` |
| Flaky test | `fragile-test-guardian` | `autonomous-test-healer-agent` | `test-enhancement-agent` |
| Doc broken link | `link-validator-agent` | `unified-doc-agent` | `doc-freshness-checker` |
| Security audit | `security-audit-agent` | `unified-security-scanner` | `dependency-vulnerability-scanner` |
| Coverage gap | `unified-coverage-agent` | `test-enhancement-agent` | `test-alignment-fixer` |

### Plan Template (Multi-Lane)

All plans MUST use this structure:

```markdown
**Lane P1 (Primary 1) — Parallel Start:**
- [ ] Task → agent_type: `<agent>` mode: `background`

**Lane P2 (Primary 2) — Parallel Start:**
- [ ] Task → agent_type: `<agent>` mode: `background`

**Lane S1 (Support 1) — Parallel Start:**
- [ ] Task → agent_type: `<agent>` mode: `background`

**Lane Seq1 (Sequential — after P1+P2 complete):**
- [ ] Task → agent_type: `<agent>` mode: `sync`
```

### Enforcement

- Sessions running agents serially (without justification) violate **CAD-Mandate Rule 1**
- All sessions with ≥2 independent workstreams **MUST** launch ≥2 background agents in the FIRST response
- Violations are detected by `comment-review-gate.yml` and block merge

**Last Updated:** 2026-08-03
**Status:** ✅ Mandatory — All Sessions
