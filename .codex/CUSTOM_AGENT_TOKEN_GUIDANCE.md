# CUSTOM_AGENT_TOKEN_GUIDANCE.md

**Token Requirements and Implementation Guide for Custom Agents**

**Document Version**: 1.0.0
**Date**: 2026-02-17
**Target Audience**: Custom Agent Developers, Agent Maintainers, Platform Engineers

---

## 🎯 Overview

This document specifies token requirements for 13 custom agents identified in Phase 1 audit. Each agent profile includes required token level, scope specifications, and implementation patterns.

### Agent Classification

**Token Levels**:
- **Level 1 (Standard)**: GITHUB_TOKEN, repo-scoped operations
- **Level 2 (Elevated)**: CODEX_BACKUP_TOKEN, cross-repo, admin read
- **Level 3 (Critical)**: CODEX_MASTER_KEY, org admin, emergency

---

## 📋 Agent Token Requirements

### 1. ci-auto-healer-agent

**Purpose**: Detect and heal CI/CD failures automatically

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read workflow files
- Read logs from workflow runs
- Create/update issues for failures
- Commit fixes to repositories

**Required Scopes**:
```
repo:full           # Full repository access
workflow            # Workflow read/write
actions:read_self   # Read self-hosted runners
contents:write      # Write to repository
```

**Implementation Pattern**:
```python
class CIAutoHealerAgent:
    def __init__(self):
        from scripts.ci._token_resolver import get_token
        
        # Requires Level 2 for cross-repo access
        self.token = get_token(
            operation="ci_auto_healing",
            required_level="elevated"
        )
    
    def read_workflow_failure_logs(self, repo, run_id):
        """Read failure logs - requires repo scope."""
        import requests
        
        url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
        response = requests.get(
            url,
            headers={"Authorization": f"token {self.token}"}
        )
        return response.content
```

**Error Handling**:
```python
# Handle scope error
try:
    logs = self.read_workflow_failure_logs(repo, run_id)
except requests.HTTPError as e:
    if e.response.status_code == 403:
        logger.error("Insufficient scope - need Level 2 token")
        # Try with fallback, or notify admin
```

**Testing Requirements**:
- [ ] Test with mock Level 2 token
- [ ] Test scope validation
- [ ] Test cross-repo access
- [ ] Test error recovery

**Status**: ✅ Active, requires Level 2 token

---

### 2. autonomous-test-healer-agent

**Purpose**: Detect, diagnose, and fix failing tests

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read test output logs
- Modify test files
- Commit fixes
- Read P19 shadow import information
- Access flaky test markers

**Required Scopes**:
```
repo:full           # Repository access
contents:write      # Write code changes
workflow            # Workflow access
```

**Implementation Pattern**:
```python
class AutonomousTestHealerAgent:
    def __init__(self):
        from scripts.ci._token_resolver import get_token
        
        self.token = get_token(required_level="elevated")
    
    def detect_flaky_tests(self):
        """Detect flaky tests marked with @pytest.mark.flaky."""
        # Uses repo access to read test markers
        pass
    
    def apply_fix(self, test_file, fix_code):
        """Modify test file with fix."""
        # Requires contents:write scope
        pass
```

**Status**: ✅ Active, Phase 5 integration complete

---

### 3. codeql-alert-resolution-agent

**Purpose**: Resolve CodeQL security alerts

**Token Level**: Level 2 (Elevated) - Level 3 for security team operations

**Operations**:
- Read code scanning alerts
- Analyze alert context
- Implement security fixes
- Mark alerts as fixed
- Create security PRs

**Required Scopes**:
```
repo:full                   # Repository access
security_events            # Security alerts read
contents:write             # Code write
pull_requests:write        # PR creation
```

**Implementation Pattern**:
```python
class CodeQLAlertResolutionAgent:
    def __init__(self):
        from scripts.ci._token_resolver import get_token
        
        self.token = get_token(
            operation="resolve_codeql_alerts",
            required_level="elevated"
        )
    
    def get_security_alerts(self, repo):
        """Fetch open CodeQL alerts."""
        import requests
        
        url = f"https://api.github.com/repos/{repo}/code-scanning/alerts"
        response = requests.get(
            url,
            headers={"Authorization": f"token {self.token}"}
        )
        return response.json()
```

**Status**: ✅ Active, security-focused

---

### 4. workflow-compliance-guardian

**Purpose**: Enforce workflow compliance and token usage rules

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read all workflow files
- Validate patterns
- Update workflows with fixes
- Enforce timeouts and concurrency

**Required Scopes**:
```
repo:full           # Repository access
contents:write      # Update workflows
workflow:write      # Workflow management
```

**Implementation Pattern**:
```python
class WorkflowComplianceGuardian:
    def __init__(self):
        from scripts.ci._token_resolver import get_token
        
        self.token = get_token(required_level="elevated")
    
    def validate_workflow_compliance(self, workflow_file):
        """Validate workflow follows compliance rules."""
        from scripts.ci.enforce_token_patterns import validate_pattern
        
        # Uses enforce_token_patterns.py for validation
        result = validate_pattern(workflow_file)
        return result.is_compliant
```

**Status**: ✅ Active, uses enforce_token_patterns.py

---

### 5. ci-failure-resolution-agent

**Purpose**: Diagnose and resolve CI/CD pipeline failures

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read workflow logs
- Read workflow definitions
- Fix common failure patterns
- Coordinate with other agents

**Required Scopes**:
```
repo:full           # Repository access
workflow:read       # Read workflows
contents:write      # Write fixes
```

**Status**: ✅ Active, integrated with ci-testing-agent

---

### 6. ci-importerror-agent

**Purpose**: Diagnose and remediate ImportError/ModuleNotFoundError failures

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read Python test output
- Analyze sys.path issues
- Fix import statements
- Update dependency lists

**Required Scopes**:
```
repo:full           # Repository access
contents:write      # Fix code/dependencies
```

**Status**: ✅ Active, Python-focused

---

### 7. test-failure-analyzer-agent

**Purpose**: Analyze test failures and recommend fixes

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read test output logs
- Analyze failure patterns
- Identify root causes
- Create diagnostic reports

**Required Scopes**:
```
repo:full           # Repository access
workflow:read       # Read test workflows
contents:read       # Analyze test code
```

**Status**: ✅ Active

---

### 8. mypy-manager-agent

**Purpose**: Manage mypy type checking health

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read mypy output and baseline
- Track type error patterns
- Update .mypy_baseline
- Create PRs for fixes

**Required Scopes**:
```
repo:full           # Repository access
contents:write      # Update baseline
pull_requests:write # Create PRs
```

**Status**: ✅ Active, integrated with mypy.manager Cognitive Brain Skill

---

### 9. dependency-vulnerability-scanner

**Purpose**: Scan dependencies for security vulnerabilities

**Token Level**: Level 1 (Standard) - Level 2 (Elevated) for remediation

**Operations**:
- Read dependency files
- Query vulnerability databases
- Create issues for vulnerabilities
- Coordinate with Dependabot

**Required Scopes**:
```
repo:full           # Repository access (standard)
issues:write        # Create vulnerability issues
```

**Status**: ✅ Active

---

### 10. python-312-type-fixer

**Purpose**: Fix Python 3.12 type annotation issues

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read Python source files
- Analyze type compatibility
- Apply automated fixes
- Update type hints

**Required Scopes**:
```
repo:full           # Repository access
contents:write      # Fix code
```

**Status**: ✅ Active

---

### 11. telemetry-classifier-agent

**Purpose**: Classify unknown CI failure patterns

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read CI artifacts
- Analyze telemetry data
- Generate classifier patches
- Create PRs with fixes

**Required Scopes**:
```
repo:full           # Repository access
contents:write      # Create patches
pull_requests:write # Create PRs
```

**Status**: ✅ Active

---

### 12. unified-coverage-agent

**Purpose**: Manage test coverage across codebase

**Token Level**: Level 2 (Elevated)

**Operations**:
- Read coverage reports
- Track coverage trends
- Identify gaps
- Create gap-fill tests

**Required Scopes**:
```
repo:full           # Repository access
contents:read       # Read test code
workflow:read       # Read coverage workflows
```

**Status**: ✅ Active

---

### 13. packaging-validation-agent

**Purpose**: Validate Python packaging configuration

**Token Level**: Level 1 (Standard) - Level 2 (Elevated) for updates

**Operations**:
- Read pyproject.toml, setup.cfg
- Validate PEP 621 compliance
- Check dependencies
- Verify security posture

**Required Scopes**:
```
repo:full           # Repository access
contents:write      # Update configs
```

**Status**: ✅ Active

---

## 🔄 Implementation Template

Use this template when implementing token access for a new agent:

```python
class CustomAgent:
    """Template for custom agent with token integration."""
    
    def __init__(self, agent_name: str, required_level: str = "standard"):
        """
        Initialize agent with token resolution.
        
        Args:
            agent_name: Name of agent (for logging)
            required_level: "standard", "elevated", or "critical"
        """
        from scripts.ci._token_resolver import get_token, validate_token_scope
        import logging
        
        self.logger = logging.getLogger(agent_name)
        
        # Get token at appropriate level
        self.token = get_token(
            operation=f"{agent_name}_operation",
            required_level=required_level
        )
        
        if not self.token:
            raise RuntimeError(f"Failed to obtain {required_level} token")
        
        # Validate scope
        required_scopes = self._get_required_scopes()
        if not validate_token_scope(self.token, required_scopes):
            raise PermissionError(
                f"Token lacks required scopes: {required_scopes}"
            )
        
        self.logger.info(f"Agent initialized with {required_level} token")
    
    def _get_required_scopes(self) -> list:
        """Return list of required scopes for this agent."""
        return ["repo:full", "contents:write"]  # Override per agent
    
    def perform_operation(self):
        """Perform agent operation with error handling."""
        try:
            # API calls using self.token
            result = self._api_call()
            return result
        
        except PermissionError as e:
            self.logger.error(f"Permission error: {e}")
            # Try with elevated token if available
            if self._can_use_elevated_token():
                return self._perform_with_elevated_token()
            raise
        
        except Exception as e:
            self.logger.error(f"Operation failed: {e}")
            raise
    
    def _api_call(self):
        """Make API call using token."""
        import requests
        
        response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {self.token}"}
        )
        return response.json()
```

---

## 📊 Agent Summary Table

| Agent | Token Level | Primary Operations | Status | Prompt Update |
|-------|:---:|---|:---:|:---:|
| ci-auto-healer-agent | L2 | Read logs, fix CI | ✅ | ⏳ Phase 6.2 |
| autonomous-test-healer-agent | L2 | Fix tests, mark flaky | ✅ | ⏳ Phase 6.2 |
| codeql-alert-resolution-agent | L2-L3 | Resolve security alerts | ✅ | ⏳ Phase 6.2 |
| workflow-compliance-guardian | L2 | Validate workflows | ✅ | ⏳ Phase 6.2 |
| ci-failure-resolution-agent | L2 | Fix CI failures | ✅ | ⏳ Phase 6.2 |
| ci-importerror-agent | L2 | Fix import errors | ✅ | ⏳ Phase 6.2 |
| test-failure-analyzer-agent | L2 | Analyze test failures | ✅ | ⏳ Phase 6.2 |
| mypy-manager-agent | L2 | Manage type checking | ✅ | ⏳ Phase 6.2 |
| dependency-vulnerability-scanner | L1-L2 | Scan vulnerabilities | ✅ | ⏳ Phase 6.2 |
| python-312-type-fixer | L2 | Fix type annotations | ✅ | ⏳ Phase 6.2 |
| telemetry-classifier-agent | L2 | Classify failures | ✅ | ⏳ Phase 6.2 |
| unified-coverage-agent | L2 | Manage coverage | ✅ | ⏳ Phase 6.2 |
| packaging-validation-agent | L1-L2 | Validate packaging | ✅ | ⏳ Phase 6.2 |

---

## ✅ Prompt Update Checklist

For Phase 6.2, update each agent prompt with:

- [ ] **Agent Name & Purpose**
  - [ ] Include token level requirement
  - [ ] List required operations
  - [ ] Specify scope requirements

- [ ] **Token Integration Code**
  - [ ] Import from scripts.ci._token_resolver
  - [ ] Use get_token() with required_level
  - [ ] Validate token scope
  - [ ] Implement error handling

- [ ] **Operation Examples**
  - [ ] Show correct token usage
  - [ ] Include error handling
  - [ ] Reference appropriate token level

- [ ] **Testing Guidance**
  - [ ] Mock token testing
  - [ ] Real token testing (CI only)
  - [ ] Scope validation testing

- [ ] **Documentation Links**
  - [ ] TOKEN_HIERARCHY_GUIDE.md
  - [ ] SCRIPT_TOKEN_INTEGRATION.md
  - [ ] CI_CD_TOKEN_TROUBLESHOOTING.md

---

## 🔗 Related Documentation

- **TOKEN_HIERARCHY_GUIDE.md** - Token selection overview
- **SCRIPT_TOKEN_INTEGRATION.md** - Token integration patterns
- **CI_CD_TOKEN_TROUBLESHOOTING.md** - Error handling and debugging

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-17
**Status**: Ready for Phase 6.2 Agent Prompt Updates
