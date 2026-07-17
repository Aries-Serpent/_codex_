# Workflow Remediation Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

## Critical Workflows - Detailed Fix Instructions


## copilot-setup-steps.yml
**Risk Level**:  CRITICAL

### Issues Found

**PUSH Trigger Filter:**
- `.github/workflows/copilot-setup-steps.yml`
- `.codex/agent_environment_config.yaml`
- `pyproject.toml`
- `requirements*.txt`

**PULL_REQUEST Trigger Filter:**
- `.github/workflows/copilot-setup-steps.yml`
- `.codex/agent_environment_config.yaml`

### Remediation Steps

1. **Update trigger paths:**
   ```yaml
   on:
     push:
       paths:
         - 'pyproject.toml'         # Repository root location
         - '.github/workflows/**'   # Keep as-is
         - '.codex/**'              # Keep as-is
   ```

2. **Update environment setup references:**
   - Search for any hardcoded references to `pyproject.toml`
   - Maintain references to the repository root location

3. **Test:**
   ```bash
   # Verify trigger works on changes to new config location
   # Manually dispatch workflow to test
   ```

4. **Validation:**
   -  Workflow triggers on .codex/ changes
   -  Workflow triggers on pyproject.toml changes
   -  Setup steps execute correctly

## required-actions-enforcer.yml
**Risk Level**:  CRITICAL

### Issues Found

**PUSH Trigger Filter:**
- `.github/workflows/**`
- `.github/misc/**`
- `scripts/ci/enforce_actions_versions.py`

**PULL_REQUEST Trigger Filter:**
- `.github/workflows/**`
- `.github/misc/**`

### Remediation Steps

1. **Update trigger paths:**
   ```yaml
   on:
     push:
       paths:
         - '.github/workflows/**'  # Ensure correct trigger
   ```

2. **Verify enforcement logic:**
   - Confirm workflow correctly validates required actions
   - No code changes needed if enforcement logic is generic

3. **Test:**
   ```bash
   # Trigger on workflow file changes
   # Verify enforcement runs
   ```

4. **Validation:**
   -  Workflow triggers on workflow file changes
   -  Enforcement validation executes

## resilient_validation.yml
**Risk Level**:  CRITICAL

### Issues Found

**PULL_REQUEST Trigger Filter:**
- `docs/**`
- `tests/**`
- `.codex/**`
- `src/**`
- `scripts/**`

### Remediation Steps

1. **Update trigger paths:**
   ```yaml
   on:
     push:
       paths:
         - 'tests/**'         # Keep test directory reference
         - '.codex/**'        # Keep CI infrastructure reference
         - 'src/**'           # Update to source if needed
   ```

2. **Update artifact references:**
   - Search for `coverage.json` references
   - Verify artifact upload paths are correct
   - Update download paths if needed

3. **Verify validation scripts:**
   - Ensure validation logic works with new file locations
   - Check environment variable references

4. **Test:**
   ```bash
   # Run validation on test changes
   # Verify coverage artifact uploads
   # Check artifact downloads in dependent workflows
   ```

5. **Validation:**
   -  Workflow triggers on test/codex changes
   -  Validation runs successfully
   -  Coverage artifacts upload correctly

## test-rag.yml
**Risk Level**:  CRITICAL

### Issues Found

**PUSH Trigger Filter:**
- `.github/actions/setup-python-cached/**`
- `.github/workflows/test-rag.yml`
- `src/codex/rag/**`
- `tests/test_rag_**`
- `pyproject.toml`

**PULL_REQUEST Trigger Filter:**
- `.github/actions/setup-python-cached/**`
- `.github/workflows/test-rag.yml`
- `src/codex/rag/**`
- `tests/test_rag_**`
- `pyproject.toml`

### Remediation Steps

1. **Update trigger paths:**
   ```yaml
   on:
     push:
       paths:
         - 'pyproject.toml'         # Repository root location
         - '.github/workflows/**'   # Keep as-is
         - 'tests/**'               # Keep as-is
   ```

2. **Update configuration references:**
   - Search for `pyproject.toml` in run commands
   - Maintain references to root location
   - Most tools auto-discover from cwd (no change needed)

3. **Update setup steps:**
   - Check environment setup commands
   - Verify Python version and dependency setup

4. **Test:**
   ```bash
   # Trigger on pyproject.toml changes
   # Trigger on test file changes
   # Verify RAG tests execute
   ```

5. **Validation:**
   -  Workflow triggers correctly
   -  Environment setup works
   -  RAG tests pass
   -  No import/config errors
