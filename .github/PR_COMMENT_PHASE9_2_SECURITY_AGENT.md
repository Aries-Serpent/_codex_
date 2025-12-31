# Phase 9.2 + Security Scan Agent - Continuation Prompt

**TO BE POSTED AS RESPONSE TO COMMENT #3702930152**

---

@copilot Continue with Phase 9.2 (Public API Coverage) + Implement security-scan-agent.v1

## Context

Phase 9.1 complete (205 tests added, 75% → target 85%). CI Testing Agent (ci-testing-agent.v1) fully implemented and production-ready. 12-agent ecosystem mapped with implementation roadmap.

**Current State**:
- Branch: copilot/sub-pr-2668-another-one
- Repository: /home/runner/work/_codex_/_codex_
- Tests: 1820 (1615 baseline + 205 Phase 9.1)
- Coverage: ~75% baseline (need to measure post-Phase 9.1)
- Agents Implemented: 1/12 (ci-testing-agent.v1 ✅)

**References**:
- `.github/agents/AGENT_ECOSYSTEM_MAP.md` - Full 12-agent specification
- `.github/agents/AGENT_IMPLEMENTATION_MAPPING.md` - Technical mapping
- `.github/agents/ci-testing-agent/` - Complete implementation example
- `docs/testing/COVERAGE_100_ROADMAP.md` - Phase 9 plan

---

## Mission Objectives

### Primary Goal 1: Phase 9.2 - Public API Coverage (85% → 92%)
Add **100-150 new tests** for public API surface area

### Primary Goal 2: Implement security-scan-agent.v1 (P0 Critical)
Create complete modular implementation following ci-testing-agent pattern

---

## Part 1: Phase 9.2 Execution Plan

### Step 1: Baseline & Gap Analysis (10 min)
```bash
cd /home/runner/work/_codex_/_codex_
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=html
# Review htmlcov/ to identify public API gaps
# Focus on __init__.py, public functions/classes
```

### Step 2: Public API Tests (60-90 min, 100-150 tests)

**Target Modules**:

1. **src/codex/__init__.py** (20-30 tests)
   - Public API exports
   - Version information
   - Entry points

2. **agents/__init__.py** (15-20 tests)
   - Agent registry
   - Public agent classes
   - Configuration

3. **src/rag/retrieval.py** (20-25 tests)
   - RAG query interface
   - Document retrieval
   - Ranking algorithms

4. **src/rag/verification.py** (15-20 tests)
   - CoVe (Chain-of-Verification)
   - Fact checking
   - Citation validation

5. **scripts/mcp/mcp_select_components.py** (15-20 tests)
   - Component selection API
   - Topic filtering
   - Manifest generation

6. **agents/workflow_navigator.py** - Additional (15-25 tests)
   - Additional workflow scenarios
   - Edge cases from Phase 9.1
   - Token execution paths

### Step 3: Coverage Validation (10 min)
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov=agents --cov=scripts --cov-report=term
# Target: 92% ±2%
```

### Step 4: Documentation (10 min)
- Update `docs/testing/PHASE9_2_TEST_SUMMARY.md`
- Update `docs/system/CODEBASE_DASHBOARD.md` with new metrics

---

## Part 2: security-scan-agent.v1 Implementation

### Required Structure
```
.github/agents/security-scan-agent/
├── Dockerfile
├── cli.py
├── requirements.txt
├── manifest.yaml
├── agent/
│   ├── __init__.py
│   ├── perception.py      # Run Bandit, Semgrep, parse SARIF
│   ├── decision.py        # Filter false positives, classify severity
│   ├── action.py          # Annotate PR, create summary
│   └── aftermath.py       # AfterMath reporting
├── tests/
│   ├── unit/
│   │   ├── test_scanners.py
│   │   ├── test_filters.py
│   │   └── test_annotator.py
│   ├── contract/
│   │   └── test_cli_interface.py
│   └── integration/
│       └── test_security_scan_e2e.py
└── docs/
    ├── README.md
    └── runbook.md
```

### manifest.yaml Specification
```yaml
name: Security Scan Agent
version: 1.0.0
agent_id: security-scan-agent.v1
description: Advisory SCA/SAST on PRs with SARIF output

use_case:
  title: Advisory SCA/SAST on PRs
  scenario: Annotate potential security issues

entry_paths:
  - src/
  - agents/
  - scripts/

triggers:
  team:
    - PR CI workflow (on pull_request)
  pro_plus:
    - On-demand security summary

metrics:
  - name: findings_count
    target: decrease
    direction: decrease
  - name: false_positive_rate
    target: "<10%"
    direction: decrease

steps:
  - name: run_scans
    description: Execute Bandit, Semgrep, Safety
    timeout: 300
  - name: parse_sarif
    description: Parse SARIF output
    timeout: 60
  - name: filter_false_positives
    description: Apply ML model to filter FPs
    timeout: 120
  - name: annotate_pr
    description: Add inline PR comments
    timeout: 60
  - name: generate_summary
    description: Create summary report
    timeout: 30

outputs:
  - name: sarif.json
    format: sarif
    location: .reports/security/
  - name: security_summary.md
    format: markdown
    location: .reports/security/

risks:
  - risk: False positives block PRs
    guardrail: Advisory-only mode by default
  - risk: Sensitive data in outputs
    guardrail: Sanitize all outputs, no secrets

cognitive_brain:
  perception: Execute security scanners, parse SARIF
  decision: Filter false positives using ML model, classify severity
  action: Annotate PR with findings, create summary
  aftermath:
    tags:
      - "#AFTERMATH_PATTERN_IDENTIFIED"
      - "#AFTERMATH_QUALITY_CHECK"
    updates:
      - .github/security_findings_history.yaml
```

### Core Modules Implementation

**agent/perception.py**:
```python
"""Security scan perception - run scanners and parse outputs."""
from pathlib import Path
from typing import List, Dict
import subprocess
import json

class SecurityPerception:
    def run_bandit(self, paths: List[Path]) -> Dict:
        """Run Bandit security scanner."""
        result = subprocess.run(
            ['bandit', '-f', 'json', '-r'] + [str(p) for p in paths],
            capture_output=True, text=True
        )
        return json.loads(result.stdout) if result.stdout else {}
    
    def run_semgrep(self, paths: List[Path]) -> Dict:
        """Run Semgrep SAST scanner."""
        result = subprocess.run(
            ['semgrep', '--json', '--config=auto'] + [str(p) for p in paths],
            capture_output=True, text=True
        )
        return json.loads(result.stdout) if result.stdout else {}
    
    def parse_sarif(self, sarif_file: Path) -> List[Finding]:
        """Parse SARIF format security findings."""
        # Implementation here
        pass
```

**agent/decision.py**:
```python
"""Security scan decision - filter and classify findings."""
from typing import List
from dataclasses import dataclass

@dataclass
class Finding:
    tool: str
    rule_id: str
    severity: str
    file: str
    line: int
    message: str
    confidence: float = 1.0

class SecurityDecision:
    def filter_false_positives(self, findings: List[Finding]) -> List[Finding]:
        """Filter false positives using ML model."""
        # Use historical data from Cognitive Brain
        # Apply confidence threshold (>0.8)
        return [f for f in findings if f.confidence > 0.8]
    
    def classify_severity(self, finding: Finding) -> str:
        """Classify finding severity (critical/high/medium/low)."""
        severity_map = {
            'ERROR': 'critical',
            'WARNING': 'high',
            'INFO': 'medium'
        }
        return severity_map.get(finding.severity, 'low')
```

**agent/action.py**:
```python
"""Security scan action - annotate and report."""
from typing import List
from pathlib import Path

class SecurityAction:
    def annotate_pr(self, findings: List[Finding], pr_number: int):
        """Add inline comments to PR."""
        # Use GitHub API to add review comments
        pass
    
    def generate_summary(self, findings: List[Finding]) -> str:
        """Generate markdown summary."""
        summary = f"""# Security Scan Summary

**Total Findings**: {len(findings)}

## By Severity
- Critical: {sum(1 for f in findings if f.severity == 'critical')}
- High: {sum(1 for f in findings if f.severity == 'high')}
- Medium: {sum(1 for f in findings if f.severity == 'medium')}
- Low: {sum(1 for f in findings if f.severity == 'low')}

## Details
"""
        for finding in findings:
            summary += f"- **{finding.severity.upper()}** ({finding.tool}): {finding.message} at {finding.file}:{finding.line}\n"
        
        return summary
```

### requirements.txt
```
bandit==1.7.5
semgrep==1.45.0
safety==2.3.5
sarif-tools==1.0.0
PyYAML>=6.0
```

### Testing Requirements

**Unit Tests** (30+ tests):
- Test scanner execution (mocked subprocess)
- Test SARIF parsing
- Test false positive filtering
- Test severity classification
- Test PR annotation (mocked GitHub API)

**Contract Tests** (10+ tests):
- Validate manifest.yaml schema
- Verify CLI interface
- Check SARIF output format

**Integration Tests** (5+ tests):
- End-to-end scan on sample repository
- Verify complete workflow
- Test error handling

---

## Success Criteria

### Phase 9.2
✅ Coverage: 92% ±2% (90%-94%)
✅ Test Count: 1920-1970 tests (1820 + 100-150)
✅ Pass Rate: 100%
✅ No Regressions: All existing tests pass
✅ Documentation: PHASE9_2_TEST_SUMMARY.md created

### security-scan-agent.v1
✅ All directories and files exist
✅ CLI accepts manifest and task
✅ All 3 core modules implemented (perception, decision, action)
✅ 45+ tests passing (30 unit, 10 contract, 5 integration)
✅ Dockerfile builds successfully
✅ Documentation complete (README, runbook)

---

## PDA Loop & AfterMath Tags

**Apply throughout execution**:
- Use Perception-Decision-Action loop for each major step
- Tag insights with #AFTERMATH_* tags
- Document lessons learned
- Create session report at completion

**AfterMath Tags**:
- #AFTERMATH_DECISION - Implementation choices
- #AFTERMATH_LESSON_LEARNED - Insights from Phase 9.2
- #AFTERMATH_QUALITY_CHECK - Test/security validations
- #AFTERMATH_METRIC - Coverage and test metrics
- #AFTERMATH_PATTERN_IDENTIFIED - Recurring security issues
- #AFTERMATH_NEXT_STEPS - Phase 9.3 recommendations

---

## If Token Budget Low

1. Complete Phase 9.2 first (higher priority for coverage target)
2. Implement security-scan-agent core modules only (skip some tests)
3. Document remaining work clearly
4. Create detailed continuation prompt for next session
5. Post continuation as response to this comment starting with `@copilot`

---

## Completion Steps

1. Run final validation: `pytest tests/ -v --cov=...`
2. Measure coverage improvement from Phase 9.2
3. Validate security-scan-agent implementation
4. Update documentation (Dashboard, Roadmap, summaries)
5. Commit all changes
6. Create Phase 9.3 + compliance-checker-agent continuation prompt
7. Post as response to this comment starting with `@copilot`

---

## Implementation Timeline

**Phase 9.2**: 90-120 minutes
- Baseline & gap analysis: 10 min
- Test implementation: 60-90 min
- Validation: 10 min
- Documentation: 10 min

**security-scan-agent.v1**: 90-120 minutes
- Directory structure: 10 min
- Core modules: 45 min
- Tests: 30 min
- Documentation: 15 min
- Dockerfile: 10 min

**Total**: 3-4 hours for complete session

---

**Focus**: Quality over speed - comprehensive testing and documentation critical

Good luck! 🚀
