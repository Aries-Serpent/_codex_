# Environment Variable Automation System

**Complete automation for managing GitHub environment variables from source code files.**

## Overview

This system automatically converts eligible Python files into base64-encoded GitHub environment variables and maintains synchronization between source files and deployed variables.

### Components

1. **env_var_converter.py** - Core converter and sync tool
2. **sync-env-vars.yml** - GitHub Actions workflow for automation
3. **pre-commit-env-check.sh** - Pre-commit hook for size validation
4. **env_var_metadata.json** - Tracking file for sync state

## Quick Start

### 1. List Candidates

```bash
python3 .github/scripts/env_var_converter.py --mode list-candidates
```

**Output:**
```
GITHUB ENVIRONMENT VARIABLE CANDIDATES
====================================================================================================

1. COGNITIVE_BRAIN_GHZ_STATES
   File: src/cognitive_brain/quantum/ghz_states.py
   Priority: 1 (⭐)
   Category: cognitive_brain
   Auto-sync: ✅ Yes
   Description: Multi-agent GHZ state management
   Size: 13,603 bytes → 18,140 bytes (base64)
   Env usage: 36.9% of 48KB
   Fits: ✅ YES (30,012 bytes headroom)
   Sync status: 🔄 NEVER SYNCED

...
```

### 2. Encode Single File

```bash
python3 .github/scripts/env_var_converter.py \
  --mode encode \
  --file src/cognitive_brain/quantum/ghz_states.py
```

**Output:**
```
ENCODING COMPLETE
====================================================================================================
Environment Variable: COGNITIVE_BRAIN_GHZ_STATES
Original Size: 13,603 bytes
Encoded Size: 18,140 bytes
Usage: 36.9% of 48KB
SHA256: a1b2c3d4...
Git Commit: abc123de

Encoded value (copy to GitHub):
----------------------------------------------------------------------------------------------------
IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiIKR0haIFN0YXRlIE1hbmFnZXIKCkdyZWV...
----------------------------------------------------------------------------------------------------
```

### 3. Dry Run Sync

```bash
python3 .github/scripts/env_var_converter.py \
  --mode sync \
  --environment production \
  --dry-run
```

**Output:**
```
🔍 DRY RUN: Syncing to environment: production
====================================================================================================

Processing: COGNITIVE_BRAIN_GHZ_STATES
  🔄 Needs update: File content has changed (hash mismatch)
  📦 Encoded: 13,603 → 18,140 bytes
  📊 Usage: 36.9% of 48KB
  🔍 Would sync to GitHub (dry run)

...

SYNC SUMMARY
====================================================================================================
Synced: 3
Skipped: 1
Failed: 0

🔍 This was a dry run. Use --no-dry-run to actually sync.
```

### 4. Actual Sync

```bash
python3 .github/scripts/env_var_converter.py \
  --mode sync \
  --environment production \
  --no-dry-run
```

**Output:**
```
Syncing to environment: production
====================================================================================================

Processing: COGNITIVE_BRAIN_GHZ_STATES
  🔄 Needs update: File content has changed (hash mismatch)
  📦 Encoded: 13,603 → 18,140 bytes
  📊 Usage: 36.9% of 48KB
  ✅ Synced to GitHub

...

SYNC SUMMARY
====================================================================================================
Synced: 3
Skipped: 1
Failed: 0
```

### 5. Verify Sync Status

```bash
python3 .github/scripts/env_var_converter.py \
  --mode verify \
  --all
```

**Output:**
```
VERIFICATION REPORT
====================================================================================================

📊 SUMMARY:
  Up to date: 3
  Needs sync: 0
  Never synced: 1

✅ UP TO DATE:
  • COGNITIVE_BRAIN_GHZ_STATES
    File: src/cognitive_brain/quantum/ghz_states.py
    Last synced: Current Cycle-01-02T19:30:15.123456
    Git commit: abc123de

  • COGNITIVE_BRAIN_COORDINATOR
    File: src/cognitive_brain/quantum/multi_agent_coordinator.py
    Last synced: Current Cycle-01-02T19:30:18.654321
    Git commit: abc123de

  • COGNITIVE_BRAIN_TOPOLOGY
    File: src/cognitive_brain/quantum/topology_manager.py
    Last synced: Current Cycle-01-02T19:30:21.987654
    Git commit: abc123de

🔄 NEVER SYNCED:
  • CODEX_ML_CONFIG
    File: src/codex_ml/config/__init__.py
```

## Automated Workflows

### GitHub Actions Workflow

**Triggers:**
- Push to `main` branch → Sync to production (actual)
- Push to `develop` branch → Sync to staging (actual)
- Push to other branches → Dry run only
- Manual dispatch → User selects environment and mode

**Workflow File:** `.github/workflows/sync-env-vars.yml`

**Workflow Steps:**
1. Checkout repository (full history)
2. Setup Python 3.11
3. Install GitHub CLI
4. Authenticate with GitHub
5. Determine target environment
6. List candidates (before sync)
7. Verify current state
8. Sync environment variables
9. Verify sync (after)
10. Upload metadata artifact
11. Create summary

**Manual Trigger:**
```bash
# Via GitHub UI
Actions → Sync Environment Variables → Run workflow
  Environment: production/staging/development
  Dry run: true/false

# Via GitHub CLI
gh workflow run sync-env-vars.yml \
  -f environment=production \
  -f dry_run=false
```

### Pre-commit Hook

**Installation:**
```bash
# Option 1: Symlink
ln -s ../../.github/scripts/pre-commit-env-check.sh .git/hooks/pre-commit

# Option 2: Copy
cp .github/scripts/pre-commit-env-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Option 3: Use pre-commit framework
# Add to .pre-commit-config.yaml:
repos:
  - repo: local
    hooks:
      - id: env-var-size-check
        name: Check environment variable file sizes
        entry: .github/scripts/pre-commit-env-check.sh
        language: script
        pass_filenames: false
```

**What It Does:**
- Checks size of candidate files being committed
- Warns if file > 30KB (approaching limit)
- Blocks commit if file > 36KB (exceeds limit)
- Provides remediation options

**Output Example:**
```bash
$ git commit -m "Update GHZ states"

🔍 Checking environment variable candidate files...

📄 src/cognitive_brain/quantum/ghz_states.py
   Original: 13603 bytes
   Base64: ~18133 bytes
   Usage: 36.9% of 48KB
   ✅ OK

📄 src/codex_ml/config/__init__.py
   Original: 33679 bytes
   Base64: ~44893 bytes
   Usage: 91.3% of 48KB
   ⚠️  WARNING: File is getting large (>30KB)
   Monitor size carefully. Close to 36KB limit.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  1 file(s) approaching size limits
Consider monitoring these files carefully.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[main abc123de] Update GHZ states
 1 file changed, 10 insertions(+), 5 deletions(-)
```

## Configuration

### Candidate Files

**File:** `.github/scripts/env_var_converter.py`

**Configuration:**
```python
CANDIDATES_CONFIG = [
    {
        "path": "src/cognitive_brain/quantum/ghz_states.py",
        "env_var": "COGNITIVE_BRAIN_GHZ_STATES",
        "priority": 1,
        "description": "Multi-agent GHZ state management",
        "category": "cognitive_brain",
        "auto_sync": True,
    },
    # ... more candidates
]
```

**Fields:**
- `path` - Relative path from repo root
- `env_var` - GitHub environment variable name
- `priority` - 1 (high), 2 (medium), 3 (low)
- `description` - Human-readable description
- `category` - Grouping category
- `auto_sync` - Enable automatic syncing (True/False)

### Adding New Candidates

1. **Add to configuration:**
```python
{
    "path": "src/new/module.py",
    "env_var": "NEW_MODULE",
    "priority": 2,
    "description": "New module description",
    "category": "category_name",
    "auto_sync": True,
}
```

2. **Update workflow triggers:**
```yaml
# .github/workflows/sync-env-vars.yml
on:
  push:
    paths:
      - 'src/new/module.py'  # Add this line
```

3. **Test:**
```bash
# List candidates
python3 .github/scripts/env_var_converter.py --mode list-candidates

# Dry run
python3 .github/scripts/env_var_converter.py --mode sync --dry-run

# Actual sync
python3 .github/scripts/env_var_converter.py --mode sync --no-dry-run
```

## Metadata Tracking

**File:** `.github/scripts/env_var_metadata.json`

**Format:**
```json
{
  "COGNITIVE_BRAIN_GHZ_STATES": {
    "env_var": "COGNITIVE_BRAIN_GHZ_STATES",
    "file_path": "src/cognitive_brain/quantum/ghz_states.py",
    "original_size": 13603,
    "encoded_size": 18140,
    "sha256": "a1b2c3d4e5f6...",
    "last_updated": "Current Cycle-01-02T19:30:15.123456",
    "git_commit": "abc123de",
    "version": "v1.2.3",
    "priority": 1,
    "category": "cognitive_brain",
    "auto_sync": true
  }
}
```

**Purpose:**
- Track sync state
- Detect file changes via SHA256
- Store metadata for auditing
- Enable verification and rollback

**Artifact Storage:**
- Uploaded to GitHub Actions artifacts
- 90-day retention
- Downloadable for debugging

## Usage in Code

### Decode from Environment

```python
import os
import base64
import tempfile
import sys
import importlib.util

def load_from_env(env_var_name: str):
    """Load Python module from environment variable."""
    # Get encoded content
    encoded = os.environ[env_var_name]
    
    # Decode
    code = base64.b64decode(encoded).decode('utf-8')
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False
    ) as f:
        f.write(code)
        temp_path = f.name
    
    # Import module
    module_name = env_var_name.lower()
    spec = importlib.util.spec_from_file_location(module_name, temp_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

# Usage
ghz = load_from_env('COGNITIVE_BRAIN_GHZ_STATES')
manager = ghz.GHZStateManager(num_agents=4)
```

### Production Example

```python
# app.py - Serverless function
import os
import base64

# Check if running in env-var mode
if 'COGNITIVE_BRAIN_GHZ_STATES' in os.environ:
    # Load from environment
    ghz_module = load_from_env('COGNITIVE_BRAIN_GHZ_STATES')
    print("✅ Loaded GHZ states from environment variable")
else:
    # Load from file system
    from cognitive_brain.quantum import ghz_states as ghz_module
    print("✅ Loaded GHZ states from file system")

# Use module normally
manager = ghz_module.GHZStateManager(num_agents=4)
state = manager.create_ghz_state()
```

## Troubleshooting

### Issue: File too large

**Error:**
```
ValueError: File too large: 40,000 bytes (max: 36,956 bytes after base64 encoding)
```

**Solutions:**
1. Split file into smaller modules
2. Remove unused code/comments
3. Extract constants to separate file
4. Disable auto_sync and manage manually

### Issue: Sync fails

**Error:**
```
❌ Failed: subprocess.CalledProcessError: gh api returned 404
```

**Solutions:**
1. Check GitHub CLI authentication:
   ```bash
   gh auth status
   gh auth login
   ```

2. Verify environment exists:
   ```bash
   gh api repos/:owner/:repo/environments
   ```

3. Create environment if missing:
   ```bash
   gh api repos/:owner/:repo/environments/production -X PUT
   ```

### Issue: Hash mismatch

**Symptom:**
```
⚠️  Needs update: File content has changed (hash mismatch)
```

**Explanation:** Source file has been modified since last sync.

**Solution:**
```bash
# Re-sync the file
python3 .github/scripts/env_var_converter.py --mode sync --no-dry-run
```

### Issue: Workflow fails

**Check workflow logs:**
```bash
gh run list --workflow=sync-env-vars.yml
gh run view <run-id> --log
```

**Common fixes:**
1. Verify file paths in CANDIDATES_CONFIG
2. Check Python version (requires 3.11+)
3. Ensure GitHub CLI is installed
4. Verify GH_TOKEN permissions

## Best Practices

### 1. Monitor File Sizes

```bash
# Check all candidates
python3 .github/scripts/env_var_converter.py --mode list-candidates | grep "Size:"

# Set up CI check
- name: Check file sizes
  run: |
    python3 .github/scripts/env_var_converter.py --mode list-candidates | \
      grep -E "(TOO LARGE|WARNING)"
    if [ $? -eq 0 ]; then
      echo "⚠️  Files approaching or exceeding size limits"
      exit 1
    fi
```

### 2. Version Control Metadata

```bash
# Commit metadata.json to track sync state
git add .github/scripts/env_var_metadata.json
git commit -m "Update env var metadata [skip ci]"
```

### 3. Test Before Production

```bash
# Always dry run first
python3 .github/scripts/env_var_converter.py \
  --mode sync \
  --environment staging \
  --dry-run

# Then actual sync to staging
python3 .github/scripts/env_var_converter.py \
  --mode sync \
  --environment staging \
  --no-dry-run

# Test in staging environment
# ...

# Finally sync to production
python3 .github/scripts/env_var_converter.py \
  --mode sync \
  --environment production \
  --no-dry-run
```

### 4. Document Versions

```bash
# Use git tags for versions
git tag -a v1.2.3 -m "GHZ states update"
git push origin v1.2.3

# Converter automatically includes version in metadata
python3 .github/scripts/env_var_converter.py --mode encode --file ...
# Output includes: Version: v1.2.3
```

### 5. Audit Regularly

```bash
# Weekly verification
python3 .github/scripts/env_var_converter.py --mode verify --all

# Check for drift
git diff .github/scripts/env_var_metadata.json

# Review GitHub environment history
gh api repos/:owner/:repo/environments/production/variables
```

## Security Considerations

### 1. Encryption Layer (Optional)

```python
# Add encryption before base64
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt code
with open(file_path, 'rb') as f:
    code = f.read()
encrypted = cipher.encrypt(code)
encoded = base64.b64encode(encrypted).decode()

# Store key in separate GitHub secret
# Use ENCRYPTION_KEY environment variable
```

### 2. Access Control

```yaml
# Restrict environment access
# Settings → Environments → production → Deployment branches
# Only allow: main branch

# Required reviewers
# Settings → Environments → production → Required reviewers
# Add: @reviewer1, @reviewer2
```

### 3. Audit Trail

```bash
# View environment variable changes
gh api repos/:owner/:repo/environments/production/variables | jq .

# Download all metadata artifacts
gh run list --workflow=sync-env-vars.yml --json databaseId --limit 100 | \
  jq -r '.[].databaseId' | \
  xargs -I {} gh run download {} --name env-var-metadata
```

## Performance Optimization

### 1. Parallel Encoding

```python
# Modify converter to use ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(encode_file, file_path)
        for file_path in candidate_files
    ]
    results = [f.result() for f in futures]
```

### 2. Caching

```bash
# Cache metadata between workflow runs
- name: Cache metadata
  uses: actions/cache@v4
  with:
    path: .github/scripts/env_var_metadata.json
    key: env-var-metadata-${{ hashFiles('src/cognitive_brain/**/*.py') }}
```

### 3. Incremental Sync

```bash
# Only sync changed files (default behavior)
python3 .github/scripts/env_var_converter.py --mode sync --no-dry-run
# Uses SHA256 hash to detect changes
```

## Future Enhancements

### Planned Features

1. **Compression:** Add gzip compression before base64 (50%+ size reduction)
2. **Splitting:** Automatically split large files across multiple env vars
3. **Rollback:** Restore previous version from metadata
4. **Web UI:** Dashboard for managing env vars
5. **Notifications:** Slack/email alerts on sync failures
6. **Multi-repo:** Sync across multiple repositories

### Contribution

To add new features:

1. Fork repository
2. Create feature branch
3. Implement feature in `env_var_converter.py`
4. Add tests
5. Update documentation
6. Submit PR

---

**Last Updated:** Current Cycle-01-02  
**Version:** 1.0  
**Maintainer:** Cognitive Brain Team
