# Integration Examples

**Version**: 1.4.0  
**Last Updated**: Previous Cycle-12-09

---

## Overview

This guide shows how to integrate the audit pipeline v1.4.0 with:
- CI/CD systems (GitHub Actions, GitLab CI, Jenkins)
- Pre-commit hooks
- Monitoring tools (MLflow, Slack, Prometheus)
- Custom workflows

---

## GitHub Actions Integration

### Basic Audit Workflow

```yaml
# .github/workflows/audit.yml
name: Audit Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install pyyaml jinja2 pytest pytest-cov
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Run audit pipeline
        run: |
          python scripts/space_traversal/audit_runner.py run
      
      - name: Upload audit artifacts
        uses: actions/upload-artifact@v3
        with:
          name: audit-results
          path: |
            audit_artifacts/
            reports/
          retention-days: 30
      
      - name: Check for regressions
        run: |
          if [ -f audit_artifacts/baselines/baseline.json ]; then
            python scripts/space_traversal/audit_runner.py diff \
              --old audit_artifacts/baselines/baseline.json \
              --new audit_artifacts/capabilities_scored.json \
              --fail-on-regression
          fi
```

### Advanced: Fail on Score Threshold

```yaml
# .github/workflows/audit-gate.yml
name: Audit Quality Gate

on: [pull_request]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install pyyaml jinja2 pytest pytest-cov
      
      - name: Generate coverage
        run: pytest --cov=src --cov-report=xml
      
      - name: Run audit
        run: make space-audit
      
      - name: Check minimum score
        run: |
          python << 'EOF'
          import json
          
          with open("audit_artifacts/capabilities_scored.json") as f:
              data = json.load(f)
          
          scores = [cap["score"] for cap in data["capabilities"]]
          avg_score = sum(scores) / len(scores)
          
          print(f"Average score: {avg_score:.2f}")
          
          if avg_score < 0.70:
              print(f"❌ Score {avg_score:.2f} below threshold 0.70")
              exit(1)
          else:
              print(f"✅ Score {avg_score:.2f} meets threshold 0.70")
          EOF
```

---

## GitLab CI Integration

```yaml
# .gitlab-ci.yml
stages:
  - test
  - audit
  - report

test:
  stage: test
  script:
    - pip install pytest pytest-cov
    - pytest --cov=src --cov-report=xml
  artifacts:
    paths:
      - coverage.xml
    expire_in: 1 day

audit:
  stage: audit
  dependencies:
    - test
  script:
    - pip install pyyaml jinja2
    - python scripts/space_traversal/audit_runner.py run
  artifacts:
    paths:
      - audit_artifacts/
      - reports/
    expire_in: 30 days

report:
  stage: report
  dependencies:
    - audit
  script:
    - echo "Audit complete. Results in artifacts."
    - python scripts/space_traversal/audit_runner.py explain --top 5
  only:
    - main
    - develop
```

---

## Pre-commit Hook Integration

### Local Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: audit-pipeline-fast
        name: Run Audit Pipeline (Fast)
        entry: make space-audit-fast
        language: system
        pass_filenames: false
        always_run: true
        verbose: true
```

### Pre-commit Script

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running audit pipeline..."

# Run fast audit (skips S2, S5, S7)
if ! make space-audit-fast; then
    echo "❌ Audit failed"
    exit 1
fi

# Check for regressions
if [ -f audit_artifacts/baselines/baseline.json ]; then
    python scripts/space_traversal/audit_runner.py diff \
        --old audit_artifacts/baselines/baseline.json \
        --new audit_artifacts/capabilities_scored.json
fi

echo "✅ Audit passed"
exit 0
```

---

## MLflow Integration

### Log Audit Results to MLflow

```python
# scripts/integrations/log_audit_to_mlflow.py
import mlflow
import json
from pathlib import Path
from datetime import datetime

def log_audit_results():
    """Log audit pipeline results to MLflow"""
    
    # Load audit results
    with open("audit_artifacts/capabilities_scored.json") as f:
        data = json.load(f)
    
    # Start MLflow run
    with mlflow.start_run(run_name=f"audit-{datetime.now().strftime('%Y%m%d')}"):
        
        # Log overall metrics
        scores = [cap["score"] for cap in data["capabilities"]]
        mlflow.log_metric("avg_capability_score", sum(scores) / len(scores))
        mlflow.log_metric("num_capabilities", len(data["capabilities"]))
        mlflow.log_metric("min_score", min(scores))
        mlflow.log_metric("max_score", max(scores))
        
        # Log per-capability scores
        for cap in data["capabilities"]:
            mlflow.log_metric(f"score_{cap['id']}", cap["score"])
            mlflow.log_metric(f"tests_{cap['id']}", cap.get("tests", {}).get("score", 0))
            mlflow.log_metric(f"consistency_{cap['id']}", cap.get("consistency", {}).get("score", 0))
        
        # Log component weights
        weights = data.get("weights", {})
        for component, weight in weights.items():
            mlflow.log_param(f"weight_{component}", weight)
        
        # Log artifacts
        mlflow.log_artifact("audit_artifacts/capabilities_scored.json")
        mlflow.log_artifact("audit_artifacts/audit_run_manifest.json")
        
        # Log reports
        for report in Path("reports").glob("capability_matrix_*.md"):
            mlflow.log_artifact(str(report))
        
        # Log coverage map if exists
        if Path("audit_artifacts/coverage_map.json").exists():
            mlflow.log_artifact("audit_artifacts/coverage_map.json")
            
            with open("audit_artifacts/coverage_map.json") as f:
                cov_data = json.load(f)
            mlflow.log_metric("coverage_files_count", len(cov_data))
            
            # Average coverage
            coverages = [v["percent"] for v in cov_data.values()]
            if coverages:
                mlflow.log_metric("avg_coverage", sum(coverages) / len(coverages))
        
        print("✅ Audit results logged to MLflow")
        print(f"   Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    log_audit_results()
```

**Usage**:
```bash
# Set MLflow tracking URI
export MLFLOW_TRACKING_URI=http://localhost:5000

# Run audit and log
make space-audit
python scripts/integrations/log_audit_to_mlflow.py
```

---

## Slack Notification Integration

### Notify Audit Results to Slack

```python
# scripts/integrations/notify_slack.py
import json
import requests
from datetime import datetime

SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def notify_slack():
    """Send audit results to Slack"""
    
    with open("audit_artifacts/capabilities_scored.json") as f:
        data = json.load(f)
    
    scores = [cap["score"] for cap in data["capabilities"]]
    avg_score = sum(scores) / len(scores)
    
    low_scores = [cap for cap in data["capabilities"] if cap["score"] < 0.70]
    high_scores = [cap for cap in data["capabilities"] if cap["score"] >= 0.85]
    
    # Build message
    message = {
        "text": "🔍 Audit Pipeline Results",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔍 Audit Pipeline v1.4.0 Results"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date*: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                            f"*Average Score*: {avg_score:.2f}\n"
                            f"*Capabilities*: {len(data['capabilities'])}\n"
                            f"*Low Maturity* (<0.70): {len(low_scores)}\n"
                            f"*High Maturity* (≥0.85): {len(high_scores)}"
                }
            }
        ]
    }
    
    # Add low maturity section if any
    if low_scores:
        low_list = "\n".join([
            f"• `{cap['id']}`: {cap['score']:.2f}"
            for cap in sorted(low_scores, key=lambda x: x['score'])[:5]
        ])
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*⚠️ Low Maturity Capabilities:*\n{low_list}"
            }
        })
    
    # Add high maturity section
    if high_scores:
        high_list = "\n".join([
            f"• `{cap['id']}`: {cap['score']:.2f}"
            for cap in sorted(high_scores, key=lambda x: -x['score'])[:3]
        ])
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*✅ Top Performers:*\n{high_list}"
            }
        })
    
    # Send to Slack
    response = requests.post(SLACK_WEBHOOK, json=message)
    response.raise_for_status()
    print("✅ Notification sent to Slack")

if __name__ == "__main__":
    notify_slack()
```

**Setup**:
1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Set webhook URL in script
3. Run after audit:
   ```bash
   make space-audit
   python scripts/integrations/notify_slack.py
   ```

---

## Jenkins Integration

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.12'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install pyyaml jinja2 pytest pytest-cov'
            }
        }
        
        stage('Test with Coverage') {
            steps {
                sh 'pytest --cov=src --cov-report=xml'
            }
        }
        
        stage('Audit Pipeline') {
            steps {
                sh 'python scripts/space_traversal/audit_runner.py run'
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'audit_artifacts/**, reports/**', fingerprint: true
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    def auditData = readJSON file: 'audit_artifacts/capabilities_scored.json'
                    def scores = auditData.capabilities.collect { it.score }
                    def avgScore = scores.sum() / scores.size()
                    
                    echo "Average score: ${avgScore}"
                    
                    if (avgScore < 0.70) {
                        error("Score ${avgScore} below threshold 0.70")
                    }
                }
            }
        }
    }
    
    post {
        always {
            junit 'test-results/**/*.xml'
        }
    }
}
```

---

## Prometheus Metrics Export

```python
# scripts/integrations/export_metrics.py
from prometheus_client import CollectorRegistry, Gauge, write_to_textfile
import json

def export_prometheus_metrics():
    """Export audit metrics to Prometheus textfile format"""
    
    registry = CollectorRegistry()
    
    # Load audit data
    with open("audit_artifacts/capabilities_scored.json") as f:
        data = json.load(f)
    
    # Create metrics
    avg_score_gauge = Gauge('audit_avg_score', 'Average capability score', registry=registry)
    cap_count_gauge = Gauge('audit_capability_count', 'Number of capabilities', registry=registry)
    low_count_gauge = Gauge('audit_low_maturity_count', 'Low maturity capabilities', registry=registry)
    
    # Set values
    scores = [cap["score"] for cap in data["capabilities"]]
    avg_score_gauge.set(sum(scores) / len(scores))
    cap_count_gauge.set(len(data["capabilities"]))
    low_count_gauge.set(sum(1 for s in scores if s < 0.70))
    
    # Per-capability metrics
    for cap in data["capabilities"]:
        cap_score = Gauge(
            f'audit_capability_score',
            'Capability score',
            ['capability'],
            registry=registry
        )
        cap_score.labels(capability=cap['id']).set(cap['score'])
    
    # Write to file for node_exporter textfile collector
    write_to_textfile('/var/lib/node_exporter/audit_metrics.prom', registry)
    print("✅ Metrics exported to Prometheus")

if __name__ == "__main__":
    export_prometheus_metrics()
```

---

## Custom Webhook Integration

```python
# scripts/integrations/webhook_notify.py
import json
import requests
import sys

def send_webhook(url, data):
    """Send audit results to generic webhook"""
    
    with open("audit_artifacts/capabilities_scored.json") as f:
        audit_data = json.load(f)
    
    scores = [cap["score"] for cap in audit_data["capabilities"]]
    
    payload = {
        "event": "audit_complete",
        "timestamp": audit_data.get("timestamp"),
        "summary": {
            "avg_score": sum(scores) / len(scores),
            "capability_count": len(audit_data["capabilities"]),
            "low_maturity_count": sum(1 for s in scores if s < 0.70),
            "high_maturity_count": sum(1 for s in scores if s >= 0.85)
        },
        "capabilities": [
            {"id": cap["id"], "score": cap["score"]}
            for cap in audit_data["capabilities"]
        ]
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    print(f"✅ Webhook delivered: {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python webhook_notify.py <webhook-url>")
        sys.exit(1)
    
    send_webhook(sys.argv[1], {})
```

---

## See Also

- [Configuration Guide](./Configuration_v1.4.0.md) - Configuration options
- [Migration Guide](./Migration_v1.3_to_v1.4.md) - Upgrading from v1.3.x
- [API Reference](./API_Reference_v1.4.0.md) - Module documentation
- [Performance Tuning](./Performance_Tuning.md) - Optimization strategies
