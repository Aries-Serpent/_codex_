# MCP agentAssignment Payload Examples

> **Generated**: 2026-02-17T11:21:00Z  
> **Repository**: Aries-Serpent/_codex_  
> **Purpose**: Complete examples of GitHub Copilot Agent task creation  
> **Status**: Production-Ready Templates

---

## ⚠️ Important Limitations

### Current Status (as of 2026-02-17)

**agentAssignment Availability**:
- ✅ **GraphQL API**: Available via GitHub Copilot Workspace UI
- ⚠️ **Direct API Access**: Limited to Copilot Workspace sessions
- ❌ **Programmatic Creation**: Not directly accessible from CLI/scripts
- ✅ **Alternative**: Use `@copilot` mentions in PR comments for agent tasks

**Recommended Approach**:
1. **For Workspace Users**: Use GraphQL `agentAssignment` mutation
2. **For PR-Based Workflows**: Use `@copilot` mentions in comments
3. **For CLI/Scripts**: Use `github-coding-agent-create-pull-request` tool

---

## Table of Contents

1. [GraphQL agentAssignment Examples](#graphql-agentassignment-examples)
2. [REST API Alternatives](#rest-api-alternatives)
3. [PR Comment @copilot Examples](#pr-comment-copilot-examples)
4. [Best Practices](#best-practices)

---

## GraphQL agentAssignment Examples

### Example 1: Basic Task Creation

**Scenario**: Fix test failures in PR #3248

```graphql
mutation CreateAgentTask {
  agentAssignment(input: {
    # Repository ID (can be found via: gh api repos/:owner/:repo --jq .node_id)
    repositoryId: "R_kgDOPjJ9Hg"
    
    # Task title (short, actionable)
    title: "Fix test failures in PR #3248"
    
    # Detailed description (supports markdown)
    description: """
# Task: Fix Test Failures in PR #3248

## Context
PR #3248 has 25 test failures that need to be addressed following the 
Investigation Protocol documented in `.codex/CODEBASE_AGENCY_POLICY.md`.

## Objectives
1. Analyze all 25 test failure logs
2. Identify root causes for each failure
3. Apply systematic fixes following repository patterns
4. Validate fixes with pytest
5. Update documentation as needed

## Success Criteria
- [ ] All 25 tests pass locally and in CI
- [ ] No new test failures introduced
- [ ] Code quality checks pass (ruff, mypy, black)
- [ ] Coverage maintained or improved
- [ ] Documentation updated for any API changes

## References
- PR: https://github.com/Aries-Serpent/_codex_/pull/3248
- Resolution Patterns: `.codex/PR_3248_RESOLUTION_PATTERNS.md`
- Policy: `.codex/CODEBASE_AGENCY_POLICY.md`
"""
    
    # Agent instructions (how to approach the task)
    instructions: """
Follow these steps in order:

1. **Investigation Phase**
   - Read all test failure logs from CI
   - Categorize failures by root cause
   - Document findings in `.codex/investigation_${PR_NUMBER}.md`

2. **Fix Phase**
   - Apply fixes systematically (one category at a time)
   - Use existing patterns from `.codex/PR_3248_RESOLUTION_PATTERNS.md`
   - Run tests after each fix to validate
   - Commit incrementally with clear messages

3. **Validation Phase**
   - Run full test suite locally
   - Run linters (ruff, black, mypy)
   - Check coverage with pytest-cov
   - Review code quality with pre-commit hooks

4. **Documentation Phase**
   - Update any affected docstrings
   - Add comments for complex fixes
   - Update CHANGELOG.md with fixes applied
   - Create summary in PR comment

Use `@codex-specific-agent` tools when available for repository-specific patterns.
"""
    
    # Files to focus on (optional, helps agent prioritize)
    files: [
      "tests/cognitive_brain/quantum/test_memory_errors.py",
      "tests/cli/test_train_probe_json_schema.py",
      "tests/cli/test_subcommands.py",
      "tests/unit/test_fixtures.py"
    ]
    
    # Branch to work on (optional, defaults to new branch)
    # branch: "fix/pr-3248-test-failures"
  }) {
    agentRun {
      id
      status
      repositoryName
      title
      createdAt
      updatedAt
      # Additional fields available:
      # description
      # instructions
      # files
      # branch
      # pullRequest { number, title, url }
    }
  }
}
```

**Response**:
```json
{
  "data": {
    "agentAssignment": {
      "agentRun": {
        "id": "AR_kwDOPjJ9Hs4AABCD",
        "status": "PENDING",
        "repositoryName": "Aries-Serpent/_codex_",
        "title": "Fix test failures in PR #3248",
        "createdAt": "2026-02-17T11:21:00Z",
        "updatedAt": "2026-02-17T11:21:00Z"
      }
    }
  }
}
```

---

### Example 2: Documentation Update Task

**Scenario**: Update MCP documentation after new capabilities added

```graphql
mutation CreateDocumentationTask {
  agentAssignment(input: {
    repositoryId: "R_kgDOPjJ9Hg"
    
    title: "Update MCP documentation for new GitHub tools"
    
    description: """
# Task: Update MCP Documentation

## Context
GitHub recently added 15 new MCP tools for Actions workflow management.
Our documentation needs to be updated to reflect these new capabilities.

## Objectives
1. Document all new MCP tools in `docs/reference/GITHUB_MCP_CAPABILITIES_DOCUMENTATION.md`
2. Update MCP capability matrix in `.codex/docs/MCP_CAPABILITY_MATRIX.md`
3. Add usage examples for top 5 most useful new tools
4. Update setup guide if configuration changes needed
5. Create migration guide for users of deprecated tools

## New Tools to Document
- `actions_rerun_workflow` - Rerun failed workflows
- `actions_cancel_workflow_run` - Cancel running workflows
- `actions_list_workflow_artifacts` - List all artifacts
- `actions_download_artifact_batch` - Download multiple artifacts
- ... (11 more)

## References
- GitHub MCP Server changelog: https://github.com/github/github-mcp-server/releases
- Existing docs: `docs/reference/GITHUB_MCP_CAPABILITIES_DOCUMENTATION.md`
"""
    
    instructions: """
1. Review GitHub MCP Server changelog for all new tools
2. For each new tool, document:
   - Tool name and signature
   - Parameters (required and optional)
   - Return type and structure
   - Example usage (practical, real-world)
   - Common use cases
   - Limitations and gotchas
3. Update capability matrix table with new tools
4. Add migration guide section if any tools are deprecated
5. Test all examples in documentation
6. Run doc linter: `markdownlint docs/`
7. Commit with message: "docs: Update MCP documentation for GitHub Actions tools"

Use existing documentation style and format.
"""
    
    files: [
      "docs/reference/GITHUB_MCP_CAPABILITIES_DOCUMENTATION.md",
      ".codex/docs/MCP_CAPABILITY_MATRIX.md",
      "docs/MCP_SETUP_GUIDE.md"
    ]
  }) {
    agentRun {
      id
      status
      repositoryName
    }
  }
}
```

---

### Example 3: Security Vulnerability Fix

**Scenario**: Fix high-severity CodeQL alert

```graphql
mutation CreateSecurityTask {
  agentAssignment(input: {
    repositoryId: "R_kgDOPjJ9Hg"
    
    title: "Fix HIGH severity XSS vulnerability in src/security/core.py"
    
    description: """
# 🔴 URGENT: High Severity Security Fix

## Alert Details
- **Type**: Cross-Site Scripting (XSS)
- **Severity**: HIGH
- **File**: `src/security/core.py`
- **Line**: 127
- **CWE**: CWE-79 (Improper Neutralization of Input)

## Vulnerability Description
User-controlled data flows into HTML output without proper sanitization.
The `sanitize_content()` function does not escape JavaScript URLs, allowing
`javascript:` protocol URLs to bypass filtering.

## Attack Vector
```python
malicious_input = 'Click here'
# Current code allows this to pass through unsanitized
```

## Required Fix
1. Add XSS pattern detection for `javascript:` URLs
2. Add test cases for all common XSS patterns
3. Run security scanner to verify fix
4. Document pattern in security guide

## References
- CodeQL Alert: https://github.com/Aries-Serpent/_codex_/security/code-scanning/alerts/1234
- CWE-79: https://cwe.mitre.org/data/definitions/79.html
- Security Policy: `SECURITY.md`
"""
    
    instructions: """
⚠️ SECURITY PRIORITY: Complete this task immediately.

1. **Understand the Vulnerability**
   - Read CodeQL alert details
   - Review affected code in `src/security/core.py`
   - Understand the data flow path

2. **Implement Fix**
   - Add XSS pattern list (javascript:, data:, vbscript:, etc.)
   - Update `sanitize_content()` to check these patterns
   - Ensure fix doesn't break legitimate use cases
   - Follow OWASP XSS Prevention Cheat Sheet

3. **Test Thoroughly**
   - Add test cases for all XSS patterns (min 10 test cases)
   - Test edge cases (case-insensitivity, URL encoding, etc.)
   - Run security scanner: `bandit -r src/security/`
   - Verify CodeQL alert is resolved

4. **Documentation**
   - Add docstring explaining XSS prevention
   - Update `SECURITY.md` with new security measure
   - Add inline comments for complex logic

5. **Commit and Report**
   - Commit with message: "security: Fix HIGH severity XSS in sanitize_content (CWE-79)"
   - Open PR with security label
   - Request review from @security-team

DO NOT skip testing. Security fixes require exhaustive validation.
"""
    
    files: [
      "src/security/core.py",
      "tests/security/test_xss_prevention.py",
      "SECURITY.md"
    ]
  }) {
    agentRun {
      id
      status
      repositoryName
    }
  }
}
```

---

## REST API Alternatives

### Using create_pull_request_with_copilot

**Note**: This is a tool available to GitHub Copilot Agent, not a public REST API endpoint.

```python
# Pseudo-code for GitHub Copilot Agent tool usage

# Tool: github-coding-agent-create-pull-request
# Creates a PR with Copilot Agent instructions

result = github_coding_agent_create_pull_request(
    owner="Aries-Serpent",
    repo="_codex_",
    title="Fix test failures in PR #3248",
    body="""
# Automated Fix: PR #3248 Test Failures

This PR addresses the 25 test failures identified in PR #3248.

## Changes Made
- Fixed quantum memory API mismatches
- Updated isinstance() calls for Python 3.12 compatibility
- Aligned MLflow configuration
- Added tokenization auto-load fallbacks

## Testing
- ✅ All 25 tests now pass
- ✅ Coverage maintained at 90%
- ✅ Code quality checks pass (ruff, mypy, black)

## References
- Parent PR: #3248
- Resolution patterns: `.codex/PR_3248_RESOLUTION_PATTERNS.md`
""",
    head="copilot/fix-pr-3248-test-failures",
    base="main",
    draft=False,
    agent_instructions="""
Follow the Investigation Protocol:
1. Analyze test failures
2. Apply systematic fixes
3. Validate with pytest
4. Update documentation

Use patterns from `.codex/PR_3248_RESOLUTION_PATTERNS.md`.
"""
)
```

---

## PR Comment @copilot Examples

### Example 1: Fix Request via PR Comment

**Location**: PR #3248 comment

```markdown
@copilot Fix the 25 test failures in this PR following the Investigation Protocol.

## Requirements
1. Analyze all test failure logs from the latest CI run
2. Apply fixes systematically (one category at a time)
3. Run tests after each fix to validate
4. Commit incrementally with clear messages
5. Update documentation for any API changes

## Reference Files
- Resolution patterns: `.codex/PR_3248_RESOLUTION_PATTERNS.md`
- Policy: `.codex/CODEBASE_AGENCY_POLICY.md`

## Testing Commands
```bash
# Run specific test file
pytest tests/cognitive_brain/quantum/test_memory_errors.py -v

# Run all failing tests
pytest --lf -v

# Check coverage
pytest --cov=src --cov-report=term-missing
```

Please provide incremental updates as you fix each category of failures.
```

**Expected**: Copilot Agent will create commits fixing the failures incrementally.

---

### Example 2: Code Review Request

**Location**: PR #3310 comment

```markdown
@copilot Review the security fix in `src/security/core.py` and verify it addresses the XSS vulnerability.

## Verification Checklist
- [ ] XSS patterns are properly escaped
- [ ] Test cases cover all attack vectors
- [ ] Performance impact is minimal
- [ ] No regressions in existing functionality
- [ ] Documentation is updated

## Security Patterns to Check
1. `javascript:` URLs
2. `data:` URLs with base64
3. `on*` event handlers (`onclick`, `onerror`, etc.)
4. `<script>` tags (case-insensitive)
5. HTML entity encoding edge cases

If any issues found, please fix them in this PR.
```

**Expected**: Copilot Agent will review the code and either approve or suggest fixes.

---

### Example 3: Documentation Generation

**Location**: PR #2671 comment

```markdown
@copilot Generate comprehensive API documentation for the new MCP tools added in this PR.

## Documentation Requirements
1. **File**: `docs/reference/GITHUB_MCP_CAPABILITIES_DOCUMENTATION.md`
2. **Format**: Follow existing documentation style
3. **Content for Each Tool**:
   - Tool name and purpose
   - Function signature with types
   - Parameters (required vs optional)
   - Return type and structure
   - Usage example (practical, tested)
   - Common use cases (3-5 examples)
   - Error handling notes
   - Related tools

4. **Additional Sections**:
   - Update capability matrix table
   - Add troubleshooting section
   - Include performance notes

## Files to Document
- New tools in `src/mcp/github_tools.py`
- Examples in `examples/mcp/`

Please commit the documentation with message: "docs: Add API documentation for new MCP tools"
```

**Expected**: Copilot Agent will generate comprehensive documentation and commit it.

---

## Best Practices

### DO ✅

1. **Provide Clear Context**
   - Link to relevant files, docs, and issues
   - Explain the "why" not just the "what"
   - Include success criteria

2. **Break Down Complex Tasks**
   - Split large tasks into smaller sub-tasks
   - Provide step-by-step instructions
   - Define validation checkpoints

3. **Reference Existing Patterns**
   - Point to similar code in the repo
   - Reference documentation and guides
   - Link to resolution patterns

4. **Include Testing Instructions**
   - Provide specific test commands
   - Define expected outcomes
   - Include validation steps

5. **Set Clear Expectations**
   - Define "done" criteria
   - Specify commit message format
   - Indicate review requirements

### DON'T ❌

1. **Don't Be Vague**
   - ❌ "Fix the tests"
   - ✅ "Fix the 25 test failures in PR #3248 following patterns in `.codex/PR_3248_RESOLUTION_PATTERNS.md`"

2. **Don't Skip Context**
   - ❌ "Update docs"
   - ✅ "Update MCP documentation to include 15 new GitHub Actions tools (see changelog)"

3. **Don't Assume Knowledge**
   - ❌ "Use the standard pattern"
   - ✅ "Follow the testing pattern in `tests/test_example.py` lines 45-67"

4. **Don't Forget Security**
   - ❌ "Just make it work"
   - ✅ "Ensure all user input is sanitized per SECURITY.md guidelines"

5. **Don't Ignore Edge Cases**
   - ❌ "Handle the happy path"
   - ✅ "Test edge cases: empty input, special characters, max length, null values"

---

## GraphQL Query for Repository ID

```graphql
query GetRepositoryId {
  repository(owner: "Aries-Serpent", name: "_codex_") {
    id
    nameWithOwner
    databaseId
  }
}
```

**Response**:
```json
{
  "data": {
    "repository": {
      "id": "R_kgDOPjJ9Hg",
      "nameWithOwner": "Aries-Serpent/_codex_",
      "databaseId": 1040037790
    }
  }
}
```

**Via GitHub CLI**:
```bash
gh api repos/Aries-Serpent/_codex_ --jq .node_id
# Output: R_kgDOPjJ9Hg
```

---

## Monitoring Agent Task Status

```graphql
query GetAgentRunStatus($runId: ID!) {
  node(id: $runId) {
    ... on AgentRun {
      id
      status
      title
      description
      createdAt
      updatedAt
      completedAt
      branch
      pullRequest {
        number
        title
        url
        state
      }
      events {
        nodes {
          ... on AgentRunEvent {
            id
            type
            createdAt
            message
          }
        }
      }
    }
  }
}
```

**Variables**:
```json
{
  "runId": "AR_kwDOPjJ9Hs4AABCD"
}
```

---

## Troubleshooting

### Issue: "Repository ID not found"

**Solution**: Ensure you're using the GraphQL node ID, not the database ID
```bash
# Wrong: 1040037790 (database ID)
# Right: R_kgDOPjJ9Hg (node ID)

gh api repos/Aries-Serpent/_codex_ --jq .node_id
```

---

### Issue: "agentAssignment not available"

**Solution**: This mutation is only available in GitHub Copilot Workspace
- Use `@copilot` mentions in PR comments instead
- Or use `github-coding-agent-create-pull-request` tool

---

### Issue: "Permission denied"

**Solution**: Ensure GitHub token has required scopes
- `repo` (full control)
- `workflow` (if modifying Actions)
- Copilot access (for agentAssignment)

---

## References

- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [GitHub Copilot Agent Docs](https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide)
- [MCP Capability Matrix](./MCP_CAPABILITY_MATRIX.md)

---

**Status**: ✅ Production-Ready  
**Version**: 1.0.0  
**Last Updated**: 2026-02-17T11:21:00Z
