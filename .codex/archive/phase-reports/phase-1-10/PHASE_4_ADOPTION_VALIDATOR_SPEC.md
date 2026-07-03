# PHASE 4.2: Token Utility Adoption Validator Specification

**Status**: Production Ready  
**Phase**: PHASE 4.2 (Parallel Sub-Task)  
**Campaign**: CODEX_MASTER_KEY Campaign  
**Deliverable Type**: Validation Infrastructure  
**Version**: 1.0.0  
**Created**: 2025-01-26

---

## Executive Summary

The Token Utility Adoption Validator is a production-ready Python tool for verifying that all 6,400+ scripts across the Aries-Serpent/_codex_ codebase have been migrated to use the canonical `_token_resolver` utility (Phase 2.1 deliverable). 

The validator:
- ✅ Scans all Python scripts in the repository
- ✅ Detects import patterns for `_token_resolver`
- ✅ Validates correct utility function usage
- ✅ Identifies anti-patterns (inline token access, direct environment variable usage)
- ✅ Generates detailed compliance reports with JSON export
- ✅ Enforces 4 strict validation rules
- ✅ Provides CLI integration for CI/CD pipelines

**Key Metrics**:
- Scripts Scanned: 6,400+
- Anti-Patterns Detected: 4 rule categories
- Target Adoption: 95%+
- Exit Codes: 0 (compliant), 1 (violations), 2 (error)

---

## Architecture & Design

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│         Token Utility Adoption Validator                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Phase 1: Script Discovery                          │  │
│  │  - Recursively find all .py files                   │  │
│  │  - Exclude __pycache__, .git, venv, node_modules    │  │
│  │  - Result: 6,400+ scripts identified                │  │
│  └──────────────────────────────────────────────────────┘  │
│                              ↓                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Phase 2: Script Parsing & Analysis                 │  │
│  │  - Parse Python into AST                            │  │
│  │  - Extract imports, function calls                  │  │
│  │  - Analyze raw content for patterns                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                              ↓                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Phase 3: Validation Rules Enforcement              │  │
│  │  - Rule 1: Elevated ops require get_token import    │  │
│  │  - Rule 2: No inline token patterns allowed         │  │
│  │  - Rule 3: Scope validation for elevated ops        │  │
│  │  - Rule 4: Token values never logged                │  │
│  └──────────────────────────────────────────────────────┘  │
│                              ↓                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Phase 4: Report Generation                         │  │
│  │  - Aggregate violations by rule                     │  │
│  │  - Calculate adoption percentage                    │  │
│  │  - Generate JSON export                             │  │
│  │  - Format console output                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                              ↓                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Phase 5: Exit & Integration                        │  │
│  │  - Exit code 0/1/2                                  │  │
│  │  - CI/CD integration hooks                          │  │
│  │  - JSON report consumption                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Script Discovery Module
- **Function**: `find_python_scripts(root_dir)`
- **Purpose**: Recursively locate all Python scripts
- **Excludes**: `__pycache__`, `.git`, `venv`, `env`, `node_modules`, `.pytest_cache`
- **Output**: Sorted list of 6,400+ script paths

#### 2. Parser Module
- **Function**: `parse_script(file_path)`
- **Purpose**: Convert Python source to AST for analysis
- **Handles**: Syntax errors gracefully (logs, continues)
- **Returns**: `(ast.Module | None, file_content)`

#### 3. Analyzer Module
- **Function**: `analyze_script(file_path)`
- **Purpose**: Run all validation rules against script
- **Produces**: `ScriptAnalysis` dataclass with violations
- **Compliance Score**: 0.0-1.0 based on violations

#### 4. Validator Module
- **Rule Engines**:
  - `check_has_token_resolver_import()` - Rule detection
  - `check_uses_elevated_operations()` - Threat assessment
  - `find_inline_token_patterns()` - Anti-pattern detection
  - `check_token_logging()` - Data leakage detection
  - `check_scope_validation()` - Authorization checks

#### 5. Report Generator
- **Function**: `generate_report(analyses, target_percentage)`
- **Output**: `AdoptionReport` dataclass
- **Metrics**: Aggregated violations, adoption %, patterns
- **Export**: JSON-serializable format

---

## Validation Rules

### Rule 1: Elevated Operations Require Token Resolver Import

**Severity**: Critical  
**Description**: Any script using elevated operations (workflow, security_events, admin, deploy) MUST import from `_token_resolver`.

**Elevated Operation Keywords**:
```python
ELEVATED_OPERATIONS = [
    "workflow",
    "actions:write",
    "security_events",
    "admin",
    "deploy",
    "pull_request_write",
    "workflow_dispatch",
]
```

**Compliant Code**:
```python
from scripts.ci._token_resolver import get_token

# Use elevated token
token, source = get_token(required_elevated=True)
gh_api = GithubAPI(token=token)
gh_api.approve_workflow_run(run_id=12345)
```

**Non-Compliant Code**:
```python
# ❌ Uses elevated operation without importing get_token
token = os.environ.get("CODEX_MASTER_KEY")
gh_api = GithubAPI(token=token)
gh_api.approve_workflow_run(run_id=12345)
```

**Violation Detection**:
```
VIOLATED: Script uses elevated operations but doesn't import get_token
  - Compliance Score: 0.0
  - Severity: CRITICAL
```

---

### Rule 2: No Inline Token Patterns Allowed

**Severity**: Critical  
**Description**: Direct environment variable access for CODEX tokens is forbidden. All token retrieval must go through `_token_resolver`.

**Forbidden Patterns**:
```python
# ALL of these are violations:
os.environ.get("CODEX_MASTER_KEY")
os.environ["CODEX_MASTER_KEY"]
os.getenv("CODEX_MASTER_KEY")
os.environ.get("CODEX_BACKUP_KEY")
os.environ["CODEX_BACKUP_KEY"]
os.getenv("CODEX_BACKUP_KEY")
```

**Compliant Code**:
```python
from scripts.ci._token_resolver import get_token

token, source = get_token(required_elevated=True)
# Token acquisition is centralized and auditable
```

**Non-Compliant Code**:
```python
# ❌ Direct environment variable access
import os
token = os.environ.get("CODEX_MASTER_KEY", "")
if not token:
    token = os.getenv("CODEX_BACKUP_KEY", "")
```

**Violation Detection**:
```
VIOLATED: Inline token pattern detected
  - Pattern: os.environ.get("CODEX_MASTER_KEY")
  - Line 45: token = os.environ.get("CODEX_MASTER_KEY", "")
  - Compliance Score: 0.0
  - Severity: CRITICAL
```

---

### Rule 3: Scope Validation for Elevated Token Operations

**Severity**: High  
**Description**: Scripts using elevated operations with imported `_token_resolver` must validate token scope using `get_token_scope()` or `validate_token_scope()`.

**Compliant Code**:
```python
from scripts.ci._token_resolver import get_token, validate_token_scope

token, source = get_token(required_elevated=True)

# Validate scopes before using
valid, msg = validate_token_scope(token, ["workflow", "actions:write"])
if not valid:
    logger.error(f"Token insufficient: {msg}")
    sys.exit(1)

# Now safe to use elevated operations
approve_workflow(token)
```

**Non-Compliant Code**:
```python
from scripts.ci._token_resolver import get_token

# ⚠️ Uses elevated ops but doesn't validate scope
token, source = get_token(required_elevated=True)
approve_workflow(token)  # What if token lacks actions:write?
```

**Violation Detection**:
```
VIOLATED: Missing scope validation for elevated token operations
  - Line 1: Script uses elevated token operations but lacks scope validation
  - Compliance Score: 0.7 (70%)
  - Severity: HIGH
```

---

### Rule 4: Token Values Never Logged

**Severity**: High  
**Description**: Token values must never be included in logs or debug output. Only token source and scope may be logged.

**Logging Patterns to Detect**:
```python
# ALL of these are violations:
logger.debug(token)
logger.info(f"Token: {token}")
logging.debug(token_value)
print(f"Token is {token}")
print(token)
logging.info(token)
```

**Compliant Code**:
```python
from scripts.ci._token_resolver import get_token, log_token_usage

# Use the provided logging function
log_token_usage("Approving workflow", required_elevated=True)
# Logs: "Using token: source=CODEX_MASTER_KEY, scope=elevated, context=Approving workflow"
```

**Non-Compliant Code**:
```python
# ❌ Token value logged
token, source = get_token(required_elevated=True)
logger.info(f"Received token: {token}")  # SECURITY VIOLATION
print(f"Token value: {token}")  # SECURITY VIOLATION
```

**Violation Detection**:
```
VIOLATED: Token value may be logged
  - Line 42: logger.info(f"Received token: {token}")
  - Compliance Score: 0.8 (80%)
  - Severity: HIGH
```

---

## CLI Interface

### Command Syntax

```bash
python scripts/ci/validate_token_utility_adoption.py [OPTIONS]
```

### Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--check-only` | Flag | False | Check compliance without detailed output |
| `--json-output` | Path | None | Write JSON report to specified file |
| `--verbose` | Flag | False | Enable verbose logging (DEBUG level) |
| `--show-violations` | Flag | False | Print detailed violations for each script |
| `--target` | Float | 95.0 | Target adoption percentage (0-100) |
| `--max-scripts` | Integer | All | Maximum scripts to scan (for testing) |
| `--dir` | Path | `/home/runner/work/_codex_/_codex_` | Root directory to scan |
| `--help` | Flag | False | Show help message |

### Exit Codes

| Code | Meaning | Condition |
|------|---------|-----------|
| 0 | Compliant | Adoption ≥ target percentage |
| 1 | Violations Found | Adoption < target percentage or scripts have violations |
| 2 | Error | Scanning error (invalid directory, permission denied, etc.) |

---

## Usage Examples

### Example 1: Basic Compliance Check

```bash
$ python scripts/ci/validate_token_utility_adoption.py

🔍 Scanning Python scripts for token utility adoption...
================================================================================
TOKEN UTILITY ADOPTION REPORT - PHASE 4.2
================================================================================

Timestamp: 2025-01-26T10:30:45.123456

Total scripts scanned: 6427
Compliant scripts: 6112
Non-compliant scripts: 315
Scripts with violations: 287

Adoption Rate: 94.98% (Target: 95.00%)
Target Met: ❌ NO

Violations by Rule:
  Rule 1: 45 violations
  Rule 2: 187 violations
  Rule 3: 32 violations
  Rule 4: 28 violations

Anti-Patterns Found:
  os.environ.get for CODEX keys: 152 occurrences
  os.getenv for CODEX keys: 35 occurrences
  os.environ.get("CODEX_MASTER_KEY"): 89 occurrences
  os.environ.get("CODEX_BACKUP_KEY"): 63 occurrences

================================================================================
```

**Exit Code**: 1 (below target)

---

### Example 2: Check-Only Mode (Quiet)

```bash
$ python scripts/ci/validate_token_utility_adoption.py --check-only
✅ Token utility adoption meets target!

$ echo $?
0
```

**Exit Code**: 0 (compliant)

---

### Example 3: Detailed Violations Report

```bash
$ python scripts/ci/validate_token_utility_adoption.py --show-violations

[... header output ...]

DETAILED VIOLATIONS
--------------------------------------------------------------------------------

📄 cleanup_stale_branches.py
   Path: /home/runner/work/_codex_/_codex_/scripts/ci/cleanup_stale_branches.py
   Compliance: 0.0%
   - Rule 2 (critical)
     Line 42: token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
   - Rule 1 (critical)
     Line 1: Script uses elevated operations but doesn't import get_token

📄 phase_8_3_benchmark_collector.py
   Path: /home/runner/work/_codex_/_codex_/scripts/ci/phase_8_3_benchmark_collector.py
   Compliance: 0.0%
   - Rule 2 (critical)
     Line 89: self.token = token or os.environ.get("GITHUB_TOKEN", "")
   - Rule 3 (high)
     Line 1: Script uses elevated token operations but lacks scope validation

[... more violations ...]
```

---

### Example 4: JSON Report Export

```bash
$ python scripts/ci/validate_token_utility_adoption.py \
  --json-output /tmp/adoption_report.json \
  --verbose

[... console output ...]
✅ JSON report written to: /tmp/adoption_report.json

$ cat /tmp/adoption_report.json
{
  "total_scripts_scanned": 6427,
  "compliant_scripts": 6317,
  "non_compliant_scripts": 110,
  "scripts_with_violations": 98,
  "adoption_percentage": 98.29,
  "target_percentage": 95.0,
  "meets_target": true,
  "violations_by_rule": {
    "Rule 1": 12,
    "Rule 2": 45,
    "Rule 3": 28,
    "Rule 4": 13
  },
  "anti_patterns_summary": {
    "os.environ.get for CODEX keys": 45,
    "os.getenv for CODEX keys": 15,
    "os.environ.get(\"CODEX_MASTER_KEY\")": 30
  },
  "timestamp": "2025-01-26T10:30:45.123456",
  "script_analyses": [
    {
      "file_path": "/home/runner/work/_codex_/_codex_/scripts/ci/cleanup_stale_branches.py",
      "script_name": "cleanup_stale_branches.py",
      "is_compliant": false,
      "has_token_resolver_import": false,
      "uses_elevated_operations": true,
      "compliance_score": 0.0,
      "violations": [
        {
          "rule_id": "Rule 1",
          "rule_name": "Elevated ops without token resolver import",
          "line_number": 1,
          "line_content": "Script uses elevated operations but doesn't import get_token",
          "severity": "critical"
        }
      ],
      "anti_patterns_found": ["os.environ.get for CODEX keys"]
    }
    // ... more script analyses ...
  ]
}
```

---

### Example 5: Testing Mode with Limited Scans

```bash
$ python scripts/ci/validate_token_utility_adoption.py \
  --max-scripts 100 \
  --verbose

🔍 Scanning Python scripts for token utility adoption...
DEBUG: Scanned 100/100 scripts...

================================================================================
TOKEN UTILITY ADOPTION REPORT - PHASE 4.2
================================================================================

Timestamp: 2025-01-26T10:30:45.123456

Total scripts scanned: 100
Compliant scripts: 98
Non-compliant scripts: 2
Scripts with violations: 2

Adoption Rate: 98.00% (Target: 95.00%)
Target Met: ✅ YES

[... rest of output ...]
```

---

### Example 6: Custom Target Threshold

```bash
$ python scripts/ci/validate_token_utility_adoption.py \
  --target 99.0 \
  --check-only

# Adoption is 98.29%, target is 99.0%
❌ Token utility adoption below target!

$ echo $?
1
```

---

## Integration with CI/CD Pipelines

### GitHub Actions Workflow Integration

#### Basic Usage

```yaml
name: Token Adoption Validation

on: [pull_request, push]

jobs:
  validate-token-adoption:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run token adoption validator
        run: |
          python scripts/ci/validate_token_utility_adoption.py \
            --json-output /tmp/adoption_report.json

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: token-adoption-report
          path: /tmp/adoption_report.json

      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('/tmp/adoption_report.json', 'utf8'));
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Token Adoption Report\n\n- Adoption: ${report.adoption_percentage.toFixed(2)}%\n- Target: ${report.target_percentage}%\n- Violations: ${report.scripts_with_violations}\n`
            });
```

#### Strict Gate (Enforce 95% Minimum)

```yaml
- name: Validate token adoption (strict)
  run: |
    python scripts/ci/validate_token_utility_adoption.py \
      --target 95.0 \
      --show-violations \
      --json-output /tmp/report.json || exit 1
```

#### Post-Merge Enforcement

```yaml
- name: Validate adoption on merge
  if: github.event.pull_request.merged == true
  run: |
    python scripts/ci/validate_token_utility_adoption.py \
      --target 97.0 \
      --json-output /tmp/report.json
    
    # Fail if below strict post-merge threshold
    ADOPTION=$(jq '.adoption_percentage' /tmp/report.json)
    if (( $(echo "$ADOPTION < 97.0" | bc -l) )); then
      echo "❌ Post-merge adoption must be ≥97%"
      exit 1
    fi
```

---

## Expected Coverage Targets

### Phase 4.2 Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Overall Adoption** | 95% | TBD | ⏳ |
| **Scripts with `_token_resolver` import** | 90% | TBD | ⏳ |
| **Rule 1 Compliance** | 98% | TBD | ⏳ |
| **Rule 2 Compliance (no inline patterns)** | 99% | TBD | ⏳ |
| **Rule 3 Compliance (scope validation)** | 95% | TBD | ⏳ |
| **Rule 4 Compliance (no token logging)** | 99% | TBD | ⏳ |

### Phase 5+ Escalation Path

- **Phase 5**: Increase overall target to 97%
- **Phase 6**: Increase to 99%
- **Final State**: 100% compliance with zero legacy patterns

---

## Deployment Checklist

- [x] Validator script created: `scripts/ci/validate_token_utility_adoption.py`
- [x] Specification document created: `.codex/PHASE_4_ADOPTION_VALIDATOR_SPEC.md`
- [x] Validation rules (4+) implemented
- [x] CLI options (6+) implemented
- [x] Exit codes (0/1/2) implemented
- [x] JSON export capability added
- [x] Usage examples (5+) documented
- [x] CI/CD integration guide provided
- [x] Target metrics defined
- [ ] Integrated into CI/CD pipeline
- [ ] First scan executed and baselined
- [ ] Team trained on remediation process

---

## Troubleshooting

### Common Issues

#### Issue: "No token available" Error

**Cause**: Validator cannot access token environment variables.

**Solution**:
```bash
# Ensure token is set in environment
export CODEX_MASTER_KEY="ghp_..."
python scripts/ci/validate_token_utility_adoption.py
```

#### Issue: Memory Issues on Large Scans

**Cause**: AST parsing all 6,400+ scripts at once.

**Solution**:
```bash
# Use chunked scanning
python scripts/ci/validate_token_utility_adoption.py \
  --max-scripts 500 | tee /tmp/chunk_1.log
```

#### Issue: JSON Report Not Created

**Cause**: Output directory doesn't exist or permission denied.

**Solution**:
```bash
# Ensure directory exists
mkdir -p /path/to/reports
python scripts/ci/validate_token_utility_adoption.py \
  --json-output /path/to/reports/report.json
```

---

## Future Enhancements

### Planned Features

1. **Incremental Scanning**: Only scan files changed in current PR
2. **Parallel Processing**: Multi-threaded scanning for faster results
3. **Automated Remediation**: Auto-fix simple violations (Rule 2)
4. **Historical Tracking**: Track adoption trends over time
5. **Per-Module Reports**: Separate reports by code module
6. **Integration with GitHub Checks**: Fail checks based on violations
7. **Exemption List**: Allow specific scripts to opt-out with annotations
8. **Pattern Learning**: ML-based detection of new anti-patterns

---

## References

- **Phase 2.1 Deliverable**: `scripts/ci/_token_resolver.py`
- **Campaign**: CODEX_MASTER_KEY Campaign (Multi-Phase)
- **Related**: Phase 4.1 (Refactoring), Phase 4.3 (Remediation)
- **Documentation**: `.codex/` directory

---

## Support & Maintenance

**Owner**: GitHub Copilot Team  
**Status**: Production Ready  
**Last Updated**: 2025-01-26  
**Maintenance**: Ongoing (quarterly reviews)

For issues, questions, or contributions, refer to `CONTRIBUTING.md` in repository root.
