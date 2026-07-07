# Security Scanning Suite Integration & Comprehensive Reporting

## Overview

This document describes the implementation of an exhaustive security findings reporting and Copilot agent coordination system for the Aries-Serpent/_codex_ repository.

**Problem Solved:**
- ✅ Consolidates ALL security findings from 5 scanners into one authoritative JSON report
- ✅ Enables Copilot agents to efficiently retrieve and triage findings
- ✅ Links security-scanning-suite failures with findings context
- ✅ Provides structured handoff format for each agent type
- ✅ Stores findings history for trend analysis

---

## Phase 1: Exhaustive Unified Findings Report Generator

### Components Implemented

#### 1. `scripts/ci/aggregate_security_findings.py`
**Purpose:** Aggregates all security findings from CodeQL, Semgrep, pip-audit, Safety, and detect-secrets into a single JSON report.

**Key Features:**
- Normalizes severity levels across tools (CRITICAL > HIGH > MEDIUM > LOW > INFO)
- Deduplicates findings (same CWE/package across multiple tools)
- Assigns unique IDs per finding (e.g., CODEQL-CWE-79-001)
- Generates agent assignment recommendations
- Produces both JSON and Markdown outputs

**Output Files:**
- `.codex/security-findings-comprehensive.json` — Machine-readable findings index
- `security-findings-comprehensive.md` — Human-readable markdown summary

**Usage:**
```bash
python scripts/ci/aggregate_security_findings.py \
  --artifacts-dir security-suite-artifacts \
  --output-json .codex/security-findings-comprehensive.json \
  --output-md security-findings-comprehensive.md
```

**Schema:**
```json
{
  "scan_metadata": {
    "repository": "...",
    "commit": "...",
    "run_id": "...",
    "timestamp": "2026-07-07T00:58:12Z",
    "security_tab_url": "..."
  },
  "findings_by_severity": {
    "CRITICAL": [...],
    "HIGH": [...],
    "MEDIUM": [...],
    "LOW": [...]
  },
  "findings_by_tool": {
    "codeql": {...},
    "semgrep": {...},
    "pip-audit": {...},
    "detect-secrets": {...}
  },
  "finding_index": [
    {
      "id": "CODEQL-CWE-79-001",
      "tool": "codeql",
      "severity": "HIGH",
      "file": "...",
      "line": "...",
      "agent_assignee": "codeql-alert-resolution-agent",
      ...
    }
  ],
  "summary": {
    "total_findings": 42,
    "critical_count": 5,
    "high_count": 12,
    "medium_count": 18,
    "low_count": 7,
    "recommended_agent_handoffs": [...]
  }
}
```

#### 2. `aggregate-all-findings` Job in security-scanning-suite.yml
**Purpose:** Runs after all security scans complete to aggregate findings.

**Key Features:**
- Downloads all security-suite-* artifacts
- Runs aggregation script
- Parses summary counts
- Posts summary to workflow step summary
- Uploads comprehensive findings artifact (90-day retention)

**Placement:** After `security-suite-summary` job in the workflow

**Job Steps:**
1. Checkout repository
2. Download all security-suite-* artifacts
3. Run findings aggregator script
4. Parse summary counts
5. Upload comprehensive findings artifact
6. Post summary to GitHub step summary

---

## Phase 2: Workflow Failure Triage Integration

### Components Implemented

#### 1. `scripts/ci/security_workflow_failure_diagnostic.py`
**Purpose:** Generates detailed diagnostics when security-scanning-suite fails.

**Key Features:**
- Classifies failure root causes (timeout, tool crash, config error, network)
- Checks for partial findings from successful scans
- Generates remediation recommendations
- Determines escalation requirements
- Produces JSON diagnostic artifact

**Output Files:**
- `.codex/security-workflow-failure-diagnostic.json` — Structured failure diagnostic

**Usage:**
```bash
python scripts/ci/security_workflow_failure_diagnostic.py \
  --run-id 12345 \
  --workflow-name "Security Scanning Suite" \
  --output .codex/security-workflow-failure-diagnostic.json
```

**Diagnostic Schema:**
```json
{
  "workflow_failure": {
    "workflow_name": "Security Scanning Suite",
    "run_id": "...",
    "run_url": "...",
    "failure_timestamp": "...",
    "head_sha": "..."
  },
  "failed_jobs": ["codeql-scan", "semgrep"],
  "failed_job_details": {
    "codeql-scan": {
      "reason": "timeout",
      "error_message": "...",
      "suggested_recovery_steps": [...]
    }
  },
  "partial_findings": {
    "available": true,
    "critical_count": 5,
    "high_count": 12
  },
  "recommended_agent": "ci-failure-resolution-agent",
  "escalation_required": false,
  "remediation_steps": [...]
}
```

#### 2. `.github/workflows/security-findings-copilot-handoff.yml`
**Purpose:** Triggered on security-scanning-suite completion to create GitHub issues for Copilot agent coordination.

**Key Features:**
- Triggered when security-scanning-suite workflow completes
- Parses comprehensive findings report
- Creates GitHub issue with findings summary
- Labels issues for agent routing (security-findings, copilot-actionable)
- Posts comments on associated PRs
- Provides agent assignment recommendations

**Job Flow:**
1. Download comprehensive findings artifacts
2. Parse findings JSON
3. Create GitHub issue with:
   - Findings summary table
   - Severity breakdown
   - Agent assignment recommendations
   - Links to detailed reports
4. Post comments on associated PRs
5. Apply labels for agent routing

**Issue Template:**
```markdown
🔐 [Auto] Security Findings — 5 CRITICAL, 12 HIGH

## Security Findings Report

**Commit:** [abc1234](...)
**Run:** [#12345](...)

## Summary

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 5 |
| 🟠 HIGH | 12 |
| 🟡 MEDIUM | 18 |
| 🟢 LOW | 7 |
| **TOTAL** | **42** |

## Recommended Agent Handoffs

- `codeql-alert-resolution-agent`: 15 findings
- `dependency-security-review-agent`: 8 findings
- `unified-security-scanner`: 12 findings
```

---

## Phase 3: Copilot Agent Coordination Protocol

### Components Implemented

#### `scripts/ci/copilot_security_agent_handoff.py`
**Purpose:** Enables Copilot agents to efficiently fetch and triage findings specific to their domain.

**Key Features:**
- Loads comprehensive findings from JSON
- Filters findings by agent type
- Formats findings in agent-specific structure
- Generates agent-specific recommendations
- Produces agent-ready output (JSON or Markdown)

**Usage:**
```bash
# Prepare findings for CodeQL agent
python scripts/ci/copilot_security_agent_handoff.py \
  --findings-json .codex/security-findings-comprehensive.json \
  --agent codeql-alert-resolution-agent \
  --format json \
  --output .codex/security-handoff-codeql-alert-resolution-agent.json

# Prepare findings for dependency agent
python scripts/ci/copilot_security_agent_handoff.py \
  --findings-json .codex/security-findings-comprehensive.json \
  --agent dependency-security-review-agent \
  --format markdown \
  --output security-handoff-deps.md
```

**Agent-Specific Formatting:**

##### CodeQL Alert Resolution Agent
- Groups findings by CWE ID
- Provides CWE-specific fix patterns
- Recommends dismissal procedures for FP
- Includes rule ID and SARIF location

##### Dependency Security Review Agent
- Groups findings by package
- Provides upgrade path recommendations
- Checks for transitive conflicts
- Prioritizes by severity

##### Unified Security Scanner (Semgrep)
- Groups findings by rule ID
- Provides rule documentation links
- Recommends pattern-based fixes
- Flags likely false positives

##### Secret Detection Agent
- Flags findings requiring credential rotation
- Provides allowlisting guidance for FP
- Suggests documentation for secret presence
- Priority: rotation > allowlist > dismiss

**Output Example:**
```json
{
  "agent_id": "codeql-alert-resolution-agent",
  "findings_count": 15,
  "findings": [...],
  "summary": {
    "total": 15,
    "by_severity": {"CRITICAL": 3, "HIGH": 7, "MEDIUM": 5},
    "by_cwe": {"CWE-79": 8, "CWE-200": 5, "CWE-434": 2}
  },
  "recommendations": [
    "1. Start with CRITICAL CWE findings",
    "2. For each CWE, identify common pattern",
    ...
  ]
}
```

---

## Integration Points

### How Findings Flow to Copilot Agents

```
1. security-scanning-suite.yml completes
   ↓
2. aggregate-all-findings job runs
   ↓
3. .codex/security-findings-comprehensive.json created
   ↓
4. security-findings-copilot-handoff.yml triggered
   ↓
5. GitHub issue created with findings summary
   ↓
6. Agents fetch findings via:
   - Issue description (summary)
   - Artifact links (detailed JSON)
   - Handoff script output (agent-specific format)
   ↓
7. Agent invokes copilot_security_agent_handoff.py
   ↓
8. Agent receives structured data ready for triage
   ↓
9. Agent creates PR with fixes
```

### Failure Scenarios

**Scenario A: Security Scanner Fails (e.g., CodeQL timeout)**
```
1. security-scanning-suite.yml fails
   ↓
2. security-suite-summary job fails
   ↓
3. aggregate-all-findings runs anyway (if: always())
   ↓
4. Partial findings available from successful scans
   ↓
5. security-findings-copilot-handoff.yml triggered
   ↓
6. Issue created with "Partial findings" status
   ↓
7. ci-failure-resolution-agent + codeql-alert-resolution-agent engage
```

**Scenario B: Aggregate Script Fails**
```
1. aggregate-all-findings job fails
   ↓
2. rescue-comment job posts diagnostic
   ↓
3. Script failures are logged
   ↓
4. Manual investigation required
```

---

## File Locations

### Artifacts Generated (in .codex/)
- `.codex/security-findings-comprehensive.json` — Primary findings index (90-day retention)
- `.codex/security-workflow-failure-diagnostic.json` — Failure diagnostics
- `.codex/security-handoff-*.json` — Agent-specific handoff files
- `.codex/security-cache/` — Historical findings cache (Phases 4+)

### Workflows
- `.github/workflows/security-scanning-suite.yml` — Modified with aggregate-all-findings job
- `.github/workflows/security-findings-copilot-handoff.yml` — NEW: Issue creation + agent routing

### Scripts
- `scripts/ci/aggregate_security_findings.py` — NEW: Findings aggregator
- `scripts/ci/security_workflow_failure_diagnostic.py` — NEW: Failure diagnostics
- `scripts/ci/copilot_security_agent_handoff.py` — NEW: Agent handoff preparation

### Documentation
- `.codex/SECURITY_FINDINGS_INTEGRATION_GUIDE.md` — THIS FILE

---

## Usage Examples

### For Copilot Code Review Agent
```bash
# Get findings for specific run
python scripts/ci/copilot_security_agent_handoff.py \
  --findings-json .codex/security-findings-comprehensive.json \
  --agent codeql-alert-resolution-agent \
  --format json

# Filter critical findings only
cat .codex/security-findings-comprehensive.json | \
  jq '.findings_by_severity.CRITICAL'
```

### For CI Failure Resolution
```bash
# Get failure diagnostic
cat .codex/security-workflow-failure-diagnostic.json | jq '.remediation_steps'

# Check partial findings
cat .codex/security-findings-comprehensive.json | jq '.summary'
```

### For Manual Review
```bash
# View comprehensive report
cat .codex/security-findings-comprehensive.json | jq '.' | less

# Filter by tool
cat .codex/security-findings-comprehensive.json | jq '.findings_by_tool.codeql'

# Find findings in specific file
cat .codex/security-findings-comprehensive.json | \
  jq ".finding_index[] | select(.file | contains(\"src/\"))"
```

---

## Future Enhancements (Phases 3-4)

### Phase 3 (Planned)
- [ ] Findings cache in `.codex/security-cache/` (last 30 runs)
- [ ] Real-time lookup API via `security-findings-api.yml` workflow
- [ ] PR body injection with findings summary
- [ ] `@copilot scan-summary` command support

### Phase 4 (Planned)
- [ ] Cross-PR trend analysis
- [ ] Findings deduplication across branches
- [ ] SLA tracking for remediation
- [ ] Dashboard metrics for security posture

---

## Troubleshooting

### Aggregation Script Fails
**Symptoms:** `aggregate-all-findings` job fails, no comprehensive.json generated

**Solutions:**
1. Check artifact downloads: `actions/download-artifact@v5` step
2. Verify JSON format of individual SARIF/JSON files
3. Check Python environment and dependencies
4. Review script logs in GitHub Actions UI

### No Findings Generated
**Symptoms:** comprehensive.json exists but contains zero findings

**Possible Causes:**
- No artifacts downloaded (scans didn't run)
- Scans completed but produced no findings (rare, usually means success)
- Artifact patterns don't match expected names

**Solutions:**
1. Check that scans actually ran: `codeql-scan`, `semgrep`, etc.
2. Verify artifact upload steps completed
3. Check artifact names: should match `security-suite-*` pattern

### Agent Handoff Script Fails
**Symptoms:** `copilot_security_agent_handoff.py` fails to load findings

**Solutions:**
1. Verify comprehensive.json exists at specified path
2. Check JSON validity: `python -m json.tool .codex/security-findings-comprehensive.json`
3. Ensure agent ID matches registered agents

---

## References

- **CodeQL Action:** https://github.com/github/codeql-action
- **Semgrep Action:** https://github.com/returntocorp/semgrep-action
- **GitHub Code Scanning:** https://docs.github.com/en/code-security/code-scanning
- **Copilot Agent Guide:** `.github/agents/`

---

**Last Updated:** 2026-07-07
**Status:** Phase 1 + Phase 2 Complete, Phase 3-4 Planned
