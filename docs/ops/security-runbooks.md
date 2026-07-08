# Security Runbooks

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2026-07-08  
**Author:** Phase 12 WS3 Documentation Team

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication Runbooks](#authentication-runbooks)
3. [Authorization Runbooks](#authorization-runbooks)
4. [Secret Management](#secret-management)
5. [Incident Response](#incident-response)
6. [Audit & Compliance](#audit--compliance)

---

## Overview

### Purpose

Operational procedures for common security tasks, incident response, and routine maintenance.

### Audience

- On-call security engineers
- Operations team
- Incident commanders
- Compliance officers

---

## Authentication Runbooks

### Runbook 1: Reset User Password

**Scenario:** User forgot password or account lockout

**Prerequisites:**
- System admin role
- User identity verified (out-of-band)

**Steps:**

1. **Verify User Identity**
   ```bash
   # Confirm user details (email, GitHub username, etc.)
   curl -H "Authorization: ******" \
     https://api.codex.local/api/v1/users?email=alice@company.com
   ```

2. **Initiate Password Reset**
   ```bash
   POST /api/v1/auth/password-reset
   {
     "user_id": "alice@company.com",
     "action": "admin_reset"
   }
   ```

3. **Send Reset Email**
   - System automatically sends reset link
   - Link expires in 1 hour
   - Ensure user receives email to registered address

4. **User Completes Reset**
   - User clicks link in email
   - Sets new password
   - Password meets requirements:
     - Minimum 12 characters
     - Mix of uppercase, lowercase, numbers, symbols
     - Not in common password list

5. **Verify Reset**
   ```bash
   # Test login with new password
   curl -X POST https://api.codex.local/api/v1/auth/login \
     -d '{"username":"alice", "password":"NewSecurePass123!"}'
   ```

**Troubleshooting:**
- **Email not received:** Check spam folder, verify email in system
- **Reset link expired:** Create new reset request
- **Password doesn't meet requirements:** Show specific requirement failed

**Duration:** 5-10 minutes

### Runbook 2: Enable MFA for User

**Scenario:** User requests MFA or system requires it

**Prerequisites:**
- User has authenticator app (Google Authenticator, Authy, etc.)
- System admin or user themselves

**Steps:**

1. **User Initiates MFA Setup**
   ```bash
   POST /api/v1/auth/mfa/setup
   Content-Type: application/json
   Authorization: ******
   
   {}  # Empty body
   
   Response:
   {
     "secret": "JBSWY3DPEBLW64TMMQ======",
     "qr_code_url": "otpauth://totp/Codex:alice@company.com?secret=..."
   }
   ```

2. **User Scans QR Code**
   - User opens authenticator app
   - Scans QR code (or manually enters secret)
   - Authenticator displays 6-digit code

3. **Verify Code**
   ```bash
   POST /api/v1/auth/mfa/verify
   {
     "code": "123456"
   }
   ```

4. **Save Backup Codes**
   - System generates 10 backup codes (single-use)
   - User stores safely (password manager, paper)
   - Used if authenticator is unavailable

5. **Confirm Setup**
   ```bash
   # MFA is now enabled
   # Required on next login
   ```

**Verification:**
- Force logout user
- User logs in again
- System prompts for MFA code
- User enters code from authenticator
- Login succeeds

**Duration:** 10-15 minutes

### Runbook 3: Recover MFA-Locked Account

**Scenario:** User lost authenticator or backup codes

**Prerequisites:**
- System admin role
- Out-of-band identity verification
- User has access to recovery email

**Steps:**

1. **Verify Identity**
   - Confirm user identity via recovery email
   - Ask security questions (if configured)
   - Verify account ownership

2. **Disable MFA Temporarily**
   ```bash
   curl -X POST https://api.codex.local/api/v1/auth/mfa/disable \
     -H "Authorization: ******" \
     -d '{"user_id": "alice@company.com"}'
   ```

3. **Notify User**
   - Email notification that MFA was disabled
   - User should re-enable ASAP

4. **User Re-Enables MFA**
   - Follow [Runbook 2](#runbook-2-enable-mfa-for-user)
   - User sets up new authenticator
   - Generates new backup codes

5. **Verify**
   - Confirm MFA working on next login

**Duration:** 15-20 minutes

---

## Authorization Runbooks

### Runbook 4: Assign Role to User

**Scenario:** New team member needs access level

**Prerequisites:**
- System admin role
- User exists in system
- Clear role requirements

**Steps:**

1. **Verify Role Requirements**
   - What tasks will user perform?
   - What resources will they access?
   - What permissions are minimum necessary?

2. **Select Appropriate Role**
   - **system_admin:** Full platform control (rare)
   - **agent_operator:** Deploy/manage agents
   - **ci_operator:** Manage CI/CD pipelines
   - **security_reviewer:** Approve security changes
   - **doc_maintainer:** Manage documentation
   - **agent_reader:** Read-only access
   - **guest:** Public-only access

3. **Assign Role**
   ```bash
   POST /api/v1/governance/roles/assign
   Authorization: ******
   Content-Type: application/json
   
   {
     "user_id": "bob@company.com",
     "role": "agent_operator"
   }
   
   Response:
   {
     "user_id": "bob@company.com",
     "role": "agent_operator",
     "assigned_at": "2026-07-08T16:30:00Z",
     "assigned_by": "admin@company.com"
   }
   ```

4. **Verify Permissions**
   ```bash
   GET /api/v1/governance/rbac/permissions?user_id=bob@company.com
   
   Response:
   {
     "user_id": "bob@company.com",
     "roles": ["agent_operator"],
     "permissions": {
       "agents": ["create", "read", "update", "execute"],
       "workflows": ["create", "read", "update", "execute"],
       "secrets": ["read"],
       ...
     }
   }
   ```

5. **Confirm Access**
   - User logs in
   - User can access assigned resources
   - User gets 403 for unauthorized resources

6. **Document in Ticket**
   - Record reason for role assignment
   - Link to approval/ticket
   - Update access control list (ACL)

**Duration:** 5-10 minutes

### Runbook 5: Revoke User Access

**Scenario:** Employee departure, lateral move, role change

**Prerequisites:**
- System admin role
- Manager approval
- User identified

**Steps:**

1. **Verify Revocation Authorization**
   - Get manager approval
   - Confirm effective date
   - Identify all access to revoke

2. **Revoke Role**
   ```bash
   POST /api/v1/governance/roles/revoke
   Authorization: ******
   
   {
     "user_id": "alice@company.com",
     "role": "agent_operator",
     "reason": "departee_sep_15",
     "effective_date": "2026-07-15T17:00:00Z"
   }
   ```

3. **Revoke Active Tokens**
   ```bash
   POST /api/v1/auth/token/revoke-all
   Authorization: ******
   
   {
     "user_id": "alice@company.com",
     "reason": "access_revocation"
   }
   ```

4. **Revoke API Tokens**
   ```bash
   GET /api/v1/auth/tokens?user_id=alice@company.com
   # For each token created by user:
   POST /api/v1/auth/token/revoke
   {
     "token_id": "token_001"
   }
   ```

5. **Verify Access Denied**
   - Verify user gets 403 when accessing resources
   - Verify API tokens no longer work

6. **Archive Audit Records**
   - Export audit logs for user
   - Store in cold storage (90+ days)
   - Keep for compliance (SOX, HIPAA, etc.)

7. **Offboarding Checklist**
   - [ ] Credentials revoked
   - [ ] API tokens revoked
   - [ ] SSH keys revoked
   - [ ] GitHub access removed
   - [ ] VPN access disabled
   - [ ] Audit logs archived
   - [ ] Manager notified

**Duration:** 10-15 minutes

### Runbook 6: Approve Sensitive Operation

**Scenario:** Approval request pending for agent deployment, secret rotation, etc.

**Prerequisites:**
- Approver role
- Request pending approval
- Authority to approve

**Steps:**

1. **Review Request Details**
   ```bash
   GET /api/v1/governance/approvals/{request_id}
   Authorization: ******
   
   Response:
   {
     "request_id": "req-xyz-123",
     "policy_code": "AGENT_DEPLOY_PROD",
     "requester_id": "alice@company.com",
     "resource_id": "agent_prod_001",
     "context": {
       "agent_name": "DataProcessor",
       "version": "2.1.0",
       "change_summary": "Q3 ML model update"
     },
     "created_at": 1720000000,
     "expires_at": 1720000300,
     "status": "pending"
   }
   ```

2. **Review Change Details**
   - Verify requester identity
   - Review proposed change
   - Check against security policies
   - Assess risk level

3. **Make Decision**
   
   **Approval:**
   ```bash
   POST /api/v1/governance/approvals/{request_id}/approve
   Authorization: ******
   Content-Type: application/json
   
   {
     "reason": "Change reviewed and validated against security policies",
     "notes": "ML model evaluated on Q3 dataset"
   }
   ```
   
   **Rejection:**
   ```bash
   POST /api/v1/governance/approvals/{request_id}/reject
   Authorization: ******
   
   {
     "reason": "Model has not been validated against Q3 requirements"
   }
   ```

4. **Document Decision**
   - Provide clear reason in approval/rejection
   - Allow requester to address concerns (if rejected)
   - Note any conditions or requirements

5. **Confirm Action**
   - If approved: verify action executes
   - If rejected: requester resubmits after changes
   - Monitor execution (if applicable)

**Duration:** 5-20 minutes (depends on review complexity)

---

## Secret Management

### Runbook 7: Rotate API Key/Secret

**Scenario:** Monthly rotation, credential compromise, team member departure

**Prerequisites:**
- System admin or security_reviewer role
- Service account or user identified
- Planned maintenance window

**Steps:**

1. **Prepare Rotation Plan**
   - Identify all dependent services
   - Planned maintenance window
   - Rollback procedure

2. **Generate New Secret**
   ```bash
   POST /api/v1/auth/tokens
   Authorization: ******
   
   {
     "name": "DataPipeline Service (rotated)",
     "scopes": ["api:agents:read", "api:workflows:exec"],
     "expires_in": 7776000  # 90 days
   }
   
   Response:
   {
     "token": "codex_pat_xyz789abc456",
     "created_at": 1720000000,
     "expires_at": 1727776000
   }
   ```

3. **Store New Secret Securely**
   - Save to secret manager (HashiCorp Vault, AWS Secrets Manager, etc.)
   - Do NOT share via email or chat
   - Encrypt before storing

4. **Test New Secret**
   - Use new secret in staging environment
   - Verify all integrations work
   - Monitor for errors

5. **Deploy New Secret**
   - Update dependent services with new secret
   - Stage deployment (1 service at a time)
   - Monitor for issues

6. **Verify All Integrations**
   ```bash
   # Verify each service using new secret
   curl -H "Authorization: ******" \
     https://api.codex.local/api/v1/agents
   
   # Should get 200 OK response
   ```

7. **Revoke Old Secret**
   ```bash
   POST /api/v1/auth/token/revoke
   Authorization: ******
   
   {
     "token_id": "old_token_id"
   }
   ```

8. **Document Rotation**
   - Record date of rotation
   - Note reason (monthly/compromise/offboarding)
   - Update runbook if needed

**Timeline:**
- Test: 1 hour
- Deploy: 1-2 hours
- Verification: 30 minutes
- **Total:** 2.5-3.5 hours

### Runbook 8: Respond to Exposed Secret

**Scenario:** Secret accidentally committed, exposed in logs, or compromised

**Prerequisites:**
- Discovery of exposure (GH secret scanning, log review, etc.)
- System admin role

**Steps:**

1. **Assess Exposure Severity**
   - What secret was exposed? (API key, password, encryption key)
   - Where was it exposed? (GitHub, logs, Slack)
   - How long was it exposed?
   - Was it accessed by unauthorized parties?

2. **Immediate Containment (< 5 min)**
   ```bash
   # Revoke exposed secret immediately
   POST /api/v1/auth/token/revoke
   Authorization: ******
   
   {
     "token_id": "exposed_token_id",
     "reason": "compromised"
   }
   ```

3. **Remove from Public Sources**
   - Force-push to remove from Git history (if applicable)
   - Delete from GitHub gists/issues
   - Remove from Slack/email logs

4. **Issue New Secret**
   - Follow [Runbook 7](#runbook-7-rotate-api-keysecret)
   - Deploy to all dependent services
   - Verify functionality

5. **Investigation (if needed)**
   - Audit logs: Who had access? What did they do?
   - Monitor: Unauthorized use of exposed secret
   - Threat assessment: Was it exploited?

6. **Notification (compliance requirement)**
   - Notify affected users/services
   - Provide timeline and impact assessment
   - Recommend password changes (if user credentials)

7. **Post-Incident Review**
   - Root cause: How was it exposed?
   - Prevention: Enhanced controls (secret scanning in pre-commit)
   - Document: Add to incident tracking system

**Duration:** 15-60 minutes (depends on exposure scope)

---

## Incident Response

### Runbook 9: Unauthorized Access Detected

**Scenario:** Suspicious login, token misuse, or permission denial spike

**Prerequisites:**
- Security team notified
- Incident commander assigned
- System access credentials

**Steps:**

1. **Immediate Triage (< 5 min)**
   - Confirm alert is real (not false positive)
   - Determine affected user/service
   - Assess scope (single user vs. widespread)

2. **Contain Threat (< 15 min)**
   ```bash
   # Option 1: Revoke user sessions (minimal impact)
   POST /api/v1/auth/token/revoke-all
   {
     "user_id": "compromised_user@company.com"
   }
   
   # Option 2: Disable user account (maximum containment)
   POST /api/v1/users/disable
   {
     "user_id": "compromised_user@company.com",
     "reason": "suspicious_activity"
   }
   ```

3. **Gather Evidence**
   ```bash
   # Extract audit logs for investigation
   GET /api/v1/audit-logs?user_id=compromised_user@company.com&hours=24
   
   # Get failed permission checks
   GET /api/v1/audit-logs?event_type=permission_denied&hours=24
   
   # Timeline of all actions
   GET /api/v1/audit-logs?user_id=compromised_user@company.com&sort=desc
   ```

4. **Communicate**
   - Notify incident commander
   - Update status in incident tracking
   - Prepare status for stakeholders

5. **Investigation**
   - What actions did attacker/compromised user perform?
   - Were any sensitive operations executed?
   - Were any secrets accessed?
   - Which systems were impacted?

6. **Remediation**
   - Reset user password
   - Re-enable MFA
   - Review and revoke suspicious API tokens
   - If internal threat: escalate to HR/legal

7. **Recovery**
   - Monitor system for residual activity
   - Check for privilege escalation attempts
   - Verify logs are clean for 24 hours

8. **Post-Incident**
   - Document incident timeline
   - Root cause analysis
   - Preventive measures implemented
   - Lessons learned

**Duration:** 30 min - several hours (depends on severity)

### Runbook 10: Malicious Deployment Detected

**Scenario:** Unauthorized or suspicious agent deployed to production

**Prerequisites:**
- Alert triggered (unusual deployment pattern, approval bypass)
- Incident commander assigned

**Steps:**

1. **Verify Deployment** (< 2 min)
   ```bash
   # Get deployment details
   GET /api/v1/agents/{agent_id}/versions/{version}
   
   # Check approval history
   GET /api/v1/governance/approvals?resource_id={agent_id}
   ```

2. **Rollback Deployment** (< 5 min)
   ```bash
   # Immediate rollback to previous version
   POST /api/v1/agents/{agent_id}/rollback
   Authorization: ******
   
   {
     "target_version": "previous_stable_version",
     "reason": "security_incident"
   }
   
   # Monitor rollback progress
   GET /api/v1/agents/{agent_id}/deployments/{deployment_id}
   ```

3. **Disable Agent** (if needed)
   ```bash
   POST /api/v1/agents/{agent_id}/disable
   {
     "reason": "security_incident",
     "duration_minutes": 60  # Temporary disable
   }
   ```

4. **Investigation**
   - Who deployed it? (audit logs)
   - Was approval properly obtained?
   - What did the agent do? (code review)
   - Who approved it? (approval audit)
   - Was approval workflow bypassed?

5. **Containment**
   ```bash
   # Review approver's actions
   GET /api/v1/audit-logs?user_id={approver_id}&hours=24
   
   # Check for other suspicious deployments
   GET /api/v1/agents/deployments?status=recent&hours=24
   ```

6. **Communication**
   - Notify users impacted by deployment
   - Provide status of remediation
   - Give timeline for agent restoration

7. **Recovery**
   - Monitor previous stable version in production
   - Collect evidence from malicious version (code, logs)
   - Once investigation complete, re-enable agent

**Duration:** 15-60 minutes + investigation

---

## Audit & Compliance

### Runbook 11: Generate Compliance Report

**Scenario:** Annual audit, SOC 2 assessment, compliance requirement

**Prerequisites:**
- System admin or compliance officer role
- Audit scope defined (date range, resources)

**Steps:**

1. **Define Audit Scope**
   - Date range (last 90 days, calendar year, etc.)
   - Resources (all agents, specific agents, APIs)
   - Event types (deployments, approvals, access)

2. **Query Audit Logs**
   ```bash
   GET /api/v1/audit-logs?start_date=2026-04-08&end_date=2026-07-08
   
   # Filter by event type
   GET /api/v1/audit-logs?event_type=agent_deployed&hours=2160  # 90 days
   
   # Filter by resource
   GET /api/v1/audit-logs?resource_type=agents&resource_id=prod_agents
   ```

3. **Generate Report**
   ```python
   # Export audit logs to CSV for analysis
   audit_logs = query_audit_logs(...)
   
   report = {
     "period": "2026-04-08 to 2026-07-08",
     "total_events": len(audit_logs),
     "deployments": count_by_event_type("agent_deployed"),
     "approvals": count_by_event_type("approval"),
     "failed_access": count_by_event_type("permission_denied"),
     "role_changes": count_by_event_type("role_changed"),
   }
   ```

4. **Prepare Report**
   - Summary of activities
   - Breakdown by event type
   - User access matrix
   - Approval latency metrics
   - Security events (failed access, denied permissions)
   - Compliance findings

5. **Review & Sign-off**
   - Review with security team
   - Compliance officer approval
   - Audit team sign-off

**Duration:** 2-4 hours

---

## References

- [Governance API Reference](../api/governance-api-reference.md)
- [RBAC Design](../arch/RBAC-design-detailed.md)
- [Approval Policies](../arch/approval-policies-detailed.md)
- [Token Management](../api/token-hierarchy.md)
- [Threat Model](../security/threat-model-phase12.md)

---

**Last Updated:** 2026-07-08  
**Version:** 1.0.0  
**Status:** Production Ready
