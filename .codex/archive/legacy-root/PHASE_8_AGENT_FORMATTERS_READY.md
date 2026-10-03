# 🤖 Phase 8: Agent-Specific Formatters - Ready for Execution

**Status**: Ready for Launch (awaiting Phase 7 completion)  
**Created**: 2026-07-07T02:15:00Z  
**Target Agents**: 3 specialized agents in parallel execution

---

## 🎯 PHASE 8 OVERVIEW

Phase 8 creates specialized formatters to route security findings to the most appropriate agent specialists for remediation:

1. **CodeQL Agent Formatter** — CWE-based remediation routing
2. **Dependency Agent Formatter** — Package upgrade recommendations
3. **Secrets Agent Categorizer** — Secret rotation and allowlist management

Each formatter prepares findings in the exact format needed by its target agent, enabling efficient handoff and autonomous remediation.

---

## 🔧 FORMATTER 1: CodeQL Agent Formatter

**File**: `scripts/ci/security_codeql_agent_format.py` (150 lines)  
**Target Agent**: `codeql-alert-resolution-agent`  
**Purpose**: Group CodeQL findings by CWE with code context and fix patterns

### Functions to Implement

```python
def group_findings_by_cwe(findings: list) -> dict:
    """
    Organize CodeQL findings by CWE ID.
    
    Returns:
    {
        "CWE-79": [finding1, finding2, ...],
        "CWE-22": [finding3, ...],
        ...
    }
    """

def enrich_with_code_snippets(findings: list, repo_path: Path) -> list:
    """
    Add source code context for each finding.
    
    For each finding with file:line, extract:
    - 5 lines before
    - Target line (highlighted)
    - 5 lines after
    - Function context
    """

def suggest_fix_patterns(findings: list) -> dict:
    """
    Return common fix patterns per CWE.
    
    Examples:
    - CWE-79: Use html.escape(), Markup(), or similar
    - CWE-22: Use pathlib.Path.resolve() with validation
    - CWE-89: Use parameterized queries
    
    Returns mapping: CWE → [patterns]
    """

def generate_remediation_checklist(findings: list) -> str:
    """
    Generate ordered remediation steps.
    
    Group by CWE, include:
    - Issue count
    - Severity
    - Files affected
    - Suggested fix
    - Effort estimate (low/medium/high)
    
    Return markdown checklist
    """
```

### Output Format

```json
{
  "agent": "codeql-alert-resolution-agent",
  "total_findings": 7,
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
            "fix_guide": "...",
            "full_report": ".codex/security-findings-comprehensive.md#CWE-79"
          }
        }
      ]
    }
  },
  "remediation_checklist": [
    "[ ] CWE-79: Fix 4 XSS findings in HTML output (HIGH effort)",
    "[ ] CWE-22: Fix 3 path traversal findings (MEDIUM effort)"
  ]
}
```

### CLI Interface

```bash
python scripts/ci/security_codeql_agent_format.py format \
  --findings .codex/security-findings-comprehensive.json \
  --repo-path /home/runner/work/_codex_/_codex_ \
  --output codeql-format.json
```

### Testing Requirements

- [ ] CodeQL findings correctly grouped by CWE
- [ ] Code snippets extracted accurately (5 lines context)
- [ ] Fix patterns relevant to each CWE
- [ ] Remediation checklist properly prioritized
- [ ] Output JSON is valid and complete
- [ ] Handles missing fields gracefully
- [ ] Performance < 2s for typical findings (7-20 issues)

---

## 🔧 FORMATTER 2: Dependency Agent Formatter

**File**: `scripts/ci/security_dependency_agent_format.py` (150 lines)  
**Target Agent**: `dependency-security-review-agent`  
**Purpose**: Organize dependency vulnerabilities by package with safe upgrade paths

### Functions to Implement

```python
def group_findings_by_package(findings: list) -> dict:
    """
    Organize dependency findings by package name.
    
    Returns:
    {
        "numpy": [vuln1, vuln2, ...],
        "requests": [vuln3, ...],
        ...
    }
    """

def suggest_upgrade_paths(findings: list) -> dict:
    """
    Determine safe upgrade paths for vulnerable packages.
    
    For each package:vulnerability pair:
    - Current version
    - Latest secure version
    - Intermediate versions (if multiple major upgrades needed)
    - Breaking changes between versions
    - Deprecation warnings
    
    Returns: Package → {safe_versions, upgrade_path, risks}
    """

def calculate_upgrade_risk(package: str, from_version: str, to_version: str) -> dict:
    """
    Assess compatibility risk for version upgrade.
    
    Returns:
    {
        "risk_level": "low|medium|high",  # pragma: allowlist secret
        "breaking_changes": [list of changes],
        "deprecations": [deprecated items],
        "test_effort": "low|medium|high",
        "rollback_difficulty": "easy|moderate|hard"
    }
    """

def generate_dependency_diff(package: str, from_version: str, to_version: str) -> str:
    """
    Generate requirements.txt style diff.
    
    Example:
    - numpy==1.21.0
    + numpy==1.23.5
    
    Returns: Diff string for visual reference
    """
```

### Output Format

```json
{
  "agent": "dependency-security-review-agent",
  "total_findings": 5,
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
          "deprecations": [],
          "risk_level": "low",
          "test_effort": "low",
          "diff": "- numpy==1.21.0\n+ numpy==1.23.5"
        }
      ]
    }
  },
  "upgrade_summary": "5 packages have upgrades. 4 low-risk, 1 medium-risk."
}
```

### CLI Interface

```bash
python scripts/ci/security_dependency_agent_format.py format \
  --findings .codex/security-findings-comprehensive.json \
  --output deps-format.json
```

### Testing Requirements

- [ ] Dependencies grouped by package name
- [ ] Upgrade paths calculated correctly
- [ ] Risk assessment accurate (breaking changes detected)
- [ ] Safe upgrades marked correctly
- [ ] Deprecation warnings included
- [ ] Output JSON is valid
- [ ] Performance < 2s (typical: 5-10 packages)

---

## 🔧 FORMATTER 3: Secrets Agent Categorizer

**File**: Enhanced `scripts/ci/copilot_security_agent_handoff.py` (100 lines)  
**Target Agent**: `secret-detection-agent`  
**Purpose**: Categorize secrets findings and manage rotation/allowlist

### Functions to Implement

```python
def categorize_secrets(findings: list) -> dict:  # pragma: allowlist secret
    """
    Group secrets by type and risk level.  # pragma: allowlist secret
    
    Categories:
    - AWS keys (CRITICAL)
    - GitHub tokens (CRITICAL)  # pragma: allowlist secret
    - Private keys (CRITICAL)
    - API keys (HIGH)
    - Database credentials (CRITICAL)
    - False positives (informational)
    
    Returns categorized findings
    """

def check_allowlist(findings: list, allowlist_file: Path = None) -> tuple:
    """
    Filter findings against allowlist with expiry dates.
    
    Returns: (action_required, allowlisted)
    - action_required: findings needing immediate rotation
    - allowlisted: findings with documented exceptions
    """

def generate_rotation_checklist(rotation_required: list) -> str:
    """
    Generate step-by-step rotation guide.
    
    For each secret:  # pragma: allowlist secret
    1. Revoke current secret  # pragma: allowlist secret
    2. Update GitHub Actions secrets  # pragma: allowlist secret
    3. Update application configs
    4. Verify functionality
    5. Document rotation date
    
    Returns: Markdown checklist
    """
```

### Output Format

```json
{
  "agent": "secret-detection-agent",
  "total_findings": 0,
  "categories": {
    "aws_keys": 0,
    "github_tokens": 0,
    "private_keys": 0,
    "api_keys": 0,
    "database_creds": 0,
    "false_positives": 1
  },
  "rotation_required": [],
  "allowlisted": [
    {
      "type": "github_token",
      "value_masked": "ghp_****",
      "file": ".github/workflows/test.yml",
      "line": 45,
      "reason": "Example token in documentation",
      "allowlist_expiry": "2026-12-31",
      "documented_by": "Security Review"
    }
  ],
  "rotation_summary": "All secrets managed. No rotation required."
}
```

### CLI Interface

```bash
python scripts/ci/copilot_security_agent_handoff.py format-secrets \
  --findings .codex/security-findings-comprehensive.json \
  --allowlist .codex/secrets-allowlist.json \
  --output secrets-format.json
```

### Testing Requirements

- [ ] Secrets correctly categorized by type
- [ ] Rotation urgency properly assigned
- [ ] Allowlist filtering accurate
- [ ] Expiry dates honored
- [ ] Rotation checklists clear and actionable
- [ ] Output JSON is valid
- [ ] Performance instant (< 100ms)

---

## 📊 PHASE 8 ORCHESTRATION

All three formatters run in parallel:

```
Phase 8 START
    ↓
codeql-alert-resolution-agent ─→ formats CodeQL findings (150 lines)
dependency-security-review-agent ─→ formats dependencies (150 lines)
secret-detection-agent ─→ categorizes secrets (100 lines)  # pragma: allowlist secret
    ↓ (all parallel, ~10-15 minutes each)
    ↓
Phase 8 COMPLETE
```

---

## ✅ INTEGRATION STRATEGY

After Phase 8 formatters complete:

1. **Findings flow** → Cache manager (Phase 4A)
2. **Cache** → Dashboard (Phase 4B)
3. **Dashboard** → API queries (Phase 5)
4. **PR body** → Enhanced with findings (Phase 6)
5. **@copilot commands** → Route to formatters (Phase 7)
6. **Formatters** → Agent-specific routing (Phase 8)
7. **Agents** → Autonomous remediation

---

## 🎯 SUCCESS CRITERIA

- ✅ All 3 formatters implemented (400 lines total)
- ✅ Comprehensive test coverage (80%+ per formatter)
- ✅ JSON output valid and parseable
- ✅ Agent routing correct (CodeQL → CodeQL agent, Deps → Deps agent, etc.)
- ✅ Performance targets met (< 2s per formatter)
- ✅ Ready for autonomous agent execution

---

## 📋 DEPENDENCIES

Phase 8 requires:
- ✅ Phase 4A: Cache system (delivers findings)
- ✅ Phase 4B: Dashboard (visualizes trends)
- ✅ Phase 5: API (enables queries)
- ✅ Phase 6: PR enhancement (context for findings)
- ✅ Phase 7: @copilot commands (triggers formatting)

All dependencies will be complete before Phase 8 launch.

---

## 🚀 NEXT STEPS

1. Upon Phase 7 completion → Launch Phase 8 (3 agents)
2. Estimated Phase 8 start: 2026-07-07T02:40:00Z
3. Estimated Phase 8 complete: 2026-07-07T03:15:00Z
4. Campaign finish: Integration testing + final report
5. **Campaign Completion Target: 2026-07-07T04:00:00Z**

---

**Authority**: D-tier autonomous (@mbaetiong: GO CONTINUE)  
**Status**: READY FOR EXECUTION ✅  
**Next Event**: Phase 7 Completion Trigger
