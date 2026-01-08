# Environment Variables for CRM SaaS Integration

## Zendesk Configuration

### Required for Knowledge Sync Service

```bash
# Zendesk API Credentials
ZENDESK_URL=https://your-subdomain.zendesk.com
ZENDESK_USER=your-email@example.com/token
ZENDESK_TOKEN=your_api_token_here

# Optional: Sync Configuration
ZENDESK_SYNC_INTERVAL=3600  # Seconds between syncs (default: 3600)
ZENDESK_RATE_LIMIT=100      # API calls per minute (default: 100)
```

### Obtaining Credentials

1. Log in to your Zendesk instance as an admin
2. Navigate to Admin Center > Apps and integrations > APIs > Zendesk API
3. Enable Token Access
4. Click "Add API token"
5. Copy the token and set as `ZENDESK_TOKEN`

## Dynamics 365 Configuration

### Required for SLA Policy Integration

```bash
# Dynamics 365 API Credentials
D365_URL=https://your-org.crm.dynamics.com
D365_CLIENT_ID=your_client_id_here
D365_CLIENT_SECRET=your_client_secret_here
D365_TENANT_ID=your_tenant_id_here

# Optional: SLA Configuration
D365_SLA_POLICY_PATH=configs/deployment/d365/sla_policies.json
```

### Obtaining Credentials

1. Register an application in Azure AD
2. Grant API permissions for Dynamics 365
3. Generate a client secret
4. Note the Client ID, Tenant ID, and Secret

## Bridge Security

### Secure IPC Configuration

```bash
# Bridge Manager Configuration
CODEX_BRIDGE_MODE=named_pipe  # or unix_socket
CODEX_BRIDGE_DIR=/tmp/codex_secure_bridge
CODEX_BRIDGE_OWNER_ONLY=true  # Enforce 0o600 permissions
```

## MLOps & Training

### Training Data Sources

```bash
# Knowledge Loader Configuration
CODEX_ZENDESK_DOCS_ROOT=docs/vendors/zendesk
CODEX_D365_POLICIES_PATH=configs/deployment/d365/sla_policies.json

# MLflow Configuration (optional)
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=saas_knowledge_training
```

## DVC Configuration

### Data Version Control

```bash
# DVC Remote Storage
DVC_REMOTE_URL=s3://your-bucket/codex-dvc  # or other DVC remote
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Or for local testing
DVC_REMOTE_URL=/path/to/dvc/storage
```

## GitHub Actions Secrets

### Required Secrets in Repository

Set these in GitHub: Settings > Secrets and variables > Actions

```
ZENDESK_URL
ZENDESK_USER  
ZENDESK_TOKEN
D365_URL
D365_CLIENT_ID
D365_CLIENT_SECRET
D365_TENANT_ID
CODEX_MASTER_KEY  # For production deployments
```

## Security Best Practices

1. **Never commit secrets to git**
   - Use `.env` file locally (in `.gitignore`)
   - Use GitHub Secrets for CI/CD
   - Use environment-specific configs

2. **Rotate credentials regularly**
   - API tokens: Every 90 days
   - Client secrets: Every 180 days
   - Document rotation dates

3. **Principle of least privilege**
   - Grant only required API permissions
   - Use read-only tokens where possible
   - Separate dev/prod credentials

4. **Audit access**
   - Log all API calls with credentials
   - Review access logs monthly
   - Monitor for unusual activity

## Example: Local Development Setup

Create `.env` file in repository root:

```bash
# .env (DO NOT COMMIT)
ZENDESK_URL=https://codex-test.zendesk.com
ZENDESK_USER=test@example.com/token
ZENDESK_TOKEN=test_token_12345

D365_URL=https://codex-test.crm.dynamics.com
D365_CLIENT_ID=test-client-id
D365_CLIENT_SECRET=test-secret
D365_TENANT_ID=test-tenant-id

CODEX_BRIDGE_MODE=named_pipe
CODEX_BRIDGE_OWNER_ONLY=true
```

Load with:

```bash
source .env
# or
export $(cat .env | xargs)
```

## Validation

Test environment variables:

```bash
# Test Zendesk connection
python scripts/test_zendesk_connection.py

# Test D365 connection
python scripts/test_d365_connection.py

# Test bridge security
python -c "from src.bridge_manager import BridgeManager; BridgeManager().validate_security()"
```

## Troubleshooting

### Issue: "No module named 'pydantic'"
**Solution:** Install dependencies: `pip install -e .`

### Issue: "Zendesk authentication failed"
**Solution:** Verify `ZENDESK_TOKEN` is correct and not expired

### Issue: "D365 permission denied"
**Solution:** Check Azure AD app permissions include required APIs

### Issue: "Bridge permission denied"
**Solution:** Ensure `CODEX_BRIDGE_OWNER_ONLY=true` and running as correct user

---

**Last Updated:** 2026-01-08
**Maintainer:** Lead Systems Architect & Integration Engineer
