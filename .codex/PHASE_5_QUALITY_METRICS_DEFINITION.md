# Phase 5 Quality Metrics Definition

**Document Version**: 1.0.0  
**Created**: 2026-07-18  
**Phase**: 5 Lane 3  
**Status**: Active  

---

## 📊 Executive Summary

This document defines 10+ quality metrics for the Codex repository, establishing a comprehensive monitoring framework to track code quality, test health, performance, and operational excellence.

**Key Statistics**:
- Total Metrics Defined: 12 core + 3 extended = 15 metrics
- Update Frequency: Per CI run (GitHub Actions)
- Dashboard Platform: GitHub Projects + Custom JSON
- Baseline Coverage: 34% (Phase 5 transition target)
- SLO Enforcement: Advisory (Phase 5) → Blocking (Phase 6)

---

## 🎯 Metrics Categories

### 1. Code Coverage Metrics

#### Metric 1.1: Overall Coverage Percentage
- **Description**: Overall test coverage across all source code in `src/`
- **Unit**: Percentage (%)
- **Target**: ≥70% by Phase 6
- **Current Baseline**: 34% (2026-07-02 transition baseline)
- **Data Source**: pytest-cov via GitHub Actions
- **Collection Method**:
  ```bash
  pytest --cov=src --cov-report=json --cov-report=term-missing
  ```
- **Update Frequency**: Per merge to main, per PR
- **Storage**: `.reports/metrics/coverage_latest.json`
- **Trend Analysis**: 7-day rolling average + monthly snapshots

#### Metric 1.2: Per-Module Coverage Breakdown
- **Description**: Coverage percentage for each critical module (≥20 modules tracked)
- **Unit**: Percentage per module
- **Targets**: 
  - Critical (auth, data validation, API): ≥80%
  - Core (business logic, algorithms): ≥70%
  - Utility (helpers, formatters): ≥50%
- **Data Source**: pytest-cov module-level reports
- **Collection Method**: Parse coverage JSON output by module
- **Update Frequency**: Per merge to main
- **Storage**: `.reports/metrics/module_coverage_latest.json`
- **Alert Threshold**: Any module drops >1% in single PR

#### Metric 1.3: Coverage Trend (7-day Rolling Average)
- **Description**: Coverage percentage trend over 7-day window
- **Unit**: Percentage trend line
- **Data Source**: Historical coverage reports
- **Collection Method**: 
  - Collect daily coverage snapshot
  - Calculate 7-day rolling average
  - Detect trend direction (↑ improving, ↓ regressing)
- **Update Frequency**: Daily
- **Storage**: `.reports/metrics/coverage_trend_7day.json`
- **Alert Threshold**: Coverage drops >1% in 24-hour window

---

### 2. Test Health Metrics

#### Metric 2.1: Test Flakiness Rate
- **Description**: Percentage of tests that flaked (required retries) in last 50 runs
- **Unit**: Percentage (%)
- **Target**: <5% flaky tests
- **Data Source**: GitHub Actions workflow logs + test metadata
- **Collection Method**:
  1. Parse pytest output for retry count
  2. Track tests with retry_count > 0
  3. Calculate: (flaky_tests / total_tests) × 100
- **Update Frequency**: Per workflow run
- **Storage**: `.reports/metrics/test_flakiness_latest.json`
- **Alert Threshold**: Flakiness increases >5% in 24-hour window

#### Metric 2.2: Test Execution Time (Latencies)
- **Description**: Test execution latency percentiles (p50, p95, p99)
- **Unit**: Seconds
- **Targets**:
  - p50: <2s
  - p95: <10s
  - p99: <30s
- **Data Source**: pytest execution time logs
- **Collection Method**:
  ```bash
  pytest --durations=100 --benchmark-json=benchmark.json
  ```
- **Update Frequency**: Per workflow run
- **Storage**: `.reports/metrics/test_latency_latest.json`
- **Alert Threshold**: p95 latency increases >10% in single PR

#### Metric 2.3: Test Count & Distribution
- **Description**: Total test count and distribution across test types
- **Unit**: Count by category (unit, integration, e2e, perf)
- **Target**: Grow test count 5-10% per Phase
- **Data Source**: pytest collection output
- **Collection Method**: Parse pytest --collect-only output
- **Update Frequency**: Per merge to main
- **Storage**: `.reports/metrics/test_count_latest.json`
- **Alert Threshold**: Test count decreases >5%

---

### 3. Build & Pipeline Metrics

#### Metric 3.1: Build Time (Workflow Duration)
- **Description**: End-to-end CI workflow execution time
- **Unit**: Minutes
- **Target**: <15 minutes for full suite
- **Data Source**: GitHub Actions workflow timing
- **Collection Method**:
  ```bash
  gh workflow-run view <run-id> --json duration
  ```
- **Update Frequency**: Per workflow run
- **Storage**: `.reports/metrics/build_time_latest.json`
- **Alert Threshold**: Build time increases >10% in single PR

#### Metric 3.2: CI Pass Rate
- **Description**: Percentage of workflow runs that pass without manual intervention
- **Unit**: Percentage (%)
- **Target**: ≥95% pass rate
- **Data Source**: GitHub Actions workflow results
- **Collection Method**:
  1. Track last 100 workflow runs
  2. Count passed vs failed
  3. Calculate: (passed / total) × 100
- **Update Frequency**: Per workflow run
- **Storage**: `.reports/metrics/ci_pass_rate_latest.json`
- **Alert Threshold**: Pass rate drops <90%

---

### 4. Code Quality Metrics

#### Metric 4.1: Mutation Kill Rate
- **Description**: Percentage of mutations caught by test suite
- **Unit**: Percentage (%)
- **Target**: ≥80% mutation kill rate
- **Data Source**: mutmut/cosmic-ray mutation test runs
- **Collection Method**:
  ```bash
  mutmut run --coverage --report-file=mutmut_report.json
  ```
- **Update Frequency**: Weekly (or per major PR)
- **Storage**: `.reports/metrics/mutation_kill_rate_latest.json`
- **Alert Threshold**: Kill rate drops >5%

#### Metric 4.2: Code Complexity (Cyclomatic & Cognitive)
- **Description**: Average cyclomatic complexity and cognitive complexity per module
- **Unit**: Complexity score
- **Target**:
  - Cyclomatic: <10 per function
  - Cognitive: <15 per function
- **Data Source**: radon / pylint complexity reports
- **Collection Method**:
  ```bash
  radon cc src/ --json > complexity_report.json
  radon mi src/ --json > maintainability_report.json
  ```
- **Update Frequency**: Per PR / Weekly
- **Storage**: `.reports/metrics/code_complexity_latest.json`
- **Alert Threshold**: Average complexity increases >10%

---

### 5. Dependency & Security Metrics

#### Metric 5.1: Dependency Health Score
- **Description**: Composite score based on outdated packages, CVE count, license compliance
- **Unit**: Score 0-100 (100 = healthy)
- **Target**: ≥90/100
- **Data Source**: 
  - Dependabot alerts
  - pip-audit
  - license-check
- **Collection Method**:
  1. Count outdated packages (age >6 months)
  2. Count critical CVEs detected
  3. Check license compliance (SPDX approved)
  4. Formula: 100 - (outdated_weight × 0.3 + cve_weight × 0.5 + license_violations × 0.2)
- **Update Frequency**: Daily (Dependabot), per PR (pip-audit)
- **Storage**: `.reports/metrics/dependency_health_latest.json`
- **Alert Threshold**: Score drops <80 or critical CVEs detected

#### Metric 5.2: Security Vulnerability Count
- **Description**: Number of active security vulnerabilities (by severity)
- **Unit**: Count (critical, high, medium, low)
- **Target**: 0 critical/high, <5 medium
- **Data Source**: GitHub Advanced Security, CodeQL
- **Collection Method**: GitHub API query
- **Update Frequency**: Per PR / Daily
- **Storage**: `.reports/metrics/security_vulnerabilities_latest.json`
- **Alert Threshold**: Any critical/high vulnerabilities or +5 medium

---

### 6. Documentation Metrics

#### Metric 6.1: Documentation Coverage (Docstring %)
- **Description**: Percentage of functions/classes with docstrings
- **Unit**: Percentage (%)
- **Target**: ≥90% for critical modules, ≥80% overall
- **Data Source**: AST analysis + pydocstyle
- **Collection Method**:
  ```bash
  pydocstyle src/ --json > docstring_report.json
  ```
- **Update Frequency**: Per PR / Weekly
- **Storage**: `.reports/metrics/docstring_coverage_latest.json`
- **Alert Threshold**: Coverage drops >2%

#### Metric 6.2: README & Documentation Freshness
- **Description**: Age of key documentation files (days since last update)
- **Unit**: Days
- **Target**: <30 days for README, <60 for module docs
- **Data Source**: Git commit history
- **Collection Method**: Parse git log for doc files
- **Update Frequency**: Weekly
- **Storage**: `.reports/metrics/doc_freshness_latest.json`
- **Alert Threshold**: README stale >60 days

---

### 7. Performance Metrics

#### Metric 7.1: Critical Module SLO Coverage
- **Description**: Percentage of critical modules meeting their SLO targets
- **Unit**: Percentage (%)
- **Target**: 100% of critical modules within SLO
- **Data Source**: Per-module SLO tracking
- **Collection Method**: Compare actual metrics vs defined SLOs
- **Update Frequency**: Per PR
- **Storage**: `.reports/metrics/slo_compliance_latest.json`
- **Alert Threshold**: Any critical module drops below SLO

---

## 📈 Metric Collection Infrastructure

### GitHub Actions Integration

All metrics are collected via the Quality Metrics Collection workflow:

```yaml
# File: .github/workflows/quality-metrics-collection.yml
name: Quality Metrics Collection
on: [push, pull_request, schedule]
jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run quality metrics
        run: |
          python scripts/collect_quality_metrics.py
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: quality-metrics
          path: .reports/metrics/
```

### Storage Format

**Location**: `.reports/metrics/`

**File Structure**:
```
.reports/metrics/
├── coverage_latest.json           # Latest overall coverage
├── coverage_trend_7day.json        # 7-day coverage trend
├── module_coverage_latest.json     # Per-module coverage
├── test_flakiness_latest.json      # Test flakiness rate
├── test_latency_latest.json        # Test execution latencies
├── test_count_latest.json          # Test count distribution
├── build_time_latest.json          # Build duration
├── ci_pass_rate_latest.json        # CI pass rate
├── mutation_kill_rate_latest.json  # Mutation testing results
├── code_complexity_latest.json     # Code complexity metrics
├── dependency_health_latest.json   # Dependency health score
├── security_vulnerabilities_latest.json  # Security alert count
├── docstring_coverage_latest.json  # Docstring coverage
├── doc_freshness_latest.json       # Documentation age
├── slo_compliance_latest.json      # SLO compliance tracking
└── metrics_index.json              # Master index of all metrics
```

**Sample Format** (coverage_latest.json):
```json
{
  "timestamp": "2026-07-18T22:51:01Z",
  "metric_id": "coverage_overall",
  "value": 34.2,
  "unit": "%",
  "target": 70.0,
  "status": "below_target",
  "trend": "stable",
  "data_points": {
    "total_lines": 150000,
    "covered_lines": 51300,
    "branches": 12000,
    "covered_branches": 8100
  },
  "source": "pytest-cov",
  "workflow_run_id": 12345678,
  "commit_sha": "abc123def456"
}
```

---

## 🔄 Metric Update Schedule

| Metric | Frequency | Trigger | Retention |
|--------|-----------|---------|-----------|
| Coverage | Per PR | push, pull_request | 90 days |
| Test Flakiness | Per run | Every workflow | 30 days |
| Test Latency | Per run | Every workflow | 30 days |
| Build Time | Per run | Every workflow | 30 days |
| CI Pass Rate | Per run | Every workflow | 30 days (rolling 100 runs) |
| Mutation Kill Rate | Weekly | Scheduled | 1 year |
| Code Complexity | Weekly | Scheduled | 1 year |
| Dependency Health | Daily | Scheduled | 90 days |
| Security Vulns | Per PR | push, pull_request | 90 days |
| Docstring Coverage | Weekly | Scheduled | 1 year |
| Doc Freshness | Weekly | Scheduled | 1 year |
| SLO Compliance | Per PR | push, pull_request | 30 days |

---

## 📊 Dashboard Integration

### GitHub Projects Dashboard

Location: https://github.com/aries-serpent/codex/projects

**Views**:
1. **Overview**: All metrics at a glance with status indicators
2. **Coverage Trends**: Coverage timeline with 7-day rolling average
3. **Test Health**: Flakiness, latency, and test count
4. **Quality Score**: Composite score across all metrics
5. **Alerts**: Threshold violations and SLO misses

### Custom JSON Dashboard

**Location**: `.reports/quality_dashboard.json`

**Accessible via**:
- GitHub Pages (published to docs/)
- REST API (via GitHub raw content)
- CI/CD logs (pretty-printed)

---

## 🎯 Success Criteria

- [x] 10+ metrics defined with clear data sources
- [x] Collection methods documented
- [x] Update frequencies established
- [x] Alert thresholds defined
- [x] Storage format standardized
- [x] Dashboard integration planned
- [ ] Collection scripts implemented
- [ ] GitHub workflow created
- [ ] Dashboard published
- [ ] SLO enforcement active

---

## 🔗 Related Documents

- `.codex/PHASE_5_COVERAGE_SLOS.yaml` - Per-module SLO targets
- `.codex/PHASE_5_ALERT_POLICY.md` - Alert threshold definitions
- `docs/quality_dashboard/DASHBOARD_README.md` - Dashboard user guide
- `.github/workflows/quality-metrics-collection.yml` - Metrics collection workflow

---

**Next Steps:**
1. Implement metric collection scripts in `scripts/collect_quality_metrics.py`
2. Create GitHub Actions workflow
3. Build dashboard visualization
4. Integrate with CI pipeline
5. Establish alerting and notifications
6. Train team on dashboard usage

**Maintained By**: @mbaetiong (Phase 5 Lead)  
**Last Updated**: 2026-07-18
