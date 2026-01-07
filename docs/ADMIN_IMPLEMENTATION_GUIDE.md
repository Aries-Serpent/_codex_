# _codex_ Repository: Complete Admin Implementation Guide

> **Version:** 1.0.0 | **Generated:** 2024-12-21 | **Status:** IMPLEMENTATION_REQUIRED

---

## 🎯 Executive Summary for Administrators

### Purpose

This guide provides Repository/Organization Administrators with a complete checklist and documentation to enable 100% functionality of all _codex_ repository systems.

### Your Role as Administrator

You need to:

1. **Verify/enable** specific GitHub settings
2. **Create** required tokens and secrets
3. **Configure** organization permissions
4. **Provide** specific values back to Copilot Agent

### Systems Requiring Admin Action

- [ ] GitHub Copilot Agent Configuration
- [ ] Custom PR Reviewer Bot
- [ ] Security Scanning Integration
- [ ] Workflow Automation
- [ ] Knowledge Evolution System

---

## 📊 Quick Status Dashboard

| System | Current Status | Admin Actions Required | Priority |
|--------|---------------|----------------------|----------|
| Copilot Agent | ❌ Not Configured | 5 actions | **CRITICAL** |
| PR Reviewer | ❌ App Not Created | 8 actions | **HIGH** |
| Security Scanning | ⚠️ Partial | 3 actions | **HIGH** |
| Workflows | ⚠️ Failing | 4 actions | **MEDIUM** |
| Evolution System | ❌ Not Deployed | 6 actions | **MEDIUM** |

---

## 🔐 Section 1: GitHub Organization Settings

### 1.1 Enable GitHub Copilot for Organization

**Admin Portal:** `https://github.com/organizations/Aries-Serpent/settings/copilot`

**Required Actions:**

1. Navigate to: **Settings → Copilot → Policies**
2. Enable: **"Allow Copilot"**
3. Set: **"Organization members can use Copilot"**
4. Enable: **"Copilot Agents"** (if available in your plan)
5. Copy and provide: **Organization ID**

> 💡 **How to find Organization ID:**
> - Go to `https://api.github.com/orgs/Aries-Serpent`
> - Look for the `"id"` field in the JSON response

**Information to Return:**

```yaml
organization_settings:
  org_name: "Aries-Serpent"
  org_id: [YOUR_ORG_ID]  # e.g., 123456789
  copilot_enabled: [true/false]
  copilot_agents_enabled: [true/false]
  copilot_tier: [free/team/enterprise]
```

### 1.2 Repository Permissions

**Admin Portal:** `https://github.com/Aries-Serpent/_codex_/settings`

**Required Settings Checklist:**

| Setting | Location | Required Value |
|---------|----------|---------------|
| Actions | Settings → Actions → General | ✅ Enabled |
| Workflow Permissions | Settings → Actions → General | Read and write permissions |
| Allow PR approval | Settings → Actions → General | ✅ Allow GitHub Actions to create and approve pull requests |
| Dependency Graph | Settings → Security → Code security | ✅ Enabled |
| Dependabot Alerts | Settings → Security → Code security | ✅ Enabled |
| Dependabot Security Updates | Settings → Security → Code security | ✅ Enabled |
| Secret Scanning | Settings → Security → Code security | ✅ Enabled |
| Push Protection | Settings → Security → Code security | ✅ Enabled |
| GitHub Pages | Settings → Pages | ✅ Enabled (Deploy from Actions) |

**Step-by-Step for Actions Permissions:**

1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/actions`
2. Scroll to **"Workflow permissions"**
3. Select: **"Read and write permissions"**
4. Check: **"Allow GitHub Actions to create and approve pull requests"**
5. Click: **Save**

<!-- Screenshot placeholder: [Actions Permissions Settings] -->

---

## 🤖 Section 2: GitHub App Creation (PR Reviewer Bot)

### 2.1 Create GitHub App

**Portal:** `https://github.com/organizations/Aries-Serpent/settings/apps/new`

> ⚠️ **IMPORTANT:** You must be an Organization Owner or Admin to create a GitHub App.

**Step-by-Step Instructions:**

#### Step 1: Basic Information

Copy these values exactly:

| Field | Value |
|-------|-------|
| GitHub App name | `codex-quantum-reviewer` |
| Homepage URL | `https://github.com/Aries-Serpent/_codex_` |
| Description | `Quantum-inspired PR reviewer with self-evolution capabilities for the _codex_ repository` |

#### Step 2: Identifying and authorizing users

| Setting | Value |
|---------|-------|
| Callback URL | Leave empty |
| Expire user authorization tokens | ✅ Enabled |
| Request user authorization (OAuth) during installation | ❌ Disabled |
| Enable Device Flow | ❌ Disabled |

#### Step 3: Post installation

| Setting | Value |
|---------|-------|
| Setup URL (optional) | Leave empty |
| Redirect on update | ❌ Disabled |

#### Step 4: Webhook Configuration

| Setting | Value |
|---------|-------|
| Active | ✅ Enabled |
| Webhook URL | `https://github.com/Aries-Serpent/_codex_/dispatches` (or leave empty initially) |
| Webhook secret | Generate using command below |

**Generate Webhook Secret:**

```bash
# Run this command to generate a secure webhook secret
openssl rand -hex 32
```

> 📋 **SAVE THIS VALUE SECURELY** - You will need it later for the `CODEX_WEBHOOK_SECRET` secret.

#### Step 5: Repository Permissions (CRITICAL)

Set these permissions exactly as specified:

| Permission | Access Level |
|------------|-------------|
| **Actions** | Read-only |
| **Checks** | Read and write |
| **Commit statuses** | Read and write |
| **Contents** | Read-only |
| **Issues** | Read and write |
| **Metadata** | Read-only (mandatory) |
| **Pull requests** | Read and write |

#### Step 6: Subscribe to Events

Check these events:

- [x] Check run
- [x] Check suite
- [x] Issue comment
- [x] Issues
- [x] Pull request
- [x] Pull request review
- [x] Pull request review comment
- [x] Push

#### Step 7: Where can this GitHub App be installed?

Select: **"Only on this account"**

#### Step 8: Create GitHub App

Click the green **"Create GitHub App"** button.

---

### 2.2 After App Creation - Collect Required Information

After creating the app, you'll be redirected to the app settings page.

**Collect these values:**

1. **App ID:** Shown at the top of the page (e.g., `123456`)
2. **Client ID:** Listed in the "About" section
3. **Generate Private Key:**
   - Scroll down to "Private keys"
   - Click **"Generate a private key"**
   - A `.pem` file will download - **KEEP THIS SECURE**

**Return this information:**

```yaml
github_app:
  app_id: [APP_ID]  # e.g., 123456
  client_id: [CLIENT_ID]  # e.g., Iv1.abc123def456
  app_name: "codex-quantum-reviewer"
  webhook_secret: [SECRET_FROM_STEP_4]  # KEEP SECURE
  private_key_generated: [true/false]
  private_key_file: [FILENAME.pem]
```

### 2.3 Install App on Repository

1. Go to: `https://github.com/apps/codex-quantum-reviewer/installations/new`
2. Select: **Aries-Serpent** organization
3. Choose: **"Only select repositories"**
4. Select: **`_codex_`** repository
5. Click: **"Install"**

**After installation, get the Installation ID:**

1. Go to: `https://github.com/organizations/Aries-Serpent/settings/installations`
2. Find `codex-quantum-reviewer`
3. Click **"Configure"**
4. Look at the URL - it will be like: `https://github.com/organizations/Aries-Serpent/settings/installations/12345678`
5. The number at the end is your **Installation ID**

**Return this information:**

```yaml
app_installation:
  installation_id: [INSTALLATION_ID]  # e.g., 12345678
  installed_on_repo: "_codex_"
  installation_url: "https://github.com/organizations/Aries-Serpent/settings/installations/[INSTALLATION_ID]"
```

---

## 🔑 Section 3: Repository Secrets Configuration

### 3.1 Navigate to Secrets Settings

**Portal:** `https://github.com/Aries-Serpent/_codex_/settings/secrets/actions`

### 3.2 Required Secrets (CRITICAL)

Create these secrets **exactly as named**:

| Secret Name | How to Obtain | Required For | Priority |
|------------|---------------|--------------|----------|
| `CODEX_APP_ID` | From GitHub App creation (Section 2.2) | PR Reviewer | **CRITICAL** |
| `CODEX_PRIVATE_KEY` | Contents of downloaded `.pem` file | PR Reviewer | **CRITICAL** |
| `CODEX_WEBHOOK_SECRET` | Generated in Section 2.1 Step 4 | Webhook verification | **CRITICAL** |
| `CODEX_INSTALLATION_ID` | From Section 2.3 | App authentication | **CRITICAL** |

### 3.3 Optional Secrets (Enhanced Features)

| Secret Name | How to Obtain | Required For |
|------------|---------------|--------------|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys | AI-powered features |
| `PINECONE_API_KEY` | https://app.pinecone.io/ | Vector search features |
| `AWS_ACCESS_KEY_ID` | AWS Console → IAM | Cloud deployment |
| `AWS_SECRET_ACCESS_KEY` | AWS Console → IAM | Cloud deployment |
| `AZURE_CREDENTIALS` | Azure Portal | Azure deployment |
| `ENABLE_LIVE_TESTS` | Set to `true` | Integration testing |

### 3.4 How to Add a Secret

1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/secrets/actions`
2. Click: **"New repository secret"**
3. Enter:
   - **Name:** The secret name exactly as shown in the table
   - **Secret:** The value
4. Click: **"Add secret"**

**For the Private Key Secret (`CODEX_PRIVATE_KEY`):**

1. Open the downloaded `.pem` file in a text editor
2. Copy the **entire contents** including:
   ```
   -----BEGIN RSA PRIVATE KEY-----
   [multiple lines of characters]
   -----END RSA PRIVATE KEY-----
   ```
3. Paste into the secret value field

### 3.5 Personal Access Token (if needed)

If any workflow requires a PAT:

1. Go to: `https://github.com/settings/tokens?type=beta`
2. Click: **"Generate new token"**
3. Configure:
   - **Token name:** `codex-automation`
   - **Expiration:** 90 days (recommended) or no expiration
   - **Repository access:** Only select repositories → `Aries-Serpent/_codex_`
   - **Permissions:**
     - Repository permissions:
       - Contents: Read and write
       - Issues: Read and write
       - Metadata: Read-only
       - Pull requests: Read and write
       - Workflows: Read and write
4. Click: **"Generate token"**
5. Copy the token and save as secret `GH_PAT` (if needed)

**Return Secrets Status:**

```yaml
secrets_configured:
  # Required secrets
  CODEX_APP_ID: [configured/missing]
  CODEX_PRIVATE_KEY: [configured/missing]
  CODEX_WEBHOOK_SECRET: [configured/missing]
  CODEX_INSTALLATION_ID: [configured/missing]
  
  # Optional secrets
  optional_secrets:
    OPENAI_API_KEY: [configured/missing/not_needed]
    PINECONE_API_KEY: [configured/missing/not_needed]
    AWS_ACCESS_KEY_ID: [configured/missing/not_needed]
    AWS_SECRET_ACCESS_KEY: [configured/missing/not_needed]
    ENABLE_LIVE_TESTS: [configured/missing/not_needed]
```

---

## 🚀 Section 4: Deployment Infrastructure

### 4.1 Choose Deployment Method

Select ONE of the following options based on your needs:

#### Option A: GitHub Actions Only (Simplest - RECOMMENDED for start)

**Pros:**
- No external infrastructure needed
- Runs entirely on GitHub
- Zero additional cost
- Fastest to set up

**Cons:**
- 6-hour max runtime per job
- No persistent storage
- Limited to GitHub Events

**Setup:** No additional configuration needed!

---

#### Option B: AWS Lambda (Recommended for Production)

**Pros:**
- Serverless, scales automatically
- Pay only for what you use
- Supports webhooks
- Persistent storage options

**Cons:**
- Requires AWS account
- Additional cost
- More complex setup

**Requirements:**
- AWS Account
- IAM User with Lambda permissions
- S3 bucket for artifacts

---

#### Option C: Azure Functions

**Pros:**
- Similar to AWS Lambda
- Good Microsoft ecosystem integration

**Cons:**
- Requires Azure account
- Additional complexity

---

#### Option D: Self-Hosted Runner

**Pros:**
- Full control
- No time limits
- Can use specialized hardware

**Cons:**
- Requires infrastructure
- Maintenance overhead
- Security responsibility

---

**Return Your Decision:**

```yaml
deployment_choice: [actions_only/aws_lambda/azure_functions/self_hosted]
deployment_details:
  # Only fill if NOT using actions_only
  cloud_provider: [aws/azure/gcp/none]
  account_id: [IF_APPLICABLE]
  region: [IF_APPLICABLE]
  infrastructure_ready: [true/false]
  webhook_url: [URL or "not_deployed"]
```

### 4.2 GitHub Actions Runner Configuration

If using GitHub-hosted runners (recommended):

1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/actions/runners`
2. Verify: **"GitHub-hosted runners"** are enabled
3. For private repos: Ensure you have sufficient Actions minutes

**Self-Hosted Runner Setup (if chosen):**

```bash
# On your server:
mkdir actions-runner && cd actions-runner

# Download runner (get URL from Settings → Actions → Runners → New self-hosted runner)
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure (token from GitHub Settings)
./config.sh --url https://github.com/Aries-Serpent/_codex_ --token [YOUR_TOKEN]

# Run
./run.sh
```

---

## 🛡️ Section 5: Security & Compliance

### 5.1 Security Settings Verification

**Portal:** `https://github.com/Aries-Serpent/_codex_/settings/security_analysis`

**Required Security Features:**

| Feature | Status Required | How to Enable |
|---------|----------------|---------------|
| Dependency graph | ✅ Enabled | Settings → Security → Enable |
| Dependabot alerts | ✅ Enabled | Settings → Security → Enable |
| Dependabot security updates | ✅ Enabled | Settings → Security → Enable |
| Secret scanning | ✅ Enabled | Settings → Security → Enable |
| Push protection | ✅ Enabled | Settings → Security → Enable |
| Code scanning | ⚠️ Optional | Configure in workflow |

### 5.2 Branch Protection Rules

**Portal:** `https://github.com/Aries-Serpent/_codex_/settings/branches`

**Configure for `main` branch:**

1. Click: **"Add branch protection rule"**
2. Branch name pattern: `main`
3. Enable these settings:

| Setting | Value |
|---------|-------|
| Require a pull request before merging | ✅ |
| Require approvals | 1 |
| Dismiss stale pull request approvals | ✅ |
| Require review from Code Owners | ⚠️ Optional |
| Require status checks to pass | ✅ |
| Require branches to be up to date | ✅ |
| **Required status checks:** | See list below |
| Require conversation resolution | ✅ |
| Do not allow bypassing | ⚠️ Optional |
| Restrict who can push | ⚠️ Optional |

**Required Status Checks (add these):**

- `CI — Optimized with Caching / cache-dependencies`
- `CI — Optimized with Caching / parallel-tests`
- `PR Checks (Isolated Cache) / pr-test`
- `CodeQL / Analyze`

4. Click: **"Create"** or **"Save changes"**

### 5.3 CODEOWNERS File

Verify the CODEOWNERS file exists at `.github/CODEOWNERS`:

```bash
# View current CODEOWNERS
cat .github/CODEOWNERS
```

If missing, create it:

```
# Default owners for everything
* @Aries-Serpent/owners

# Workflow files require owner approval
.github/ @Aries-Serpent/owners

# Security-sensitive files
requirements*.txt @Aries-Serpent/owners
pyproject.toml @Aries-Serpent/owners
Dockerfile* @Aries-Serpent/owners
```

---

## 📋 Section 6: Verification Checklist

Use this checklist to verify all configurations are complete:

### Organization Level

- [ ] Copilot enabled for organization
- [ ] Copilot Agents enabled (if available)
- [ ] Organization ID obtained and recorded
- [ ] Organization allows GitHub Apps

### Repository Level

- [ ] Actions enabled with read/write permissions
- [ ] All required secrets configured (Section 3)
- [ ] GitHub App created and configured
- [ ] GitHub App installed on repository
- [ ] Branch protection rules configured
- [ ] Security features enabled

### GitHub App

- [ ] App created with correct name (`codex-quantum-reviewer`)
- [ ] All required permissions set
- [ ] All required events subscribed
- [ ] Private key downloaded and stored securely
- [ ] App installed on `_codex_` repository
- [ ] Installation ID recorded

### Secrets

- [ ] `CODEX_APP_ID` configured
- [ ] `CODEX_PRIVATE_KEY` configured
- [ ] `CODEX_WEBHOOK_SECRET` configured
- [ ] `CODEX_INSTALLATION_ID` configured

### Infrastructure

- [ ] Deployment method chosen
- [ ] Runner configuration verified
- [ ] Webhook endpoint configured (if applicable)

### Testing

- [ ] Can manually trigger workflows
- [ ] Workflows complete successfully
- [ ] Security scans run automatically

---

## 🔄 Section 7: Information to Return to Copilot

Copy and complete this template, then provide it to the Copilot Agent:

```yaml
# ==============================================================================
# Admin Configuration Report for _codex_
# ==============================================================================
# Date: [TODAY'S DATE - e.g., 2024-12-21]
# Administrator: [YOUR_NAME]
# ==============================================================================

organization:
  name: "Aries-Serpent"
  id: [ORG_ID]  # Numeric ID from API
  copilot_enabled: [true/false]
  copilot_agents_available: [true/false]
  copilot_tier: [free/team/enterprise]

repository:
  name: "_codex_"
  full_name: "Aries-Serpent/_codex_"
  default_branch: "main"
  visibility: [public/private]
  
github_app:
  created: [true/false]
  app_id: [APP_ID or "not_created"]
  app_name: [APP_NAME or "not_created"]  # Should be "codex-quantum-reviewer"
  installation_id: [INSTALLATION_ID or "not_installed"]
  webhook_configured: [true/false]
  private_key_generated: [true/false]

secrets_status:
  # Required (all must be "configured" for full functionality)
  CODEX_APP_ID: [configured/missing]
  CODEX_PRIVATE_KEY: [configured/missing]
  CODEX_WEBHOOK_SECRET: [configured/missing]
  CODEX_INSTALLATION_ID: [configured/missing]
  
  # Optional
  OPENAI_API_KEY: [configured/missing/not_needed]
  PINECONE_API_KEY: [configured/missing/not_needed]
  AWS_ACCESS_KEY_ID: [configured/missing/not_needed]
  AWS_SECRET_ACCESS_KEY: [configured/missing/not_needed]
  ENABLE_LIVE_TESTS: [configured/missing/not_needed]

deployment:
  method_chosen: [actions_only/aws_lambda/azure_functions/self_hosted/not_decided]
  infrastructure_ready: [true/false]
  webhook_url: [URL or "not_deployed" or "not_applicable"]

security:
  branch_protection_enabled: [true/false]
  required_status_checks_configured: [true/false]
  security_scanning_enabled: [true/false]
  secret_scanning_enabled: [true/false]
  dependabot_enabled: [true/false]

actions_permissions:
  workflow_permissions: [read_only/read_write]
  can_approve_prs: [true/false]

# List any issues or blockers
blockers:
  - [LIST ANY BLOCKERS - e.g., "Cannot create GitHub App - need owner permissions"]
  - [OR "None" if no blockers]

# Questions for Copilot Agent
questions:
  - [ANY QUESTIONS - e.g., "Should I enable Copilot Agents if available?"]
  - [OR "None" if no questions]

# Additional notes
notes: |
  [Any additional observations or information that might be helpful]
```

---

## 📚 Section 8: Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "Copilot Agents not available"

**Cause:** Copilot Agents may be in preview or not available for your plan.

**Solution:**
1. Check your Copilot subscription tier
2. Contact GitHub support or your account manager
3. **Workaround:** The GitHub App approach (Section 2) provides similar functionality

---

#### Issue: "Workflows failing with permission errors"

**Cause:** Workflow permissions not properly configured.

**Solution:**
1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/actions`
2. Under **"Workflow permissions"**, select **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**
4. Save changes

---

#### Issue: "Cannot create GitHub App"

**Cause:** Insufficient permissions in the organization.

**Solution:**
1. You must be an **Organization Owner** or have **Admin** permissions
2. Ask an owner to create the app, or
3. Create under your personal account, then transfer to organization

---

#### Issue: "Webhook not receiving events"

**Cause:** Webhook URL not accessible or secret mismatch.

**Solution:**
1. Verify webhook URL is publicly accessible (if using external endpoint)
2. Check webhook secret matches in both GitHub App settings and repository secret
3. View delivery history: GitHub App Settings → Advanced → Recent Deliveries
4. Check for failed deliveries and error messages

---

#### Issue: "Secret scanning blocking push"

**Cause:** Code contains patterns that look like secrets.

**Solution:**
1. Remove the secret from code
2. If false positive, use `.github/secret_scanning.yml` to allow:
   ```yaml
   paths-ignore:
     - "docs/**"
     - "**/*.md"
   ```

---

#### Issue: "Required status checks not found"

**Cause:** Workflow jobs haven't run yet or names don't match.

**Solution:**
1. Trigger workflows manually first to register job names
2. Go to Actions tab → Select workflow → Run workflow
3. After completion, status check names become available
4. Update branch protection with correct names

---

## 📞 Section 9: Support Resources

### Documentation Links

| Resource | URL |
|----------|-----|
| GitHub Copilot Docs | https://docs.github.com/copilot |
| GitHub Apps Guide | https://docs.github.com/developers/apps |
| GitHub Actions Docs | https://docs.github.com/actions |
| Repository Security | https://docs.github.com/code-security |
| Branch Protection | https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository |

### Getting Help

1. **Copilot Agent:** Reply with the filled template from Section 7
2. **GitHub Support:** https://support.github.com
3. **GitHub Community:** https://github.community
4. **Repository Issues:** https://github.com/Aries-Serpent/_codex_/issues

### Repository-Specific Resources

| Document | Purpose |
|----------|---------|
| `CONTRIBUTING.md` | Contribution guidelines |
| `SECURITY.md` | Security policies |
| `docs/QUICKSTART.md` | Quick start guide |
| `docs/SECRETS_RUNBOOK.md` | Secrets management details |

---

## ✅ Section 10: Final Validation

Once all sections are complete, perform these validation tests:

### Test 1: Verify Workflow Execution

```bash
# Using GitHub CLI
gh workflow list

# Trigger a workflow manually
gh workflow run "CI — Optimized with Caching"

# Check recent runs
gh run list --limit 5
```

Or via GitHub UI:
1. Go to: `https://github.com/Aries-Serpent/_codex_/actions`
2. Select any workflow
3. Click **"Run workflow"**
4. Verify it completes successfully

### Test 2: Create Test PR

```bash
# Create test branch
git checkout -b test/admin-config-validation

# Make a small change
echo "# Admin Config Test $(date)" >> test-admin-config.md

# Commit and push
git add test-admin-config.md
git commit -m "test: admin configuration validation"
git push origin test/admin-config-validation
```

1. Create PR via GitHub UI
2. Verify:
   - [ ] PR checks start running
   - [ ] Status checks appear
   - [ ] If bot is configured, verify it responds

### Test 3: Verify Security Scanning

1. Go to: `https://github.com/Aries-Serpent/_codex_/security`
2. Verify:
   - [ ] Dependabot alerts section visible
   - [ ] Code scanning section visible (if enabled)
   - [ ] Secret scanning section visible

### Test 4: Verify Branch Protection

1. Try to push directly to `main` (should be blocked if protection is on)
2. Verify PR requires reviews
3. Verify status checks are required

### Cleanup Test PR

```bash
# Delete test branch
git checkout main
git branch -D test/admin-config-validation
git push origin --delete test/admin-config-validation
```

---

## 📝 Notes Section

### Admin Notes

_Use this space for any additional notes, concerns, or observations:_

```
[ADMIN: Add your notes here]




```

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12-21 | Initial comprehensive guide |

---

## 📊 Document Metadata

| Property | Value |
|----------|-------|
| **Document Status** | REQUIRES_ADMIN_ACTION |
| **Next Step** | Complete all sections and return filled template to Copilot Agent |
| **Estimated Time** | 45-60 minutes for full configuration |
| **Difficulty Level** | Intermediate |
| **Last Updated** | 2024-12-21 |

---

**🚀 Ready to Start?** Begin with Section 1 and work through each section in order. Return the completed template from Section 7 when finished.

---

*This guide is part of the _codex_ repository documentation. For updates or corrections, please open an issue or PR.*
