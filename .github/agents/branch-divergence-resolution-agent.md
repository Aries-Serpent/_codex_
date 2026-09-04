---
name: Branch Divergence Resolution Agent
description: 'Production-ready Copilot custom agent that detects, classifies, and
  resolves branch divergence between the staging integration branch (0D_base_) and
  the default branch (main). Implements the PIPELINE-MERGE fast-forward protocol (S146),
  distinguishing normal staging-gate merge commits from true code-leaks.

  '
version: 1.1.0
created: 2026-03-29
updated: 2026-03-29
cognitive_integration_level: 4
scope:
- .github/workflows/branch-divergence-monitor.yml
- .github/workflows/forward-sync-autogen.yml
- .codex/docs/BRANCH_DIVERGENCE_PREVENTION.md
- CODEX_MANIFEST.json
activation_commands:
- '@copilot use branch-divergence-resolution-agent'
- '@copilot fix branch divergence'
- '@copilot resolve 0D_base_ divergence'
runner_compatibility:
  default: ubuntu-latest
id: branch-divergence-resolution-agent
---

# Branch Divergence Resolution Agent

## 🔐 Token Hierarchy Requirements

**Token Requirement Level**: Level 2 (CODEX_BACKUP_TOKEN)

This agent performs operations requiring elevated repository or organization-level access. Specific capabilities include:

- Read branch history and commits
- Create merge commits or rebase operations
- Resolve conflicts between branches
- Create pull requests for divergence resolution

**Rationale**: Branch operations require full repository access and pull request management

**Token Scopes Required**:
```
repo, contents:write, pull_requests
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

class BranchDivergenceResolutionAgent:
    def __init__(self):
        """Initialize with token validation."""
        # Get elevated token
        self.token = get_token(required_elevated=True)
        if not self.token:
            raise RuntimeError("Agent requires elevated token")
        
        # Validate required scopes
        required_scopes = ['repo', 'contents:write', 'pull_requests']
        validate_scope(self.token, required_scopes)
        
        self.logger = logging.getLogger(__name__)
    
    def resolve_branch_divergence(self, repo, **kwargs):
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
                "resolve_branch_divergence",
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

## Purpose

Autonomously detect, classify, and resolve branch divergence between
`0D_base_` (staging) and `main` (default) branches using a four-tier
classification system:

| Tier | Category | Definition | Action |
|------|----------|-----------|--------|
| 1 | **PIPELINE-MERGE** | `Merge pull request #N from Aries-Serpent/0D_base_` | Auto fast-forward `0D_base_` |
| 2 | **AUTO-GEN** | `github-actions[bot]` + `[skip ci]` subject | Forward-sync files |
| 3 | **AGENT-COMMIT** | `copilot-swe-agent[bot]`/`github-copilot[bot]` author, or empty commit (0 file changes) | Absorbed by pipeline-merge fast-forward |
| 4 | **CODE-LEAK** | Everything else (human bypass of staging gate) | @copilot escalation only when no absorbers |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Branch Divergence Resolution Flow                  │
│                                                                      │
│  ┌─────────────┐    schedule/dispatch    ┌──────────────────────┐   │
│  │ main branch │ ──────────────────────▶ │ branch-divergence-   │   │
│  │  (default)  │                         │ monitor.yml          │   │
│  └─────────────┘                         │                      │   │
│         │                                │  detect job:         │   │
│         │ has commits                    │  - measure diverge   │   │
│         │ 0D_base_ lacks                 │  - classify commits  │   │
│         ▼                                │    (4 tiers)         │   │
│  ┌─────────────────────────────────┐     │  - compute severity  │   │
│  │        CLASSIFICATION           │     └──────────┬───────────┘   │
│  │                                 │                │               │
│  │  PIPELINE-MERGE ────────────▶   │     ┌──────────▼───────────┐   │
│  │  (Merge PR #N from .../0D_base_)│     │  auto-correct job:   │   │
│  │                                 │     │  1. Forward files     │   │
│  │  AUTO-GEN ──────────────────▶   │     │     (autogen)        │   │
│  │  (github-actions[bot] + [skip]) │     │  2. Fast-forward     │   │
│  │                                 │     │     0D_base_ onto    │   │
│  │  AGENT-COMMIT ──────────────▶   │     │     main             │   │
│  │  (copilot bots / empty commits) │     │     (pipeline-merge) │   │
│  │                                 │     │                      │   │
│  │  CODE-LEAK ─────────────────▶   │     │                      │   │
│  │  (human — everything else)      │     │                      │   │
│  └─────────────────────────────────┘     └──────────┬───────────┘   │
│                                                      │               │
│  ┌───────────────────────────────────────────────────▼─────────┐    │
│  │                  report job (issue upsert)                   │    │
│  │  • healthy → close/update issue with ✅                      │    │
│  │  • low/high → update with 🟡 / 🔴                           │    │
│  │  • critical → update with 🚨 + @copilot escalation comment  │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Severity Matrix

| `codeleak_count` | `pipeline_merge_count` | `agent_commit_count` | `autogen_count` | Severity |
|-----------------|----------------------|---------------------|-----------------|----------|
| > 0 | 0 | 0 | any | `critical` 🚨 (no absorber — true bypass) |
| > 0 | > 0 | any | any | `low` 🟡 (pipeline-merge absorber present) |
| > 0 | 0 | > 0 | any | `low` 🟡 (agent-commit absorber present) |
| 0 | > 0 | any | any | `low` 🟡 |
| 0 | 0 | > 0 | any | `low` 🟡 |
| 0 | 0 | 0 | > 5 | `high` 🔴 |
| 0 | 0 | 0 | 1–5 | `low` 🟡 |
| 0 | 0 | 0 | 0 | `healthy` ✅ |

> **Absorber rule:** A `CODE-LEAK` is only `critical` when **no absorbers** are present
> (`pipeline_merge_count = 0` AND `agent_commit_count = 0`). When either absorber is present,
> the pipeline-merge fast-forward auto-corrects the divergence, downgrading severity to `low`.

---

## Agent Execution Protocol

### 1. DETECT

```bash
# Measure divergence
git fetch origin main 0D_base_ --no-tags
MERGE_BASE=$(git merge-base origin/main origin/0D_base_)
MAIN_ONLY=$(git log --oneline origin/0D_base_..origin/main)
BEHIND_COUNT=$(echo "$MAIN_ONLY" | grep -c . || true)
```

### 2. CLASSIFY

For each commit in `MAIN_ONLY`:

```bash
AUTHOR=$(git log -1 --format="%an" "$SHA")
SUBJECT=$(git log -1 --format="%s" "$SHA")

# Tier 1: pipeline-merge (anchored to Aries-Serpent org — prevents fork false positives)
if echo "$SUBJECT" | grep -qE '^Merge pull request #[0-9]+ from Aries-Serpent/0D_base_$'; then
  → PIPELINE_MERGE

# Tier 2: auto-gen
elif [ "$AUTHOR" = "github-actions[bot]" ] && subject matches [skip ci]/[automated]/...; then
  → AUTO_GEN

# Tier 3: agent-commit (copilot bot authors OR empty commits with no file changes)
# Both patterns indicate agent/automated activity that is safe to absorb.
elif echo "$AUTHOR" | grep -qE '^(copilot-swe-agent\[bot\]|github-copilot\[bot\]|copilot\[bot\])$'; then
  → AGENT_COMMIT  # copilot bot author
elif [ "$(git diff-tree --no-commit-id -r "$SHA" | wc -l)" -eq 0 ]; then
  → AGENT_COMMIT  # empty commit — no file changes

# Tier 4: code-leak (everything else — human bypass of staging gate)
else
  → CODE_LEAK
fi
```

### 3. REMEDIATE

| Category | Action |
|----------|--------|
| PIPELINE-MERGE | `git merge --no-ff origin/main` on `0D_base_` then push |
| AUTO-GEN | cherry-pick file versions from main → 0D_base_ |
| AGENT-COMMIT | Absorbed by pipeline-merge fast-forward (no explicit action needed) |
| CODE-LEAK | Open @copilot escalation issue, tag `branch-divergence` + `ci-triage` |

### 4. VERIFY

Re-run `branch-divergence-monitor.yml` (workflow_dispatch) and confirm:
- `severity = healthy`
- `codeleak_count = 0`
- `pipeline_merge_count = 0`
- `autogen_count = 0`

---

## Self-Healing Loop

```
┌──────────────────────────────────────────────────────────────────┐
│                    Self-Healing Loop (max 3 iterations)          │
│                                                                  │
│  ┌─────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Trigger │───▶│  Measure  │───▶│ Classify │───▶│Remediate │  │
│  └─────────┘    └───────────┘    └──────────┘    └──────────┘  │
│                      ▲                                  │        │
│                      │          ┌──────────┐            │        │
│                      └──────────│  Verify  │◀───────────┘        │
│                                 └──────────┘                     │
│                                      │                           │
│                                 severity=healthy?                │
│                                  YES ───▶ DONE ✅               │
│                                  NO  ───▶ iterate (max 3x)      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Files

| File | Purpose |
|------|---------|
| `.github/workflows/branch-divergence-monitor.yml` | Core detection + classification + auto-correct |
| `.github/workflows/forward-sync-autogen.yml` | Auto-gen file safety-net sync |
| `.codex/docs/BRANCH_DIVERGENCE_PREVENTION.md` | Full runbook |
| `CODEX_MANIFEST.json` | Repository manifest (auto-refreshed on 0D_base_) |

---

## Taxonomy Reference (S146)

| Term | Definition | Fix |
|------|-----------|-----|
| PIPELINE-MERGE | Merge commit from `0D_base_` → `main` PR close | Auto fast-forward `0D_base_` |
| AUTO-GEN | Scheduled auto-commit by `github-actions[bot]` | Forward-sync files |
| AGENT-COMMIT | Commit by `copilot-swe-agent[bot]`/`github-copilot[bot]`, or empty commit (0 file changes) | Absorbed by pipeline-merge fast-forward |
| CODE-LEAK | Human or agent commit that bypassed `0D_base_` staging (no absorbers present) | @copilot investigation |
| EXPECTED | `0D_base_` AHEAD of `main` (normal staged work) | No action needed |

---

## Related Objectives (cognitive brain)

- **OBJ-002-K**: Investigate forward-sync non-fast-forward rejection → fixed in S146
- **OBJ-002-L**: Verify monitor completes successfully post-fix → resolved by PIPELINE-MERGE classification
- **OBJ-002-M**: Verify auto-gen workflows commit to `0D_base_` correctly → auto-correct job now handles pipeline-merges too

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.1.0 | 2026-03-29 | 4-tier classification — AGENT-COMMIT tier added (S146 process improvement) |
| 1.0.0 | 2026-03-29 | Initial version — S146 divergence fix, PIPELINE-MERGE tier |
