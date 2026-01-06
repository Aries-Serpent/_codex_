# GitHub Workflows Examples for MCP Integration

This directory contains example workflow templates for integrating MCP (Model Context Protocol) with GitHub Actions and Copilot Agent.

## 📋 Available Examples

### 1. `mcp-cache-warm.yml`

**Purpose**: Automate cache warming for faster CI/CD runs

**Features**:
- Python wheels caching
- Playwright browsers caching
- MCP Docker image building
- Automated cache cleanup

**Usage**:
```bash
# Manual trigger with custom targets
gh workflow run mcp-cache-warm.yml -f targets=python,playwright -f force=true

# Scheduled daily at 3:15 AM UTC
```

**Setup**:
1. Copy to `.github/workflows/mcp-cache-warm.yml`
2. Customize `PYTHON_VERSION`, `NODE_VERSION` as needed
3. Ensure required secrets are configured (see [GITHUB_ENVIRONMENT_SETUP.md](../../../docs/admin/integration/GITHUB_ENVIRONMENT_SETUP.md))

---

### 2. `copilot-with-mcp.yml`

**Purpose**: Execute Copilot Agent tasks with full MCP context

**Features**:
- MCP service container integration
- Token authentication with encryption
- Context manifest retrieval
- Task execution with enhanced context

**Usage**:
```bash
# Manual trigger with task description
gh workflow run copilot-with-mcp.yml \
  -f task="Implement user authentication module" \
  -f mcp_enabled=true
```

**Setup**:
1. Copy to `.github/workflows/copilot-with-mcp.yml`
2. Configure required secrets:
   - `CODEX_GHP_TOKEN_BASE64`
   - `CODEX_GHP_TOKEN_CONFIG`
   - `CODEX_MASTER_KEY`
3. Build and push MCP Docker image to GHCR
4. Customize task execution step for your use case

---

## 🚀 Quick Start

### Prerequisites

1. **Configure Secrets**: Follow [GITHUB_ENVIRONMENT_SETUP.md](../../../docs/admin/integration/GITHUB_ENVIRONMENT_SETUP.md)
2. **Build MCP Image**: See [GITHUB_MCP_INTEGRATION_GUIDE.md](../../../docs/admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md#advanced-configuration)
3. **Verify Permissions**: Ensure workflow has necessary permissions

### Step-by-Step

1. **Generate Secrets**:
   ```bash
   python3 docs/admin/integration/generate_mcp_secrets.py
   ```

2. **Configure GitHub**:
   - Navigate to repository settings
   - Add secrets as instructed by script
   - Add variables (optional)

3. **Copy Example Workflows**:
   ```bash
   # Copy cache warming workflow
   cp .github/workflows/examples/mcp-cache-warm.yml .github/workflows/
   
   # Copy Copilot integration workflow
   cp .github/workflows/examples/copilot-with-mcp.yml .github/workflows/
   ```

4. **Customize**:
   - Edit workflow files to match your requirements
   - Adjust Python version, cache paths, etc.
   - Modify task execution logic

5. **Test**:
   ```bash
   # Test cache warming
   gh workflow run mcp-cache-warm.yml
   
   # Test Copilot integration
   gh workflow run copilot-with-mcp.yml -f task="Test MCP integration"
   ```

---

## 🔧 Customization

### Adjusting Cache Strategy

Edit cache keys and paths in `mcp-cache-warm.yml`:

```yaml
- name: Cache Python wheels
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      /your/custom/cache/path  # Add custom paths
    key: wheels-${{ runner.os }}-py${{ env.PYTHON_VERSION }}-${{ hashFiles('**/requirements*.txt') }}
```

### Adding Node.js Cache

Add to `mcp-cache-warm.yml`:

```yaml
warm-node-cache:
  name: Warm Node Modules Cache
  runs-on: ubuntu-latest
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v6
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
```

### Custom Copilot Task Execution

Edit `copilot-with-mcp.yml` to integrate your task runner:

```yaml
- name: Execute Copilot task
  run: |
    # Your custom task execution logic
    python3 my_copilot_runner.py \
      --task "${{ github.event.inputs.task }}" \
      --context-file mcp_manifest.json \
      --output results.json
```

---

## 📊 Monitoring

### Cache Hit Rates

Check workflow summaries for cache performance:

```
Python Cache Report
- Cache Hit: true
- Cache Size: 847 MB
- Package Count: 203
```

### MCP Service Health

Monitor MCP container logs:

```bash
# In workflow run logs
✅ MCP service is healthy
✅ Token decryption successful
✅ Received MCP manifest
   Cache keys: 47
```

---

## 🔐 Security Best Practices

1. **Never Commit Secrets**: Use GitHub Secrets, not hardcoded values
2. **Rotate Tokens**: Follow 90-day rotation schedule
3. **Limit Permissions**: Grant minimal required permissions
4. **Use GitHub Apps**: Preferred over Personal Access Tokens
5. **Enable Audit Logging**: Track MCP access and usage

---

## 🐛 Troubleshooting

### Issue: MCP Service Not Starting

**Symptom**: Health check fails, container exits

**Solution**:
```yaml
# Add debug logging
services:
  mcp:
    options: >-
      --health-cmd "curl -v http://localhost:8080/health || exit 1"
      --log-driver json-file
```

Check container logs in workflow output.

### Issue: Token Decryption Failed

**Symptom**: `❌ Token decryption failed`

**Solution**:
1. Verify `CODEX_MASTER_KEY` is set correctly
2. Regenerate token using `generate_mcp_secrets.py`
3. Ensure `cryptography` package is installed

### Issue: Cache Not Restored

**Symptom**: Cache hit: false every run

**Solution**:
1. Check cache key includes correct hash files
2. Verify paths match installation locations
3. Ensure cache size < 10 GB

---

## 📚 Additional Resources

- [MCP Integration Guide](../../../docs/admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md)
- [Environment Setup Guide](../../../docs/admin/integration/GITHUB_ENVIRONMENT_SETUP.md)
- [MCP Developer Guide](../../../docs/mcp/MCP_DEVELOPER_GUIDE.md)
- [Token Security Guide](../../../docs/admin/security/ADMIN_TOKEN_SETUP.md)

---

## 🤝 Contributing

To add new example workflows:

1. Create workflow file in this directory
2. Add documentation to this README
3. Test workflow in your fork
4. Submit PR with examples and docs

---

**Last Updated**: Previous Cycle-12-30  
**Maintainer**: @mbaetiong  
**Status**: Example Templates ✅
