# Workflow Token Patterns Guide

This guide provides standardized token usage patterns for GitHub Actions workflows. All 209 workflows should follow these patterns to ensure consistent, secure authentication and proper API access levels.

## Section 1: Token Patterns by Operation Type

### Pattern A: Elevated Operations

Use this pattern for workflows that perform operations requiring elevated permissions such as PR edits, workflow dispatch triggers, repository variable writes, or workflow approvals.

**Characteristics:**
- Modifies repository state (PR body, variables, workflow configs)
- Requires higher API scopes
- Must use CODEX_MASTER_KEY with fallback

**Implementation:**
```yaml
jobs:
  elevated-operations:
    env:
      GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
    steps:
      - name: Edit pull request
        run: |
          gh pr edit ${{ github.event.pull_request.number }} \
            --body "Updated PR body"
      
      - name: Write repository variable
        run: |
          gh api -X PATCH /repos/${{ github.repository }}/actions/variables/MY_VAR \
            -f name='MY_VAR' \
            -f value='new_value'
      
      - name: Dispatch workflow
        run: |
          gh workflow run deploy.yml \
            --ref main \
            -f environment=production
```

**When to Use:**
- ✅ Modifying PR properties (title, body, labels)
- ✅ Writing to repository variables
- ✅ Triggering workflow dispatch
- ✅ Creating/updating workflow runs
- ✅ Managing repository settings via API

---

### Pattern B: Standard Operations

Use this pattern for read-only operations or standard interactions like listing runs, posting comments, managing artifacts, or checking status.

**Characteristics:**
- Read-only or low-privilege operations
- Safe with github.token
- No fallback chain needed

**Implementation:**
```yaml
jobs:
  standard-operations:
    env:
      GH_TOKEN: ${{ github.token }}
    steps:
      - name: List workflow runs
        run: |
          gh run list \
            --workflow main.yml \
            --status completed \
            --limit 10
      
      - name: Post comment on PR
        run: |
          gh pr comment ${{ github.event.pull_request.number }} \
            --body "Automated comment"
      
      - name: Download artifact
        run: |
          gh run download ${{ github.run_id }} \
            --name test-results
      
      - name: Check run status
        run: |
          gh run view ${{ github.run_id }} \
            --json status,conclusion
```

**When to Use:**
- ✅ Listing/viewing workflow runs
- ✅ Posting PR/issue comments
- ✅ Managing artifacts (download, upload)
- ✅ Reading repository data
- ✅ Checking CI/CD status

---

### Pattern C: Mixed Operations

Use this pattern when a workflow performs both elevated and standard operations. The elevated token allows all operations while maintaining compatibility.

**Characteristics:**
- Combines elevated and standard operations
- Single token handles both types
- Maximizes code reuse and simplicity

**Implementation:**
```yaml
jobs:
  mixed-operations:
    env:
      GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
    steps:
      - name: List runs and update PR
        run: |
          # Standard operation
          RUNS=$(gh run list --limit 5 --json status)
          echo "Recent runs: $RUNS"
          
          # Elevated operation
          gh pr edit ${{ github.event.pull_request.number }} \
            --body "Status: $(echo $RUNS | jq -r '.[0].status')"
      
      - name: Fetch data and manage variables
        run: |
          # Standard operation
          CHECKS=$(gh run view ${{ github.run_id }} --json checkRuns)
          
          # Elevated operation
          gh api -X PATCH /repos/${{ github.repository }}/actions/variables/LAST_RUN \
            -f value="$CHECKS"
```

**When to Use:**
- ✅ Workflows combining read and write operations
- ✅ CI gates that read status and update variables
- ✅ Monitoring workflows that collect data and post results

---

## Section 2: Critical Operations Pattern

Critical operations are those that enforce system policies, manage rate limits, handle session management, or perform essential infrastructure tasks. These **MUST** use CODEX_MASTER_KEY without fallback to github.token.

**Critical Operation Categories:**

1. **Workflow Execution Control (WEC)**
   - Enforcing concurrency rules
   - Managing workflow timeouts
   - Controlling job execution flow

2. **Rate Limit Management**
   - Checking API rate limits
   - Managing request queuing
   - Implementing backoff strategies

3. **Session Management**
   - Session state persistence
   - Session cleanup and recovery
   - Context synchronization

4. **Infrastructure Policy Enforcement**
   - Variable consistency checks
   - Secret rotation verification
   - Permission audits

**Implementation:**

```yaml
jobs:
  critical-operations:
    permissions:
      contents: read
      # No github.token fallback for critical ops
    env:
      GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}
    steps:
      - name: Enforce WEC concurrency rules
        run: |
          # CRITICAL: Must use CODEX_MASTER_KEY
          gh api /repos/${{ github.repository }}/actions/runs/${{ github.run_id }} \
            -H "Authorization: ******" \
            -H "X-GitHub-Api-Version: 2022-11-28"
      
      - name: Check rate limits
        run: |
          # CRITICAL: Requires elevated token
          REMAINING=$(gh api /rate_limit -q '.rate.remaining')
          if [ "$REMAINING" -lt 100 ]; then
            echo "::error::API rate limit critically low"
            exit 1
          fi
      
      - name: Verify session state
        run: |
          # CRITICAL: Session verification requires master key
          gh api /repos/${{ github.repository }}/actions/variables \
            -H "Authorization: ******" \
            --paginate
```

**Important Note:** This operation **REQUIRES CODEX_MASTER_KEY** — github.token will fail with a 403 Forbidden error. Always include CODEX_MASTER_KEY without fallback for these operations.

---

## Section 3: Operation Type Reference

This table maps common GitHub Actions operations to their required token levels and patterns.

| Operation | Category | Token Level | Pattern | Notes |
|-----------|----------|-------------|---------|-------|
| **Edit PR body/title** | Write | ELEVATED | Pattern A | Requires repo:write scope |
| **Add PR labels** | Write | ELEVATED | Pattern A | Requires pull_requests:write |
| **Change PR state** | Write | ELEVATED | Pattern A | Close, reopen, convert to draft |
| **Write repo variable** | Write | ELEVATED | Pattern A | Via API /repos/{repo}/actions/variables |
| **Create workflow dispatch** | Write | ELEVATED | Pattern A | Via gh workflow run |
| **Approve workflow run** | Write | ELEVATED | Pattern A | Requires workflow approval scope |
| **Create environment** | Write | ELEVATED | Pattern A | Requires admin scope |
| **Post PR comment** | Write | STANDARD | Pattern B | Safe with github.token |
| **Create issue comment** | Write | STANDARD | Pattern B | Safe with github.token |
| **List workflow runs** | Read | STANDARD | Pattern B | Public information |
| **View run details** | Read | STANDARD | Pattern B | Status, logs accessible |
| **Download artifact** | Read | STANDARD | Pattern B | Workflow artifacts |
| **Get rate limit info** | Read | CRITICAL | Pattern C | WEC enforcement |
| **Enforce WEC rules** | Write | CRITICAL | Pattern C | Requires MASTER_KEY |
| **Verify rate limits** | Read | CRITICAL | Pattern C | Session management |
| **Check session state** | Read | CRITICAL | Pattern C | Infrastructure audit |
| **Update variable via API** | Write | ELEVATED | Pattern A | Direct API call |
| **Dispatch with parameters** | Write | ELEVATED | Pattern A | With inputs |
| **Create PR check run** | Write | ELEVATED | Pattern A | Requires checks:write |
| **Update status check** | Write | ELEVATED | Pattern A | Requires statuses:write |

**Key Rules:**
- Any **write operation** = ELEVATED token required
- Any **infrastructure policy** = CRITICAL token required (no fallback)
- **Read-only operations** = github.token acceptable
- **Mixed workflows** = Use ELEVATED token (safe for both)
- **WEC/Rate limit checks** = CRITICAL (CODEX_MASTER_KEY only)

---

## Section 4: Troubleshooting

### Error: "Resource not accessible by integration"

**Symptoms:**
```
Error: HTTP 403: Resource not accessible by integration
```

**Root Cause:**
The token being used lacks required permissions for the operation. This typically occurs when:
- Using github.token for elevated operations
- CODEX_MASTER_KEY not set or referenced incorrectly
- Operation requires specific API scope not available

**Solution:**
1. Check the operation type against the reference table
2. If it's ELEVATED or CRITICAL, add CODEX_MASTER_KEY to the fallback chain:
   ```yaml
   GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
   ```
3. For CRITICAL operations, remove github.token fallback:
   ```yaml
   GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}
   ```
4. Verify CODEX_MASTER_KEY secret exists in repository settings

---

### Error: "token not found"

**Symptoms:**
```
Error: could not read secret: token not found
```

**Root Cause:**
Referenced secret doesn't exist in repository.

**Solution:**
1. Check secret name spelling and capitalization
2. Verify secret exists in repository Settings → Secrets and variables → Actions
3. If using `secrets.GITHUB_TOKEN` - this doesn't exist! Use `github.token` instead
4. Create missing secrets if needed:
   ```bash
   gh secret set CODEX_MASTER_KEY --body "your-token"
   ```

---

### Error: "gh: not found"

**Symptoms:**
```
sh: gh: command not found
```

**Root Cause:**
GitHub CLI (gh) not installed in the runner environment.

**Solution:**
Add setup step before using gh commands:
```yaml
- name: Install GitHub CLI
  run: |
    sudo apt-get update
    sudo apt-get install -y gh
    gh --version
```

Or use a pre-built action:
```yaml
- name: Install GitHub CLI
  uses: cli/setup-gh-action@v1
```

---

### Error: "api rate limit exceeded"

**Symptoms:**
```
Error: API rate limit exceeded
```

**Root Cause:**
Too many API calls in short time period. GitHub allows 5,000 requests per hour per token.

**Solution:**
1. Check rate limits before operations:
   ```yaml
   - name: Check rate limits
     run: gh api /rate_limit -q '.rate | "\(.remaining)/\(.limit)"'
   ```

2. Implement exponential backoff:
   ```yaml
   - name: Retry with backoff
     run: |
       for attempt in {1..3}; do
         gh api ... && break || sleep $((2**attempt))
       done
   ```

3. Reduce API call frequency where possible
4. Use pagination to batch requests efficiently

---

### Workflow Passes Locally but Fails in CI

**Symptoms:**
- Running `gh` commands manually works
- Same commands fail in GitHub Actions workflow

**Root Cause:**
Environment differences between local and CI. Token scopes, permissions, or authentication context differs.

**Solution:**
1. Add `--verbose` flag to gh commands for debugging:
   ```yaml
   run: gh pr view --verbose
   ```

2. Check workflow permissions:
   ```yaml
   permissions:
     contents: read
     pull-requests: read  # Add required scopes
   ```

3. Verify secrets are set (note: they won't display in logs)
4. Use `gh auth status` to verify authentication:
   ```yaml
   - name: Verify auth
     run: |
       gh auth status
       gh auth token | head -c 20  # Show first 20 chars only
   ```

---

## Quick Reference Checklist

When creating or updating a workflow with GitHub API calls:

- [ ] Identify if operations are **Read**, **Write**, or **Critical**
- [ ] Select appropriate pattern (A, B, or C)
- [ ] Ensure GH_TOKEN env var is set correctly
- [ ] For ELEVATED ops: Include `secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY`
- [ ] For CRITICAL ops: Use CODEX_MASTER_KEY **without github.token fallback**
- [ ] Test locally: `gh auth login` and try commands
- [ ] Add `--verbose` flag during development/debugging
- [ ] Include error handling for API failures
- [ ] Document any custom operations in code comments
- [ ] Run `enforce_token_patterns.py --check-only` to validate

---

## Related Documentation

- [GitHub API Reference](https://docs.github.com/en/rest)
- [GitHub CLI Manual](https://cli.github.com/manual)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
