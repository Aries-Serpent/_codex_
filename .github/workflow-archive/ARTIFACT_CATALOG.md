# GitHub Actions Artifact Catalog

**Purpose**: Complete catalog of all GitHub Actions workflow artifacts for retrieval and analysis by Copilot agent sessions

**Last Updated**: 2025-12-28  
**Version**: 1.0.0

---

## 📋 Overview

This document catalogs all artifacts produced by GitHub Actions workflows in this repository, providing:
- Artifact names and locations
- Content descriptions
- Retrieval methods for Copilot agent sessions
- Usage examples and analysis commands

**Total Active Workflows**: 49  
**Workflows Producing Artifacts**: 20+  
**Artifact Types**: Reports, Metrics, Test Results, Audits, Coverage Data

---

## 🔍 Quick Reference: Artifact Retrieval

### Method 1: GitHub CLI (Recommended for Copilot Sessions)

```bash
# List recent artifacts
gh run list --limit 10

# Get artifacts from specific run
gh run view <run-id> --log

# Download artifact
gh run download <run-id> --name <artifact-name>

# Download all artifacts from latest run
gh run download $(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')
```

### Method 2: GitHub API

```bash
# List artifacts for repository
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/Aries-Serpent/_codex_/actions/artifacts

# Download specific artifact
curl -L -H "Authorization: token $GITHUB_TOKEN" \
  -o artifact.zip \
  https://api.github.com/repos/Aries-Serpent/_codex_/actions/artifacts/<artifact-id>/zip
```

### Method 3: Direct File Access (Post-Workflow)

Some artifacts are committed to the repository:
- `reports/` directory
- `audit_artifacts/` directory  
- `.codex/reports/` directory

---

## 📊 Artifact Catalog by Category

### 1. Security & Code Quality Artifacts

#### 1.1 Code Quality Report
- **Workflow**: `code-quality.yml`
- **Artifact Name**: `code-quality-report`
- **Path**: `.codex/reports/smells.json`
- **Content**: Code smell detection results
- **Format**: JSON
- **Retention**: 90 days
- **Size**: ~50-200 KB
- **Retrieval**:
  ```bash
  gh run download --name code-quality-report
  cat .codex/reports/smells.json | jq '.'
  ```

#### 1.2 AST Similarity Report
- **Workflow**: `code-quality.yml`
- **Artifact Name**: `ast-similarity-report`
- **Path**: `audit_artifacts/ast_similarity.json`
- **Content**: Abstract Syntax Tree similarity analysis
- **Format**: JSON
- **Retrieval**:
  ```bash
  gh run download --name ast-similarity-report
  cat audit_artifacts/ast_similarity.json | jq '.similarities | length'
  ```

#### 1.3 CodeQL Security Scanning
- **Workflow**: `codeql-analysis.yml`
- **Artifact**: Results uploaded to GitHub Security tab
- **View**: Navigate to Security → Code scanning alerts
- **API Access**:
  ```bash
  gh api repos/Aries-Serpent/_codex_/code-scanning/alerts
  ```

---

### 2. Test & Coverage Artifacts

#### 2.1 Coverage Report
- **Workflow**: `coverage_report.yml`
- **Artifact Name**: `coverage-artifacts`
- **Path**: 
  - `htmlcov/` (HTML report)
  - `coverage.xml` (XML format)
  - `.coverage` (SQLite database)
- **Content**: Test coverage data
- **Format**: Multiple formats (HTML, XML, SQLite)
- **Retention**: 90 days
- **Retrieval**:
  ```bash
  gh run download --name coverage-artifacts
  # View summary
  coverage report --show-missing
  # Generate HTML
  coverage html
  open htmlcov/index.html
  ```

#### 2.2 Test Results
- **Workflow**: `copilot-self-evolution.yml`
- **Artifact Name**: `test-results`
- **Path**: `.github/copilot-evolution/data/test_results.json`
- **Content**: Test execution results, pass/fail counts
- **Format**: JSON
- **Retrieval**:
  ```bash
  gh run download --name test-results
  cat .github/copilot-evolution/data/test_results.json | \
    jq '{passed: .passed, failed: .failed, total: .total}'
  ```

#### 2.3 Pre-Release Test Results
- **Workflow**: `pre-release-deployment.yml`
- **Artifact Name**: `test-results`
- **Path**: `test_results.txt`
- **Content**: Pre-release test execution log
- **Format**: Plain text
- **Retrieval**:
  ```bash
  gh run download --name test-results
  cat test_results.txt | grep -E "PASSED|FAILED|ERROR"
  ```

---

### 3. CI/CD Health & Monitoring Artifacts

#### 3.1 Workflow Trends
- **Workflow**: `ci-health-monitor.yml`
- **Artifact Name**: `workflow-trends-<run-number>`
- **Path**: `/tmp/workflow_trend.csv`
- **Content**: CI health metrics over time
- **Format**: CSV
- **Columns**: `timestamp,active_count,disabled_count,target,variance,health_score`
- **Retention**: 30 days
- **Retrieval**:
  ```bash
  gh run download --name workflow-trends-12345
  cat workflow_trend.csv | column -t -s,
  # Plot trend
  python -c "import pandas as pd; df=pd.read_csv('workflow_trend.csv'); \
    print(df.describe())"
  ```

#### 3.2 Post-Merge Validation Report
- **Workflow**: `post-merge-validation-optimized.yml`
- **Artifact Name**: `modernization-report`
- **Path**: 
  - `modernization_summary.json`
  - `import_verification.log`
- **Content**: Post-merge validation results
- **Format**: JSON + log files
- **Retrieval**:
  ```bash
  gh run download --name modernization-report
  cat modernization_summary.json | jq '.status'
  ```

---

### 4. Audit & Analysis Artifacts

#### 4.1 Audit Results
- **Workflow**: `audit-improvement-pipeline.yml`
- **Artifact Name**: `audit-results`
- **Path**: 
  - `audit_run_manifest.json`
  - `audit_artifacts/capabilities_scored.json`
  - `audit_artifacts/gaps.json`
  - `audit_artifacts/evidence/`
- **Content**: Comprehensive capability audit
- **Format**: JSON + evidence files
- **Retention**: 90 days
- **Size**: 1-50 MB (varies with evidence)
- **Retrieval**:
  ```bash
  gh run download --name audit-results
  # View capability scores
  cat audit_artifacts/capabilities_scored.json | \
    jq '.capabilities[] | select(.score > 80) | {id, score}'
  # Check gaps
  cat audit_artifacts/gaps.json | jq '.low_maturity | length'
  ```

#### 4.2 Determinism Audit
- **Workflow**: `determinism.yml`
- **Artifact Name**: `determinism-audit-<run-number>`
- **Path**:
  - `determinism_report.json`
  - `seed_variations.csv`
  - `run_comparisons/`
- **Content**: Determinism validation results
- **Format**: JSON + CSV
- **Retrieval**:
  ```bash
  gh run download --name determinism-audit-12345
  cat determinism_report.json | jq '.deterministic_rate'
  ```

#### 4.3 Duplicate Detection Report
- **Workflow**: `detect-duplicates.yml`
- **Artifact Name**: `duplicate-detection-report`
- **Path**: `.codex/duplicate_analysis_pr/`
- **Content**: Code duplication analysis
- **Format**: JSON + markdown reports
- **Retrieval**:
  ```bash
  gh run download --name duplicate-detection-report
  cat .codex/duplicate_analysis_pr/summary.json | jq '.duplicates_found'
  ```

---

### 5. Agent & Automation Artifacts

#### 5.1 Agent Execution Report
- **Workflow**: `agent-runtime.yml`
- **Artifact Name**: `agent-execution-report-<run-id>`
- **Path**: `.agents/reports/`
- **Content**: Agent execution logs and results
- **Format**: JSON + log files
- **Retention**: 30 days
- **Retrieval**:
  ```bash
  gh run download --name agent-execution-report-123456789
  cat .agents/reports/execution_summary.json | jq '.tasks_completed'
  ```

#### 5.2 Agent State
- **Workflow**: `autonomous-agent.yml`
- **Artifact Name**: `agent-state-<run-number>`
- **Path**: `.codex/agent_state/`
- **Content**: Agent state snapshots
- **Format**: JSON
- **Retrieval**:
  ```bash
  gh run download --name agent-state-12345
  cat .codex/agent_state/latest.json | jq '.current_phase'
  ```

#### 5.3 Evolution State
- **Workflow**: `copilot-self-evolution.yml`
- **Artifact Name**: `evolution-state`
- **Path**:
  - `.github/copilot-evolution/data/evolution_state.json`
  - `.github/copilot-evolution/data/iteration_log.jsonl`
- **Content**: Copilot evolution tracking
- **Format**: JSON + JSONL
- **Retrieval**:
  ```bash
  gh run download --name evolution-state
  cat .github/copilot-evolution/data/evolution_state.json | \
    jq '{iteration: .iteration, improvements: .improvements | length}'
  ```

---

### 6. Documentation & Visual Artifacts

#### 6.1 Link Check Report
- **Workflow**: `documentation-link-checker.yml`
- **Artifact Name**: `link-check-report`
- **Path**: `link-check-report.json`
- **Content**: Broken link detection results
- **Format**: JSON
- **Retrieval**:
  ```bash
  gh run download --name link-check-report
  cat link-check-report.json | jq '.broken_links | length'
  ```

#### 6.2 HTML Visual Baseline
- **Workflow**: `html_visual_baseline.yml`
- **Artifact Name**: `status-html-visual`
- **Path**:
  - `screenshots/baseline/`
  - `baseline_manifest.json`
- **Content**: Visual regression testing baselines
- **Format**: PNG images + JSON manifest
- **Retention**: 180 days (long retention for baselines)
- **Retrieval**:
  ```bash
  gh run download --name status-html-visual
  ls screenshots/baseline/*.png
  ```

#### 6.3 HTML Screenshots
- **Workflow**: `html_visual_regression.yml`
- **Artifact Name**: `status-html-screenshots`
- **Path**:
  - `screenshots/current/`
  - `screenshots/diff/`
  - `regression_report.json`
- **Content**: Visual regression test results
- **Format**: PNG images + JSON report
- **Retrieval**:
  ```bash
  gh run download --name status-html-screenshots
  cat regression_report.json | jq '.differences_found'
  ```

---

### 7. Specialized Artifacts

#### 7.1 Cascade Review Results
- **Workflow**: `copilot-cascade-review.yml`
- **Artifact Name**: `cascade-review-results`
- **Path**: `cascade_results.json`
- **Content**: Cascading code review analysis
- **Format**: JSON
- **Retrieval**:
  ```bash
  gh run download --name cascade-review-results
  cat cascade_results.json | jq '.reviews[] | {file, issues: .issues | length}'
  ```

#### 7.2 Pattern Report
- **Workflow**: `copilot-self-evolution.yml`
- **Artifact Name**: `pattern-report`
- **Path**: `.github/copilot-evolution/data/pattern_report.json`
- **Content**: Detected code patterns and anti-patterns
- **Format**: JSON
- **Retrieval**:
  ```bash
  gh run download --name pattern-report
  cat .github/copilot-evolution/data/pattern_report.json | \
    jq '.patterns | group_by(.type) | map({type: .[0].type, count: length})'
  ```

#### 7.3 Repository Organization
- **Workflow**: `repo-organization.yml`
- **Artifact Name**: Multiple artifacts
- **Content**: Repository structure analysis
- **Retrieval**: Check workflow for latest artifact names

#### 7.4 Genesis Validation
- **Workflow**: `genesis-bootstrap.yml`
- **Artifact Name**: `genesis-validation-report`
- **Path**: `.codex/genesis_validation.json`
- **Content**: Genesis template validation results
- **Format**: JSON
- **Retrieval**:
  ```bash
  gh run download --name genesis-validation-report
  cat .codex/genesis_validation.json | jq '.validation_status'
  ```

---

## 🤖 Copilot Agent Retrieval Patterns

### Pattern 1: Latest Artifact Analysis

```python
# Python script for Copilot agent sessions
import subprocess
import json

def get_latest_artifact(artifact_name_pattern):
    """Retrieve latest artifact matching pattern."""
    # Get latest run ID
    result = subprocess.run(
        ["gh", "run", "list", "--limit", "1", "--json", "databaseId"],
        capture_output=True, text=True
    )
    run_id = json.loads(result.stdout)[0]["databaseId"]
    
    # Download artifact
    subprocess.run(["gh", "run", "download", str(run_id), "--name", artifact_name_pattern])
    
    return f"Downloaded artifacts from run {run_id}"

# Usage
get_latest_artifact("code-quality-report")
```

### Pattern 2: Trend Analysis Across Multiple Runs

```bash
# Bash script for analyzing trends
for run_id in $(gh run list --limit 10 --json databaseId --jq '.[].databaseId'); do
  gh run download $run_id --name workflow-trends-* 2>/dev/null || true
done

# Combine all trend files
cat workflow_trend*.csv | sort | uniq > combined_trends.csv

# Analyze
python -c "
import pandas as pd
df = pd.read_csv('combined_trends.csv')
print('Health Score Trend:')
print(df.groupby('timestamp')['health_score'].mean())
"
```

### Pattern 3: Artifact Comparison

```bash
# Compare two audit runs
gh run download <run1> --name audit-results
mv audit_artifacts audit_artifacts_run1

gh run download <run2> --name audit-results
mv audit_artifacts audit_artifacts_run2

# Compare capability scores
diff <(cat audit_artifacts_run1/capabilities_scored.json | jq '.capabilities | sort_by(.id)') \
     <(cat audit_artifacts_run2/capabilities_scored.json | jq '.capabilities | sort_by(.id)')
```

---

## 📦 Artifact Retention Policy

| Artifact Type | Retention | Rationale |
|---------------|-----------|-----------|
| Test Results | 30 days | Historical analysis, recent runs most relevant |
| Coverage Reports | 90 days | Trend analysis over quarters |
| Security Scans | Permanent | Security audit trail |
| Audit Results | 90 days | Compliance and improvement tracking |
| Visual Baselines | 180 days | Long-term visual regression detection |
| Agent Logs | 30 days | Operational monitoring |
| CI Health Metrics | 30 days | Trend analysis |
| Code Quality | 90 days | Quality improvement tracking |

**Note**: GitHub Actions has a default artifact retention of 90 days. Individual workflows may override this.

---

## 🔄 Artifact Lifecycle

### 1. Creation
- Workflow executes → Generates artifact → `actions/upload-artifact@v6`

### 2. Storage
- Stored in GitHub Actions artifact storage
- Compressed automatically
- Associated with workflow run

### 3. Retrieval
- Available via GitHub UI, CLI, or API
- Downloadable as ZIP archive
- Can be downloaded programmatically

### 4. Expiration
- Automatically deleted after retention period
- Can be manually deleted before expiration
- No recovery after deletion

---

## 🛠️ Advanced Retrieval Techniques

### Technique 1: Bulk Download with Filtering

```bash
# Download all artifacts from failed runs
for run_id in $(gh run list --status failure --limit 5 --json databaseId --jq '.[].databaseId'); do
  echo "Downloading from run $run_id..."
  gh run download $run_id
done
```

### Technique 2: Automated Analysis Pipeline

```python
#!/usr/bin/env python3
"""Automated artifact analysis for Copilot sessions."""
import json
import subprocess
from pathlib import Path

def analyze_code_quality():
    """Download and analyze code quality artifacts."""
    # Download latest
    subprocess.run(["gh", "run", "download", "--name", "code-quality-report"])
    
    # Load and analyze
    with open(".codex/reports/smells.json") as f:
        smells = json.load(f)
    
    # Extract insights
    high_priority = [s for s in smells if s.get("severity") == "high"]
    
    return {
        "total_smells": len(smells),
        "high_priority": len(high_priority),
        "categories": list(set(s.get("category") for s in smells))
    }

if __name__ == "__main__":
    results = analyze_code_quality()
    print(json.dumps(results, indent=2))
```

### Technique 3: Cross-Artifact Correlation

```bash
# Correlate test failures with code quality issues
gh run download --name test-results
gh run download --name code-quality-report

python3 << 'EOF'
import json

# Load artifacts
with open('.github/copilot-evolution/data/test_results.json') as f:
    tests = json.load(f)

with open('.codex/reports/smells.json') as f:
    smells = json.load(f)

# Find correlation
failed_files = [t['file'] for t in tests.get('failed', [])]
smelly_files = [s['file'] for s in smells]

overlap = set(failed_files) & set(smelly_files)
print(f"Files with both test failures and code smells: {len(overlap)}")
for file in overlap:
    print(f"  - {file}")
EOF
```

---

## 📚 Best Practices for Copilot Sessions

### 1. Always Check Artifact Availability
```bash
# Before attempting download
gh run view <run-id> --json artifacts --jq '.artifacts[] | {name, expired}'
```

### 2. Use Temporary Directories
```bash
# Avoid cluttering workspace
mkdir -p /tmp/artifacts_$(date +%s)
cd /tmp/artifacts_*
gh run download <run-id>
```

### 3. Validate Artifact Integrity
```bash
# Check file sizes and formats
file downloaded_artifact/*
du -sh downloaded_artifact/*
```

### 4. Clean Up After Analysis
```bash
# Remove downloaded artifacts
rm -rf /tmp/artifacts_*
```

---

## 🚨 Troubleshooting

### Problem: Artifact Not Found
**Solution**: Check if artifact has expired or workflow failed
```bash
gh run list --limit 20 --json conclusion,databaseId,startedAt
```

### Problem: Download Fails
**Solution**: Verify authentication and permissions
```bash
gh auth status
gh auth refresh
```

### Problem: Corrupted Artifact
**Solution**: Re-download from source
```bash
gh run download <run-id> --name <artifact-name> --force
```

---

## 📞 Support & Documentation

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **GitHub CLI Docs**: https://cli.github.com/manual/
- **Workflow Catalog**: `.github/workflow-archive/PARITY_CHECKLIST.md`
- **Security Docs**: `.github/workflow-archive/README.md`

---

**Maintained by**: Automated CI/CD system  
**Review Frequency**: Quarterly  
**Last Reviewed**: 2025-12-28
