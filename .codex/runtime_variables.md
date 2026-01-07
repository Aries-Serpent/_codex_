# Runtime Variables Documentation

**Generated:** 2025-12-26  
**Purpose:** Central documentation for all operational variables used across the _codex_ repository  
**Audience:** Developers, CI/CD systems, and autonomous agents

---

## Overview

This document catalogs all environment variables, workflow variables, and configuration parameters used throughout the repository. Variables are organized by category and usage context.

---

## Workflow Variables (Proposed)

These standardized variables should be used across GitHub Actions workflows to ensure consistency:

| Variable | Value | Purpose | Usage Context |
|----------|-------|---------|---------------|
| `CODEX_PYTHON_VERSION` | `3.12` | Standardize Python version across workflows | GitHub Actions, Docker builds |
| `CODEX_CACHE_VERSION` | `v2` | Cache busting identifier for dependency caches | CI/CD pipelines |
| `CODEX_TEST_PARALLELISM` | `auto` | Pytest parallel execution mode | Test workflows |
| `CODEX_COVERAGE_THRESHOLD` | `80` | Minimum test coverage percentage gate | Coverage reporting |
| `CODEX_LINT_STRICT` | `true` | Enable strict linting mode | Pre-commit, CI linting |

### Implementation Notes

These variables can be:
1. Set as repository-level variables in GitHub Settings → Secrets and variables → Variables
2. Defined in workflow `env:` blocks for consistency
3. Referenced in multiple workflows using `${{ vars.VARIABLE_NAME }}` or `${{ env.VARIABLE_NAME }}`

### Example Workflow Usage

```yaml
env:
  CODEX_PYTHON_VERSION: "3.12"
  CODEX_CACHE_VERSION: "v2"
  CODEX_TEST_PARALLELISM: "auto"
  CODEX_COVERAGE_THRESHOLD: "80"
  CODEX_LINT_STRICT: "true"

jobs:
  test:
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ env.CODEX_PYTHON_VERSION }}
```

---

## Environment Variables (Existing)

### Session and Logging

| Variable | Default | Purpose | Reference |
|----------|---------|---------|-----------|
| `CODEX_SESSION_ID` | auto-generated | Identifier for a logical session; groups log events | AGENTS.md |
| `CODEX_SESSION_LOG_DIR` | `.codex/sessions` | Directory for session log files | AGENTS.md |
| `CODEX_LOG_DB_PATH` | `.codex/session_logs.db` | Path to SQLite database for logging | AGENTS.md |
| `CODEX_DB_PATH` | `data/codex.db` | Alternative path to SQLite database | AGENTS.md |
| `CODEX_SQLITE_POOL` | `0` | Set to `1` to enable per-session SQLite connection pooling | AGENTS.md |

### Language Version Selection

| Variable | Default | Purpose | Reference |
|----------|---------|---------|-----------|
| `CODEX_ENV_PYTHON_VERSION` | `3.11` | Select Python version during environment setup | AGENTS.md |
| `CODEX_ENV_NODE_VERSION` | (none) | Select Node.js version during environment setup | AGENTS.md |
| `CODEX_ENV_RUST_VERSION` | (none) | Select Rust version during environment setup | AGENTS.md |
| `CODEX_ENV_GO_VERSION` | (none) | Select Go version during environment setup | AGENTS.md |
| `CODEX_ENV_SWIFT_VERSION` | (none) | Select Swift version during environment setup | AGENTS.md |

### API and Security

| Variable | Default | Purpose | Reference |
|----------|---------|---------|-----------|
| `CODEX_API_KEY` | (required) | API key for Codex API authentication | services/api/main.py |
| `CODEX_MASTER_KEY` | (secret) | Primary authentication token (Fine-grained PAT) | .codex/guardrails.md |
| `CODEX_WEBHOOK_SECRET` | (secret) | Webhook signature verification secret | .codex/guardrails.md |
| `CODEX_BACKUP_KEY` | (secret) | Fallback authentication token (optional) | .codex/guardrails.md |

### Monitoring and Tracking

| Variable | Default | Purpose | Reference |
|----------|---------|---------|-----------|
| `WANDB_MODE` | `online` | Weights & Biases mode (set to `offline` for local runs) | deploy_codex_pipeline.py |
| `MLFLOW_TRACKING_URI` | (none) | MLflow tracking server URI | deploy_codex_pipeline.py |

### Training and ML

| Variable | Default | Purpose | Reference |
|----------|---------|---------|-----------|
| `HF_HOME` | `~/.cache/huggingface` | Hugging Face cache directory | transformers |
| `TORCH_HOME` | `~/.cache/torch` | PyTorch model cache directory | torch |

---

## Python Package Configuration

Variables affecting Python package behavior:

### Project Metadata

- **Package Name:** `codex-ml` (defined in `pyproject.toml`)
- **Python Version:** `>=3.11` (minimum requirement)
- **Build System:** `setuptools>=67`

### Key Dependencies Version Ranges

From `pyproject.toml`:
- `hydra-core==1.3.2` (exact version)
- `transformers>=4.41,<5`
- `mlflow>=2.4,<4`
- `torch>=2.2.2`
- `peft>=0.11,<1`
- `accelerate>=0.31,<2`

---

## Testing Configuration

### Pytest Configuration

From `pytest.ini`:
- **Test Paths:** `tests/`
- **Markers:** Various including `slow`, `integration`, `gpu`, `requires_network`
- **Plugins:** `pytest-cov`, `pytest-timeout`, `pytest-randomly`

### Coverage Configuration

- **Minimum Coverage:** 80% (proposed in `CODEX_COVERAGE_THRESHOLD`)
- **Coverage Tool:** `pytest-cov` with coverage.py
- **Reports:** `.coverage`, `coverage_reports/`

---

## Linting and Code Quality

### Black Configuration

- **Line Length:** 100 (from `.ruff.toml` and Black settings)
- **Target Version:** Python 3.11+

### Ruff Configuration

From `.ruff.toml`:
- **Line Length:** 100
- **Target Version:** `py311`
- **Selected Rules:** Multiple rule sets including `F` (pyflakes), `E` (pycodestyle errors)

### MyPy Configuration

From `mypy.ini`:
- **Python Version:** 3.11
- **Strict Mode:** Varies by module
- **Baseline:** `.mypy-baseline.txt`

---

## Docker and Container Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DOCKER_BUILDKIT` | Enable BuildKit features | `1` |
| `COMPOSE_DOCKER_CLI_BUILD` | Use Docker CLI for builds | `1` |
| `GPU_OPT` | GPU passthrough flag | `--gpus all` (if nvidia-smi available) |

---

## CI/CD Specific Variables

### GitHub Actions Context Variables

Standard variables available in workflows:
- `GITHUB_WORKSPACE` - Working directory path
- `GITHUB_SHA` - Commit SHA triggering the workflow
- `GITHUB_REF` - Git ref triggering the workflow
- `GITHUB_REPOSITORY` - Repository name (Aries-Serpent/_codex_)
- `RUNNER_OS` - Operating system of the runner

### Custom Workflow Variables

Variables set in specific workflows:
- `NOX_SESSION` - Nox session to execute
- `HYPOTHESIS_PROFILE` - Hypothesis testing profile
- `PYTEST_MARKERS` - Pytest marker filters

---

## Development Environment

### Recommended Environment Variables

For local development, set these in your shell or `.env` file:

```bash
# Python version
export CODEX_ENV_PYTHON_VERSION="3.12"

# Enable SQLite pooling
export CODEX_SQLITE_POOL="1"

# Set session log directory
export CODEX_SESSION_LOG_DIR=".codex/sessions"

# Offline mode for ML tools
export WANDB_MODE="offline"
export TRANSFORMERS_OFFLINE="1"

# Cache directories (optional)
export HF_HOME="$HOME/.cache/huggingface"
export TORCH_HOME="$HOME/.cache/torch"
```

---

## Variable Naming Conventions

All Codex-specific variables follow these conventions:

1. **Prefix:** All variables start with `CODEX_`
2. **Format:** `SCREAMING_SNAKE_CASE`
3. **Structure:** `CODEX_<CATEGORY>_<PURPOSE>`
4. **Examples:**
   - `CODEX_SESSION_ID` - Session management
   - `CODEX_ENV_PYTHON_VERSION` - Environment configuration
   - `CODEX_LOG_DB_PATH` - Logging configuration

---

## Security Considerations

### Secret Variables

**Never commit these to version control:**
- `CODEX_MASTER_KEY`
- `CODEX_WEBHOOK_SECRET`
- `CODEX_BACKUP_KEY`
- `CODEX_API_KEY`

**Storage:**
- Use GitHub Secrets for CI/CD
- Use environment variables or secure vaults locally
- Rotate regularly (every 90 days for tokens)

### Public Variables

Safe to include in configuration files:
- Version numbers
- Cache identifiers
- Threshold values
- Non-sensitive paths

---

## Migration Guide

### Adopting Standardized Variables

To migrate existing workflows to use standardized variables:

1. **Add to repository variables:**
   - Navigate to Settings → Secrets and variables → Variables
   - Add each variable from the "Workflow Variables (Proposed)" section

2. **Update workflow files:**
   ```yaml
   # Before
   python-version: '3.11'
   
   # After
   python-version: ${{ vars.CODEX_PYTHON_VERSION }}
   ```

3. **Update documentation:**
   - Reference this file for variable definitions
   - Document any workflow-specific overrides

4. **Test changes:**
   - Validate workflows in a feature branch
   - Ensure backward compatibility during transition

---

## Troubleshooting

### Common Issues

**Variable not found in workflow:**
- Ensure variable is set at repository level
- Check variable name spelling and case
- Verify workflow has access to repository variables

**SQLite database locking:**
- Set `CODEX_SQLITE_POOL=1` for concurrent access
- Ensure only one writer per database file

**Cache invalidation:**
- Increment `CODEX_CACHE_VERSION` to force rebuild
- Clear local caches: `rm -rf ~/.cache/`

---

## API and CLI Access Limitations

### GitHub API Token Requirements

**Current Status:** ⚠️ Limited API access in automated environments

**Environment Analysis:**
- ✅ Git credentials: Configured and functional via credential helper
- ✅ Repository access: Confirmed (read/write via git operations)
- ✅ GitHub Actions context: Available when running in CI/CD
- ❌ Explicit GitHub API tokens: Not available in all environments
  - `GITHUB_TOKEN`: may not be set in all execution contexts
  - `GH_TOKEN`: Not configured by default
  - `CODEX_MASTER_KEY`: Requires human admin setup

**Impact:**
- GitHub CLI (`gh`) commands Phase 5 fail without explicit token
- Some GitHub API operations require workarounds
- Direct API calls via `curl` require authentication headers

### Workarounds

**For AI Agents:**

1. **Use git commands instead of gh CLI:**
   ```bash
   # ✅ Works: git operations
   git ls-remote --heads origin
   git fetch origin
   git push origin branch-name
   
   # ❌ Phase 5 fail: gh CLI operations
   gh pr view 123
   gh issue create --title "..."
   ```

2. **Use available GitHub Actions context:**
   ```yaml
   # In workflows, use context variables
   - name: Get repo info
     run: |
       echo "Repo: ${{ github.repository }}"
       echo "Actor: ${{ github.actor }}"
       echo "Ref: ${{ github.ref }}"
   ```

3. **Document operations requiring API access:**
   - PR comment creation/updates
   - Issue creation/updates
   - Release management
   - Repository settings changes

**For Human Admins:**

To enable full API access:

1. **Create Personal Access Token:**
   - Navigate to: https://github.com/settings/tokens
   - Generate new token (classic or fine-grained)
   - Required scopes: repo, workflow, read:org

2. **Configure GITHUB_TOKEN:**
   ```bash
   # Local environment
   export GITHUB_TOKEN="your_token_here"
   
   # Verify
   gh auth status
   ```

3. **Add to CI/CD secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Add secret: `GITHUB_TOKEN` or `CODEX_MASTER_KEY`
   - Reference in workflows: `${{ secrets.GITHUB_TOKEN }}`

### Verification Commands

```bash
# Check current authentication
gh auth status

# Test API access
gh api /repos/Aries-Serpent/_codex_

# Check available credentials
git config credential.helper
```

### Related Issues

- See `.codex/phase2_dependency_testing_status.md` for current limitations
- See `.github/workflows/README.md` for workflow authentication
- See `docs/admin/GENESIS_SETUP_GUIDE.md` for token setup

---

## Related Documentation

- **Configuration Management:** `configs/README.md`
- **Agent Guidelines:** `AGENTS.md`
- **Guardrails:** `.codex/guardrails.md`
- **CI/CD Workflows:** `.github/workflows/README.md`
- **Environment Setup:** `docs/getting-started.md`
- **Phase 2 Status:** `.codex/phase2_dependency_testing_status.md`

---

## Maintenance

**Ownership:** Repository maintainers  
**Review Frequency:** Quarterly or when adding new variables  
**Update Process:**
1. Document new variable in appropriate section
2. Update related workflows/code
3. Add migration notes if breaking change
4. Notify team of changes

**Last Updated:** 2025-12-26  
**Next Review:** 2025-03-26
