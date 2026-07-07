# 🚀 Phases 6-8: PR Enhancement, @copilot Commands, Agent Formatters

**Status**: Awaiting Phase 4B-5 completion  
**Created**: 2026-07-07T01:58:40Z  
**Target**: Fully parallelized execution  
**Authority**: D-tier autonomous (@mbaetiong approved)

---

## 📋 PHASE 6: PR BODY ENHANCEMENT & WEC INTEGRATION (8-10 hours)

**Recommended Agents**: `pr-check-remediation-agent`, `workflow-ci-fixer`  
**Depends On**: Phase 5 (API ready)  
**Trigger Condition**: Wait for Phase 5A-5B completion

### 6.1 Workflow Implementation

**File**: `.github/workflows/security-pr-enhancement.yml` (200 lines)

**Trigger**: `pull_request_target` (opened, synchronize)

```yaml
name: Security PR Enhancement
on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  enhance-pr:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: pip
      
      - name: Generate Findings Section
        id: findings
        run: |
          python scripts/ci/security_pr_formatter.py generate \
            --findings ".codex/security-findings-comprehensive.json" \
            --output pr-findings.md
          
          cat pr-findings.md >> $GITHUB_STEP_SUMMARY
      
      - name: Update PR Body
        uses: actions/github-script@v8
        with:
          script: |
            const fs = require('fs');
            const findings = fs.readFileSync('pr-findings.md', 'utf8');
            const pr = context.payload.pull_request;
            const body = pr.body || '';
            
            // Remove old findings section
            const newBody = body.replace(/## 🔐 Security Findings[\s\S]*?(?=##|$)/, '');
            
            // Inject new findings section
            const updatedBody = newBody.trim() + '\n\n## 🔐 Security Findings\n\n' + findings;
            
            github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: pr.number,
              body: updatedBody
            });
```

**Validation Requirements**:
- GitHub Actions versions: v5, v6, v8 enforced
- YAML indentation correct (2-space lists)
- Permissions block includes `pull-requests: write`
- Trigger on both opened and synchronize events
- Script logic preserves WEC section
- Artifact handling for findings JSON

### 6.2 Formatter Module

**File**: `scripts/ci/security_pr_formatter.py` (150 lines)

**Functions**:
```python
def generate_findings_section(findings_path: Path) -> str
    # Load findings, generate markdown section
    
def format_findings_table(findings: list) -> str
    # Group by severity, create markdown table
    # Include emoji indicators
    
def list_top_issues(findings: list, limit: int = 5) -> str
    # Sort by severity/recency, format as list
    # Include CWE/CVE, file:line, tool, fix recommendation
    
def get_agent_assignments(findings: list) -> str
    # Count by type, recommend agents
    # Return markdown with @ mentions
    
def generate_pr_summary(findings: list) -> str
    # One-line summary with count and timestamp
    # Link to full report
```

**CLI Interface**:
```bash
python scripts/ci/security_pr_formatter.py generate \
  --findings .codex/security-findings-comprehensive.json \
  --output pr-findings.md \
  --limit 5
```

**Example Output**:
```markdown
**Summary**: 5 CRITICAL, 12 HIGH, 18 MEDIUM (Last scan: 2h ago)

### Severity Distribution

| Severity | Count | Tools | Trend |
|----------|-------|-------|-------|
| CRITICAL | 5 | CodeQL (2), Semgrep (3) | 🔴 New! |
| HIGH | 12 | CodeQL (5), pip-audit (7) | 🟡 Stable |
| MEDIUM | 18 | Safety (8), detect-secrets (10) | 🟢 Improving | <!-- pragma: allowlist secret -->

### Top Issues

1. **[CRITICAL]** CWE-79: XSS in user input handler
   - File: `codex/cli.py:125`
   - Tool: CodeQL
   - Fix: Use `html.escape()` before HTML output

2. **[HIGH]** CWE-22: Path traversal in file operations
   - File: `codex/utils/file_ops.py:45`
   - Tool: Semgrep
   - Fix: Use `pathlib.Path.resolve()` with parent check

### Recommended Agents

- **@codeql-alert-resolution-agent** (7 findings)
- **@dependency-security-review-agent** (5 findings)
- **@secret-detection-agent** (0 findings)

[View Full Report](.codex/security-findings-comprehensive.md)
```

### 6.3 WEC Integration

**Update PR body section preservation**:
- Don't overwrite `## 🔄 Workflow Execution Checklist` section
- Inject findings section after WEC (or before, if configured)
- Preserve all manually edited sections
- Add informational note: "Security findings detected (informational only)"

### 6.4 Testing Checklist

- [ ] Workflow triggers on PR open
- [ ] Updates on each new commit to PR
- [ ] PR body injection preserves WEC section
- [ ] Findings section preserves other PR body content
- [ ] Severity color coding displays correctly
- [ ] Agent @ mentions are functional
- [ ] Update latency < 5 minutes
- [ ] No failures if PR already has findings section
- [ ] Empty findings handled gracefully

---

## 🎯 PHASE 7: @COPILOT CONVERSATIONAL COMMANDS (7-9 hours)

**Recommended Agents**: `cognitive-brain-cli-agent`, `ci-auto-healer-agent`  
**Depends On**: Phase 5 API (findings queries ready)  
**Trigger Condition**: Wait for Phase 5B completion, then Phase 6 completion

### 7.1 Command Parser

**File**: Enhanced `scripts/ci/copilot_security_agent_handoff.py` (150 lines addition)

**Command Pattern**: `@copilot scan-summary [filters...]`

**Filter Options**:
```
cwe:CWE-79          → Query CWE-79 findings
severity:CRITICAL   → Query CRITICAL findings  
for src/path        → Query findings in file/directory
package:numpy       → Query package vulnerabilities

# Combinations
@copilot scan-summary cwe:CWE-79
@copilot scan-summary critical for src/cognitive_brain
@copilot scan-summary critical severity:HIGH
```

**Parser Function**:
```python
def parse_scan_summary_command(comment_body: str) -> dict:
    """
    Parse @copilot scan-summary command with optional filters.
    
    Returns:
        {
            'command': 'scan-summary',
            'query_type': 'cwe|severity|file|package',
            'value': 'CWE-79|CRITICAL|src/path|package_name',
            'scope': optional file/dir scope
        } or None if not a scan-summary command
    """
    pattern = r'@copilot\s+scan-summary(?:\s+(.+))?'
    # Parse filters from captured group
    # Return structured dict
```

### 7.2 Response Generator

**Function**:
```python
def generate_scan_summary_response(findings: list, query_info: dict) -> str:
    """
    Generate GitHub comment markdown for scan summary.
    
    Includes:
    - Summary table (Severity | Count | Status)
    - Top 3 issues with links
    - Recommended agents
    - Links to full reports
    - Trending indicators
    """
```

**Response Format Example**:
```markdown
## Security Scan Summary

**Repository**: Aries-Serpent/_codex_  
**Query**: critical findings  
**Source**: Aggregated from 5 tools (CodeQL, Semgrep, pip-audit, Safety, detect-secrets)  
**Scan Time**: 2 hours ago

### Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 5 | 🔴 Action Required |
| HIGH | 12 | 🟡 Review |
| MEDIUM | 18 | 🟢 Monitor |

### Top Issues

1. **[CRITICAL]** CWE-79: Unescaped user input in HTML output
   - File: `codex/cli.py:125`
   - Function: `handle_user_input()`
   - Tool: CodeQL
   - Pattern: Use `html.escape()` or `Markup()`
   - [View in CodeQL](.codex/security-findings-comprehensive.md#CWE-79)

2. **[HIGH]** CWE-22: Path traversal vulnerability
   - File: `codex/utils/file_ops.py:45`
   - Tool: Semgrep
   - Pattern: Validate and sanitize file paths

3. **[HIGH]** numpy security vulnerability
   - Package: numpy (1.21.0 → 1.23.5)
   - CVE: CVE-2023-XXXXX
   - Tool: pip-audit
   - Upgrade: Safe with no breaking changes

### Recommended Actions

- **@codeql-alert-resolution-agent** — CWE remediation (7 findings)
- **@dependency-security-review-agent** — Package upgrades (5 findings)
- **@secret-detection-agent** — Secrets rotation (0 findings)

### Trending

- 🔴 **2 NEW** findings in last 24 hours
- 🟢 **3 RESOLVED** findings since last week
- 📊 **Velocity**: 1.5 findings/day cleared

[View Full Dashboard](.codex/security-findings-dashboard.md)  
[View Full Report](.codex/security-findings-comprehensive.md)
```

### 7.3 GitHub Actions Integration

**Workflow** (new or existing):
```yaml
name: Security Copilot Commands
on:
  issue_comment:
    types: [created, edited]

jobs:
  handle-command:
    if: contains(github.event.comment.body, '@copilot scan-summary')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: pip
      
      - name: Parse Command
        id: parse
        run: |
          python scripts/ci/copilot_security_agent_handoff.py parse-command \
            --comment "${{ github.event.comment.body }}" \
            --output command.json
      
      - name: Generate Response
        if: steps.parse.outputs.valid == 'true'
        id: response
        run: |
          python scripts/ci/copilot_security_agent_handoff.py generate-response \
            --query "${{ steps.parse.outputs.query }}" \
            --output response.md
      
      - name: Post Comment
        if: steps.parse.outputs.valid == 'true'
        uses: actions/github-script@v8
        with:
          script: |
            const fs = require('fs');
            const response = fs.readFileSync('response.md', 'utf8');
            
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: response
            });
```

### 7.4 Testing Checklist

- [ ] Command recognized in PR/Issue comments
- [ ] All filter variants parse correctly
- [ ] Query executed via Phase 5 API
- [ ] Response generated within 30s
- [ ] All links functional and accessible
- [ ] Agent @ mentions work
- [ ] Empty results handled gracefully
- [ ] Special characters in paths escaped properly
- [ ] Works in both PRs and Issues

---

## 🤖 PHASE 8: AGENT-SPECIFIC FORMATTING (8-10 hours)

**Recommended Agents**: `codeql-alert-resolution-agent`, `dependency-security-review-agent`, `secret-detection-agent`  
**Depends On**: All findings integration complete (Phases 4B-7)  
**Trigger Condition**: Wait for Phase 7 completion

### 8.1 CodeQL Agent Formatter

**File**: `scripts/ci/security_codeql_agent_format.py` (150 lines)

**Purpose**: Format findings for `codeql-alert-resolution-agent`

**Output Format**:
```json
{
  "total": 7,
  "by_cwe": {
    "CWE-79": {
      "count": 4,
      "severity": "CRITICAL",
      "description": "Cross-site scripting (XSS)",
      "findings": [
        {
          "id": "codeql-cwe79-001",
          "file": "codex/cli.py",
          "line": 125,
          "column": 15,
          "function": "handle_user_input",
          "code_snippet": "output = request.args.get('q')\nreturn f\"<h1>{output}</h1>\"",
          "message": "Unescaped user input in HTML output",
          "fix_pattern": "Use html.escape() or Markup()",
          "cwe": "CWE-79",
          "severity": "CRITICAL",
          "rule": "py/xss",
          "links": {
            "cwe_reference": "https://cwe.mitre.org/data/definitions/79.html",
            "fix_guide": "..."
          }
        }
      ]
    }
  }
}
```

**Functions**:
```python
def group_findings_by_cwe(findings: list) -> dict
    # Organize by CWE ID
    
def enrich_with_code_snippets(findings: list, repo_path: Path) -> list
    # Add source code context (5 lines before/after)
    
def suggest_fix_patterns(findings: list) -> dict
    # Common fixes per CWE
    # Return mapping: CWE → [fix patterns]
    
def generate_remediation_checklist(findings: list) -> str
    # Ordered list of fixes (priority order)
    # Include effort estimates
```

### 8.2 Dependency Agent Formatter

**File**: `scripts/ci/security_dependency_agent_format.py` (150 lines)

**Purpose**: Format findings for `dependency-security-review-agent`

**Output Format**:
```json
{
  "total": 5,
  "by_package": {
    "numpy": {
      "current_version": "1.21.0",
      "latest_version": "1.26.0",
      "vulnerabilities": [
        {
          "id": "pip-audit-001",
          "severity": "HIGH",
          "cve": "CVE-2023-XXXXX",
          "title": "NumPy security vulnerability",
          "description": "...",
          "affected_versions": ["<=1.21.0"],
          "fixed_versions": ["1.23.5"],
          "upgrade_to": "1.23.5",
          "is_safe_upgrade": true,
          "breaking_changes": [],
          "risk_level": "low",
          "deprecations": []
        }
      ]
    }
  }
}
```

**Functions**:
```python
def group_findings_by_package(findings: list) -> dict
    # Organize by package name
    
def suggest_upgrade_paths(findings: list) -> dict
    # Safe version upgrades
    # Check pypi.org for latest safe versions
    
def calculate_upgrade_risk(package: str, from_version: str, to_version: str) -> dict
    # Compatibility assessment
    # Breaking changes detection
    # Deprecation warnings
    
def generate_dependency_diff(package: str, from_version: str, to_version: str) -> str
    # What changes in requirements
    # pip freeze output
```

### 8.3 Secrets Agent Categorizer

**File**: Enhanced `scripts/ci/copilot_security_agent_handoff.py` (100 lines)

**Purpose**: Categorize findings for `secret-detection-agent`

**Output Format**:
```json
{
  "total": 0,
  "rotation_required": [],
  "allowlisted": [
    {
      "type": "github_token",
      "value_masked": "ghp_****",
      "file": ".github/workflows/test.yml",
      "line": 45,
      "reason": "Example token in documentation",
      "allowlist_expiry": "2026-12-31"
    }
  ],
  "categories": {
    "aws_keys": 0,
    "github_tokens": 0,
    "private_keys": 0,
    "api_keys": 0,
    "database_creds": 0,
    "false_positives": 1
  }
}
```

**Functions**:
```python
def categorize_secrets(findings: list) -> dict  # pragma: allowlist secret
    # Group by secret type  # pragma: allowlist secret
    
def check_allowlist(findings: list) -> list
    # Filter against allowlist with expiry
    
def generate_rotation_checklist(rotation_required: list) -> str
    # Step-by-step rotation guide
    # Include GitHub Actions token update procedure  # pragma: allowlist secret
```

### 8.4 Testing Checklist

- [ ] CodeQL formatter groups findings correctly by CWE
- [ ] Code snippets extracted accurately
- [ ] Dependency formatter finds safe upgrade paths
- [ ] Upgrade risk correctly assessed (no breaking changes recommended)
- [ ] Secrets categorizer separates actionable from allowlisted
- [ ] All output JSON valid and parseable
- [ ] Performance < 2s for each formatter
- [ ] Error handling for missing/invalid findings
- [ ] Integration with agent handoff workflow successful

---

## 🔄 EXECUTION SEQUENCE

### Parallel Lanes (Can run simultaneously):

**Lane 1: Dashboard & API**
- Phase 4B: Dashboard generation + workflow integration
- Phase 5A-B: API workflow + query module

**Lane 2: PR Enhancement**
- Phase 6: PR formatter + workflow (after Phase 5 complete)

**Lane 3: Commands & Formatting**
- Phase 7: @copilot commands (after Phase 6 complete)
- Phase 8: Agent formatters (after Phase 7 complete)

### Dependency Graph:
```
Phase 4A (COMPLETE)
    ↓
Phase 4B + 5A-B (PARALLEL)
    ↓
Phase 6 (After 5B)
    ↓
Phase 7 (After 6)
    ↓
Phase 8 (After 7)
```

**Total Timeline**:
- Sequential: 40 hours (5 days, 8 hours/day)
- Parallelized: 15-20 hours (2-3 days with overlaps)

---

## 📊 SUCCESS METRICS

✅ All 5 security tools integrated  
✅ Dashboard shows trends and metrics  
✅ API enables querying by CWE/severity/file/package  
✅ PR body auto-enhanced with findings  
✅ @copilot commands functional  
✅ Agent-specific formatters ready for remediation  
✅ All 65 hours of work estimated (8 phases)  
✅ Zero new dependencies (stdlib + existing tools)  
✅ Performance targets met (< 500ms cache, < 2s API)  
✅ Full test coverage for all modules  

---

## 🎯 NEXT STEPS

1. ✅ Phases 4B-5B: Agents currently executing in parallel
2. ⏳ Monitor agent progress and get updates
3. ⏳ Phase 6: Launch after Phase 5B completion
4. ⏳ Phase 7: Launch after Phase 6 completion
5. ⏳ Phase 8: Launch after Phase 7 completion
6. ✅ Document all decisions and decisions in accountability report

---

**Ready for execution!**  
**GO CONTINUE** 🚀
