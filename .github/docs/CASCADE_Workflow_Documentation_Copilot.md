# CASCADE Copilot PR Review Workflow Documentation

**Document Version:** 1.0  
**Last Updated:** 2025-12-22  
**Maintained By:** mbaetiong

---

## Table of Contents

1. [Overview](#overview)
2. [Workflow Architecture](#workflow-architecture)
3. [Workflow Triggers](#workflow-triggers)
4. [Workflow Steps](#workflow-steps)
5. [Changed Files Detection](#changed-files-detection)
6. [Python Script Execution](#python-script-execution)
7. [CASCADE Integration](#cascade-integration)
8. [Environment Variables](#environment-variables)
9. [Permissions](#permissions)
10. [Error Handling](#error-handling)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The **Copilot CASCADE PR Review Workflow** is an automated GitHub Actions workflow designed to perform intelligent code reviews on pull requests using GitHub Copilot's AI capabilities. This workflow integrates with the CASCADE (Cascading Automated Source Code Analysis, Documentation, and Enhancement) system to provide comprehensive, context-aware code reviews.

### Key Features

- **Automated PR Reviews**: Automatically triggered on pull request events
- **Intelligent Code Analysis**: Leverages GitHub Copilot for AI-powered code review
- **Changed Files Detection**: Identifies and analyzes only modified files
- **CASCADE Integration**: Integrates with the broader CASCADE ecosystem
- **Python-Based Processing**: Uses custom Python scripts for advanced analysis
- **Configurable Review Levels**: Supports multiple review depth levels

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Pull Request Event                        │
│           (opened, synchronize, reopened)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Workflow Triggered                          │
│            (copilot-cascade-review.yml)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Checkout Repository Code                        │
│                  (actions/checkout@v4)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            Detect Changed Files in PR                        │
│              (tj-actions/changed-files@v45)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Setup Python Environment                        │
│                  (actions/setup-python@v5)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         Install Python Dependencies                          │
│              (PyGithub, requests, etc.)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│      Execute CASCADE Copilot Review Script                   │
│        (.github/scripts/cascade_copilot_review.py)           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│        GitHub Copilot API Analysis & Review                  │
│          (AI-Powered Code Review Generation)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          Post Review Comments on PR                          │
│            (via GitHub API)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Workflow Triggers

The workflow is triggered by the following pull request events:

### Event Types

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
```

| Event Type | Description | When It Fires |
|------------|-------------|---------------|
| `opened` | PR is newly created | When a developer creates a new pull request |
| `synchronize` | New commits pushed to PR | When additional commits are added to an existing PR |
| `reopened` | Previously closed PR is reopened | When a closed PR is reopened for further work |

### Trigger Examples

- **New PR Created**: Developer opens PR #123 → Workflow runs
- **Update to Existing PR**: Developer pushes new commit to PR #123 → Workflow runs
- **PR Reopened**: Developer reopens previously closed PR #123 → Workflow runs

---

## Workflow Steps

### Step 1: Checkout Repository

```yaml
- name: Checkout code
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

**Purpose**: Clones the repository code to the GitHub Actions runner

**Configuration**:
- `fetch-depth: 0`: Fetches complete git history for accurate file comparison
- Uses latest stable version (v4) of checkout action

**Output**: Complete repository codebase available in workspace

---

### Step 2: Detect Changed Files

```yaml
- name: Get changed files
  id: changed-files
  uses: tj-actions/changed-files@v45
  with:
    separator: ','
```

**Purpose**: Identifies all files modified in the pull request

**Configuration**:
- **Action**: `tj-actions/changed-files@v45`
- **Separator**: Comma-separated list for easy parsing
- **Output ID**: `changed-files` for reference in subsequent steps

**Outputs**:
- `all_changed_files`: Comma-separated list of all modified file paths
- `any_changed`: Boolean indicating if any files changed
- `added_files`: List of newly added files
- `modified_files`: List of modified files
- `deleted_files`: List of deleted files

**Example Output**:
```
src/main.py,tests/test_main.py,.github/workflows/ci.yml
```

---

### Step 3: Setup Python Environment

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
```

**Purpose**: Configures Python runtime environment for script execution

**Configuration**:
- **Python Version**: 3.11 (stable, modern features)
- **Action Version**: v5 (latest stable)

**Features**:
- Automatic caching of pip dependencies
- Cross-platform compatibility (Linux, macOS, Windows)
- Fast setup with pre-installed runners

---

### Step 4: Install Python Dependencies

```yaml
- name: Install dependencies
  run: |
    pip install PyGithub requests
```

**Purpose**: Installs required Python packages for the review script

**Dependencies**:

| Package | Version | Purpose |
|---------|---------|---------|
| `PyGithub` | Latest | GitHub API interaction |
| `requests` | Latest | HTTP requests to Copilot API |

**Additional Implicit Dependencies**:
- `json`: JSON parsing (built-in)
- `os`: Environment variable access (built-in)
- `sys`: System operations (built-in)

---

### Step 5: Execute CASCADE Copilot Review Script

```yaml
- name: Run Copilot CASCADE Review
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    CHANGED_FILES: ${{ steps.changed-files.outputs.all_changed_files }}
    PR_NUMBER: ${{ github.event.pull_request.number }}
    REPOSITORY: ${{ github.repository }}
  run: |
    python .github/scripts/cascade_copilot_review.py
```

**Purpose**: Executes the main Python script that performs the AI-powered review

**Environment Variables Passed**:
- `GITHUB_TOKEN`: Authentication token for GitHub API
- `CHANGED_FILES`: Comma-separated list of modified files
- `PR_NUMBER`: Pull request number
- `REPOSITORY`: Full repository name (owner/repo)

**Script Location**: `.github/scripts/cascade_copilot_review.py`

---

## Changed Files Detection

### Detection Mechanism

The workflow uses `tj-actions/changed-files@v45` to detect file changes by:

1. **Git Diff Analysis**: Compares PR head with base branch
2. **Path Resolution**: Resolves absolute paths for all files
3. **Change Type Classification**: Categorizes changes (added, modified, deleted)

### File Change Categories

```python
# Example of categorized changes
{
    "added": ["new_feature.py", "tests/test_new_feature.py"],
    "modified": ["src/main.py", "README.md"],
    "deleted": ["deprecated/old_module.py"],
    "renamed": [{"from": "old_name.py", "to": "new_name.py"}]
}
```

### Integration with Review Script

```python
import os

# In cascade_copilot_review.py
changed_files_str = os.getenv('CHANGED_FILES', '')
changed_files = [f.strip() for f in changed_files_str.split(',') if f.strip()]

# Filter for reviewable files
reviewable_files = [
    f for f in changed_files 
    if f.endswith(('.py', '.js', '.java', '.go', '.rs'))
]
```

### File Filtering Strategy

The review script typically filters files based on:

- **File Extensions**: Only review code files (e.g., `.py`, `.js`, `.java`)
- **Path Exclusions**: Skip generated files, vendor directories, locks
- **Size Limits**: Exclude extremely large files
- **Binary Detection**: Skip binary files

---

## Python Script Execution

### Script: `cascade_copilot_review.py`

#### Core Functionality

```python
#!/usr/bin/env python3
"""
CASCADE Copilot PR Review Script
Performs AI-powered code review using GitHub Copilot
"""

import os
import sys
from github import Github
import requests

def main():
    # 1. Initialize GitHub client
    github_token = os.getenv('GITHUB_TOKEN')
    repository_name = os.getenv('REPOSITORY')
    pr_number = int(os.getenv('PR_NUMBER'))
    changed_files = os.getenv('CHANGED_FILES', '').split(',')
    
    g = Github(github_token)
    repo = g.get_repo(repository_name)
    pr = repo.get_pull(pr_number)
    
    # 2. Fetch file contents
    for file_path in changed_files:
        if not file_path.strip():
            continue
            
        file_content = get_file_content(repo, file_path, pr.head.sha)
        
        # 3. Request Copilot review
        review_result = request_copilot_review(file_path, file_content)
        
        # 4. Post review comments
        post_review_comment(pr, file_path, review_result)

def get_file_content(repo, file_path, sha):
    """Fetch file content from repository"""
    try:
        content = repo.get_contents(file_path, ref=sha)
        return content.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"Error fetching {file_path}: {e}")
        return None

def request_copilot_review(file_path, content):
    """Request AI review from GitHub Copilot"""
    # Implementation details for Copilot API integration
    pass

def post_review_comment(pr, file_path, review):
    """Post review comment to PR"""
    try:
        pr.create_review_comment(
            body=review['comment'],
            path=file_path,
            line=review.get('line', 1)
        )
    except Exception as e:
        print(f"Error posting comment: {e}")

if __name__ == "__main__":
    main()
```

#### Script Workflow

1. **Initialization**: Load environment variables and authenticate
2. **File Retrieval**: Fetch content of changed files from PR
3. **AI Analysis**: Send code to GitHub Copilot for review
4. **Comment Generation**: Format AI feedback as PR comments
5. **Comment Posting**: Submit comments via GitHub API

#### Error Handling

```python
try:
    # Main execution logic
    review_files()
except Exception as e:
    print(f"CASCADE Review Error: {e}")
    sys.exit(1)  # Non-zero exit code signals failure
```

---

## CASCADE Integration

### CASCADE System Overview

CASCADE (Cascading Automated Source Code Analysis, Documentation, and Enhancement) is a comprehensive code quality and automation framework.

### Integration Points

#### 1. Review Context Integration

```python
# CASCADE provides additional context for reviews
cascade_context = {
    "project_standards": load_coding_standards(),
    "architecture_patterns": load_architecture_docs(),
    "previous_reviews": fetch_historical_reviews(),
    "team_preferences": load_team_config()
}
```

#### 2. Multi-Stage Review Process

```
┌──────────────────┐
│  Stage 1: Syntax │
│   & Style Check  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Stage 2: Security│
│   & Vulnerability│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Stage 3: Logic   │
│  & Architecture  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Stage 4: Best    │
│   Practices      │
└──────────────────┘
```

#### 3. Review Categories

The CASCADE system categorizes reviews into:

| Category | Focus Area | Priority |
|----------|-----------|----------|
| **Critical** | Security vulnerabilities, breaking changes | P0 |
| **High** | Logic errors, performance issues | P1 |
| **Medium** | Code style, documentation | P2 |
| **Low** | Suggestions, optimizations | P3 |

#### 4. Feedback Loop

```python
# CASCADE tracks review effectiveness
review_metrics = {
    "comments_addressed": 0,
    "comments_dismissed": 0,
    "false_positives": 0,
    "missed_issues": 0,
    "review_time": 0
}

# Continuous improvement through metrics
update_cascade_model(review_metrics)
```

---

## Environment Variables

### Required Variables

| Variable | Description | Source | Example |
|----------|-------------|--------|---------|
| `GITHUB_TOKEN` | GitHub API authentication | Auto-provided by Actions | `ghp_xxxxx...` |
| `CHANGED_FILES` | Comma-separated file list | Changed files step output | `src/a.py,src/b.py` |
| `PR_NUMBER` | Pull request number | GitHub context | `123` |
| `REPOSITORY` | Full repository name | GitHub context | `owner/repo` |

### Optional Variables

| Variable | Description | Default | Usage |
|----------|-------------|---------|-------|
| `REVIEW_LEVEL` | Depth of review | `standard` | `quick\|standard\|deep` |
| `MAX_FILES` | Maximum files to review | `50` | Prevent API rate limits |
| `COPILOT_MODEL` | AI model version | `latest` | Specify model version |

### Access in Script

```python
import os

# Required
github_token = os.getenv('GITHUB_TOKEN')
if not github_token:
    raise ValueError("GITHUB_TOKEN is required")

# Optional with defaults
review_level = os.getenv('REVIEW_LEVEL', 'standard')
max_files = int(os.getenv('MAX_FILES', '50'))
```

---

## Permissions

### GitHub Token Permissions

The workflow requires the following permissions:

```yaml
permissions:
  contents: read          # Read repository content
  pull-requests: write    # Post review comments
  issues: write          # Optional: Create issues for critical findings
```

### Token Scope Requirements

- **Read Access**: Fetch file contents, PR metadata
- **Write Access**: Post comments, request changes
- **API Rate Limits**: ~5000 requests/hour for authenticated requests

### Security Considerations

1. **Token Storage**: Use GitHub Secrets, never hardcode
2. **Scope Minimization**: Request only necessary permissions
3. **Token Rotation**: Regularly rotate personal access tokens
4. **Audit Logging**: Monitor token usage for suspicious activity

---

## Error Handling

### Workflow-Level Error Handling

```yaml
- name: Run Copilot CASCADE Review
  continue-on-error: true  # Don't fail PR on review error
  run: |
    python .github/scripts/cascade_copilot_review.py || echo "Review failed, check logs"
```

### Script-Level Error Handling

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    perform_review()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    sys.exit(0)  # Don't block PR
except RateLimitExceededException as e:
    logger.warning(f"Rate limit hit: {e}")
    post_rate_limit_warning()
    sys.exit(0)
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    sys.exit(1)  # Signal failure
```

### Common Error Scenarios

| Error | Cause | Resolution |
|-------|-------|------------|
| **401 Unauthorized** | Invalid token | Check token permissions |
| **404 Not Found** | File deleted/moved | Handle gracefully |
| **403 Rate Limited** | Too many API calls | Implement backoff/retry |
| **500 Server Error** | GitHub API issue | Retry with exponential backoff |

---

## Best Practices

### 1. Review Scope Management

- **Focus on Changed Lines**: Only review modified code
- **Batch Processing**: Group related files together
- **Time Limits**: Set maximum review duration

### 2. Comment Quality

```python
# Good: Specific, actionable feedback
comment = """
**Security Issue**: SQL injection vulnerability detected on line 45.

**Recommendation**: Use parameterized queries:
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Priority**: Critical
"""

# Bad: Vague, unhelpful
comment = "This code has issues. Please fix."
```

### 3. Performance Optimization

- **Parallel Processing**: Review multiple files concurrently
- **Caching**: Cache file contents and API responses
- **Incremental Reviews**: Only re-review changed sections

### 4. Continuous Improvement

- Track review metrics
- Collect developer feedback
- Regular model updates
- A/B testing for improvements

---

## Troubleshooting

### Issue: Workflow Not Triggering

**Symptoms**: No workflow run appears after PR creation

**Possible Causes**:
1. Workflow file not on default branch
2. YAML syntax errors
3. Repository permissions

**Solutions**:
```bash
# Validate YAML syntax
yamllint .github/workflows/copilot-cascade-review.yml

# Check workflow status
gh workflow list
gh workflow view "Copilot CASCADE Review"
```

### Issue: Python Script Errors

**Symptoms**: Workflow fails at script execution step

**Debugging Steps**:
```bash
# Test locally
export GITHUB_TOKEN="your_token"
export CHANGED_FILES="file1.py,file2.py"
export PR_NUMBER="123"
export REPOSITORY="owner/repo"

python .github/scripts/cascade_copilot_review.py
```

### Issue: No Review Comments Posted

**Symptoms**: Script runs successfully but no comments appear

**Checklist**:
- [ ] Verify `pull-requests: write` permission
- [ ] Check token validity: `gh auth status`
- [ ] Confirm PR is not from a fork (limited permissions)
- [ ] Review API rate limits: `gh api rate_limit`

### Issue: Rate Limiting

**Symptoms**: HTTP 403 errors with "rate limit exceeded"

**Mitigation**:
```python
from time import sleep
import requests

def make_api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 403:
            sleep(2 ** attempt)  # Exponential backoff
            continue
        return response
    raise Exception("Rate limit exceeded after retries")
```

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Copilot API](https://docs.github.com/en/copilot)
- [PyGithub Library](https://pygithub.readthedocs.io/)
- [CASCADE Project Documentation](../_codex_/CASCADE/)

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-22 | mbaetiong | Initial comprehensive documentation |

---

## Support & Contact

For questions or issues related to this workflow:

- **Repository Issues**: [GitHub Issues](../../issues)
- **Documentation**: [CASCADE Docs](./)
- **Maintainer**: @mbaetiong

---

*This document is part of the CASCADE automated code review system.*
