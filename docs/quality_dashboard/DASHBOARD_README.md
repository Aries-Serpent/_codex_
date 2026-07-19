# Codex Quality Dashboard

**Status**: 🚀 Phase 5 Lane 3 Active  
**Last Updated**: 2026-07-18  
**Dashboard Version**: 1.0.0  

---

## 📊 Dashboard Overview

The Codex Quality Dashboard provides real-time visibility into code quality, test health, performance, and operational metrics across the repository. This dashboard aggregates 15+ quality metrics and tracks progress toward Phase 5 and Phase 6 goals.

### Quick Links

- **Live Dashboard**: https://github.com/aries-serpent/_codex_/projects (GitHub Projects)
- **Metrics Data**: `.reports/metrics/metrics_index.json`
- **SLO Definitions**: `.codex/PHASE_5_COVERAGE_SLOS.yaml`
- **Alert Policy**: `.codex/PHASE_5_ALERT_POLICY.md`
- **Metrics Definition**: `.codex/PHASE_5_QUALITY_METRICS_DEFINITION.md`

---

## 🎯 Key Metrics at a Glance

### Coverage
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Overall Coverage | 34.0% | 70.0% | 🔴 Below Target |
| Critical Modules | 45.0% avg | 80.0% | 🔴 Below Target |
| Core Modules | 36.0% avg | 70.0% | 🔴 Below Target |
| Utility Modules | 32.0% avg | 50.0% | 🟡 Below Target |

### Test Health
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Flakiness Rate | <2% | <5% | ✅ Healthy |
| Test Count | 8,247 | Growing | ✅ Growing |
| p95 Latency | 8.2s | <10s | ✅ Healthy |
| CI Pass Rate | 96% | >95% | ✅ Healthy |

### Quality
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Mutation Kill Rate | 75% | >80% | 🟡 Below Target |
| Avg Cyclomatic | 7.2 | <10 | ✅ Healthy |
| Security Vulns | 0 critical | 0 critical | ✅ Compliant |
| Doc Coverage | 78% | >80% | 🟡 Below Target |

---

## 📈 Dashboard Views

### 1. Overview Dashboard
**Purpose**: High-level status of all key metrics  
**Refresh**: Real-time from GitHub Actions  
**Audience**: All contributors, leads  

**Sections**:
- Status summary (green/yellow/red indicators)
- Top metrics (coverage, test health, build time)
- Recent alerts and SLO misses
- Weekly trend summary

**Access**: https://github.com/aries-serpent/_codex_/projects

### 2. Coverage Trends
**Purpose**: Track coverage progress over time  
**Refresh**: Daily  
**Audience**: Quality team, leadership  

**Shows**:
- Overall coverage 7-day rolling average
- Per-module coverage trends
- Coverage velocity (improving/stable/regressing)
- SLO attainment by module category

**Data Source**: `.reports/metrics/coverage_trend_7day.json`

**Sample Visualization**:
```
Overall Coverage Trend (7-day rolling avg)
70% |
65% |
60% |                           ╱
55% |                      ╱╱
50% |                  ╱╱
45% |              ╱╱
40% |          ╱╱
35% |______╱╱________________________
30% |
    └─────────────────────────────────
     M   T   W   T   F   S   S   (last 7 days)
```

### 3. Test Health Dashboard
**Purpose**: Monitor test suite quality and performance  
**Refresh**: Per workflow run  
**Audience**: Test engineers, automation team  

**Metrics**:
- Test flakiness rate (trending)
- Test execution latencies (p50, p95, p99)
- Test count by category (unit, integration, e2e)
- Failed/skipped test trends
- Slow test outliers (>30s)

**Data Sources**:
- `.reports/metrics/test_flakiness_latest.json`
- `.reports/metrics/test_latency_latest.json`
- `.reports/metrics/test_count_latest.json`

### 4. Quality Score Card
**Purpose**: Single composite score of overall health  
**Refresh**: Per merge to main  
**Audience**: Leadership, stakeholders  

**Score Calculation**:
```
Quality Score = (
  Coverage (34%) +
  Test Health (20%) +
  Build Health (15%) +
  Security (15%) +
  Documentation (8%) +
  Performance (8%)
) / 100
```

**Current Score**: 52/100 (🟡 At Risk)

### 5. Alerts & Violations
**Purpose**: Surface SLO misses and policy violations  
**Refresh**: Real-time  
**Audience**: All contributors  

**Alert Types**:
- 🔴 Critical: Blocking merge (security, critical SLO miss)
- 🟠 High: Warnings on PR (any SLO miss >5%)
- 🟡 Medium: Information (trend concerns, documentation gaps)
- 🔵 Low: Informational (metrics updates, archival)

**Current Alerts** (as of 2026-07-18):
- 🟡 Coverage below Phase 5 intermediate target (+36% gap)
- 🟡 Mutation kill rate below 80% target
- ✅ No critical security vulnerabilities
- ✅ CI pass rate healthy (96%)

---

## 🔍 Metric Explanations

### Coverage Percentage
**What it measures**: Percentage of source code lines executed by tests

**Why it matters**: Higher coverage reduces risk of untested code bugs

**How to improve**:
1. Identify uncovered lines: `pytest --cov=src --cov-report=html`
2. Add tests for critical paths first (auth, data persistence)
3. Focus on cyclomatic complexity hotspots

**Current Status**: 34% (baseline from 2026-07-02)
**Phase 5 Target**: Reach 60% by end of phase
**Phase 6 Gate**: Must reach 70% to proceed

### Test Flakiness Rate
**What it measures**: Percentage of tests that fail intermittently

**Why it matters**: Flaky tests erode confidence and hide real regressions

**How to reduce**:
1. Add retries only as last resort (investigate root cause first)
2. Use proper async/await patterns
3. Mock external dependencies reliably
4. Use timestamps/freezegun for time-dependent tests

**Current Status**: <2% (healthy)
**Target**: <5% at all times
**Alert**: If exceeds 5%, investigate root cause

### Build Time
**What it measures**: End-to-end CI workflow duration

**Why it matters**: Faster feedback loops improve developer productivity

**Current Status**: ~12 minutes (healthy)
**Target**: <15 minutes
**Optimization**: Parallel jobs, better caching, test selection

### Mutation Kill Rate
**What it measures**: Percentage of code mutations caught by tests

**Why it matters**: Validates that tests actually catch bugs

**How to improve**:
1. Run `mutmut run --coverage`
2. Add assertions for each key code path
3. Test boundary conditions

**Current Status**: 75% (below 80% target)

### Documentation Coverage
**What it measures**: Percentage of functions/classes with docstrings

**Why it matters**: Good docs reduce maintenance burden and onboarding time

**How to improve**:
1. Add docstrings following PEP 257
2. Include param types, return types, examples
3. Use tools like `pydocstyle` to validate

**Current Status**: 78% (near 80% target)

---

## 📊 SLO Definitions by Module

### Critical Modules (80% Coverage Target)
- `aries_serpent_core/auth` - Authentication & session management
- `aries_serpent_core/authz` - Authorization & access control
- `aries_serpent_core/db` - Data persistence layer
- `aries_serpent_core/api` - Public API contracts
- `aries_serpent_core/crypto` - Cryptographic operations
- `codex_ml/training` - Model training pipeline
- `aries_serpent_core/rag` - RAG retrieval engine

### Core Modules (70% Coverage Target)
- `aries_serpent_core/cognitive` - Cognitive brain logic
- `aries_serpent_core/governance` - Policy evaluation
- `aries_serpent_core/autonomy` - Agent decision-making
- `codex_ml/inference` - Model inference engine
- `aries_serpent_core/metrics` - Metrics collection
- `aries_serpent_core/agents` - Agent orchestration

### Utility Modules (50% Coverage Target)
- `aries_serpent_core/cache` - Caching layer
- `aries_serpent_core/logging` - Logging infrastructure
- `aries_serpent_core/cli` - Command-line interface
- `codex/utils` - General utilities
- `aries_serpent_core/config` - Configuration management

**Full SLO details**: `.codex/PHASE_5_COVERAGE_SLOS.yaml`

---

## 🚨 Alert Thresholds & Escalation

### Coverage Alerts
| Condition | Severity | Action |
|-----------|----------|--------|
| Module drops >5% in single PR | 🟠 High | Block PR, require manual review |
| Coverage drops >1% in 24h | 🟡 Medium | Comment on PR, notify team |
| Critical module below SLO | 🔴 Critical | Block merge, escalate to lead |

### Test Health Alerts
| Condition | Severity | Action |
|-----------|----------|--------|
| Test flakiness >5% | 🟡 Medium | Comment with flaky test list |
| Build time increases >10% | 🟠 High | Investigate CI performance |
| Test count decreases >5% | 🟠 High | Require justification in PR |

### Quality Alerts
| Condition | Severity | Action |
|-----------|----------|--------|
| Security vulnerability detected | 🔴 Critical | Block PR immediately |
| Mutation kill rate drops >5% | 🟠 High | Comment with low-coverage areas |

**Full alert policy**: `.codex/PHASE_5_ALERT_POLICY.md`

---

## 📱 Accessing the Dashboard

### GitHub Projects (Primary)
1. Navigate to: https://github.com/aries-serpent/_codex_/projects
2. Select "Quality Dashboard" project
3. Browse views: Overview, Coverage, Tests, Quality

**Features**:
- Real-time updates
- Drill-down to specific modules
- Historical trending
- Alert filtering

### JSON API (Programmatic)
Access raw metrics data:

```bash
# Get latest coverage
curl https://raw.githubusercontent.com/aries-serpent/_codex_/main/.reports/metrics/coverage_latest.json

# Get coverage trend
curl https://raw.githubusercontent.com/aries-serpent/_codex_/main/.reports/metrics/coverage_trend_7day.json

# Get all metrics index
curl https://raw.githubusercontent.com/aries-serpent/_codex_/main/.reports/metrics/metrics_index.json
```

### GitHub Pages Dashboard (Coming Soon)
Dedicated dashboard webpage at: https://aries-serpent.github.io/_codex_/quality

---

## 📋 SLO Enforcement Policy

### Phase 5 (Current - Advisory)
- Coverage misses generate PR comments (informational)
- No merge blocking for coverage misses
- Weekly review of SLO attainment
- Focus on awareness and gradual improvement

### Phase 6 (Upcoming - Blocking)
- Coverage misses block PR merge
- Automatic escalation to team leads
- Daily enforcement reporting
- Strict adherence required

**Transition Date**: 2026-10-31 (Phase 6 gate)

---

## 🔄 Workflow Integration

### GitHub Actions Metrics Collection
Metrics are collected automatically by the Quality Metrics workflow:

```yaml
# File: .github/workflows/quality-metrics-collection.yml
# Runs on: Every push, PR, and daily schedule
# Duration: ~5 minutes
# Artifacts: .reports/metrics/
```

### Manual Metric Collection
To collect metrics locally:

```bash
# Install dependencies
pip install pytest-cov pytest mutmut radon pydocstyle

# Run coverage
pytest --cov=src --cov-report=json --cov-report=html

# Run complexity analysis
radon cc src/ --json > reports/complexity.json

# Run mutation testing
mutmut run --coverage

# Collect all metrics
python scripts/collect_quality_metrics.py
```

---

## 📈 Trend Analysis

### 7-Day Rolling Averages
Coverage is tracked as a 7-day rolling average to smooth day-to-day fluctuations:

```
Raw coverage:     34%, 34.5%, 34.2%, 35%, 34.8%, 35.2%, 36%
7-day average:    34.7% (stable)
Trend:            → (holding steady, slight upward momentum)
```

### Monthly Snapshots
First day of each month captures a baseline for longer-term trend analysis:
- 2026-07-01: 34.0% (Phase 5 baseline)
- 2026-08-01: TBD
- 2026-09-01: TBD (Target: 60%)
- 2026-10-01: TBD (Target: 70% for Phase 6 gate)

---

## 🎓 Getting Started

### For Contributors
1. Check the Quality Dashboard before submitting PR
2. If PR would lower coverage >1%, add tests
3. Review SLO targets for modules you modify
4. Respond to coverage alerts in PR comments

### For Quality Team
1. Review dashboard daily for violations
2. Investigate trend changes
3. Escalate blockers to team leads
4. Generate weekly summary report

### For Leadership
1. Track overall Quality Score weekly
2. Monitor Phase 5 milestone progress
3. Plan Phase 6 enforcement rollout
4. Allocate resources for coverage gaps

---

## 🔗 Related Documents

| Document | Purpose |
|----------|---------|
| [PHASE_5_QUALITY_METRICS_DEFINITION.md](.codex/PHASE_5_QUALITY_METRICS_DEFINITION.md) | Metric definitions and collection methods |
| [PHASE_5_COVERAGE_SLOS.yaml](.codex/PHASE_5_COVERAGE_SLOS.yaml) | Per-module SLO targets |
| [PHASE_5_ALERT_POLICY.md](.codex/PHASE_5_ALERT_POLICY.md) | Alert thresholds and escalation |
| [quality-metrics-collection.yml](.github/workflows/quality-metrics-collection.yml) | GitHub Actions workflow |

---

## 📞 Support & Contact

- **Quality Issues**: Open issue with `quality` label
- **Dashboard Access**: Contact @mbaetiong
- **SLO Questions**: Review `.codex/PHASE_5_COVERAGE_SLOS.yaml`
- **Metrics Collection**: See `.codex/PHASE_5_QUALITY_METRICS_DEFINITION.md`

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-18 | Initial dashboard README and metric definitions |

**Next Updates**:
- Phase 5 Milestone 1 (2026-07-31): Dashboard UI launch
- Phase 5 Milestone 2 (2026-08-31): Trend analysis enabled
- Phase 6 Preparation (2026-10-01): Enforcement mode activation

---

**Maintained By**: @mbaetiong (Phase 5 Lane 3 Lead)  
**Last Updated**: 2026-07-18T22:51:00Z
