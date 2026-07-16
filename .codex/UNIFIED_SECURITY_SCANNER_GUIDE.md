# Unified Security Scanner Implementation Guide — Phase 4D Planset 005

**Status**: 🟢 Implementation Active  
**Components Deployed**: 4/7  
**Timeline**: Day 1 (Complete) | Day 2 (In Progress)  
**Target**: 99.95%+ CodeQL Reliability  

---

## Deployed Components

### ✅ 1. CodeQL Reliability Monitor
**File**: `scripts/ci/codeql_reliability_monitor.py`

Monitors CodeQL workflow reliability with 99.95%+ SLO target.

**Features**:
- Tracks success/failure rates across 14-day rolling window
- Identifies failure patterns and root causes
- Compares to baseline for improvement tracking
- Generates automated alerts on SLO violations
- Provides remediation recommendations

**Usage**:
```bash
# Run comprehensive reliability check
python scripts/ci/codeql_reliability_monitor.py --days 14

# Save baseline (run once at start)
python scripts/ci/codeql_reliability_monitor.py --save-baseline

# Custom SLO threshold
python scripts/ci/codeql_reliability_monitor.py --threshold 0.99 --days 30
```

**Output**:
- `.codex/reports/codeql-reliability/reliability-current.json` — Current metrics
- `.codex/reports/codeql-reliability/reliability-baseline.json` — Baseline
- `.codex/reports/codeql-reliability/audit.jsonl` — Audit trail

**SLO Target**: 99.95% (≤3.65h downtime/year)

---

### ✅ 2. Vulnerability Risk Scorer
**File**: `scripts/ci/vulnerability_risk_scorer.py`

Unified risk scoring using CVSS + entropy + context formula.

**Formula**:
```
risk_score = (0.50 × cvss_score + 0.30 × entropy_score + 0.20 × context_score) / 1.0  # pragma: allowlist secret

Classification:
- CRITICAL: 8.0-10.0
- HIGH: 6.0-7.9
- MEDIUM: 3.0-5.9
- LOW: 0.0-2.9
```

**Capabilities**:
- Score CVEs with CVSS + criticality
- Score secrets with entropy (E-09 patterns)
- Score CodeQL alerts with CWE classification
- Batch scoring with deduplication
- Export JSON reports

**Usage**:
```python
from scripts.ci.vulnerability_risk_scorer import VulnerabilityRiskScorer  # pragma: allowlist secret

scorer = VulnerabilityRiskScorer()

# Score a CVE
cve_score = scorer.score_cve(
    cve_id="CVE-2024-1234",
    cvss_base_score=8.5,
    affected_package="requests==2.28.0",
    criticality="high"
)

# Batch score with export
vulnerabilities = [...]
scored = scorer.batch_score_vulnerabilities(vulnerabilities)
scorer.export_scoring_report(scored)
```

**Output**: `.codex/reports/vulnerability-scoring/vulnerability-scoring-report.json`

---

### ✅ 3. Unified Vulnerability Aggregator
**File**: `scripts/ci/vulnerability_aggregator.py`

Consolidates security findings from all sources.

**Supported Sources**:
- CodeQL alerts (SARIF format)
- GitHub Advanced Security (GHAS)
- Semgrep SAST findings
- Container vulnerabilities (Trivy)
- Dependency vulnerabilities (pip-audit, npm, cargo)
- Secret detections (entropy-based)

**Features**:
- Normalizes findings across sources
- Deduplicates using fingerprinting
- Computes severity/source breakdown
- Exports JSON/CSV/SARIF formats

**Usage**:
```python
from scripts.ci.vulnerability_aggregator import VulnerabilityAggregator

aggregator = VulnerabilityAggregator()

# Ingest from multiple sources
codeql_findings = aggregator.ingest_codeql_alerts(Path("codeql-sarif/python"))
ghas_findings = aggregator.ingest_ghas_alerts(Path("ghas-export.json"))
semgrep_findings = aggregator.ingest_semgrep_findings(Path("semgrep.sarif"))

# Aggregate
all_findings = aggregator.aggregate_findings(
    codeql_findings,
    ghas_findings,
    semgrep_findings
)

# Export
aggregator.export_inventory(all_findings, format="json")
```

**Output**: 
- `.codex/reports/vulnerability-inventory/vulnerability-inventory-*.json`
- `.codex/reports/vulnerability-inventory/vulnerability-inventory-*.csv`

---

### ✅ 4. Automated Remediation Orchestrator
**File**: `scripts/ci/remediation_orchestrator.py`

Coordinates automatic remediation workflows.

**Built-in Patterns**:

1. **CVE Dependency Bump** (`cve-dep-bump`)
   - Trigger: CRITICAL/HIGH CVE with fix available
   - Action: Auto-create PR bumping dependency
   - Approval: Automatic if tests pass
   - Example: `CVE-2024-1234` in `requests` → Auto-PR to `requests==2.31.0`

2. **Secret Rotation** (`secret-rotation`)
   - Trigger: Detected secret with >80% confidence
   - Action: Immediate credential rotation + notifications
   - Approval: Manual (security team)
   - Timeline: Immediate notification, 1h rotation, 24h audit

3. **CodeQL Pattern Fix** (`codeql-pattern-fix`)
   - Trigger: High-severity CodeQL alert in pattern library
   - Action: Create issue with fix suggestion
   - Approval: Code review required
   - Example: `py/sql-injection` → Suggest parameterized query

**Usage**:
```python
from scripts.ci.remediation_orchestrator import RemediationOrchestrator

orchestrator = RemediationOrchestrator()

# Analyze findings and generate plan
plan = orchestrator.analyze_and_plan(findings)

# Export plan
orchestrator.export_plan(plan)

# Generate PRs (auto-remediations)
prs = orchestrator.generate_pr_batch(plan)

# Generate issues (manual review)
issues = orchestrator.generate_issues_batch(plan)

# Print summary
print(orchestrator.generate_summary_report(plan))
```

**Priority Categorization**:
- **Immediate**: CRITICAL findings with auto-fix (no approval)
- **Urgent**: CRITICAL/HIGH findings requiring manual review
- **Scheduled**: MEDIUM/LOW findings for batch processing

**Output**: `.codex/reports/remediation-plans/remediation-plan-*.json`

---

## Workflow Integration

### CodeQL Enhanced Workflow
**File**: `.github/workflows/codeql-analysis.yml` (existing, enhanced)

**Enhancements for 99.95% Reliability**:
```yaml
jobs:
  analyze:
    runs-on: ubuntu-latest
    timeout-minutes: 90  # Increased from 60
    
    strategy:
      fail-fast: false
      max-parallel: 3
    
    steps:
      # ... existing steps ...
      
      - name: Retry logic (exponential backoff)
        if: failure()
        run: |
          # Exponential backoff: 30s, 60s, 120s
          for attempt in 1 2 3; do
            sleep $((30 * 2 ** (attempt - 1)))
            echo "Retry attempt $attempt..."
            exit 0  # Placeholder
          done
```

### Security Scanning Suite
**File**: `.github/workflows/security-scanning-suite.yml` (existing)

**Integrated with Unified Scanner**:
- Uses CodeQL Reliability Monitor for health checks
- Uses Vulnerability Aggregator for findings consolidation
- Uses Vulnerability Risk Scorer for prioritization
- Uses Remediation Orchestrator for action generation

---

## Daily Operations

### Morning: Run Reliability Check
```bash
# Check CodeQL reliability
python scripts/ci/codeql_reliability_monitor.py --days 14

# Expected output: "✅ CodeQL reliability SLO met (99.95%+)"
```

### When Vulnerabilities Detected
```bash
# Ingest all findings
python scripts/ci/vulnerability_aggregator.py

# Score for priority
python scripts/ci/vulnerability_risk_scorer.py

# Generate remediation plan
python scripts/ci/remediation_orchestrator.py

# Expected output: Categorized actions (immediate/urgent/scheduled)
```

### Weekly: Generate Trend Report
```bash
# Compare current to baseline
python scripts/ci/codeql_reliability_monitor.py --days 7

# Export full inventory
python scripts/ci/vulnerability_aggregator.py --export-all

# Compute security score
python scripts/ci/compute_security_score.py --weekly
```

---

## Gate Criteria Status

| Gate | Target | Current | Status |
|------|--------|---------|--------|
| CodeQL Reliability | 99.95%+ | Monitoring | 🟡 In Progress |
| False Negatives (CRITICAL) | <0.01% | Validating | 🟡 In Progress |
| PR Scanning Coverage | 100% | ~95% | 🟡 Improving |
| Time-to-Remediation (HIGH) | <4h | ~5h | 🟡 Optimizing |
| Vulnerability Inventory | 100% | Aggregate mode | 🟡 In Progress |
| Security Score | +5-10 pts | Baseline → 75 | 🟡 Tracking |
| Breaking Changes | 0 | 0 | ✅ Maintained |

---

## Next Steps (Day 2)

### Phase 2: Security Dashboard
- [ ] Build dashboard component for Cognitive App
- [ ] Implement trend analysis engine
- [ ] Create compliance report generator

### Phase 3: Operational Runbooks
- [ ] Write incident response playbooks
- [ ] Create troubleshooting guide
- [ ] Document false positive handling

### Phase 4: Final Validation
- [ ] Verify all gate criteria met
- [ ] Run 2-week reliability baseline
- [ ] Complete compliance report

---

## Testing the Components

### Test CodeQL Monitor
```bash
cd /home/runner/work/_codex_/_codex_
python scripts/ci/codeql_reliability_monitor.py --days 7
# Expected: Success rate report with SLO comparison
```

### Test Risk Scorer
```bash
python scripts/ci/vulnerability_risk_scorer.py
# Expected: Sample scoring output showing CRITICAL/HIGH classifications
```

### Test Aggregator
```bash
python scripts/ci/vulnerability_aggregator.py
# Expected: Aggregated findings summary with source breakdown
```

### Test Orchestrator
```bash
python scripts/ci/remediation_orchestrator.py
# Expected: Remediation plan with immediate/urgent/scheduled actions
```

---

## Troubleshooting

### CodeQL Timeout
**Issue**: CodeQL job exceeds 60m timeout
**Solution**:
1. Increase timeout to 90m in workflow
2. Skip optional languages (JavaScript) on large codebases
3. Enable graceful degradation (partial results)
4. Check for large binary files in scan path

### Missing Vulnerability
**Issue**: Known CVE not detected in scan
**Solution**:
1. Verify database is up-to-date (pip-audit, cargo-audit)
2. Check for transitive vs direct dependency
3. Ensure package version parsing is correct
4. Review false-positive suppressions

### False Positive Alert
**Issue**: Non-security finding flagged as vulnerability
**Solution**:
1. Add to allowlist with `# pragma: allowlist` comment
2. Update CodeQL config to suppress known patterns
3. Document in false-positive tracking log
4. Review pattern accuracy quarterly

---

## Key Metrics for Dashboard

### Reliability Metrics
- CodeQL success rate (target: 99.95%)
- Scan execution time (target: <90m)
- Alert detection accuracy (target: >98%)

### Vulnerability Metrics
- Total findings (broken down by source, severity)
- Finding velocity (new/week, closed/week)
- Mean time to remediation (target: <4h for HIGH)
- Escape rate (findings reaching production)

### Security Posture
- Security score (0-100, trending)
- Coverage by language (Python/JS/Go)
- Compliance alignment (NIST, OWASP, CWE)
- Risk trend (week-over-week, month-over-month)

---

## References

- **CVSS Scoring**: https://www.first.org/cvss/v3.1/specification-document
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **NIST Guidelines**: https://csrc.nist.gov/publications/fips
- **GitHub GHAS API**: https://docs.github.com/en/rest/reference/code-scanning
- **CodeQL Queries**: https://github.com/github/codeql

---

## Support

For issues with Unified Security Scanner Phase 4D Planset 005:
1. Check troubleshooting guide above
2. Review `.codex/reports/` for detailed logs
3. Check workflow run logs in GitHub Actions
4. Open issue with: workflow name, error, and reproducible steps

---

**Generated**: 2026-07-14  
**Campaign**: Phase 4D Planset 005  
**Authority**: D-tier Autonomous  
**Target**: 99.95%+ CodeQL Reliability
