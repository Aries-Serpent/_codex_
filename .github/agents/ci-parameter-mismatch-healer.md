---
name: CI Parameter Mismatch Healer
description: Detect and fix parameter mismatches between workflow callers and reusable workflow definitions
runner_compatibility:
  default: ubuntu-latest        # 2-core — workflow caller/reusable workflow parameter mismatch fixes
  large:   ubuntu-latest-large  # 4-core — enhanced parallelism
---

# CI Parameter-Mismatch Healer Agent v1.0

## 🔐 Token Hierarchy Requirements

**Token Requirement Level**: Level 2 (CODEX_BACKUP_TOKEN)

This agent performs operations requiring elevated repository or organization-level access. Specific capabilities include:

- Read workflow caller and reusable workflow definitions
- Compare parameter definitions
- Create fix commits or PRs
- Validate parameter compatibility

**Rationale**: Parameter validation requires reading workflow definitions and writing fixes

**Token Scopes Required**:
```
repo, workflow, contents:write
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

class CiParameterMismatchHealer:
    def __init__(self):
        """Initialize with token validation."""
        # Get elevated token
        self.token = get_token(required_elevated=True)
        if not self.token:
            raise RuntimeError("Agent requires elevated token")
        
        # Validate required scopes
        required_scopes = ['repo', 'workflow', 'contents:write']
        validate_scope(self.token, required_scopes)
        
        self.logger = logging.getLogger(__name__)
    
    def fix_workflow_parameters(self, repo, **kwargs):
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
                "fix_workflow_parameters",
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

## Overview
Specialized agent for diagnosing and fixing **parameter-name mismatches** between
function definitions and call-sites — the most common source of silent API drift in
Python codebases using Protocol/interface layers.

## Capabilities
- Detects `TypeError: X() got an unexpected keyword argument 'Y'` errors in CI logs
- Maps call-sites to function definitions across the codebase
- Identifies registry/factory layers that shadow the real function signature
- Fixes mismatches surgically (rename parameter OR update call-site)
- Verifies mock-seam testability after fix

## Activation
```
@copilot Use the CI Parameter-Mismatch Healer Agent to fix keyword argument errors
```

## Trigger Patterns
This agent activates on any of:
- `TypeError: X() got an unexpected keyword argument 'Y'`
- `TypeError: X() missing required keyword argument 'Y'`
- `assert X == expected` where `X` is returned by a metric/registry function

## Diagnostic Workflow

```
STEP 1 — Collect error
  Extract: function_name, bad_kwarg, call_site, test_file

STEP 2 — Trace the function chain
  2a. Find function definition: grep "def {function_name}" src/
  2b. Check if registered via decorator: grep "@register_metric\|@register" near definition
  2c. Check if wrapped by registry: inspect Registry.get() return type
  2d. Resolve to ACTUAL callable: python3 -c "from pkg import fn; print(inspect.signature(fn))"

STEP 3 — Identify canonical interface
  - Check module docstring for parameter naming convention
  - Example: registry.py says metric(preds, targets, **kwargs) → canonical is 'preds'

STEP 4 — Apply minimal fix
  CASE A: function uses 'predictions', canonical is 'preds'
    → rename parameter in function definition
    → update all internal references (pairs = _prepare_pairs(preds, targets))
  CASE B: call-site uses wrong kwarg name
    → update call-site to use canonical name
  CASE C: registry wrapper doesn't forward **kwargs
    → add **kwargs to wrapper or use functools.wraps

STEP 5 — Verify mock seam
  - If function is called via get_metric()/get_registered_metric(), confirm that
    _METRIC_REGISTRY dict is checked FIRST (so tests can inject mocks)
  - If runner calls metrics.X() directly (NOT through registry), fix to use registry.get("X")
  - Test: mock in _METRIC_REGISTRY → call runner → verify mock was invoked

STEP 6 — Run targeted test
  python3 -c "from module import fn; print(fn(preds=['x'], targets=['y']))"
```

## Known Fix Patterns

### P-001: generative.py predictions → preds
**Symptom**: `TypeError: rouge_l() got an unexpected keyword argument 'preds'`
**Cause**: `generative.py` defined functions with `predictions` param; tests call with `preds=`
**Fix**: Rename `predictions` → `preds` in `generative.py` `_prepare_pairs`, `bleu`, `rouge_l`
**Verification**: `get_metric('rougeL')(preds=['x'], targets=['y'])` returns float

### P-002: runner.py direct metric call bypasses _METRIC_REGISTRY
**Symptom**: `assert 0.95 == 1.0` — mock returns 1.0 (real value) instead of mocked 0.95
**Cause**: `runner.py` calls `metrics.bleu()` / `metrics.rouge_l()` directly, NOT through registry
**Fix**: Replace `metrics.X(predictions, targets)` with `get_registered_metric("X")(preds=predictions, targets=targets)`
**Verification**: `monkeypatch.setitem(_METRIC_REGISTRY, "bleu", mock)` → `run_evaluation()` uses mock

### P-003: CLI probe-json blocked by sys.exit() guard
**Symptom**: `test_probe_json_with_hydra_missing` → `proc.returncode == 2`, not 0
**Cause**: `main()` calls `sys.exit(2)` on hydra-missing BEFORE parsing `--probe-json`
**Fix**: Pre-parse `--probe-json` with a minimal argparse, handle it, THEN do the hydra check
**Verification**: Run script with `sys.modules['hydra']=None` → returncode 0, valid JSON on stdout

### P-004: Class attribute accessed as direct property but stored in sub-object
**Symptom**: `AttributeError: 'Engine' object has no attribute 'impact_weight'`
**Cause**: `engine.weights.impact_weight` exists but test accesses `engine.impact_weight`
**Fix**: Add `@property def impact_weight(self): return self.weights.impact_weight`
**Verification**: `engine = Engine(); print(engine.impact_weight)` → float value

## Codebase Alignment Diagram

```
Test code                    Registry layer            Function def
──────────                   ──────────────            ────────────
metric(preds=["x"])         get_metric("rougeL")      def rouge_l(
                            → _METRIC_REGISTRY?            preds: Sequence[object],  ← MUST match
                            → metric_registry.get()        targets: Sequence[object]
                            → registry._items["rougel"]    ) -> float:
                            .value → rouge_l function

Runner code                  Registry layer            Mock seam
───────────                  ──────────────            ─────────
get_registered_metric("X")  get(name)                 _METRIC_REGISTRY = {}
→ _METRIC_REGISTRY["X"]?    → if name in _METRIC...   monkeypatch.setitem(
→ metric_registry.get("X")    return _METRIC_REGISTRY    registry._METRIC_REGISTRY,
                              [name]  ← mock seam        "rouge_l", mock_fn)
                            → _items[normalize(name)]
                              .value → real fn
```

## Files Typically Modified
- `src/codex_ml/metrics/generative.py` — parameter names
- `src/codex_ml/eval/runner.py` — metric lookup path
- `src/codex_ml/cli/hydra_main.py` — pre-check patterns
- `tests/*/test_adaptive_scoring*.py` — missing property patterns
- `tests/conftest.py` — xfail/preexisting failure registration

## Self-Healing Loop
```
ITERATION 1: Fix parameter name
ITERATION 2: Fix call-site to use registry (not direct module call)
ITERATION 3: Verify mock seam works
ITERATION 4: Run targeted test locally
ITERATION 5: If pass → commit; if fail → diagnose with inspect.signature()
```

## Success Criteria
- `get_metric("X")(preds=..., targets=...)` → no TypeError
- `monkeypatch.setitem(_METRIC_REGISTRY, "X", mock)` → runner uses mock (not real fn)
- All previously failing tests PASS
- No new regressions introduced

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
