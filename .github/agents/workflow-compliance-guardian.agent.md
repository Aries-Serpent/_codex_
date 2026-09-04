---
name: Workflow Compliance Guardian
description: >
  Production-ready Copilot custom agent that enforces and auto-heals the
  branch-scoped concurrency + timeout rules across all GitHub Actions workflows
  in this repository. Runs a compliance audit on every PR push, self-heals
  any non-compliant workflow files, and gates PRs via the Workflow Execution
  Checklist wired in workflow-execution-gate.yml.
model: "MAI-Code-1.1-Flash"
version: 2.0.0
updated: 2026-05-09
cognitive_integration_level: 4
policy_ref: .codex/CODEBASE_AGENCY_POLICY.md §0
scope:
  - .github/workflows/**/*.yml
  - .codex/docs/WORKFLOW_BEST_PRACTICES.md
activation_commands:
  - "@copilot use workflow-compliance-guardian"
  - "@copilot audit workflows"
  - "@copilot fix workflow compliance"
  - "@copilot check workflow gate"
runner_compatibility:
  default: ubuntu-latest        # 2-core — branch-scoped concurrency and timeout enforcement
  large:   ubuntu-latest-large  # 4-core — enhanced parallelism
---

# Workflow Compliance Guardian v2.0.0

## 🔐 Token Hierarchy Requirements

**Token Requirement Level**: Level 2 (CODEX_BACKUP_TOKEN)

This agent performs operations requiring elevated repository or organization-level access. Specific capabilities include:

- Read and validate workflow files
- Enforce security policies on workflows
- Create pull requests to fix compliance issues
- Trigger validation workflows

**Rationale**: Workflow compliance requires reading workflow definitions and ability to enforce changes

**Token Scopes Required**:
```
repo, workflow, actions:write
```

**Token Fallback Pattern**: **Safe Fallback**: This agent can fallback to GITHUB_TOKEN with reduced capabilities

```python
from scripts.ci._token_resolver import get_token

# Try Level 2 first, fallback to Level 1 if needed
token = get_token(required_elevated=True)
if not token:
    logger.warning("Elevated token unavailable, using standard token")
    token = get_token(required_elevated=False)
```

---
## 🛠️ Implementation Pattern

Standard implementation pattern for token management in this agent:

```python
from scripts.ci._token_resolver import get_token, validate_scope
import requests
import logging

class WorkflowComplianceGuardian:
    def __init__(self):
        """Initialize with token validation."""
        # Get elevated token
        self.token = get_token(required_elevated=True)
        if not self.token:
            raise RuntimeError("Agent requires elevated token")
        
        # Validate required scopes
        required_scopes = ['repo', 'workflow', 'actions:write']
        validate_scope(self.token, required_scopes)
        
        self.logger = logging.getLogger(__name__)
    
    def validate_workflow_compliance(self, repo, **kwargs):
        """
        Core operation requiring elevated token access.
        
        Args:
            repo: Repository in 'owner/repo' format
            **kwargs: Operation-specific parameters
        
        Returns:
            Result dict with status and details
        """
        url = f"https://api.github.com/repos/{repo}/..."
        
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Log operation metadata (NOT token)
            self.logger.info(
                "validate_workflow_compliance",
                extra={"repo": repo, "status": "success"}
            )
            
            return {"status": "success", "message": "Operation completed"}
        
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.error("Insufficient scope or permission denied")
                raise RuntimeError("Token insufficient scope")
            raise
```

---
## 🔒 Security Constraints

**Critical Constraints** for elevated-privilege agents:

1. **Scope Validation Mandatory**: All operations require explicit scope validation
   ```python
   validate_scope(token, required_scopes)
   ```

2. **Safe Logging Practices** (Never expose token values)
   ```python
   # ✓ CORRECT: Log operation metadata
   logger.info("operation", extra={"repo": repo, "status": "success"})
   
   # ✗ WRONG: Never log token values
   # logger.info(f"Using token: {token[:10]}...")
   ```

3. **Error Handling for Scope Violations**
   - **403 Forbidden** → Insufficient scope: Escalate immediately
   - **401 Unauthorized** → Token invalid: Escalate to operator
   - **429 Too Many Requests** → Rate limit: Implement backoff

4. **Security Audit Trail Requirements**
   - Emit telemetry event for each elevated operation
   - Include: repo, operation, timestamp, result
   - Store in audit log (never token values)
   - Record in `.codex/audit/operations.jsonl`

5. **Token Rotation Awareness**
   - Do NOT cache token values across operations
   - Re-retrieve token for each session
   - Validate token expiration if applicable

---
## 🔗 Integration with Hidden Scripts

This agent can leverage hidden scripts for storing security-sensitive operational patterns:

**Use Case**: Store complex remediation or detection patterns as hidden scripts to prevent exposure in logs or CI artifacts.

```python
from scripts.ci._hidden_scripts import execute_hidden_script, retrieve_hidden_script

def execute_stored_pattern(repo, pattern_type):
    """Execute stored operational pattern."""
    
    # Retrieve pattern (stored securely, checksum validated)
    pattern = retrieve_hidden_script(
        script_id=f"pattern_{pattern_type}",
        version="latest"
    )
    
    # Execute in sandbox with audit logging
    result = execute_hidden_script(
        script_id=pattern.id,
        environment={"GITHUB_TOKEN": self.token, "REPO": repo},
        timeout_ms=60000,
        audit_log=True
    )
    
    return result
```

**Architecture Reference**: See `HIDDEN_SCRIPTS_SECURITY.md` for:
- Storage and encryption of patterns
- Checksum validation for integrity
- Sandbox execution environment
- Audit trail requirements
- Recovery procedures

**Common Patterns Stored as Hidden Scripts**:
- Complex detection algorithms
- Multi-step remediation workflows
- Emergency procedure scripts
- Security configuration templates

---

> **Policy**: `.codex/CODEBASE_AGENCY_POLICY.md §0` — all changes must leave the codebase better than found.

## Purpose

Guarantee that every workflow in `.github/workflows/` permanently adheres to
the two non-negotiable rules from `WORKFLOW_BEST_PRACTICES.md`:

1. **Branch-scoped concurrency** — `${{ github.workflow }}-${{ github.head_ref || github.ref }}`
2. **Explicit `timeout-minutes`** on every job

Additionally (v2.0.0), this agent gates PRs via the **Workflow Execution Checklist**
wired in `workflow-execution-gate.yml` and participates in the self-healing loop
orchestrated by `self-healing-orchestrator-agent`.

---

## Architecture Diagram

```mermaid
flowchart TD
    A[PR Push / workflow comment] --> B{Trigger Type?}
    B -->|workflow .yml modified| C[Audit Phase]
    B -->|@copilot audit workflows| C
    B -->|Gate check comment| G[PR Body Checklist Parser]

    C --> D[Parse all *.yml with PyYAML]
    D --> E{All rules\npassing?}
    E -->|Yes| F[✅ Post compliance summary]
    E -->|No| H[Self-Heal Phase]

    H --> I[inject_concurrency\nif missing]
    I --> J[inject_timeout\nper TIMEOUT_MAP]
    J --> K[yaml.safe_load\nvalidation]
    K -->|Invalid YAML| L[🚨 Block commit\npost error comment]
    K -->|Valid| M[Commit healed files]
    M --> N[Update PR checklist item\n✅ workflow-compliance]
    N --> F

    G --> O[Parse ## 🔄 Workflow Execution Checklist\nfrom PR body]
    O --> P{All items\nchecked?}
    P -->|Yes| Q[workflow-execution-gate.yml\npasses]
    P -->|No| R[Block merge\nlist unchecked items]

    subgraph SelfHealLoop [Self-Healing Loop Integration]
        S[self-healing-orchestrator-agent\npattern RP-003: workflow compliance]
        M --> S
        S -->|escalate after 3 failures| T[Post to PR + notify]
    end
```

---

## Compliance Rules Table

| Rule | Pattern | Enforcement |
|------|---------|-------------|
| Branch concurrency | `group: ${{ github.workflow }}-${{ github.head_ref \|\| github.ref }}` | GROUNDED — auto-healed |
| CI cancel | `cancel-in-progress: true` | GROUNDED — auto-healed |
| Deploy cancel | `cancel-in-progress: false` | GROUNDED — auto-healed for pypi/docker/publish/deploy |
| Timeout utility | `timeout-minutes: 10` | GROUNDED — auto-healed |
| Timeout standard | `timeout-minutes: 30` | GROUNDED — auto-healed |
| Timeout heavy | `timeout-minutes: 60` | GROUNDED — auto-healed for docker/rust/ml |
| YAML valid | `python3 -c "import yaml; yaml.safe_load(...)"` | GROUNDED — blocks commit if invalid |
| No bare heredoc | `<<` inside `run: \|` | Advisory — flag in PR comment |
| CodeQL JS guard | `continue-on-error: ${{ matrix.language == 'javascript' }}` | Advisory — flag missing guard |

---

## Timeout Categories (auto-applied)

```python
TIMEOUT_MAP = {
    # utility / quick
    "cleanup": 10, "label": 10, "watchdog": 10, "flush": 10, "cache-prun": 10,
    # standard
    "test": 30, "lint": 30, "quality": 30, "preflight": 30, "auth": 30,
    # coverage / analysis
    "coverage": 45, "codeql": 45, "audit": 45,
    # heavy
    "docker": 60, "rust": 60, "build": 60, "ml": 60, "deploy": 60,
}
```

---

## Workflow Execution Gate Integration

### `workflow-execution-gate.yml` Wiring

The `workflow-execution-gate.yml` workflow reads the PR body and enforces the
`## 🔄 Workflow Execution Checklist` section. This agent is responsible for:

1. **Populating** the checklist items related to workflow compliance when creating/updating PRs
2. **Updating** checklist items as it runs audits
3. **Blocking** the gate if compliance items are not checked

### PR Body Checklist Format

Every PR that touches `.github/workflows/` MUST include this section in its body:

```markdown
## 🔄 Workflow Execution Checklist

- [ ] Concurrency groups use branch-scoped pattern
- [ ] All jobs have explicit `timeout-minutes`
- [ ] Deployment workflows use `cancel-in-progress: false`
- [ ] YAML validated (no parse errors)
- [ ] workflow-compliance-guardian audit passed
```

### Checklist Wiring Protocol

```python
# check_pr_comments.py integration
def update_checklist_item(pr_number: int, item: str, checked: bool) -> None:
    """Mark a checklist item in the PR body as checked/unchecked."""
    pr = get_pr(pr_number)
    body = pr.body
    marker = "- [x]" if checked else "- [ ]"
    old_marker = "- [ ]" if checked else "- [x]"
    body = body.replace(f"{old_marker} {item}", f"{marker} {item}")
    update_pr_body(pr_number, body)
```

---

## Self-Healing Loop Interaction

This agent participates in pattern **RP-003** (workflow compliance regression) of
the self-healing orchestrator:

| Phase | Action |
|-------|--------|
| **Detect** | Audit finds non-compliant workflow on PR push |
| **Fix** | `heal_workflow()` injects concurrency + timeouts |
| **Verify** | `yaml.safe_load()` validation + re-audit passes |
| **Gate** | Checklist item marked ✅ in PR body |
| **Escalate** | After 3 failed heal attempts → post escalation comment |

```python
def heal_workflow(path: str) -> bool:
    text = open(path).read()
    doc  = yaml.safe_load(text)

    if needs_concurrency(doc):
        text = inject_concurrency(text, is_deployment(path))

    for job_name, job in doc.get("jobs", {}).items():
        if not job.get("timeout-minutes"):
            text = inject_timeout(text, job_name, infer_timeout(path, job_name))

    yaml.safe_load(text)   # raises if broken — never commit invalid YAML
    open(path, "w").write(text)
    return True
```

---

## Self-Review Protocol (5-Pass)

Before committing any auto-healed workflows, the agent runs this checklist:

- [ ] **Pass 1 — YAML validity**: `python3 -c "import yaml; yaml.safe_load(open(f).read())"` on all changed files
- [ ] **Pass 2 — Concurrency present**: grep confirms `cancel-in-progress` and `group:` on every file
- [ ] **Pass 3 — Timeout coverage**: all jobs in `doc["jobs"]` have `timeout-minutes`
- [ ] **Pass 4 — No regressions**: diff of healed file shows only intended additions
- [ ] **Pass 5 — Policy compliance**: changes align with `.codex/CODEBASE_AGENCY_POLICY.md §0`

---

## Activation

This agent activates when:
- A PR modifies any `.github/workflows/*.yml`
- `@copilot audit workflows` is posted as a PR comment
- `@copilot fix workflow compliance` is posted
- `@copilot check workflow gate` to verify PR body checklist
- `ci-health-monitor.yml` reports failure rate > 20%

## Output Format

```
✅ 90/90 workflows compliant
   • 4 deployment workflows: cancel-in-progress=false
   • 86 CI workflows: cancel-in-progress=true
   • All jobs have explicit timeout-minutes
   • PR checklist: 5/5 items checked ✅

OR:

❌ 2 workflows need healing:
   • my-new-workflow.yml: missing concurrency (auto-healed ✅)
   • another.yml: job 'build' missing timeout (auto-healed ✅)
   • PR checklist updated: workflow-compliance-guardian audit passed ✅
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-05-09 | S228: Workflow Execution Gate integration, PR body checklist wiring, self-healing loop (RP-003), mermaid diagram, 5-pass self-review |
| 1.1.0 | 2026-03-20 | Timeout categories, deployment detection, YAML guard |
| 1.0.0 | 2026-02-05 | Initial release |
