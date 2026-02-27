# Phase 11.x Promptsets - Execution Templates

**Purpose**: Ready-to-use prompts for AI agents to execute Phase 11.x features  
**Target**: GitHub Copilot, custom agents, and automation systems  
**Status**: Production-ready templates

---

## Master Execution Prompt

```
@copilot Begin Phase 11.x implementation following the comprehensive planning document.

CONTEXT:
- Phase 10.2 complete with 64 issues resolved
- All security utilities operational
- CI/CD pipeline stable
- Production-ready codebase

REQUIREMENTS:
1. Follow AI Agency Policy (zero deferred work)
2. Implement features in priority order
3. Maintain test coverage >90%
4. Document all changes comprehensively
5. Run security scans after each feature
6. Update cognitive brain status continuously

DELIVERABLES:
- Complete implementation of 7 priorities
- Comprehensive test suite
- Production deployment automation
- Integration documentation
- Success metrics dashboard

Start with Priority 1: Advanced Authentication (OAuth, MFA, HSM).
```

---

## Priority 1: Advanced Authentication Promptset

### Prompt 1.1 - OAuth Manager Implementation

```
@copilot Implement OAuth2 authentication manager for Codex platform.

TASK: Create src/codex/auth/oauth_manager.py with OAuth2 flow implementation

REQUIREMENTS:
1. Support multiple providers (Google, GitHub, Azure AD, Okta)
2. Implement PKCE for security
3. Handle token exchange and refresh
4. Add state parameter for CSRF protection
5. Store tokens securely (encrypted at rest)
6. Implement rate limiting

SPECIFICATIONS:
- File: src/codex/auth/oauth_manager.py (~300 lines)
- Class: OAuthManager
- Methods:
  - initiate_flow(provider: str) -> str (returns auth URL)
  - exchange_code(code: str, state: str) -> OAuthToken
  - refresh_token(refresh_token: str) -> OAuthToken
  - revoke_token(token: str) -> bool
  - validate_state(state: str) -> bool

SECURITY:
- Use secrets.token_urlsafe(32) for state
- Encrypt tokens with Fernet
- Log all auth events
- Implement exponential backoff on failures

TESTING:
- Create tests/auth/test_oauth_flow.py
- Mock external OAuth providers
- Test all error scenarios
- Validate token lifecycle

Follow security_utils.py patterns for consistency.
```

### Prompt 1.2 - MFA Provider Implementation

```
@copilot Implement Multi-Factor Authentication provider for Codex.

TASK: Create src/codex/auth/mfa_provider.py with TOTP and backup codes

REQUIREMENTS:
1. TOTP generation (Google Authenticator compatible)
2. SMS/Email OTP support
3. Backup codes generation (10 codes, single-use)
4. Recovery mechanisms
5. Rate limiting on verification attempts

SPECIFICATIONS:
- File: src/codex/auth/mfa_provider.py (~200 lines)
- Class: MFAProvider
- Methods:
  - generate_totp_secret() -> str
  - generate_qr_code(secret: str, user: str) -> bytes
  - verify_totp(secret: str, code: str) -> bool
  - send_otp(user: str, method: str) -> str
  - verify_otp(session_id: str, code: str) -> bool
  - generate_backup_codes(count: int = 10) -> List[str]
  - verify_backup_code(user: str, code: str) -> bool

DEPENDENCIES:
- pyotp for TOTP
- qrcode for QR generation
- Twilio for SMS (optional)
- SendGrid for email (optional)

SECURITY:
- Store backup codes hashed (bcrypt)
- Invalidate codes after use
- 3 attempts before lockout (15 min)
- Audit log all MFA events

TESTING:
- Create tests/auth/test_mfa_provider.py
- Test TOTP validation window
- Test backup code lifecycle
- Test rate limiting
```

### Prompt 1.3 - HSM Integration

```
@copilot Implement Hardware Security Module integration for token signing.

TASK: Create src/codex/auth/hsm_integration.py with HSM support

REQUIREMENTS:
1. AWS CloudHSM support
2. Azure Key Vault support
3. On-premise PKCS#11 support
4. Fallback to software signing
5. Key rotation support

SPECIFICATIONS:
- File: src/codex/auth/hsm_integration.py (~150 lines)
- Class: HSMIntegration
- Methods:
  - connect(config: Dict) -> bool
  - sign_token(data: bytes) -> bytes
  - verify_signature(data: bytes, signature: bytes) -> bool
  - rotate_key() -> str (returns new key ID)
  - get_public_key() -> bytes

CONFIGURATION:
- Environment-based provider selection
- Connection pooling for performance
- Automatic retry on connection failures
- Health check endpoint

SECURITY:
- Store HSM credentials in secrets manager
- Use IAM roles for AWS CloudHSM
- Implement key versioning
- Audit all signing operations

FALLBACK:
- Use RSA keys if HSM unavailable
- Log warnings on fallback
- Alert operations team
```

---

## Priority 2: Workflow Automation Promptset

### Prompt 2.1 - Google Drive Integration

```
@copilot Implement Google Drive integration for automated repository uploads.

TASK: Create scripts/phase11/auto_upload_gdrive.py for automated uploads

REQUIREMENTS:
1. OAuth2 authentication with Google Drive API
2. Create folder structure (repos/{repo_name}/{date})
3. Upload flatten-repo outputs
4. Manage versions (keep last 10, cleanup >90 iterations)
5. Share links generation

SPECIFICATIONS:
- File: scripts/phase11/auto_upload_gdrive.py (~400 lines)
- Class: GoogleDriveUploader
- Methods:
  - authenticate() -> Credentials
  - create_folder_structure(repo: str) -> str (folder ID)
  - upload_file(path: str, folder_id: str) -> str (file ID)
  - list_versions(folder_id: str) -> List[FileInfo]
  - cleanup_old_versions(folder_id: str, keep: int = 10)
  - generate_share_link(file_id: str) -> str

API:
- Google Drive API v3
- Scopes: drive.file, drive.appdata
- Rate limiting: 1000 requests per 100 seconds per user

ERROR HANDLING:
- Retry on 429 (rate limit) with exponential backoff
- Handle quota exceeded gracefully
- Log all errors to Datadog
- Alert on consecutive failures (>3)

TESTING:
- Mock Google Drive API
- Test upload flow
- Test cleanup logic
- Test error scenarios
```

### Prompt 2.2 - NotebookLM Sync

```
@copilot Implement NotebookLM synchronization for knowledge management.

TASK: Create scripts/phase11/notebooklm_sync.py for document sync

REQUIREMENTS:
1. Connect to NotebookLM API
2. Upload flattened repository
3. Maintain document index
4. Handle incremental updates
5. Sync metadata

SPECIFICATIONS:
- File: scripts/phase11/notebooklm_sync.py (~350 lines)
- Class: NotebookLMSync
- Methods:
  - connect(api_key: str) -> bool
  - upload_document(content: str, metadata: Dict) -> str
  - update_document(doc_id: str, content: str) -> bool
  - delete_document(doc_id: str) -> bool
  - get_index() -> List[DocumentInfo]
  - sync_incremental(changes: List[Change])

SYNC STRATEGY:
- Full sync: per-phase
- Incremental: On file changes
- Conflict resolution: Last-write-wins
- Version tracking: Git SHA

ERROR HANDLING:
- Retry failed uploads (3 attempts)
- Queue failed syncs for retry
- Alert on repeated failures
- Maintain sync status log

TESTING:
- Mock NotebookLM API
- Test sync flow
- Test conflict resolution
- Test error recovery
```

---

## Priority 3: Testing Expansion Promptset

### Prompt 3.1 - E2E Test Suite

```
@copilot Create comprehensive end-to-end test suite for Codex platform.

TASK: Create tests/e2e/test_secrets_workflow.py for full workflow testing

REQUIREMENTS:
1. Test complete secrets management lifecycle
2. User authentication flows
3. Secret rotation end-to-end
4. Error recovery scenarios
5. Multi-user interactions

SPECIFICATIONS:
- File: tests/e2e/test_secrets_workflow.py (~500 lines)
- Framework: Playwright + pytest
- Test Scenarios:
  1. User creates secret
  2. User retrieves secret
  3. User updates secret
  4. User rotates secret
  5. User deletes secret
  6. User handles rotation failure
  7. Multiple users access same secret

TEST STRUCTURE:
```python
@pytest.mark.e2e
class TestSecretsWorkflow:
    def test_create_secret_flow(self, authenticated_user):
        # Create secret through UI
        # Verify API response
        # Verify database state
        # Verify audit log

    def test_rotation_flow(self, authenticated_user, existing_secret):
        # Initiate rotation
        # Verify zero-downtime
        # Verify old secret invalidated
        # Verify new secret active
```

FIXTURES:
- authenticated_user: User with valid session
- existing_secret: Pre-created test secret
- test_database: Isolated test DB
- mock_hsm: Mocked HSM for signing

ASSERTIONS:
- Response times <200ms
- Zero data loss
- Audit logs complete
- Error messages clear
```

### Prompt 3.2 - Performance Test Suite

```
@copilot Create performance and load testing suite for Codex platform.

TASK: Create tests/performance/benchmark_suite.py for performance validation

REQUIREMENTS:
1. Throughput benchmarks (requests/second)
2. Latency measurements (p50, p95, p99)
3. Resource utilization (CPU, memory, disk)
4. Baseline comparison
5. Regression detection

SPECIFICATIONS:
- File: tests/performance/benchmark_suite.py (~600 lines)
- Framework: Locust + pytest-benchmark
- Metrics:
  - Throughput: >100 req/s per core
  - Latency p95: <200ms
  - Latency p99: <500ms
  - Memory: <1GB per process
  - CPU: <80% sustained

TEST SCENARIOS:
1. Secret creation (1000 operations)
2. Secret retrieval (10000 operations)
3. Secret rotation (100 operations)
4. Concurrent users (100 simultaneous)
5. Spike load (0→1000 users in 10s)

IMPLEMENTATION:
```python
@pytest.mark.performance
class TestPerformance:
    @pytest.mark.benchmark(group="create")
    def test_secret_creation_throughput(self, benchmark):
        result = benchmark(create_secret, {"name": "test", "value": "secret"})
        assert result.stats.mean < 0.1  # 100ms average

    @pytest.mark.load
    def test_concurrent_access(self, locust_env):
        # Simulate 100 users
        # Measure response times
        # Check for errors
        # Verify throughput
```

REPORTING:
- HTML report with graphs
- Comparison to baseline
- Regression alerts
- Performance trends
```

---

## Priority 4: Integration Expansion Promptset

### Prompt 4.1 - MLflow Integration

```
@copilot Implement MLflow experiment tracking integration for Codex.

TASK: Create src/codex/integrations/mlflow_tracker.py for experiment tracking

REQUIREMENTS:
1. Track experiments and runs
2. Log parameters and metrics
3. Store artifacts
4. Model registry integration
5. Auto-logging for supported frameworks

SPECIFICATIONS:
- File: src/codex/integrations/mlflow_tracker.py (~400 lines)
- Class: MLflowTracker
- Methods:
  - create_experiment(name: str) -> str
  - start_run(experiment_id: str) -> RunContext
  - log_param(key: str, value: Any)
  - log_metric(key: str, value: float, step: int)
  - log_artifact(path: str)
  - register_model(name: str, run_id: str) -> ModelVersion
  - end_run()

INTEGRATION:
- Automatic experiment creation per project
- Tag runs with Git SHA and branch
- Store environment information
- Link to GitHub PR/commit

METRICS TO TRACK:
- Model accuracy, precision, recall
- Training time and resources
- Inference latency
- Data quality metrics

USAGE EXAMPLE:
```python
with mlflow_tracker.start_run(experiment_id="codex-training"):
    mlflow_tracker.log_param("learning_rate", 0.001)
    mlflow_tracker.log_metric("accuracy", 0.95, step=100)
    mlflow_tracker.log_artifact("model.pkl")
```
```

### Prompt 4.2 - Slack Integration

```
@copilot Implement Slack notification system for Codex alerts and updates.

TASK: Create src/codex/integrations/slack_notifier.py for Slack integration

REQUIREMENTS:
1. Send formatted notifications
2. Thread support for related messages
3. Interactive components (buttons, menus)
4. Rich media (code blocks, images)
5. Rate limiting compliance

SPECIFICATIONS:
- File: src/codex/integrations/slack_notifier.py (~300 lines)
- Class: SlackNotifier
- Methods:
  - send_message(channel: str, text: str, blocks: List) -> str
  - send_thread_reply(parent_ts: str, text: str)
  - send_alert(severity: str, message: str)
  - send_deployment_notification(deploy_info: Dict)
  - send_error_report(error: Exception, context: Dict)

MESSAGE TYPES:
1. Deployment notifications
2. Error alerts
3. Performance degradation
4. Security alerts
5. per-iteration summaries

FORMATTING:
```python
{
    "blocks": [
        {"type": "header", "text": {"type": "plain_text", "text": "🚨 High Severity Alert"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Error*: Database connection failed"}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": "*Environment:*\nProduction"},
            {"type": "mrkdwn", "text": "*Time:*\n2026-01-15 10:30 UTC"}
        ]},
        {"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "View Logs"}, "url": "..."},
            {"type": "button", "text": {"type": "plain_text", "text": "Acknowledge"}}
        ]}
    ]
}
```

RATE LIMITING:
- Tier 3: 50+ requests per minute
- Batch messages when possible
- Queue during rate limit
```

---

## Priority 5: Security Enhancements Promptset

### Prompt 5.1 - Secret Rotation Automation

```
@copilot Implement automated secret rotation system for Codex platform.

TASK: Create src/codex/security/secret_rotation.py for automated rotation

REQUIREMENTS:
1. Schedule-based rotation (per-iteration, per-phase, monthly, quarterly)
2. Zero-downtime rotation
3. Rollback on failure
4. Multi-provider support (AWS, GitHub, Database)
5. Audit logging

SPECIFICATIONS:
- File: src/codex/security/secret_rotation.py (~350 lines)
- Class: SecretRotation
- Methods:
  - schedule_rotation(secret_id: str, frequency: str)
  - rotate_secret(secret_id: str) -> RotationResult
  - rollback_rotation(secret_id: str, version: int)
  - get_rotation_history(secret_id: str) -> List[RotationEvent]
  - validate_rotation(secret_id: str) -> bool

ROTATION PROCESS:
1. Generate new secret value
2. Store new version (inactive)
3. Test new secret with downstream services
4. Activate new secret
5. Deprecate old secret (grace period: 24 hours)
6. Delete old secret
7. Update all references

ZERO-DOWNTIME STRATEGY:
- Dual-secret period (both old and new valid)
- Gradual rollout (canary → 50% → 100%)
- Automatic validation before activation
- Instant rollback on errors

ERROR HANDLING:
- Retry failed rotations (3 attempts)
- Alert on consecutive failures
- Maintain old secret on failure
- Log all rotation events

TESTING:
- Test rotation flow
- Test rollback
- Test error scenarios
- Test concurrent rotations
```

---

## Priority 6: Custom Agent Development Promptset

### Prompt 6.1 - Code Migration Agent

```
@copilot Create Code Migration Agent for automated codebase migrations.

TASK: Create .github/agents/code-migration-agent.agent.yml

AGENT CAPABILITIES:
1. Python 2 to Python 3 migration
2. Framework upgrades (Django, Flask, FastAPI)
3. Library migrations (requests → httpx)
4. Syntax modernization
5. Breaking change detection

AGENT DEFINITION:
```yaml
name: code-migration-agent
description: Automates codebase migrations with intelligent code transformation
version: 1.0.0
model: gpt-4-turbo-preview
temperature: 0.2
max_tokens: 4000

capabilities:
  - code-analysis
  - code-transformation
  - dependency-management
  - test-generation
  - documentation-update

tools:
  - ast-parser
  - 2to3
  - pyupgrade
  - modernize
  - git

prompts:
  main: |
    You are a code migration expert. Analyze the codebase and perform safe,
    incremental migrations following best practices.

    Steps:
    1. Analyze codebase structure
    2. Identify migration targets
    3. Plan migration strategy
    4. Execute transformations
    5. Update tests
    6. Validate changes
    7. Generate migration report

examples:
  - input: "Migrate from Python 2.7 to Python 3.10"
    output: |
      Migration Plan:
      1. Run 2to3 for automatic conversions
      2. Update print statements
      3. Fix integer division
      4. Update exception syntax
      5. Modernize string formatting
      6. Update imports
      7. Run tests and fix issues
```

IMPLEMENTATION FILES:
- .github/agents/code-migration-agent/prompts/main.md
- .github/agents/code-migration-agent/scripts/analyze.py
- .github/agents/code-migration-agent/scripts/transform.py
- .github/agents/code-migration-agent/scripts/validate.py
```

### Prompt 6.2 - Documentation Generator Agent

```
@copilot Create Documentation Generator Agent for automated documentation.

TASK: Create .github/agents/documentation-generator-agent.agent.yml

AGENT CAPABILITIES:
1. API documentation from code
2. README generation
3. Changelog generation
4. Architecture diagrams
5. Tutorial creation

AGENT DEFINITION:
```yaml
name: documentation-generator-agent
description: Generates comprehensive documentation from code and commits
version: 1.0.0
model: gpt-4-turbo-preview
temperature: 0.3

capabilities:
  - code-analysis
  - docstring-parsing
  - diagram-generation
  - markdown-formatting
  - api-documentation

tools:
  - ast-parser
  - sphinx
  - mkdocs
  - mermaid
  - git-log

prompts:
  main: |
    You are a technical writer specializing in developer documentation.
    Generate clear, comprehensive, and maintainable documentation.

    Documentation types:
    1. API Reference (from docstrings)
    2. User Guides (step-by-step tutorials)
    3. Architecture Docs (system design)
    4. Changelogs (from git history)
    5. Contributing Guidelines

    Quality criteria:
    - Clear and concise
    - Code examples for all APIs
    - Visual diagrams where helpful
    - Up-to-date with latest code
    - Properly structured and indexed
```

OUTPUTS:
- API documentation in Sphinx format
- README with badges and quickstart
- CHANGELOG following Keep a Changelog format
- Architecture diagrams in Mermaid
- Contributing guidelines
```

---

## Validation Promptset

### Final Validation Prompt

```
@copilot Perform comprehensive validation of Phase 11.x implementation.

VALIDATION CHECKLIST:

1. FUNCTIONALITY
   - [ ] All OAuth flows working
   - [ ] MFA challenges successful
   - [ ] HSM integration operational
   - [ ] Google Drive uploads working
   - [ ] NotebookLM sync functional
   - [ ] E2E tests passing
   - [ ] Performance benchmarks met
   - [ ] All integrations active
   - [ ] Secret rotation automated
   - [ ] 4 custom agents functional

2. SECURITY
   - [ ] No new CodeQL alerts
   - [ ] Secrets encrypted at rest
   - [ ] Audit logging comprehensive
   - [ ] Rate limiting enforced
   - [ ] CSRF protection active
   - [ ] Input validation complete

3. PERFORMANCE
   - [ ] Latency p95 <200ms
   - [ ] Throughput >100 req/s
   - [ ] Memory usage <1GB
   - [ ] Zero-downtime deployments
   - [ ] Graceful degradation

4. TESTING
   - [ ] Unit test coverage >90%
   - [ ] Integration tests passing
   - [ ] E2E tests passing
   - [ ] Performance tests passing
   - [ ] Chaos tests passing

5. DOCUMENTATION
   - [ ] API docs complete
   - [ ] User guides written
   - [ ] Architecture diagrams created
   - [ ] Changelog updated
   - [ ] Migration guides available

6. MONITORING
   - [ ] Datadog metrics flowing
   - [ ] Slack alerts configured
   - [ ] PagerDuty integrated
   - [ ] MLflow tracking active
   - [ ] Health checks passing

Generate comprehensive validation report with pass/fail for each item.
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-15  
**Author**: GitHub Copilot  
**Status**: Production-Ready Templates
