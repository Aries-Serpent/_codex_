# Self-Healing and Capability Gap Detection

## Purpose
Implement feedback loops to detect capability gaps, self-correct issues, and iteratively improve the codebase based on AI Agent interactions and usage patterns.

## Prerequisites
- Python 3.9+ installed
- SQLite database for tracking
- GitHub API access (for issue creation)

## Commands

### 1. Detect Capability Gaps
```bash
cd /home/runner/work/_codex_/_codex_

# Analyze missing capabilities
python -c "
from pathlib import Path
import json

# Load current capabilities
with open('.copilot-space/workflow.yaml') as f:
    import yaml
    workflow = yaml.safe_load(f)
    current_caps = set(c['name'] for c in workflow.get('capabilities', []))

# Define expected capabilities (from Azure MLOps maturity model)
expected_caps = {
    'Automated Testing', 'Model Monitoring', 'CI/CD Pipeline',
    'Feature Store', 'Data Versioning', 'Model Registry',
    'A/B Testing', 'Shadow Deployment', 'Canary Release',
    # ... add all 71 Azure MLOps capabilities
}

# Find gaps
gaps = expected_caps - current_caps

# Save gap analysis
with open('capability_gaps.json', 'w') as f:
    json.dump({
        'detected_at': '$(date -Iseconds)',
        'gaps': list(gaps),
        'current_count': len(current_caps),
        'expected_count': len(expected_caps),
        'coverage': len(current_caps) / len(expected_caps) * 100
    }, f, indent=2)

print(f'Found {len(gaps)} capability gaps')
for gap in sorted(gaps):
    print(f'  - {gap}')
"
```

### 2. Analyze Agent Feedback
```bash
# Parse agent interaction logs
python -c "
import json
from pathlib import Path
from collections import Counter

logs = Path('.codex/sessions')
feedback = []

# Extract feedback from session logs
for log_file in logs.glob('*.jsonl'):
    with open(log_file) as f:
        for line in f:
            event = json.loads(line)
            if event.get('role') == 'user' and 'error' in event.get('content', '').lower():
                feedback.append({
                    'timestamp': event.get('timestamp'),
                    'content': event.get('content'),
                    'session_id': event.get('session_id')
                })

# Analyze common issues
if feedback:
    print(f'Analyzed {len(feedback)} feedback items')
    # Categorize feedback
    categories = Counter()
    for item in feedback:
        content = item['content'].lower()
        if 'not found' in content:
            categories['missing_feature'] += 1
        elif 'error' in content:
            categories['error'] += 1
        elif 'unclear' in content or 'confusing' in content:
            categories['documentation'] += 1
    
    print('\\nFeedback categories:')
    for category, count in categories.most_common():
        print(f'  {category}: {count}')
else:
    print('No feedback found')
"
```

### 3. Create Self-Healing Plans
```bash
# Generate improvement plan from gaps
python -c "
import json
from pathlib import Path

# Load gaps
with open('capability_gaps.json') as f:
    gaps = json.load(f)

# Generate plan
plan = {
    'created_at': '$(date -Iseconds)',
    'objective': 'Close capability gaps identified in analysis',
    'phases': []
}

# Group gaps by priority
high_priority = ['Model Monitoring', 'Feature Store', 'A/B Testing']
medium_priority = ['Shadow Deployment', 'Canary Release']

for gap in gaps['gaps']:
    priority = 'high' if gap in high_priority else 'medium' if gap in medium_priority else 'low'
    plan['phases'].append({
        'capability': gap,
        'priority': priority,
        'tasks': [
            f'Research {gap} implementation',
            f'Design {gap} architecture',
            f'Implement {gap} core functionality',
            f'Add {gap} tests',
            f'Update {gap} documentation'
        ]
    })

# Save plan
with open('self_healing_plan.json', 'w') as f:
    json.dump(plan, f, indent=2)

print(f'Generated plan with {len(plan[\"phases\"])} phases')
"
```

### 4. Implement Feedback Loop
```bash
# Create feedback loop script
cat > scripts/feedback_loop.py << 'EOF'
#!/usr/bin/env python3
\"\"\"
Automated feedback loop for capability improvement.
Monitors agent interactions, detects gaps, and creates improvement issues.
\"\"\"
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

def analyze_recent_sessions(hours=24):
    \"\"\"Analyze recent agent sessions for feedback.\"\"\"
    cutoff = datetime.now() - timedelta(hours=hours)
    sessions = Path('.codex/sessions')
    
    feedback_items = []
    for log_file in sessions.glob('*.jsonl'):
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
            continue
            
        with open(log_file) as f:
            for line in f:
                event = json.loads(line)
                # Look for error patterns
                content = event.get('content', '')
                if any(keyword in content.lower() for keyword in 
                       ['error', 'missing', 'not found', 'unclear', 'bug']):
                    feedback_items.append(event)
    
    return feedback_items

def create_improvement_issue(feedback):
    \"\"\"Create GitHub issue for improvement.\"\"\"
    title = f"[Auto] Capability Gap: {feedback['summary']}"
    body = f\"\"\"
## Detected Issue
{feedback['description']}

## Context
- Session ID: {feedback.get('session_id', 'unknown')}
- Timestamp: {feedback.get('timestamp', 'unknown')}
- Source: Automated feedback loop

## Suggested Action
{feedback.get('suggestion', 'Review and implement fix')}

## Labels
- enhancement
- ai-agent-feedback
- auto-detected
\"\"\"
    
    # Create issue using GitHub CLI
    result = subprocess.run(
        ['gh', 'issue', 'create', '--title', title, '--body', body,
         '--label', 'enhancement,ai-agent-feedback'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f\"✅ Created issue: {title}\")
    else:
        print(f\"❌ Failed to create issue: {result.stderr}\")

def main():
    print(\"Starting feedback loop analysis...\")
    
    # Analyze sessions
    feedback = analyze_recent_sessions(hours=24)
    print(f\"Found {len(feedback)} feedback items in last 24 hours\")
    
    # Process high-priority feedback
    # (implement your logic here)
    
    print(\"Feedback loop complete\")

if __name__ == '__main__':
    main()
EOF

chmod +x scripts/feedback_loop.py
```

### 5. Run Feedback Loop
```bash
# Run feedback loop analysis
python scripts/feedback_loop.py
```

## Validation

1. **Check Gap Analysis**:
   ```bash
   cat capability_gaps.json | jq '.gaps'
   ```

2. **Review Self-Healing Plan**:
   ```bash
   cat self_healing_plan.json | jq '.phases[] | select(.priority == "high")'
   ```

3. **Verify Issues Created**:
   ```bash
   gh issue list --label ai-agent-feedback
   ```

4. **Monitor Feedback Loop**:
   ```bash
   tail -f logs/feedback_loop.log
   ```

## Expected Output

### Capability Gaps Analysis
```json
{
  "detected_at": "2025-12-10T18:00:00",
  "gaps": [
    "Shadow Deployment",
    "Canary Release",
    "Feature Flagging"
  ],
  "current_count": 39,
  "expected_count": 71,
  "coverage": 54.93
}
```

### Self-Healing Plan
```json
{
  "created_at": "2025-12-10T18:00:00",
  "objective": "Close capability gaps identified in analysis",
  "phases": [
    {
      "capability": "Shadow Deployment",
      "priority": "medium",
      "tasks": [
        "Research Shadow Deployment implementation",
        "Design Shadow Deployment architecture",
        ...
      ]
    }
  ]
}
```

### Feedback Loop Output
```
Starting feedback loop analysis...
Found 12 feedback items in last 24 hours

Analyzing feedback:
  - 5 missing feature requests
  - 4 error reports
  - 3 documentation issues

Creating improvement issues:
✅ Created issue: [Auto] Capability Gap: Feature Store Integration
✅ Created issue: [Auto] Documentation: Unclear A/B Testing Guide
✅ Created issue: [Auto] Bug: Model Registry Connection Error

Feedback loop complete
```

## Self-Correction Mechanisms

### 1. Automated Test Generation
```python
# Generate tests for missing coverage
from hypothesis import given, strategies as st

@given(st.text())
def test_auto_generated_capability(input_data):
    """Auto-generated test for capability validation"""
    # Test implementation
    assert capability_exists(input_data)
```

### 2. Documentation Auto-Update
```bash
# Detect outdated documentation
python -c "
from pathlib import Path
import re

docs = Path('docs')
code = Path('src')

# Find functions without docs
for py_file in code.glob('**/*.py'):
    with open(py_file) as f:
        content = f.read()
        # Extract functions
        functions = re.findall(r'def (\w+)\(', content)
        # Check if documented
        for func in functions:
            if func not in content or '\"\"\"' not in content:
                print(f'Undocumented: {py_file}::{func}')
"
```

### 3. Dependency Health Check
```bash
# Auto-update vulnerable dependencies
pip-audit --fix --dry-run > dependency_fixes.txt

# Review and apply
cat dependency_fixes.txt
pip-audit --fix
```

## Integration with GitHub Actions

Automate feedback loop:

```yaml
name: Self-Healing Feedback Loop

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  feedback-loop:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Dependencies
        run: pip install -e .
      
      - name: Analyze Capability Gaps
        run: python scripts/analyze_gaps.py
      
      - name: Run Feedback Loop
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/feedback_loop.py
      
      - name: Upload Analysis
        uses: actions/upload-artifact@v3
        with:
          name: gap-analysis
          path: |
            capability_gaps.json
            self_healing_plan.json
```

## Iterative Improvement Process

### Phase 1: Detection (Pre-commit 1-2)
- Monitor agent interactions
- Collect feedback data
- Identify patterns

### Phase 2: Analysis (Pre-commit 3-4)
- Categorize feedback
- Prioritize gaps
- Generate improvement plans

### Phase 3: Implementation (Pre-commit 5-8)
- Implement high-priority fixes
- Add missing capabilities
- Update documentation

### Phase 4: Validation (Pre-commit 9-10)
- Test improvements
- Verify gap closure
- Measure impact

### Phase 5: Iteration (Ongoing)
- Continuous monitoring
- Regular feedback analysis
- Incremental improvements

## Metrics Tracking

```python
# Track improvement metrics
metrics = {
    'capability_coverage': 0.0,  # Percentage of capabilities implemented
    'feedback_resolution_time': 0.0,  # Hours to resolve feedback
    'gap_closure_rate': 0.0,  # Gaps closed per week
    'agent_satisfaction': 0.0,  # Success rate of agent tasks
}

# Update metrics after each iteration
def update_metrics():
    with open('improvement_metrics.json', 'r+') as f:
        data = json.load(f)
        data['last_updated'] = datetime.now().isoformat()
        data['metrics'] = metrics
        f.seek(0)
        json.dump(data, f, indent=2)
```

## Troubleshooting

### Issue: No feedback detected
**Solution**: Check session logging is enabled
```bash
export CODEX_SESSION_LOG_DIR=".codex/sessions"
python -m codex.logging.session_logger
```

### Issue: Issues not created
**Solution**: Verify GitHub CLI authentication
```bash
gh auth status
gh auth login
```

### Issue: Gap analysis incomplete
**Solution**: Update capability definitions
```bash
# Edit workflow.yaml to include all expected capabilities
vim .copilot-space/workflow.yaml
```

## Related Prompts
- [run-full-audit.md](../audit/run-full-audit.md) - Audit for gaps
- [check-regressions.md](../audit/check-regressions.md) - Detect regressions
- [repository-cleanup.md](../organization/repository-cleanup.md) - Maintain cleanliness
