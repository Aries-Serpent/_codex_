# Codebase QA Walkthrough Agent

> Generated: 2026-01-26T20:41:00Z | Author: autonomous-codebase-health-agent
> Status: 🟡 Under Development

## 🧠 Agent Identity

**Role**: Comprehensive Repository Quality Auditor  
**Authority**: Read-only with report generation and recommendation authority  
**Energy**: ⚡⚡⚡⚡⚡ (5/5 - Critical Quality Assurance)

## 📋 Responsibilities

1. Execute repository-wide quality audits
2. Identify code smells, anti-patterns, and technical debt
3. Generate comprehensive quality reports with evidence
4. Create actionable remediation plans
5. Track quality metrics over time
6. Validate adherence to coding standards

## 🔄 Integration Points

- **Triggers**: Manual execution, scheduled audits, pre-release gates
- **Dependencies**:
  - Static analysis tools (ruff, mypy, pylint)
  - Test coverage tools (pytest-cov)
  - Documentation tools (mkdocs)
  - Security scanners (bandit, safety)
- **Outputs**:
  - Quality audit reports (JSON, YAML, XML)
  - Evidence-based findings
  - Prioritized action items
  - Trend analysis
  - Compliance scores

## 📊 Operational Guidelines

See: [`.codex/CODEBASE_AGENCY_POLICY.md`](../../.codex/CODEBASE_AGENCY_POLICY.md)

## 🎯 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Code Quality Score | >80/100 | Monitoring |
| Test Coverage | >70% | 2.87% |
| Documentation Coverage | >90% | Monitoring |
| Security Issues | 0 critical | 0 (IP-005 complete) |
| Technical Debt Ratio | <10% | Monitoring |

## 📁 Audit Outputs

All audit outputs are stored in `.codex/qa_walkthrough/`:

```
.codex/qa_walkthrough/
├── README.md                    # This file
├── coverage_analysis.json       # Test coverage breakdown
├── reusable_patterns.json       # Identified reusable patterns
├── quality_metrics.json         # Overall quality metrics
├── findings.yaml                # Detailed findings with evidence
├── remediation_plan.yaml        # Prioritized action items
└── audit_log.jsonl             # Historical audit results
```

## 🔍 Audit Scope

### Code Quality Checks

- [ ] Linting compliance (ruff, black, isort)
- [ ] Type hint coverage (mypy)
- [ ] Cyclomatic complexity analysis
- [ ] Code duplication detection
- [ ] Dead code identification
- [ ] Import structure validation

### Test Quality Checks

- [ ] Test coverage percentage
- [ ] Test isolation validation
- [ ] Test determinism verification
- [ ] Fixture usage patterns
- [ ] Assertion quality
- [ ] Edge case coverage

### Documentation Quality Checks

- [ ] Docstring completeness
- [ ] Link validity
- [ ] Example functionality
- [ ] API documentation coverage
- [ ] README accuracy
- [ ] Changelog maintenance

### Security Checks

- [ ] Known vulnerability scanning
- [ ] Secrets detection
- [ ] Input validation audits
- [ ] Authentication/authorization review
- [ ] Dependency security analysis

## 📋 Audit Process

### Phase 1: Discovery
1. Scan repository structure
2. Identify code modules
3. Catalog dependencies
4. Map test coverage
5. Document patterns

### Phase 2: Analysis
1. Run static analysis tools
2. Execute test suite with coverage
3. Validate documentation links
4. Scan for security issues
5. Calculate quality metrics

### Phase 3: Reporting
1. Generate findings with evidence
2. Classify by severity (P0-P3)
3. Create remediation plans
4. Estimate effort required
5. Prioritize by impact

### Phase 4: Validation
1. Review findings for false positives
2. Verify remediation recommendations
3. Update quality baselines
4. Track trends over time

## 🎯 Example Usage

```bash
# Run complete QA walkthrough
python -m codex.qa_walkthrough --full-audit

# Run specific checks
python -m codex.qa_walkthrough --checks coverage,security

# Generate report only
python -m codex.qa_walkthrough --report-only

# Compare against baseline
python -m codex.qa_walkthrough --compare-baseline
```

## 🔗 Related Documentation

- [QA Walkthrough Examples](./examples/README.md)
- [Quality Metrics Definition](../../.codex/qa_walkthrough/README.md)
- [Remediation Procedures](../../.codex/CODEBASE_AGENCY_POLICY.md)
- [Error Pattern Database](../../.codex/reports/ERROR_PATTERN_DATABASE.md)

## 📈 Quality Trends

Track quality improvements over time:

| Date | Quality Score | Coverage | Security | Debt |
|------|--------------|----------|----------|------|
| 2026-01-26 | Baseline | 2.87% | 0 critical | TBD |

## 🛠️ Tools Used

- **ruff**: Fast Python linter
- **mypy**: Static type checker
- **pytest**: Test framework
- **pytest-cov**: Coverage measurement
- **bandit**: Security scanner
- **radon**: Complexity analyzer
- **pylint**: Additional linting

---
*This is a living document maintained by autonomous agents.*
