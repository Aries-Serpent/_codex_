# Post-Merge Copilot Setup Validation Checklist

**Created**: 2026-06-25T22:20:00Z  
**Purpose**: Validate copilot-setup-steps.yml functionality immediately post-merge  
**Trigger**: Automatic on post-merge session start  
**Owner**: Copilot agent (post-merge session)

---

## Validation Philosophy

This checklist is NOT about fixing issues. It is about:
1. **Detecting regressions** - Did the merge break copilot-setup-steps.yml?
2. **Capturing baseline** - What is the post-merge environment state?
3. **Decision making** - Should we revert or proceed?

See `.codex/POST_MERGE_REVERSION_PROTOCOL.md` for reversion triggers.

---

## Pre-Validation Setup

### Checkpoint: Before Any Other Work
This validation MUST run before:
- Creating new files
- Making code changes
- Installing additional packages
- Running tests

### Required Files
- `.github/workflows/copilot-setup-steps.yml` (validate syntax)
- `.codex/AGENTIC_REPO_STATE.md` (verify post-merge state)
- `pyproject.toml` (verify Python version requirement)
- `requirements/dev.txt` (verify optional deps)

---

## Validation Checklist

### ✓ Section 1: YAML Syntax Validation

**Purpose**: Ensure workflow file is valid YAML  
**Command**: 
```bash
yamllint .github/workflows/copilot-setup-steps.yml
```

**Expected Result**: 
- Exit code `0` (no errors)
- No output or warnings only

**Failure Action**:
- If `ERROR`: Revert (Category A - YAML parse error)
- If warnings only: Proceed to next check

**Pass Indication**: 
```
.github/workflows/copilot-setup-steps.yml
  39:81     warning  line too long (103 > 100 characters)
```
(Warnings are acceptable)

---

### ✓ Section 2: Copilot-Setup-Steps Job Recognition

**Purpose**: Verify GitHub Copilot will recognize the workflow job  
**Check**: 
```bash
grep "jobs:" .github/workflows/copilot-setup-steps.yml | head -5
```

**Expected Output**: Contains job definition block

**Critical Requirement**: Job MUST be named `copilot-setup-steps` for GitHub Copilot recognition  
**Verify**:
```bash
grep -A 2 "^jobs:" .github/workflows/copilot-setup-steps.yml
```

**Expected**: 
```yaml
jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
```

**Failure Action**: If job name is wrong → Revert

---

### ✓ Section 3: Session Preload Step Integrity

**Purpose**: Validate lines 132-170 (session preload) use correct syntax  
**Critical**: This step must use block scalar `run: |`, NOT flow scalar

**Check 1: Block Scalar Syntax**
```bash
sed -n '132,140p' .github/workflows/copilot-setup-steps.yml | grep "run: |"
```

**Expected**: Line contains `run: |`

**Failure Action**: If `run:` without pipe, or flow scalar `run: ||` → Revert

**Check 2: No Hard-Failing Exit**
```bash
sed -n '132,170p' .github/workflows/copilot-setup-steps.yml | grep -c "exit 1"
```

**Expected**: 0 (no hard exit statements that would fail the job)

**Failure Action**: If exit 1 found → Revert

**Check 3: If-Then Syntax Validity**
```bash
sed -n '137,139p' .github/workflows/copilot-setup-steps.yml | grep -E "if !|then|fi"
```

**Expected**: Safe shell syntax (brace-free `if ! ...; then ...; fi`)

**Failure Action**: If brace syntax found → Revert

---

### ✓ Section 4: Environment Variables

**Purpose**: Verify CCA version lock and deduplication vars are present  
**Location**: Lines 99-101 in workflow

**Check 1: Version Lock**
```bash
grep "COPILOT_AGENT_CCA_VERSION_LOCK" .github/workflows/copilot-setup-steps.yml
```

**Expected**: `COPILOT_AGENT_CCA_VERSION_LOCK: "stable"`

**Check 2: Deduplication**
```bash
grep "COPILOT_AGENT_DEDUPLICATION_ENABLED" .github/workflows/copilot-setup-steps.yml
```

**Expected**: `COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"`

**Check 3: Turn Isolation**
```bash
grep "COPILOT_AGENT_TURN_ISOLATION_ENABLED" .github/workflows/copilot-setup-steps.yml
```

**Expected**: `COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"`

**Failure Action**: If any missing or set to `"false"` → Revert

---

### ✓ Section 5: Python Version Requirement

**Purpose**: Verify Python >=3.12 is enforced

**Check 1: pyproject.toml**
```bash
grep "requires-python" /home/runner/work/_codex_/_codex_/pyproject.toml
```

**Expected**: `requires-python = ">=3.12"`

**Check 2: Current Python**
```bash
python3 --version
```

**Expected**: Python 3.12.x or higher

**Failure Action**: If <3.12 → Escalate (environment issue, not reversion trigger)

---

### ✓ Section 6: LFS Configuration

**Purpose**: Verify LFS opt-in defaults are preserved

**Check**: 
```bash
grep "GIT_LFS_SKIP_SMUDGE" .github/workflows/copilot-setup-steps.yml
```

**Expected**: `GIT_LFS_SKIP_SMUDGE: "1"` (default opt-in behavior)

**Purpose**: LFS should NOT be fetched by default, only on explicit workflow_dispatch targets

**Failure Action**: If missing → Revert

---

### ✓ Section 7: Secret Injection Setup

**Purpose**: Verify secrets are properly declared for injection

**Check**: 
```bash
grep -E "CODEX_MASTER_KEY|CODEX_BACKUP_KEY" .github/workflows/copilot-setup-steps.yml
```

**Expected**: Both secrets referenced in env block

**Note**: Secret values are NOT validated here (that's external GitHub configuration). We only verify they're declared.

**Failure Action**: If declarations missing → Revert

---

## Post-Validation Actions

### All Checks Pass ✅
```
Outcome: Copilot-setup-steps.yml is valid and post-merge-compatible
Action:
  1. Log: "✅ copilot-setup-steps.yml validation passed"
  2. Create: .codex/POST_MERGE_VALIDATION_CHECKLIST_PASSED.txt
  3. Proceed to test collection validation
```

### Any Check Fails ❌
```
Outcome: Critical failure detected
Action:
  1. Document failure in .codex/REVERSION_FAILURE_SNAPSHOT.txt
  2. Create root cause analysis: .codex/REVERSION_ROOT_CAUSE.md
  3. Follow reversion protocol: .codex/POST_MERGE_REVERSION_PROTOCOL.md
  4. Create escalation issue
  5. STOP — wait for @mbaetiong approval
```

---

## Validation Commands (Automated)

Run this script to execute all checks:

```bash
#!/bin/bash
set -e

echo "=== Post-Merge Copilot Setup Validation ==="

# Check 1: YAML syntax
if ! yamllint .github/workflows/copilot-setup-steps.yml; then
  echo "❌ YAML syntax error - REVERT REQUIRED"
  exit 1
fi

# Check 2: Job name
if ! grep -q "^\s*copilot-setup-steps:" .github/workflows/copilot-setup-steps.yml; then
  echo "❌ Job name not 'copilot-setup-steps' - REVERT REQUIRED"
  exit 1
fi

# Check 3: Block scalar syntax
if ! sed -n '132,140p' .github/workflows/copilot-setup-steps.yml | grep -q "run: |"; then
  echo "❌ Session preload not using block scalar - REVERT REQUIRED"
  exit 1
fi

# Check 4-6: Environment variables
for var in COPILOT_AGENT_CCA_VERSION_LOCK COPILOT_AGENT_DEDUPLICATION_ENABLED COPILOT_AGENT_TURN_ISOLATION_ENABLED; do
  if ! grep -q "$var" .github/workflows/copilot-setup-steps.yml; then
    echo "❌ Missing env var: $var - REVERT REQUIRED"
    exit 1
  fi
done

# Check 7: Python version
if ! python3 --version | grep -q "3.12\|3.13"; then
  echo "⚠️ Python version issue - escalate (not automatic revert)"
fi

# Check 8: LFS configuration
if ! grep -q "GIT_LFS_SKIP_SMUDGE" .github/workflows/copilot-setup-steps.yml; then
  echo "❌ LFS opt-in not configured - REVERT REQUIRED"
  exit 1
fi

echo "✅ All checks passed"
touch .codex/POST_MERGE_VALIDATION_CHECKLIST_PASSED.txt
```

---

## Integration with Other Validations

After this checklist passes:
1. Run test collection validation: `.codex/POST_MERGE_ENVIRONMENT_BASELINE.md`
2. Document baseline: `pytest --collect-only`
3. If collection has pre-existing errors: Document in accountability report
4. Proceed to post-merge work

If this checklist fails:
1. Do NOT proceed
2. Follow reversion protocol
3. Escalate to @mbaetiong
