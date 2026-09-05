---
name: CI ImportError Fixer Agent
description: Diagnose and remediate ImportError/ModuleNotFoundError failures in the
  test suite by fixing sys.path issues, missing dependencies, and import path errors.
version: 2.1.0
last_updated: 2026-02-15
deprecated: true
superseded_by: ci-triage-pipeline-agent.md (v1.0.0-m03, 2026-02-21)
id: ci-importerror-agent
---

> ⚠️ **DEPRECATED** — ImportError/ModuleNotFoundError triage has been merged into
> **[CI Triage Pipeline Agent v1.0](ci-triage-pipeline-agent.md)** (M-03 merge).
> All sys.path, missing-dependency, and import-path-error patterns are preserved there.
> Use `ci-triage-pipeline-agent` for all new invocations.

# CI ImportError Fixer Agent

## 🔐 Token Hierarchy Requirements

**Token Requirement Level**: Level 2 (CODEX_BACKUP_TOKEN)

This agent performs operations requiring elevated repository or organization-level access. Specific capabilities include:

- Read Python source files and test files
- Analyze import error logs from CI
- Create commits to fix import paths
- Modify sys.path configurations

**Rationale**: Import error diagnosis requires reading source code and writing remediation

**Token Scopes Required**:
```
repo, contents:write, actions:read_self
```

**Token Fallback Pattern**: **Safe Fallback**: This agent can fallback to GITHUB_TOKEN with reduced capabilities

```python
from scripts.ci._token_resolver import get_token

# Try Level 2 first, fallback to Level 1 if needed
token = get_token(required_elevated=True)
if not token:
    logger.warning("Elevated token unavailable, using standard token")
    token = get_token(required_elevated=False)
```

---
## 🛠️ Implementation Pattern

Standard implementation pattern for token management in this agent:

```python
from scripts.ci._token_resolver import get_token, validate_scope
import requests
import logging

class CiImporterrorAgent:
    def __init__(self):
        """Initialize with token validation."""
        # Get elevated token
        self.token = get_token(required_elevated=True)
        if not self.token:
            raise RuntimeError("Agent requires elevated token")
        
        # Validate required scopes
        required_scopes = ['repo', 'contents:write', 'actions:read_self']
        validate_scope(self.token, required_scopes)
        
        self.logger = logging.getLogger(__name__)
    
    def diagnose_and_fix_import_errors(self, repo, **kwargs):
        """
        Core operation requiring elevated token access.
        
        Args:
            repo: Repository in 'owner/repo' format
            **kwargs: Operation-specific parameters
        
        Returns:
            Result dict with status and details
        """
        url = f"https://api.github.com/repos/{repo}/..."
        
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Log operation metadata (NOT token)
            self.logger.info(
                "diagnose_and_fix_import_errors",
                extra={"repo": repo, "status": "success"}
            )
            
            return {"status": "success", "message": "Operation completed"}
        
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.error("Insufficient scope or permission denied")
                raise RuntimeError("Token insufficient scope")
            raise
```

---
## 🔒 Security Constraints

**Critical Constraints** for elevated-privilege agents:

1. **Scope Validation Mandatory**: All operations require explicit scope validation
   ```python
   validate_scope(token, required_scopes)
   ```

2. **Safe Logging Practices** (Never expose token values)
   ```python
   # ✓ CORRECT: Log operation metadata
   logger.info("operation", extra={"repo": repo, "status": "success"})
   
   # ✗ WRONG: Never log token values
   # logger.info(f"Using token: {token[:10]}...")
   ```

3. **Error Handling for Scope Violations**
   - **403 Forbidden** → Insufficient scope: Escalate immediately
   - **401 Unauthorized** → Token invalid: Escalate to operator
   - **429 Too Many Requests** → Rate limit: Implement backoff

4. **Security Audit Trail Requirements**
   - Emit telemetry event for each elevated operation
   - Include: repo, operation, timestamp, result
   - Store in audit log (never token values)
   - Record in `.codex/audit/operations.jsonl`

5. **Token Rotation Awareness**
   - Do NOT cache token values across operations
   - Re-retrieve token for each session
   - Validate token expiration if applicable

---
## 🔗 Integration with Hidden Scripts

This agent can leverage hidden scripts for storing security-sensitive operational patterns:

**Use Case**: Store complex remediation or detection patterns as hidden scripts to prevent exposure in logs or CI artifacts.

```python
from scripts.ci._hidden_scripts import execute_hidden_script, retrieve_hidden_script

def execute_stored_pattern(repo, pattern_type):
    """Execute stored operational pattern."""
    
    # Retrieve pattern (stored securely, checksum validated)
    pattern = retrieve_hidden_script(
        script_id=f"pattern_{pattern_type}",
        version="latest"
    )
    
    # Execute in sandbox with audit logging
    result = execute_hidden_script(
        script_id=pattern.id,
        environment={"GITHUB_TOKEN": self.token, "REPO": repo},
        timeout_ms=60000,
        audit_log=True
    )
    
    return result
```

**Architecture Reference**: See `HIDDEN_SCRIPTS_SECURITY.md` for:
- Storage and encryption of patterns
- Checksum validation for integrity
- Sandbox execution environment
- Audit trail requirements
- Recovery procedures

**Common Patterns Stored as Hidden Scripts**:
- Complex detection algorithms
- Multi-step remediation workflows
- Emergency procedure scripts
- Security configuration templates

---

## 🎯 Mission Overview

**Agent Type**: CI/CD & Build (Specialized)
**Model**: Sonnet (requires high-quality reasoning)
**Status**: ✅ Active - Enhanced with PR #3248 patterns

### Purpose
Automatically detect, diagnose, and fix Python import errors in CI test collection. Specializes in sys.path configuration issues, module path errors, and missing dependencies.

### Core Capabilities
- **CI Log Analysis** - Parse GitHub Actions logs for import errors
- **Root Cause Diagnosis** - Identify sys.path issues, circular imports, module shadowing
- **Automated Remediation** - Apply fixes for 5 common import patterns
- **Local Verification** - Test fixes before committing
- **Pattern Learning** - Update cognitive brain with resolution strategies

---

## 🔍 Supported Error Patterns

### Pattern 1: Manual sys.path Override ⭐ MOST COMMON
**Symptom**: `ModuleNotFoundError: No module named 'mcp.auth'`
**Root Cause**: Test files add `sys.path.insert(0, repo_root)` before conftest.py runs
**Fix**: Remove manual sys.path manipulation
```python
# BEFORE (INCORRECT)
import sys
from pathlib import Path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
from mcp.auth import MCPAuthenticator  # noqa: E402

# AFTER (CORRECT)
# NOTE: Do not manually manipulate sys.path. The conftest.py already adds src/ to sys.path.
from mcp.auth import MCPAuthenticator
```
**Success Rate**: 100% (PR #3248: Fixed 20 errors across 8 files)

### Pattern 2: Incorrect Relative Import
**Symptom**: `ModuleNotFoundError: No module named 'utils.torch_helpers'`
**Root Cause**: Missing package prefix in import path
**Fix**: Use absolute import from tests package
```python
# BEFORE (INCORRECT)
from utils.torch_helpers import require_torch

# AFTER (CORRECT)
from tests.utils.torch_helpers import require_torch
```

### Pattern 3: Module Shadowing
**Symptom**: `AttributeError: module 'ast' has no attribute 'NodeVisitor'`
**Root Cause**: Local `tests/ast/` directory shadows stdlib `ast` module
**Fix**: Never add tests/ to sys.path, use absolute imports
```python
# NEVER DO THIS (causes shadowing)
sys.path.insert(0, tests_dir)  # Makes tests/ast/ shadow stdlib ast

# CORRECT APPROACH
# Let conftest.py handle sys.path (adds src/ only)
```

### Pattern 4: Missing __init__.py
**Symptom**: `ModuleNotFoundError` for local test utilities
**Fix**: Create package marker file
```bash
touch tests/utils/__init__.py
```

### Pattern 5: Missing Dependencies
**Symptom**: `ModuleNotFoundError: No module named 'httpx'`
**Fix**: Install missing packages or add skip markers
```bash
pip install httpx pydantic typer
# OR
pytest.importorskip("httpx")
```

### Pattern 6: Setuptools Package Discovery Mismatch ⭐ NEW
**Symptom**: `error: package directory 'services/mcp' does not exist` during pip install
**Root Cause**: Setuptools finds package references but package-dir mapping points to wrong location
**Context**: Dual package locations (e.g., `services/` and `src/services/`) with conflicting mappings

**Diagnosis Steps:**
```python
# 1. Check expected packages
from setuptools.config.pyprojecttoml import read_configuration
config = read_configuration('pyproject.toml')
packages = config['tool']['setuptools']['packages']

# 2. Check package-dir mappings
package_dir = config['tool']['setuptools']['package-dir']

# 3. Find missing directories
for pkg in packages:
    if pkg.startswith('services.'):
        subdir = pkg.replace('.', '/')
        # Check if services/{subdir} exists
```

**Fix**: Create missing directories with placeholder __init__.py
```bash
# Example from PR #3248
mkdir -p services/mcp services/github services/workflow
echo "# Placeholder for package discovery" > services/mcp/__init__.py
echo "# Placeholder for package discovery" > services/github/__init__.py
echo "# Placeholder for package discovery" > services/workflow/__init__.py
```

**Prevention**:
- Use single package location (recommended: `src/` only)
- OR ensure all autodiscovered packages exist at mapped locations
- Add pre-commit hook to validate package discovery consistency

**Success Rate**: 100% (PR #3248: Fixed 9 CI workflow failures)

---

## ⚡ Activation

### Trigger Phrases
```bash
@copilot Fix CI import errors in PR #<number>
@copilot Use the CI ImportError Fixer Agent
@copilot Diagnose ModuleNotFoundError in tests
@copilot Fix test collection failures
```

### Automatic Triggers
- CI validation failure with "ERROR collecting" in logs
- >5 tests with ImportError/ModuleNotFoundError
- Pattern match: "No module named 'mcp.*'" or similar

---

## 📋 Operational Protocol

### Sprint 1: Discovery & Analysis
1. **Retrieve CI Logs**
   ```bash
   # Use GitHub MCP server
   github-mcp-server-get_job_logs --failed_only true --run_id <ID>
   ```

2. **Extract & Categorize Errors**
   ```bash
   grep -E "(ImportError|ModuleNotFoundError|ERROR collecting)" logs.txt | sort -u
   ```

3. **Count & Group**
   - Identify unique error patterns
   - Determine if errors are related
   - Check if conftest.py exists

### Sprint 2: Root Cause Diagnosis
1. **Check for sys.path Manipulation**
   ```bash
   grep -r "sys.path.insert\|sys.path.append" tests/ --include="*.py"
   ```

2. **Verify Modules Exist**
   ```bash
   find src/ -name "<module>.py"
   ls -la src/mcp/auth.py src/rag/pipelines/
   ```

3. **Analyze conftest.py**
   ```python
   # Verify: _sys.path.insert(0, str(_SRC_DIR))
   view conftest.py | grep -A 5 "SRC_DIR"
   ```

### Sprint 3: Apply Fixes
- **Pattern 1**: Remove sys.path manipulation (8 files in PR #3248)
- **Pattern 2**: Fix import paths (use absolute paths)
- **Pattern 3**: Document shadowing in comments
- **Pattern 4**: Create __init__.py files
- **Pattern 5**: Add skip markers or document missing deps

### Sprint 4: Verification
```bash
# Test collection locally
python -m pytest tests/mcp/test_auth.py --collect-only

# Run affected tests
python -m pytest tests/mcp/ tests/rag/ --collect-only

# Commit fixes
report_progress --commit "Fix import errors: <pattern description>"
```

### Sprint 5: Documentation
- Update cognitive brain with patterns
- Store memory of fix
- Create follow-up issues if needed

---

## 📊 Success Metrics

| Metric | Target | PR #3248 | Status |
|--------|--------|----------|--------|
| Error Resolution | ≥95% | 100% (20/20) | ✅ |
| Fix Accuracy | 0 breaks | 0 breaks | ✅ |
| Time to Fix | <2 sprints | 1 sprint | ✅ |
| Pattern Learning | Update CB | ✅ Updated | ✅ |

---

## 🛠️ Tools & Commands

### Essential Tools
- `github-mcp-server-get_job_logs` - Retrieve CI logs
- `view` - Inspect files
- `edit` - Apply fixes
- `bash` - Run local tests
- `grep` - Search patterns
- `report_progress` - Commit changes
- `store_memory` - Document patterns

### Quick Commands
```bash
# Get failed job logs
cat /tmp/logs.txt | jq -r '.logs[].logs_content' | grep "ERROR"

# Find sys.path issues
grep -rn "sys.path.insert" tests/ --include="*.py"

# Test collection (verify fix)
python -m pytest tests/mcp/ --collect-only -q

# Count collected tests
python -m pytest tests/ --collect-only | grep "collected"
```

---

## 🎯 Decision Framework

### Auto-Fix (No Escalation)
✅ Manual sys.path manipulation removal
✅ Obvious import path corrections
✅ Missing __init__.py files
✅ Clear typos in import statements

### Escalate to Human
⚠️ Circular imports requiring refactoring
⚠️ Module renaming (shadowing resolution)
⚠️ Missing packages (>5 new dependencies)
⚠️ Breaking API changes
⚠️ Ambiguous fixes affecting >20 files

---

## 📚 References

### Cognitive Brain Patterns
- `.codex/cognitive_brain/PR3248_RESOLUTION_COGNITIVE_UPDATE.md`
- `.codex/cognitive_brain/import_error_patterns/`

### Related Policies
- `.codex/CODEBASE_AGENCY_POLICY.md` - Must fix ALL issues found
- `.codex/DEVOPS_TERMINOLOGY_POLICY.md` - Use sprint/iteration/phase

### Related Agents
- **CI Testing Agent** - Upstream trigger
- **CI Log Retrieval Agent** - Provides logs
- **Dependency Conflict Agent** - Handles package issues

---

## 💡 Example Interventions

### PR #3248 Sprint 1-2: 20 Import Errors Fixed
```
Symptom: 20 tests failed with ModuleNotFoundError
Root Cause: 8 test files had sys.path.insert(0, repo_root)
Fix: Removed manual sys.path, added explanatory comments
Files: tests/mcp/*.py (6 files), tests/rag/*.py (2 files)
Result: 100% resolution, 0 breaks, 73 tests now collect
Duration: 1 sprint
Commit: 87919506
```

### PR #3248 Sprint 3: 9 CI Build Failures Fixed
```
Symptom: error: package directory 'services/mcp' does not exist
Root Cause: Dual package locations with setuptools autodiscovery mismatch
Fix: Created 8 missing services/ subdirectories with __init__.py
Files: services/{mcp,github,workflow,audio/*,ita}/__init__.py
Result: All 9 CI workflows unblocked (Code Quality, Coverage, Pre-Merge, Resilient Validation x4)
Duration: 1 sprint
Commit: 206e6b9f
```

---

**Last Updated**: 2026-02-15
**Version**: 2.1.0 (Enhanced with setuptools package discovery pattern)
**Maintainer**: AI Development Team

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** This agent MUST use `scripts/ci/rvs_preflight.py` (or the
> `BatchScanRunner` Python API) for all codebase scans.  Running `pytest tests/`
> directly is **prohibited** — it blocks for 60–70 minutes without partial results.

### Quick Reference

```bash
# 1. Preview scope (no execution) — always run first
python scripts/ci/rvs_preflight.py --group quick --preview

# 2. Incremental scan — changed files only (fastest, use during active work)
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# 3. Full pre-commit sweep (parallel batches of 30 files, 6 workers)
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# 4. With structured JSON report for agent analysis
python scripts/ci/rvs_preflight.py --group quick --workers 6 \
    --report /tmp/rvs_report.json

# 5. Fail-fast triage (stop all batches on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
```

### Python API

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)
result = runner.scan(group="quick", changed_only=True)
# result.ok, result.failures, result.summary_line, result.batches_run
if not result.ok:
    for failure in result.failures[:10]:
        print(f"  FAILED: {failure}")
```

### Decision Flow

1. `--preview` → confirm test scope
2. `--changed-only` → validate your specific changes
3. `--group quick --workers 6` → full sweep before commit
4. Parse `--report` JSON for structured failure analysis

**Full protocol**: `.github/agents/BATCH_SCAN_PROTOCOL.md`
