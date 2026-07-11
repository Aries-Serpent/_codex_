# Configuration & Setup Master Guide
**Last Updated:** 2026-07-11

> **Consolidated Master Document** for Codex Configuration  
> **Created**: 2026-07-08  
> **Consolidation Campaign**: Phase 12 WS3  
> **Status**:  Active Master Document

**Consolidated from** 6 source files:
- docs/CONSISTENCY_CHECKS_SETUP.md
- docs/setup/NOTEBOOKLM_SETUP.md
- docs/admin/COPILOT_AGENT_ADMIN_SETUP.md
- docs/admin/REPOSITORY_SECURITY_SETUP.md
- docs/MCP_SETUP_GUIDE.md
- docs/LOCAL_DEV_ENV_SETUP.md

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development Setup](#local-development-setup)
3. [MCP Configuration](#mcp-configuration)
4. [Agent Configuration](#agent-configuration)
5. [Repository Security](#repository-security)
6. [Consistency Checks](#consistency-checks)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For Local Development

```bash
# 1. Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Configure local environment
cp .env.example .env
# Edit .env with your settings

# 5. Run setup validation
python scripts/validate_setup.py

# 6. Start development server
python -m codex.cli --help
```

### For Docker

```bash
# 1. Build image
docker build -t codex:latest .

# 2. Run container
docker run -it -v $(pwd):/workspace codex:latest

# 3. Inside container
cd /workspace
python scripts/validate_setup.py
```

---

## Local Development Setup

### Prerequisites

**System Requirements**:
- Python 3.11+ (3.12 recommended)
- Git 2.40+
- 4GB RAM minimum (8GB recommended)
- 10GB disk space

**Required Tools**:
- `pip` (Python package manager)
- `git` (version control)
- `make` (for running tasks)
- `nox` (for test automation)

### Environment Setup

**Step 1: Create Virtual Environment**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

**Step 2: Install Core Dependencies**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Step 3: Install Development Tools**
```bash
pip install -r requirements-dev.txt
pip install -r requirements-test.txt  # for testing
```

**Step 4: Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with:
# - GITHUB_TOKEN
# - OPENAI_API_KEY
# - DATABASE_URL
# - DEBUG=true
```

**Step 5: Initialize Database**
```bash
python scripts/init_db.py
python scripts/migrate_db.py
```

**Step 6: Validate Setup**
```bash
python scripts/validate_setup.py
# Output:  All checks passed
```

### IDE Configuration

**VS Code Settings**:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  }
}
```

**PyCharm Settings**:
```
Settings → Project → Python Interpreter → Add Local
  → Select: ./venv/bin/python
```

---

## MCP Configuration

### What is MCP?

**Model Context Protocol** - A standardized way for AI models to access tools and data.

### Setup MCP Tools

**Step 1: Register MCP Tools**
```yaml
# .codex/mcp_config.yaml
mcp:
  version: 1.0
  tools:
    - name: "bash"
      enabled: true
      
    - name: "grep"
      enabled: true
      
    - name: "view"
      enabled: true
      
    - name: "edit"
      enabled: true
      
    - name: "create"
      enabled: true
```

**Step 2: Initialize MCP Server**
```bash
python scripts/mcp/init_server.py
# Output: MCP server listening on localhost:8765
```

**Step 3: Connect Copilot to MCP**
```bash
# In VS Code Copilot settings
copilot.mcp.endpoints = [
  "http://localhost:8765"
]
```

**Step 4: Test Connection**
```python
import requests

response = requests.get("http://localhost:8765/health")
print(response.json())  # {"status": "healthy"}
```

### Common MCP Tools

| Tool | Purpose | Example |
|------|---------|---------|
| bash | Execute shell commands | `bash --command "ls -la"` |
| grep | Search files | `grep --pattern "TODO" --paths "src/"` |
| view | Read file contents | `view --path "src/main.py"` |
| edit | Modify files | `edit --path "src/main.py" --old_str "x" --new_str "y"` |
| create | Create new files | `create --path "new_file.py" --file_text "content"` |

---

## Agent Configuration

### Register Custom Agent

**Step 1: Create Agent Prompt**
```yaml
# agents/my_agent/MY_AGENT.yaml
name: my-agent
description: Custom agent for specialized task
model: claude-sonnet-4.5
tools:
  - bash
  - grep
  - view
capability_tags:
  - code-analysis
  - testing
```

**Step 2: Add to Agent Registry**
```yaml
# agents/AGENT_REGISTRY.yaml
agents:
  - name: my-agent
    type: custom
    status: active
    owner: your-team
    capability_tags:
      - code-analysis
      - testing
    activation_pattern: "@copilot Use my-agent for [task]"
```

**Step 3: Deploy Agent**
```bash
python scripts/agents/deploy_agent.py --agent my-agent
# Output:  Agent deployed successfully
```

### Agent Configuration Options

```yaml
agent:
  name: string
  description: string
  model: string (claude-sonnet-4.5, gpt-5.4, etc.)
  tools:
    - name: string
      enabled: boolean
  capabilities:
    - string
  constraints:
    max_tokens: integer
    timeout_seconds: integer
    max_retries: integer
  logging:
    level: string (debug, info, warn, error)
    destination: string (stdout, file, cloud)
```

---

## Repository Security

### Essential Security Settings

**GitHub Repository Settings**:
```bash
# Enable branch protection
gh api repos/{owner}/{repo}/branches/main/protection \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["build", "test", "lint"]
  },
  "enforce_admins": true,
  "require_code_owner_reviews": true,
  "required_approving_review_count": 1
}
EOF
```

**Secrets Management**:
```bash
# Store secrets in GitHub Actions
gh secret set GITHUB_TOKEN --body "your-token"
gh secret set OPENAI_API_KEY --body "your-key"
gh secret set DATABASE_URL --body "your-url"

# Verify secrets
gh secret list
```

**Deploy Keys**:
```bash
# Create deploy key (read-only)
ssh-keygen -t ed25519 -f deploy_key -N ""
gh deploy-key add deploy_key.pub --title "Deploy Key" --read-only
```

### Security Checklist

- [ ] Enable branch protection on `main`
- [ ] Require code owner reviews
- [ ] Enable status checks
- [ ] Enable secret scanning
- [ ] Enable dependabot
- [ ] Review collaborator access
- [ ] Rotate deploy keys quarterly
- [ ] Enable 2FA for all maintainers

---

## Consistency Checks

### Pre-Commit Checks

**Install pre-commit hooks**:
```bash
pip install pre-commit
pre-commit install
```

**Run checks manually**:
```bash
# Check single file
pre-commit run --file src/main.py

# Check all files
pre-commit run --all-files

# Check specific hook
pre-commit run black --all-files
```

### Available Checks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        stages: [commit]
```

### Run Consistency Checks

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# Run tests
make test

# All checks
make check-all
```

---

## Advanced Configuration

### Hydra Configuration

**Main config**:
```yaml
# config/app_config.yaml
defaults:
  - _self_
  - environment: local

app:
  name: codex
  version: 1.0.0
  debug: true

database:
  driver: sqlite
  url: sqlite:///./data/codex.db

logging:
  level: DEBUG
  format: json
```

**Environment overrides**:
```yaml
# config/environment/local.yaml
debug: true
database:
  driver: sqlite
  
# config/environment/production.yaml
debug: false
database:
  driver: postgresql
  url: ******host/db
```

**Load configuration**:
```python
from omegaconf import OmegaConf, DictConfig
from hydra import compose, initialize

with initialize(config_path="config", version_base="1.1"):
    cfg = compose(config_name="app_config", overrides=["environment=local"])
    print(OmegaConf.to_yaml(cfg))
```

### NotebookLM Integration

**Configuration**:
```python
# .codex/notebooklm_config.py
NOTEBOOKLM_API_KEY = "your-api-key"
NOTEBOOKLM_PROJECT_ID = "your-project-id"

# Sources to process
SOURCES = [
    "docs/README.md",
    "docs/ARCHITECTURE.md",
    "docs/api/API_REFERENCE.md"
]

# Output settings
OUTPUT = {
    "format": "markdown",
    "include_citations": True,
    "max_length": 2000
}
```

**Initialize NotebookLM**:
```bash
python scripts/notebooklm/init_project.py
python scripts/notebooklm/upload_sources.py
python scripts/notebooklm/generate_summary.py
```

---

## Troubleshooting

### Virtual Environment Issues

**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
# Verify virtual environment is active
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check for conflicting packages
pip list
pip check
```

### Database Connection Issues

**Problem**: `Connection refused` or `Database error`

**Solution**:
```bash
# Check database status
python scripts/check_db.py

# Reinitialize database
python scripts/init_db.py --force

# Run migrations
python scripts/migrate_db.py --latest
```

### GitHub Token Issues

**Problem**: `401 Unauthorized` when accessing GitHub API

**Solution**:
```bash
# Verify token is set
echo $GITHUB_TOKEN

# Test token validity
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Regenerate token if needed
# GitHub Settings → Developer settings → Personal access tokens
```

### MCP Connection Issues

**Problem**: Cannot connect to MCP server

**Solution**:
```bash
# Check MCP server status
curl http://localhost:8765/health

# Restart MCP server
python scripts/mcp/restart_server.py

# Check for port conflicts
lsof -i :8765
```

### Import Linter Errors

**Problem**: `ImportError` or layer violations

**Solution**:
```bash
# Run import linter
import-linter --check-only

# Fix violations
import-linter --fix

# Verify fixes
import-linter --check-only
```

---

## Configuration Reference

### Environment Variables

```bash
# Required
GITHUB_TOKEN=ghp_...
OPENAI_API_KEY=sk-...

# Optional
DEBUG=true|false
LOG_LEVEL=DEBUG|INFO|WARN|ERROR
DATABASE_URL=sqlite:///./data/codex.db
MCP_PORT=8765
```

### Common Commands

```bash
# Development
make dev          # Start dev server
make test         # Run tests
make lint         # Lint code
make format       # Format code

# Production
make build        # Build package
make deploy       # Deploy to production
make release      # Create release

# Maintenance
make clean        # Clean build artifacts
make docs         # Generate documentation
make check-all    # Run all checks
```

---

**This document is the authoritative configuration and setup guide for Codex.**

*Last Updated: 2026-07-08
*Consolidation Status:  Complete (6 files merged)*
