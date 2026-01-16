# Google Drive Integration — Future Scope (DEFERRED)

**Document Version**: 1.0.0  
**Created**: 2026-01-16T13:10:00Z  
**Deferral Type**: **HUMAN DEFERRAL** (requires manual external setup)  
**Status**: DEFERRED  
**Next Review**: Phase 11.x/12 Planning

---

## 🧠 Cognitive Brain: Deferral Policy & Classification

**IMPORTANT**: This is a **HUMAN DEFERRAL** (`docs/deferred/`) - the ONLY allowed type of deferral per AI Agency Policy.

### AI Agency Policy on Deferrals

```
✅ ALLOWED: Human Deferral (docs/deferred/)
   - Requires external manual setup that AI agents physically cannot complete
   - Must be documented in docs/deferred/ with complete implementation checklist
   - Examples: Cloud account setup, billing configuration, OAuth consent screens

❌ NOT ALLOWED: AI Agent Deferral
   - AI agents claiming they "cannot implement" due to complexity or capability
   - Per AI Agency Policy: AI agents MUST attempt all technical implementations
   - If blocked: escalate with specific error messages, not defer
```

### Why This is a Human Deferral (ALLOWED)

This Google Drive integration is classified as **Human Deferral** (permitted) because:

**AI Agents CAN Implement** ✅:
- Workflow YAML updates and authentication logic
- Service account integration code
- Error handling and retry mechanisms
- Security scanning and validation
- Documentation and testing

**AI Agents CANNOT Complete (Physical Limitations)** ❌:
- Creating Google Cloud Project (requires Google account login + browser)
- Enabling billing (requires payment method + legal agreements)
- Generating OAuth consent screen (requires human authorization)
- Downloading service account keys (requires Google Console UI access)
- Configuring GitHub Secrets (requires repository admin credentials)

### Implementation Responsibilities

| Phase | Who | Reason |
|-------|-----|--------|
| **Phases 1-2** | Human Admin | External account/billing setup (physical limitation) |
| **Phases 3-8** | AI Agents | Technical implementation (NO deferrals allowed) |

**Policy Compliance**: This deferral is VALID because it documents external prerequisites that AI agents physically cannot complete, not technical work that AI agents are avoiding.

---

## Executive Summary

The Google Drive / NotebookLM integration has been **deferred to future scope** due to incomplete Google Cloud OAuth2 setup and missing authentication credentials. This document consolidates all components, scripts, secrets, and prerequisites needed to implement this functionality in the future.

**Current State**: The `.github/workflows/notebooklm-sync.yml` workflow is disabled (automated triggers commented out) to prevent CI failures. All code and configuration remain intact for future re-enablement.

**Failure Root Cause**: The workflow fails at the "Upload to Google Drive" step with:
```
oauth2: cannot fetch token: 400 Bad Request
Response: {"error": "invalid_request"}
```

This occurs because the `satackey/action-google-drive@v1` action attempts an interactive OAuth2 browser flow, which is incompatible with headless CI environments.

---

## 1. Components Requiring Google Drive Authentication

### 1.1 GitHub Actions Workflow

| Component | Location | Description |
|-----------|----------|-------------|
| **Workflow File** | `.github/workflows/notebooklm-sync.yml` | Main automation workflow for repository consolidation and Drive sync |
| **Drive Upload Step** | Lines 214-223 | Uses `satackey/action-google-drive@v1` action |
| **Dependencies** | - | Requires skicka tool and OAuth2 credentials |
| **Trigger Status** | DISABLED | Automated triggers (push/schedule) commented out; manual dispatch only |

**Key Implementation Details**:
- Consolidates repository using Repomix to XML format
- Performs security scanning (secretlint, detect-secrets)
- Uploads to `/codex-sync/` folder in Google Drive
- Maintains artifact backup in GitHub Actions

### 1.2 Scripts and Tools

| Script | Path | Purpose |
|--------|------|---------|
| **Secret Validation** | `scripts/phase10/validate_gdrive_secrets.sh` | Validates presence and format of required GitHub secrets |
| **Secret Injection** | `scripts/phase10/execute_secrets_injection_now.py` | Orchestrates automated secret injection flows |
| **Secret Manager** | `scripts/phase10/automated_secrets_manager.py` | Programmatic secret management helpers and validation |

### 1.3 Documentation References

| Document | Location | Relevance |
|----------|----------|-----------|
| **Phase 10 Master Plan** | `PHASE_10_MASTER_INTEGRATION_PLANSET.md` | Task 2: Google Drive upload configuration |
| **Phase 11 Prompts** | `PHASE_11_X_PROMPTSETS.md` | Prompt 2.1: Google Drive integration implementation |
| **Phase 12 Continuation** | `PHASE_12_CONTINUATION_PROMPT.md` | Week 1 Day 1-2: Google OAuth + Drive setup |
| **Admin Action Tracker** | `HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md` | HA-GC-001, HA-GH-001, HA-NB-001 action items |
| **Automation Analysis** | `AUTOMATION_CAPABILITY_ANALYSIS_PHASE10.md` | §2.3: Google Drive upload automation analysis |
| **NotebookLM Setup** | `docs/TASK_3_NOTEBOOKLM_SKILL_SETUP.md` | Claude Code integration guide for NotebookLM |

---

## 2. Required GitHub Secrets

Configure these secrets in repository settings before re-enabling the workflow:

| Secret Name | Purpose | Format/Content | Priority |
|-------------|---------|----------------|----------|
| `GDRIVE_SERVICE_ACCOUNT_JSON` | Service account credentials for headless CI authentication | JSON object with `type`, `project_id`, `private_key_id`, `private_key`, `client_email` fields | **CRITICAL** |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 client ID (Desktop app type) | String (e.g., `xxxxx.apps.googleusercontent.com`) | Required for interactive flows |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 client secret | String | Required for interactive flows |
| `NOTEBOOKLM_WEBHOOK_URL` | Webhook endpoint for sync completion notifications | HTTPS URL | Optional |

**Security Notes**:
- Service account JSON contains sensitive private key data — store securely
- Never commit secrets to repository or logs
- Rotate credentials if exposed
- Use GitHub's encrypted secrets feature exclusively

**Validation**:
```bash
# Run validation script after configuring secrets
./scripts/phase10/validate_gdrive_secrets.sh
```

---

## 3. Google Cloud Setup Prerequisites (HA-GC-001)

**Status**: NOT COMPLETED — Required before workflow can function

### 3.1 Project Creation

1. **Create Google Cloud Project**:
   ```bash
   # Via Console: https://console.cloud.google.com/
   # Project Name: "Codex NotebookLM Integration"
   # Project ID: codex-notebooklm-integration
   ```

2. **Enable Drive API**:
   ```bash
   gcloud services enable drive.googleapis.com \
     --project=codex-notebooklm-integration
   ```

### 3.2 Service Account Setup (Recommended for CI)

1. **Create Service Account**:
   ```bash
   gcloud iam service-accounts create notebooklm-sync \
     --display-name="NotebookLM Sync Service Account" \
     --project=codex-notebooklm-integration
   ```

2. **Grant Drive Permissions**:
   - Navigate to Google Drive
   - Create/locate target folder (e.g., `/codex-sync/`)
   - Share folder with service account email: `notebooklm-sync@codex-notebooklm-integration.iam.gserviceaccount.com`
   - Grant **Editor** permissions

3. **Create and Download JSON Key**:
   ```bash
   gcloud iam service-accounts keys create ~/gdrive-service-account.json \
     --iam-account=notebooklm-sync@codex-notebooklm-integration.iam.gserviceaccount.com
   ```

4. **Inject into GitHub Secrets**:
   ```bash
   gh secret set GDRIVE_SERVICE_ACCOUNT_JSON < ~/gdrive-service-account.json
   # Securely delete local copy after injection
   shred -u ~/gdrive-service-account.json
   ```

### 3.3 OAuth 2.0 Client Setup (Optional — Interactive Use Only)

**Note**: Not suitable for CI; service account is preferred.

1. **Create OAuth 2.0 Client ID**:
   - Navigate to: APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth client ID"
   - Application Type: **Desktop app**
   - Name: "Codex NotebookLM Desktop Client"

2. **Configure Consent Screen**:
   - User Type: Internal (if using Google Workspace) or External
   - Scopes: `https://www.googleapis.com/auth/drive.file`

3. **Store Credentials**:
   ```bash
   gh secret set GOOGLE_CLIENT_ID --body "YOUR_CLIENT_ID"
   gh secret set GOOGLE_CLIENT_SECRET --body "YOUR_CLIENT_SECRET"
   ```

### 3.4 Verification

```bash
# Verify project exists
gcloud projects describe codex-notebooklm-integration

# Verify Drive API is enabled
gcloud services list --enabled --project=codex-notebooklm-integration | grep drive

# Verify service account exists
gcloud iam service-accounts list --project=codex-notebooklm-integration
```

---

## 4. NotebookLM Integration (HA-NB-001)

**Status**: BLOCKED — Requires Google Drive upload to function

### 4.1 Notebook Setup

1. **Create NotebookLM Notebook**:
   - Navigate to: https://notebooklm.google.com/
   - Click "New Notebook"
   - Name: "Codex Architecture Knowledge Base"

2. **Add Google Drive Source**:
   - Click "Add Source" → "Google Drive"
   - Navigate to `/codex-sync/codex-architecture-sync.xml`
   - Select file and confirm

3. **Configure AI Architect Instructions**:
   - Open notebook settings
   - Add custom instructions from `docs/notebooklm-architect-prompt.md`
   - Save configuration

### 4.2 Claude Code Integration (HA-CC-001)

Follow detailed setup in `docs/TASK_3_NOTEBOOKLM_SKILL_SETUP.md`:

1. Install NotebookLM Claude Code skill
2. Authenticate with Google account
3. Register notebook URL
4. Test integration with sample queries

---

## 5. Known Issues & Solutions

### 5.1 OAuth2 Interactive Flow Incompatibility

**Issue**: Current workflow uses `satackey/action-google-drive@v1` which may attempt browser-based OAuth flow.

**Error Symptom**:
```
oauth2: cannot fetch token: 400 Bad Request
Response: {"error": "invalid_request"}
```

**Root Cause**: Interactive OAuth requires browser interaction, which is impossible in headless CI environments.

**Solution**: Use service account authentication (JSON key) instead of interactive OAuth.

### 5.2 Alternative Actions

**Recommended Replacement**:
```yaml
- name: Upload to Google Drive
  uses: google-github-actions/upload-cloud-storage@v1
  with:
    credentials: ${{ secrets.GDRIVE_SERVICE_ACCOUNT_JSON }}
    path: ${{ env.OUTPUT_FILE }}
    destination: gs://your-bucket/codex-sync/
```

**Benefits**:
- Native support for service account JSON
- No interactive OAuth flow
- Better maintained by Google
- Supports retry and error handling

### 5.3 Rate Limiting

**Issue**: Drive API has usage quotas (per-user/per-project).

**Mitigation**:
- Implement exponential backoff on 429 errors
- Cache uploads (only upload on content changes)
- Monitor quota usage in Google Cloud Console

### 5.4 File Overwrite Strategy

**Current Configuration**: `remove-outdated: true`

**Alternatives**:
- **Versioned Uploads**: Append timestamp to filename
- **Retention Policy**: Keep last N versions
- **Differential Sync**: Only upload changed files

---

## 6. Future Implementation Checklist

When ready to implement Google Drive integration, complete these phases in order:

### Phase 1: Google Cloud Setup (HA-GC-001) — 20-30 minutes

- [ ] Create Google Cloud Project (`codex-notebooklm-integration`)
- [ ] Enable Google Drive API
- [ ] Create Service Account (`notebooklm-sync`)
- [ ] Grant Drive permissions to service account email
- [ ] Download service account JSON key
- [ ] (Optional) Create OAuth 2.0 Client ID (Desktop app)
- [ ] (Optional) Note OAuth client ID and secret
- [ ] Verify setup with gcloud commands

### Phase 2: GitHub Secrets Configuration (HA-GH-001) — 10-15 minutes

- [ ] Inject `GDRIVE_SERVICE_ACCOUNT_JSON` via GitHub CLI or UI
- [ ] Inject `GOOGLE_CLIENT_ID` (if using OAuth)
- [ ] Inject `GOOGLE_CLIENT_SECRET` (if using OAuth)
- [ ] (Optional) Inject `NOTEBOOKLM_WEBHOOK_URL`
- [ ] Validate secrets using `scripts/phase10/validate_gdrive_secrets.sh`
- [ ] Verify secrets are accessible in workflow runs (use masked output test)

### Phase 3: CI/CD Authentication Fix — 30-45 minutes

- [ ] **Option A**: Update workflow to use service account directly
  - Replace `satackey/action-google-drive@v1` with service-account compatible action
  - Configure action to use `GDRIVE_SERVICE_ACCOUNT_JSON` secret
  - Remove interactive OAuth configuration
- [ ] **Option B**: Use Google's official action
  - Implement `google-github-actions/upload-cloud-storage@v1`
  - Configure bucket/folder structure
  - Set up appropriate IAM permissions
- [ ] Add retry logic with exponential backoff for rate limits
- [ ] Add error handling and alerting for upload failures
- [ ] Test headless authentication in CI environment (use `workflow_dispatch`)

### Phase 4: Workflow Validation — 15-20 minutes

- [ ] Create test Drive folder (e.g., `/codex-sync-staging/`)
- [ ] Update workflow to upload to staging folder
- [ ] Trigger manual workflow run (`workflow_dispatch`)
- [ ] Verify XML file uploads successfully
- [ ] Verify file content and format are correct
- [ ] Verify security scans complete successfully
- [ ] Check for any authentication errors in logs

### Phase 5: NotebookLM Integration (HA-NB-001) — 15-20 minutes

- [ ] Create NotebookLM notebook
- [ ] Add Google Drive XML source to notebook
- [ ] Configure AI Architect instructions (from `docs/notebooklm-architect-prompt.md`)
- [ ] Wait for source indexing (5-10 minutes)
- [ ] Test sample queries to verify context
- [ ] Validate responses include recent repository changes

### Phase 6: Claude Code Integration (HA-CC-001) — 30-45 minutes

- [ ] Install NotebookLM skill in Claude Code
- [ ] Authenticate with Google account
- [ ] Register notebook URL
- [ ] Test `@architect health check` command
- [ ] Verify comprehensive responses with architectural context
- [ ] Test various query types (architecture, security, dependencies)

### Phase 7: Re-enable Workflow — 10-15 minutes

- [ ] Switch workflow to upload to production folder (`/codex-sync/`)
- [ ] Uncomment automated triggers (push + schedule)
- [ ] Update workflow documentation header
- [ ] Commit changes with descriptive message
- [ ] Monitor first automated run (push to main)
- [ ] Verify end-to-end flow completes successfully

### Phase 8: Production Monitoring — Ongoing (1 week minimum)

- [ ] Monitor workflow runs for 1 week
- [ ] Check for authentication failures
- [ ] Verify upload success rate
- [ ] Monitor Drive quota usage
- [ ] Validate NotebookLM source stays current
- [ ] Test AI Architect responses reflect recent changes
- [ ] Document any issues and solutions
- [ ] Update this document with lessons learned

---

## 7. Reference Links

### Repository Files

- **Workflow**: [`.github/workflows/notebooklm-sync.yml`](../../.github/workflows/notebooklm-sync.yml)
- **Secret Validation**: [`scripts/phase10/validate_gdrive_secrets.sh`](../../scripts/phase10/validate_gdrive_secrets.sh)
- **Secret Injector**: [`scripts/phase10/execute_secrets_injection_now.py`](../../scripts/phase10/execute_secrets_injection_now.py)
- **Automation Manager**: [`scripts/phase10/automated_secrets_manager.py`](../../scripts/phase10/automated_secrets_manager.py)
- **NotebookLM Setup**: [`docs/TASK_3_NOTEBOOKLM_SKILL_SETUP.md`](../TASK_3_NOTEBOOKLM_SKILL_SETUP.md)
- **Architect Prompt**: [`docs/notebooklm-architect-prompt.md`](../notebooklm-architect-prompt.md)

### Documentation

- **Phase 10 Master Plan**: [`PHASE_10_MASTER_INTEGRATION_PLANSET.md`](../../PHASE_10_MASTER_INTEGRATION_PLANSET.md) — Task 2
- **Admin Action Tracker**: [`HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md`](../../HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md) — HA-GC-001, HA-GH-001, HA-NB-001
- **Phase 11 Prompts**: [`PHASE_11_X_PROMPTSETS.md`](../../PHASE_11_X_PROMPTSETS.md) — Prompt 2.1
- **Phase 12 Continuation**: [`PHASE_12_CONTINUATION_PROMPT.md`](../../PHASE_12_CONTINUATION_PROMPT.md) — Week 1 Day 1-2
- **Automation Analysis**: [`AUTOMATION_CAPABILITY_ANALYSIS_PHASE10.md`](../../AUTOMATION_CAPABILITY_ANALYSIS_PHASE10.md) — §2.3

### External Resources

- **Google Cloud Console**: https://console.cloud.google.com/
- **Google Drive API Docs**: https://developers.google.com/drive/api/guides/about-sdk
- **Service Account Auth**: https://cloud.google.com/iam/docs/service-accounts
- **NotebookLM**: https://notebooklm.google.com/
- **GitHub Actions Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets

---

## 8. Implementation Notes

### 8.1 For Future Implementers

- **Use service accounts for CI**: Avoid interactive OAuth flows in workflows
- **Test in staging first**: Create a test Drive folder before production deployment
- **Monitor quota usage**: Drive API has per-user and per-project limits
- **Document folder structure**: Maintain clear folder organization in Drive
- **Implement error handling**: Add retry logic and alerting for failures
- **Security first**: Validate secrets, scan files before upload, audit access

### 8.2 For Copilot Agents

When implementing this scope:
1. Read this entire document before starting
2. Follow the checklist phases in order
3. Validate each phase before proceeding
4. Update this document with any new findings
5. Report blocking issues immediately
6. Maintain all existing security measures

### 8.3 For Human Admins

- Manual steps are clearly marked with "HA-" prefix
- Each phase has time estimates for planning
- Secrets must be injected manually (security policy)
- Validate using provided scripts before troubleshooting
- Refer to action tracker for dependencies between tasks

---

## 9. Success Criteria

The Google Drive integration is considered successfully implemented when:

- ✅ Workflow runs automatically on push to main/develop
- ✅ XML files upload successfully to Drive without errors
- ✅ Service account authentication works in CI
- ✅ NotebookLM notebook stays synced with repository changes
- ✅ AI Architect queries return accurate, current information
- ✅ Security scans complete before uploads
- ✅ No authentication failures for 1 week continuous operation
- ✅ Drive quota usage is within acceptable limits
- ✅ Error handling and retry logic functions correctly
- ✅ Documentation reflects actual implementation

---

## 10. Rollback Plan

If issues occur after re-enabling:

1. **Immediate**: Disable automated triggers (comment out push/schedule)
2. **Monitor**: Check workflow logs for specific error messages
3. **Isolate**: Test components individually (consolidation, security, upload)
4. **Revert**: Roll back to manual-dispatch-only mode
5. **Document**: Record issues in this document's Known Issues section
6. **Fix**: Address root cause before re-enabling
7. **Test**: Validate fix in staging environment
8. **Re-enable**: Gradually restore automated triggers with monitoring

---

**Document Maintenance**: Update this document whenever:
- New components require Google Drive integration
- Authentication methods change
- Secrets are rotated or updated
- Known issues are discovered or resolved
- Implementation phases are completed
- Lessons learned from production deployment

**Last Updated**: 2026-01-16T13:10:00Z  
**Next Review**: Upon Phase 11.x/12 planning kickoff
