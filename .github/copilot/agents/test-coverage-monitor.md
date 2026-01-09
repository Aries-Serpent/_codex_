# Test Coverage Monitor Agent

**Agent Type:** Autonomous Monitoring  
**Purpose:** Automated test coverage monitoring and alerting  
**Version:** 1.0  
**Created:** 2026-01-09

---

## Agent Specification

### Overview
Monitors test coverage across the codebase, alerts on coverage drops, and suggests areas for improvement. Runs on schedule and on PR events.

### Triggers

#### Automatic Triggers
1. **PR Opened/Synchronized:** Run coverage analysis on changed files
2. **Scheduled:** Daily at 02:00 UTC
3. **Manual:** `/coverage-check` comment on PR

#### Trigger Conditions
```yaml
on:
  pull_request:
    types: [opened, synchronize]
  schedule:
    - cron: '0 2 * * *'
  issue_comment:
    types: [created]
```

---

## Agent Capabilities

### Core Functions

#### 1. Coverage Analysis
```python
def analyze_coverage():
    """Run pytest with coverage for all modules."""
    result = subprocess.run([
        'pytest', 
        '--cov=src', 
        '--cov=agents',
        '--cov-report=json',
        '--cov-report=term'
    ], capture_output=True)
    
    return parse_coverage_json('coverage.json')
```

#### 2. Coverage Comparison
```python
def compare_coverage(baseline: float, current: float) -> dict:
    """Compare current coverage against baseline."""
    delta = current - baseline
    status = 'improved' if delta > 0 else 'degraded' if delta < 0 else 'stable'
    
    return {
        'baseline': baseline,
        'current': current,
        'delta': delta,
        'status': status,
        'severity': 'critical' if delta < -5 else 'warning' if delta < -2 else 'info'
    }
```

#### 3. Module-Level Analysis
```python
def analyze_module_coverage(module_path: str) -> dict:
    """Analyze coverage for specific module."""
    coverage_data = load_coverage_data()
    module_cov = coverage_data['files'][module_path]
    
    return {
        'module': module_path,
        'statements': module_cov['summary']['num_statements'],
        'missing': module_cov['summary']['missing_lines'],
        'coverage': module_cov['summary']['percent_covered'],
        'threshold': get_module_threshold(module_path)
    }
```

#### 4. Alert Generation
```python
def generate_alert(comparison: dict) -> str:
    """Generate alert message based on coverage comparison."""
    if comparison['severity'] == 'critical':
        emoji = '🚨'
        message = f"CRITICAL: Coverage dropped by {abs(comparison['delta']):.2f}%"
    elif comparison['severity'] == 'warning':
        emoji = '⚠️'
        message = f"Warning: Coverage dropped by {abs(comparison['delta']):.2f}%"
    else:
        emoji = '✅'
        message = f"Coverage stable/improved: {comparison['delta']:+.2f}%"
    
    return f"{emoji} {message}"
```

---

## Workflow Implementation

### GitHub Actions Workflow

```yaml
name: Test Coverage Monitor
on:
  pull_request:
    types: [opened, synchronize]
  schedule:
    - cron: '0 2 * * *'
  issue_comment:
    types: [created]

jobs:
  coverage-monitor:
    runs-on: ubuntu-latest
    if: |
      github.event_name != 'issue_comment' || 
      contains(github.event.comment.body, '/coverage-check')
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      
      - name: Load baseline coverage
        id: baseline
        run: |
          if [ -f .codex/coverage_baseline.json ]; then
            BASELINE=$(jq -r '.summary.percent_covered' .codex/coverage_baseline.json)
          else
            BASELINE=0
          fi
          echo "baseline=$BASELINE" >> $GITHUB_OUTPUT
      
      - name: Run coverage analysis
        id: coverage
        run: |
          pytest --cov=src --cov=agents --cov-report=json --cov-report=term
          CURRENT=$(jq -r '.totals.percent_covered' coverage.json)
          echo "current=$CURRENT" >> $GITHUB_OUTPUT
      
      - name: Compare coverage
        id: compare
        run: |
          python .github/agents/scripts/compare_coverage.py \
            --baseline ${{ steps.baseline.outputs.baseline }} \
            --current ${{ steps.coverage.outputs.current }} \
            --output comparison.json
      
      - name: Generate alert
        id: alert
        run: |
          python .github/agents/scripts/generate_coverage_alert.py \
            --comparison comparison.json \
            --output alert.md
      
      - name: Post comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const alert = fs.readFileSync('alert.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: alert
            });
      
      - name: Update baseline (main branch only)
        if: github.ref == 'refs/heads/main'
        run: |
          cp coverage.json .codex/coverage_baseline.json
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .codex/coverage_baseline.json
          git commit -m "chore: update coverage baseline"
          git push
      
      - name: Upload coverage artifacts
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: |
            coverage.json
            htmlcov/
            comparison.json
            alert.md
```

---

## Alert Templates

### Critical Coverage Drop
```markdown
## 🚨 CRITICAL: Test Coverage Drop Detected

**Coverage Alert:** Test coverage has dropped below acceptable threshold.

### Summary
- **Baseline Coverage:** {baseline}%
- **Current Coverage:** {current}%
- **Change:** {delta}% ⬇️
- **Severity:** CRITICAL

### Affected Modules
{module_list}

### Action Required
Please add tests to restore coverage to at least {baseline}% before merging.

### Coverage by Module
{module_breakdown}

**Threshold Violations:**
{violations_list}

---
*Generated by Test Coverage Monitor Agent* • [View Full Report]({artifact_url})
```

### Coverage Improved
```markdown
## ✅ Test Coverage: Improved

**Coverage Status:** Test coverage has improved!

### Summary
- **Baseline Coverage:** {baseline}%
- **Current Coverage:** {current}%
- **Improvement:** +{delta}% ⬆️

### Top Improvements
{improvements_list}

Great work on improving test coverage! 🎉

---
*Generated by Test Coverage Monitor Agent* • [View Full Report]({artifact_url})
```

---

## Configuration

### Coverage Thresholds

```yaml
# .codex/config/coverage_thresholds.yaml
global:
  minimum: 85.0
  target: 90.0
  warning_delta: -2.0
  critical_delta: -5.0

modules:
  src/codex/utils:
    minimum: 90.0
    target: 95.0
  
  src/bridge_manager.py:
    minimum: 90.0
    target: 95.0
  
  src/codex/knowledge:
    minimum: 85.0
    target: 90.0
  
  src/codex/rag:
    minimum: 80.0
    target: 85.0
  
  src/security:
    minimum: 95.0  # Security modules require higher coverage
    target: 100.0
```

### Alert Rules

```yaml
# .codex/config/coverage_alerts.yaml
rules:
  critical:
    - condition: "delta < -5.0"
      action: "block_merge"
      notify: ["@owner"]
  
  warning:
    - condition: "delta < -2.0"
      action: "require_approval"
      notify: ["@maintainers"]
  
  info:
    - condition: "delta >= 0"
      action: "informational"
      notify: []

notifications:
  slack_webhook: "${SLACK_COVERAGE_WEBHOOK}"
  email: ["coverage-alerts@example.com"]
```

---

## Agent Scripts

### compare_coverage.py
```python
#!/usr/bin/env python3
"""Compare coverage between baseline and current."""
import argparse
import json

def compare_coverage(baseline: float, current: float) -> dict:
    """Compare coverage values."""
    delta = current - baseline
    
    if delta < -5.0:
        severity = 'critical'
    elif delta < -2.0:
        severity = 'warning'
    else:
        severity = 'info'
    
    return {
        'baseline': baseline,
        'current': current,
        'delta': delta,
        'severity': severity,
        'status': 'improved' if delta > 0 else 'degraded' if delta < 0 else 'stable'
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=float, required=True)
    parser.add_argument('--current', type=float, required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    comparison = compare_coverage(args.baseline, args.current)
    
    with open(args.output, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"Coverage comparison: {comparison['status']} ({comparison['delta']:+.2f}%)")
    
    # Exit with error code if critical
    if comparison['severity'] == 'critical':
        exit(1)

if __name__ == '__main__':
    main()
```

### generate_coverage_alert.py
```python
#!/usr/bin/env python3
"""Generate coverage alert message."""
import argparse
import json

TEMPLATES = {
    'critical': """## 🚨 CRITICAL: Test Coverage Drop Detected

**Coverage Alert:** Test coverage has dropped below acceptable threshold.

### Summary
- **Baseline Coverage:** {baseline:.2f}%
- **Current Coverage:** {current:.2f}%
- **Change:** {delta:+.2f}% ⬇️
- **Severity:** CRITICAL

### Action Required
Please add tests to restore coverage to at least {baseline:.2f}% before merging.

---
*Generated by Test Coverage Monitor Agent*
""",
    'warning': """## ⚠️ Warning: Test Coverage Decreased

**Coverage Status:** Test coverage has decreased.

### Summary
- **Baseline Coverage:** {baseline:.2f}%
- **Current Coverage:** {current:.2f}%
- **Change:** {delta:+.2f}% ⬇️

Please consider adding tests to improve coverage.

---
*Generated by Test Coverage Monitor Agent*
""",
    'info': """## ✅ Test Coverage: {status_emoji}

**Coverage Status:** Test coverage is {status_text}.

### Summary
- **Baseline Coverage:** {baseline:.2f}%
- **Current Coverage:** {current:.2f}%
- **Change:** {delta:+.2f}%

{message}

---
*Generated by Test Coverage Monitor Agent*
"""
}

def generate_alert(comparison: dict) -> str:
    """Generate alert message from comparison."""
    severity = comparison['severity']
    template = TEMPLATES.get(severity, TEMPLATES['info'])
    
    if severity == 'info':
        if comparison['delta'] > 0:
            status_emoji = 'Improved 📈'
            status_text = 'improving'
            message = 'Great work on improving test coverage! 🎉'
        else:
            status_emoji = 'Stable'
            status_text = 'stable'
            message = 'Coverage remains stable.'
    else:
        status_emoji = ''
        status_text = ''
        message = ''
    
    return template.format(
        baseline=comparison['baseline'],
        current=comparison['current'],
        delta=comparison['delta'],
        status_emoji=status_emoji,
        status_text=status_text,
        message=message
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--comparison', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    with open(args.comparison) as f:
        comparison = json.load(f)
    
    alert = generate_alert(comparison)
    
    with open(args.output, 'w') as f:
        f.write(alert)
    
    print(f"Alert generated: {comparison['severity']}")

if __name__ == '__main__':
    main()
```

---

## Monitoring Dashboard

### Coverage Metrics

```python
def generate_coverage_dashboard():
    """Generate coverage metrics dashboard."""
    metrics = {
        'timestamp': datetime.now(UTC).isoformat(),
        'overall_coverage': 85.7,
        'module_coverage': {
            'src/codex/utils': 90.5,
            'src/bridge_manager.py': 88.2,
            'src/codex/knowledge': 85.0,
            'src/security': 95.3
        },
        'trend': 'improving',
        'tests_total': 101,
        'tests_passing': 101,
        'tests_failing': 0
    }
    return metrics
```

---

## Usage

### Manual Trigger
Comment on PR:
```
/coverage-check
```

### Scheduled Run
Automatic daily at 02:00 UTC

### Integration
Add to CI/CD pipeline:
```yaml
- uses: ./.github/actions/coverage-monitor
  with:
    fail-on-decrease: true
    threshold: 85.0
```

---

## Maintenance

### Update Baseline
```bash
# Manual baseline update
pytest --cov=src --cov=agents --cov-report=json
cp coverage.json .codex/coverage_baseline.json
git add .codex/coverage_baseline.json
git commit -m "chore: update coverage baseline"
```

### Adjust Thresholds
Edit `.codex/config/coverage_thresholds.yaml`

---

**Created:** 2026-01-09  
**Agent Type:** Autonomous Monitoring  
**Maintenance:** Auto-update on main branch merges  
**Version:** 1.0
