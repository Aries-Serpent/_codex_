# PyGithub Installation Complete Plan Set
**Version:** 1.0.0  
**Created:** 2026-01-26  
**Purpose:** Ensure PyGithub is properly installed and integrated for artifact monitoring  
**Status:** Ready for Implementation

---

## Executive Summary

PyGithub is currently installed **only in the CI/CD workflow** (`.github/workflows/artifact-monitoring.yml`) but is not tracked as a formal project dependency. This plan ensures PyGithub is properly integrated into the project's dependency management system for both development and production use.

---

## Current State Assessment

### ✅ What's Working
- **Workflow Installation**: PyGithub is installed in `artifact-monitoring.yml`:
  ```yaml
  - name: Install dependencies
    run: |
      python -m pip install --upgrade pip
      pip install PyGithub requests PyYAML
  ```
- **Script Usage**: `scripts/monitoring/artifact_monitor.py` imports and uses PyGithub
- **Workflow Context**: Works correctly when run in GitHub Actions

### ❌ What's Missing
- **Not in pyproject.toml**: PyGithub is not listed in any dependency group
- **Not in requirements.txt**: No formal tracking of this dependency
- **Development Setup**: Developers can't run monitoring scripts locally without manual install
- **Dependency Scanning**: Security scanners may miss PyGithub vulnerabilities

---

## Implementation Plan

### Phase 1: Add PyGithub to Project Dependencies

#### Option A: Add to pyproject.toml (RECOMMENDED)

**Location:** `pyproject.toml` → `[project.optional-dependencies]`

**Create new dependency group:**
```toml
[project.optional-dependencies]
# ... existing groups ...

# GitHub Actions workflow monitoring and automation
github = [
  "PyGithub>=2.1.1,<3.0.0",  # GitHub API client for workflow monitoring
  "requests>=2.32.4",         # Already in main dependencies
  "PyYAML>=6.0",              # Already in main dependencies
]
```

**Rationale:**
- PyGithub 2.1.1+ includes important security and API updates
- Keep as optional dependency since it's only needed for monitoring workflows
- Version constraint `<3.0.0` protects against breaking changes

**Installation command:**
```bash
pip install -e ".[github]"
```

#### Option B: Add to monitoring dependency group (ALTERNATIVE)

**Location:** `pyproject.toml` → `[project.optional-dependencies.monitoring]`

**Update existing monitoring group:**
```toml
monitoring = [
  "prometheus-client>=0.14",
  "psutil>=5.9",
  "pynvml>=11.5",
  "PyGithub>=2.1.1,<3.0.0",  # Add this line
]
```

**Rationale:**
- Groups with other monitoring tools
- Already has monitoring-related dependencies

**Installation command:**
```bash
pip install -e ".[monitoring]"
```

---

### Phase 2: Update Workflow to Use Dependency Group

**File:** `.github/workflows/artifact-monitoring.yml`

**Current:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install PyGithub requests PyYAML
```

**Updated (Option A):**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e ".[github]"
```

**Updated (Option B):**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e ".[monitoring]"
```

---

### Phase 3: Documentation Updates

#### 3.1 Update Script Documentation

**File:** `scripts/monitoring/artifact_monitor.py`

**Update docstring (line 10-17):**
```python
"""
Artifact Monitor - Core monitoring engine for GitHub Actions workflows.

This module provides the main monitoring functionality including:
- GitHub API client for workflow/run/artifact retrieval
- State management for tracking workflow statuses
- Failure detection with configurable thresholds
- Rate limit handling and exponential backoff

Requirements:
    pip install -e ".[github]"  # or pip install PyGithub>=2.1.1

Usage:
    python scripts/monitoring/artifact_monitor.py --check
    python scripts/monitoring/artifact_monitor.py --workflow test-comprehensive.yml
    python scripts/monitoring/artifact_monitor.py --dry-run

Author: Artifact Monitor Agent
Version: 1.0.0
Created: 2026-01-22
"""
```

#### 3.2 Create README for Monitoring Scripts

**File:** `scripts/monitoring/README.md` (create if doesn't exist)

```markdown
# Monitoring Scripts

Automated workflow monitoring and artifact analysis for GitHub Actions.

## Setup

Install monitoring dependencies:

```bash
# Option 1: GitHub monitoring tools only
pip install -e ".[github]"

# Option 2: All monitoring tools (includes Prometheus, psutil, etc.)
pip install -e ".[monitoring]"
```

## Scripts

### artifact_monitor.py

Monitors GitHub Actions workflows and creates issues for failures.

**Requirements:** PyGithub >= 2.1.1

**Usage:**
```bash
# Check all workflows
python scripts/monitoring/artifact_monitor.py

# Check specific workflow
python scripts/monitoring/artifact_monitor.py --workflow test-suite.yml

# Dry run (no issues created)
python scripts/monitoring/artifact_monitor.py --dry-run

# Verbose output
python scripts/monitoring/artifact_monitor.py --verbose
```

**Environment Variables:**
- `GITHUB_TOKEN`: GitHub API token (required)
- `GITHUB_REPOSITORY`: Repository in format `owner/repo` (default: Aries-Serpent/_codex_)

## Configuration

See `.codex/config/monitoring.yaml` for configuration options.
```

#### 3.3 Update Main README

**File:** `README.md`

Add to installation section:
```markdown
### Optional Components

#### GitHub Workflow Monitoring
For monitoring GitHub Actions workflows:
```bash
pip install -e ".[github]"
```

Or install all monitoring tools:
```bash
pip install -e ".[monitoring]"
```
```

---

### Phase 4: Dependency Security Check

Run security scan after adding PyGithub:

```bash
# Using pip-audit
pip-audit -r <(echo "PyGithub>=2.1.1")

# Using safety
safety check --json | jq '.[] | select(.package == "pygithub")'

# Using GitHub Advisory Database
gh api /advisories --method GET -f ecosystem=pip -f package=PyGithub
```

**Expected Result:** PyGithub 2.1.1+ has no known vulnerabilities as of 2026-01-26.

---

### Phase 5: Testing

#### 5.1 Local Testing

**Verify installation:**
```bash
# Install the dependency group
pip install -e ".[github]"

# Verify PyGithub is installed
python -c "import github; print(github.__version__)"

# Expected output: 2.1.1 (or higher)
```

**Test script loading:**
```bash
# Set dummy token for testing config loading
export GITHUB_TOKEN="test_token"

# Test config loading (will fail at GitHub connection, but should load config)
python scripts/monitoring/artifact_monitor.py --help
```

#### 5.2 CI/CD Testing

**Trigger workflow manually:**
```bash
gh workflow run artifact-monitoring.yml -f dry_run=true
```

**Monitor the run:**
```bash
gh run watch
```

**Expected result:** Workflow should complete successfully with PyGithub installed from pyproject.toml.

---

## Prompt Set for AI Agents

### Prompt 1: Add PyGithub to pyproject.toml

```markdown
Add PyGithub to the project dependencies in pyproject.toml.

**Task:**
1. Open /home/runner/work/_codex_/_codex_/pyproject.toml
2. Locate the [project.optional-dependencies] section
3. Add a new dependency group called "github" with:
   - PyGithub>=2.1.1,<3.0.0 (GitHub API client)
   - Include comment explaining it's for workflow monitoring
4. Place it alphabetically after "dist" and before "gpu"

**Example:**
```toml
github = [
  "PyGithub>=2.1.1,<3.0.0",  # GitHub API client for workflow monitoring
]
```

**Validation:**
- Verify TOML syntax is correct
- Ensure version constraints are present
- Check alphabetical ordering
```

### Prompt 2: Update Workflow Installation

```markdown
Update the artifact-monitoring workflow to use the new dependency group.

**Task:**
1. Open /home/runner/work/_codex_/_codex_/.github/workflows/artifact-monitoring.yml
2. Find the "Install dependencies" step (around line 44-47)
3. Replace `pip install PyGithub requests PyYAML` with `pip install -e ".[github]"`

**Before:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install PyGithub requests PyYAML
```

**After:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e ".[github]"
```

**Validation:**
- Verify YAML syntax is correct
- Keep the pip upgrade command
- Ensure editable install flag (-e) is present
```

### Prompt 3: Update Script Documentation

```markdown
Update the artifact_monitor.py script documentation to reference the new installation method.

**Task:**
1. Open /home/runner/work/_codex_/_codex_/scripts/monitoring/artifact_monitor.py
2. Update the module docstring (lines 2-18) to include:
   - Requirements section mentioning `pip install -e ".[github]"`
   - Note about PyGithub version requirement

**Add after line 9:**
```python
Requirements:
    pip install -e ".[github]"  # or pip install PyGithub>=2.1.1
```

**Validation:**
- Maintain existing docstring formatting
- Keep other documentation sections intact
- Verify Python docstring syntax
```

### Prompt 4: Create Monitoring README

```markdown
Create a comprehensive README for the monitoring scripts directory.

**Task:**
1. Create /home/runner/work/_codex_/_codex_/scripts/monitoring/README.md
2. Include sections for:
   - Overview
   - Setup instructions with pip install commands
   - Script descriptions (artifact_monitor.py)
   - Usage examples
   - Configuration reference
   - Environment variables

**Reference:** Use the template provided in Phase 3.2 of the implementation plan.

**Validation:**
- Verify markdown syntax
- Include code blocks with proper language tags
- Test all example commands for accuracy
```

### Prompt 5: Test and Validate

```markdown
Test the PyGithub installation integration.

**Task:**
1. Run the validation script to verify dependency installation:
   ```bash
   pip install -e ".[github]"
   python -c "import github; print(f'PyGithub {github.__version__} installed successfully')"
   ```

2. Verify the monitoring config loads without errors:
   ```bash
   python validate_monitoring_config.py
   ```

3. Check that the workflow file has valid YAML:
   ```bash
   yamllint .github/workflows/artifact-monitoring.yml
   ```

4. Commit all changes with descriptive message

**Validation:**
- All imports succeed
- No YAML syntax errors
- Config validation passes
- Git status shows only intended changes
```

---

## Rollback Plan

If issues occur, rollback by:

1. **Revert pyproject.toml:**
   ```bash
   git checkout HEAD -- pyproject.toml
   ```

2. **Revert workflow:**
   ```bash
   git checkout HEAD -- .github/workflows/artifact-monitoring.yml
   ```

3. **Remove any new files:**
   ```bash
   rm scripts/monitoring/README.md  # if created
   ```

4. **Reinstall original workflow dependencies:**
   - Workflow will fall back to explicit `pip install PyGithub requests PyYAML`

---

## Success Criteria

- [ ] PyGithub added to pyproject.toml under `[project.optional-dependencies]`
- [ ] Workflow updated to use dependency group
- [ ] Documentation updated with installation instructions
- [ ] Security scan shows no vulnerabilities
- [ ] Local installation works: `pip install -e ".[github]"`
- [ ] PyGithub can be imported successfully
- [ ] Monitoring script loads configuration without errors
- [ ] CI/CD workflow completes successfully with new installation method
- [ ] All changes committed and pushed to PR

---

## Additional Considerations

### Version Pinning Strategy

**Current recommendation:** `PyGithub>=2.1.1,<3.0.0`

**Rationale:**
- Minimum 2.1.1 for latest security patches
- Upper bound <3.0.0 prevents breaking changes
- Compatible with Python 3.12+

**Alternative for stricter control:**
```toml
"PyGithub==2.1.1",  # Pin exact version
```

### Dependency Conflicts

**Check for conflicts:**
```bash
pip install -e ".[github]" --dry-run
```

**Known compatible versions:**
- PyGithub 2.1.1+ ✅
- requests 2.32.4+ ✅ (already in main dependencies)
- PyYAML 6.0+ ✅ (already in main dependencies)

### Cross-Platform Considerations

PyGithub is pure Python and works on:
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ macOS
- ✅ Windows

No platform-specific adjustments needed.

---

## Timeline Estimate

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Add to pyproject.toml | 5 minutes | Low |
| Phase 2: Update workflow | 3 minutes | Low |
| Phase 3: Documentation | 15 minutes | Medium |
| Phase 4: Security check | 5 minutes | Low |
| Phase 5: Testing | 10 minutes | Medium |
| **Total** | **~40 minutes** | **Low-Medium** |

---

## Contact & Support

**Questions?**
- Check PyGithub docs: https://pygithub.readthedocs.io/
- GitHub API docs: https://docs.github.com/en/rest
- Repository issues: https://github.com/Aries-Serpent/_codex_/issues

**Maintainer:** @mbaetiong

---

## References

- [PyGithub GitHub Repository](https://github.com/PyGithub/PyGithub)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Python Packaging Guide](https://packaging.python.org/)
- [pyproject.toml Specification](https://peps.python.org/pep-0621/)

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-26  
**Status:** ✅ Ready for Implementation
