# QA Walkthrough GitHub Action - Usage Guide

## Overview

The **Codebase QA Walkthrough** GitHub Action provides automated quality assurance analysis that can be triggered by both AI agents and human administrators.

## Trigger Methods

### 1. Manual Trigger (Human Admin)

**Via GitHub Web UI:**
1. Navigate to **Actions** → **Codebase QA Walkthrough**
2. Click **Run workflow**
3. Configure options:
   - Review depth: quick, standard, or comprehensive
   - Target ref: branch, tag, or commit SHA (optional)
   - PR number: specific PR to review (optional)
   - Focus areas: security, performance, testing, documentation
   - Fail on critical: stop workflow if critical issues found
   - Post comment: automatically comment on PR with results

**Via GitHub CLI:**
```bash
# Standard review on current branch
gh workflow run codebase-qa-walkthrough.yml

# Comprehensive review on specific PR
gh workflow run codebase-qa-walkthrough.yml \
  -f review_depth=comprehensive \
  -f pr_number=123 \
  -f fail_on_critical=true

# Quick security-focused review
gh workflow run codebase-qa-walkthrough.yml \
  -f review_depth=quick \
  -f focus_areas=security \
  -f target_ref=feature-branch
```

### 2. AI Agent Trigger (Comment-Based)

**On any Pull Request or Issue:**

```
@copilot qa walkthrough
```

**Alternative commands:**
```
@copilot qa review
@copilot quality assurance
@copilot qa check quick         # Quick review
@copilot qa check comprehensive # Deep review
```

**How it works:**
1. AI agent or human posts comment with trigger phrase
2. Workflow detects comment and parses command
3. QA analysis runs automatically
4. Results posted as comment on same PR/Issue

### 3. Automatic PR Trigger

Automatically runs on:
- Pull requests opened to `main` or `develop`
- PR synchronize (new commits pushed)
- PR reopened

Configuration in workflow:
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - develop
```

### 4. Workflow Call (From Other Workflows)

**Call from another workflow:**
```yaml
jobs:
  run-qa:
    uses: ./.github/workflows/codebase-qa-walkthrough.yml
    with:
      review_depth: comprehensive
      fail_on_critical: true
      focus_areas: security,performance
```

**Use outputs:**
```yaml
jobs:
  qa:
    uses: ./.github/workflows/codebase-qa-walkthrough.yml
    with:
      review_depth: standard
  
  deploy:
    needs: qa
    if: needs.qa.outputs.critical_issues == '0'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          echo "Quality score: ${{ needs.qa.outputs.overall_score }}"
          echo "Deploying..."
```

## Configuration Options

### Review Depth

- **quick** (5-10 min): Critical security issues, syntax errors only
- **standard** (15-30 min): Security + quality + basic performance + coverage
- **comprehensive** (45-90 min): Full analysis including architecture review

### Focus Areas

Comma-separated list of areas to analyze:
- `security`: Vulnerability scanning, secret detection, dependency checks
- `performance`: Complexity analysis, optimization opportunities
- `testing`: Coverage analysis, test quality assessment
- `documentation`: Docstring completeness, README review

**Examples:**
```bash
# Security only
-f focus_areas=security

# Security and testing
-f focus_areas=security,testing

# All areas (default)
-f focus_areas=security,performance,testing,documentation
```

### Fail on Critical

- `true` (default): Workflow fails if critical issues found (blocks merge)
- `false`: Workflow always succeeds, issues reported but don't block

**Use cases:**
- `true`: Required quality gate before merge
- `false`: Advisory analysis, doesn't block development

### Post Comment

- `true` (default): Posts results as PR/Issue comment
- `false`: No comment posted (useful for silent analysis)

## Output

### Workflow Outputs

When called via `workflow_call`, provides:

```yaml
outputs:
  critical_issues: "2"        # Number of critical issues
  warnings: "15"              # Number of warnings
  overall_score: "73"         # Quality score 0-100
  report_url: "https://..."   # Artifact download URL
```

### Artifact Contents

Downloaded artifact includes:
```
qa-reports-{run_number}/
├── qa-report.md                    # Main report (Markdown)
├── bandit-report.json              # Security (JSON)
├── bandit-report.txt               # Security (Text)
├── safety-report.json              # Dependencies (JSON)
├── pylint-report.json              # Code quality (JSON)
├── ruff-report.json                # Fast linter (JSON)
├── mypy-report.txt                 # Type checking
├── coverage-report.json            # Test coverage (JSON)
├── coverage-report.txt             # Test coverage (Text)
├── coverage-html/                  # Coverage HTML report
├── complexity-report.txt           # Radon complexity
└── maintainability-report.txt      # Maintainability index
```

### Comment Format

When `post_comment: true`, posts this on PR:

```markdown
## 🔍 QA Walkthrough Results

# QA Walkthrough Report

**Generated**: 2026-01-14T06:30:00Z
**Review Depth**: standard
**Trigger**: issue_comment
**Repository**: Aries-Serpent/_codex_
**Ref**: refs/heads/feature-branch

---

## Executive Summary

### Security Analysis
- Critical Issues: 2
- Warnings: 3

### Code Quality
- Issues Found: 15

### Test Coverage
- Coverage: 75%
- Target: 80%
- Status: ⚠️ Below target

---

## Overall Assessment

**Quality Score**: 73/100
**Critical Issues**: 2
**Warnings**: 18
**Test Coverage**: 75%

**Status**: 🔴 Critical Issues Found

---

<details>
<summary>📊 Detailed Metrics</summary>

- **Critical Issues**: 2
- **Warnings**: 18
- **Overall Score**: 73/100
- **Test Coverage**: 75%
- **Review Depth**: standard

</details>

<details>
<summary>⬇️ Download Full Reports</summary>

Download the complete QA analysis from the workflow artifacts.

Included reports:
- 🔒 Security analysis (Bandit, Safety)
- 📊 Code quality (Pylint, Ruff)
- 🧪 Test coverage (HTML report)
- 📈 Complexity analysis

</details>
```

## Integration Examples

### Example 1: Gate Merge on Quality

**Goal**: Prevent merging PRs with critical issues

**.github/workflows/merge-gate.yml:**
```yaml
name: Merge Quality Gate

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  qa-gate:
    uses: ./.github/workflows/codebase-qa-walkthrough.yml
    with:
      review_depth: standard
      fail_on_critical: true      # Blocks merge if issues found
      post_comment: true
```

**Branch protection rule:**
- Require "QA Analysis (standard)" status check to pass

### Example 2: Nightly Comprehensive Analysis

**Goal**: Deep analysis of main branch every night

**.github/workflows/nightly-qa.yml:**
```yaml
name: Nightly QA Analysis

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  comprehensive-qa:
    uses: ./.github/workflows/codebase-qa-walkthrough.yml
    with:
      review_depth: comprehensive
      target_ref: main
      fail_on_critical: false     # Don't fail, just report
      post_comment: false
  
  notify-team:
    needs: comprehensive-qa
    runs-on: ubuntu-latest
    if: needs.comprehensive-qa.outputs.critical_issues != '0'
    steps:
      - name: Notify Slack
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -H 'Content-Type: application/json' \
            -d "{
              \"text\": \"⚠️ Nightly QA found critical issues\",
              \"blocks\": [{
                \"type\": \"section\",
                \"text\": {
                  \"type\": \"mrkdwn\",
                  \"text\": \"*QA Score*: ${{ needs.comprehensive-qa.outputs.overall_score }}/100\n*Critical*: ${{ needs.comprehensive-qa.outputs.critical_issues }}\n*Warnings*: ${{ needs.comprehensive-qa.outputs.warnings }}\"
                }
              }]
            }"
```

### Example 3: Pre-Release Quality Check

**Goal**: Ensure release candidates meet quality standards

**.github/workflows/release-qa.yml:**
```yaml
name: Release QA

on:
  push:
    tags:
      - 'v*'

jobs:
  release-qa:
    uses: ./.github/workflows/codebase-qa-walkthrough.yml
    with:
      review_depth: comprehensive
      target_ref: ${{ github.ref }}
      fail_on_critical: true
      focus_areas: security,testing
  
  create-release:
    needs: release-qa
    if: needs.release-qa.outputs.overall_score >= '80'
    runs-on: ubuntu-latest
    steps:
      - name: Create Release
        run: |
          echo "Quality score: ${{ needs.release-qa.outputs.overall_score }}"
          echo "Creating release..."
          gh release create ${{ github.ref_name }} \
            --title "Release ${{ github.ref_name }}" \
            --notes "Quality Score: ${{ needs.release-qa.outputs.overall_score }}/100"
```

## AI Agent Integration

### For Custom AI Agents

Custom agents can trigger QA walkthrough programmatically:

```python
import requests

def trigger_qa_walkthrough(pr_number: int, depth: str = "standard"):
    """Trigger QA walkthrough on a PR."""
    url = f"https://api.github.com/repos/Aries-Serpent/_codex_/actions/workflows/codebase-qa-walkthrough.yml/dispatches"
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }
    
    data = {
        "ref": "main",
        "inputs": {
            "review_depth": depth,
            "pr_number": str(pr_number),
            "fail_on_critical": "true",
            "post_comment": "true"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 204
```

### For GitHub Copilot Extensions

Copilot extensions can integrate via comment trigger:

```javascript
// In your Copilot extension
async function requestQAReview(prNumber, depth = 'standard') {
  const comment = `@copilot qa walkthrough ${depth}`;
  
  await octokit.issues.createComment({
    owner: 'Aries-Serpent',
    repo: '_codex_',
    issue_number: prNumber,
    body: comment
  });
  
  console.log('QA review requested');
}
```

## Troubleshooting

### Workflow Not Triggering

**Issue**: Comment with `@copilot qa walkthrough` doesn't trigger workflow

**Solutions**:
1. Check comment is on a PR or Issue (not commit comment)
2. Verify workflow file is on default branch
3. Check repository has Actions enabled
4. Verify trigger phrase exactly matches pattern

### Analysis Tools Missing

**Issue**: Tools like `pylint` or `bandit` not found

**Solution**: Workflow automatically installs tools, but if issues persist:
```yaml
- name: Install additional tools
  run: |
    pip install your-tool-here
```

### Low Coverage Reported

**Issue**: Coverage shows 0% but tests exist

**Solutions**:
1. Ensure tests in `tests/` directory
2. Check pytest configuration (`pytest.ini`)
3. Verify test discovery patterns
4. Check workflow paths for test execution

### Critical Issues False Positives

**Issue**: Workflow fails on false positive issues

**Solutions**:
1. Add exceptions to tool configs (`.bandit`, `.ruff.toml`)
2. Use `fail_on_critical: false` for advisory mode
3. Review and update security baselines
4. Create custom quality thresholds

## Advanced Configuration

### Custom Quality Thresholds

Create `.qa-config.yml` in repo root:

```yaml
quality_thresholds:
  code_coverage: 80
  critical_issues: 0
  overall_score: 75

fail_conditions:
  - critical_issues > 0
  - overall_score < 70
  - coverage < 60

tools:
  bandit:
    confidence_level: MEDIUM
    severity_level: MEDIUM
  
  pylint:
    fail_under: 8.0
  
  ruff:
    select: ["E", "F", "W"]
```

### Tool-Specific Configuration

**Bandit (.bandit):**
```yaml
exclude_dirs:
  - /tests/
  - /docs/

skips:
  - B101  # assert_used
  - B601  # paramiko_calls
```

**Ruff (pyproject.toml):**
```toml
[tool.ruff]
select = ["E", "F", "W", "I", "N"]
ignore = ["E501"]  # Line too long
```

## Best Practices

1. **Run Early**: Trigger QA before requesting human review
2. **Use Appropriate Depth**: `quick` for WIP, `comprehensive` for releases
3. **Fix Critical First**: Address security before style
4. **Review Trends**: Track quality scores over time
5. **Automate**: Integrate into CI/CD pipeline
6. **Educate**: Use reports as learning opportunities

## Support

- **Documentation**: [Agent README](../codebase-qa-walkthrough-agent/README.md)
- **Examples**: [Agent Examples](../codebase-qa-walkthrough-agent/examples/)
- **Issues**: Report workflow issues on repository

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-14  
**Maintained By**: admin-automation-agent
