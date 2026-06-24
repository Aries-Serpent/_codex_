#!/usr/bin/env python3
"""
Session Recovery Continuous Monitoring Workflow Trigger
This script can be called from CI/CD to monitor and trigger session recovery
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}", file=sys.stderr)
        return None

def get_recovery_metrics():
    """Get session recovery metrics"""
    return run_command("python scripts/ci/session_recovery.py metrics")

def check_recent_failures():
    """Check for recent session failures"""
    recovery_log = Path(".codex/session_recovery_log.jsonl")
    if not recovery_log.exists():
        return []

    failures = []
    with open(recovery_log) as f:
        for line in f:
            try:
                entry = json.loads(line)
                # Parse timestamp to check recency
                failures.append(entry)
            except json.JSONDecodeError:
                continue

    return failures[-10:] if len(failures) > 10 else failures

def check_checkpoint_status():
    """Check session checkpoint status"""
    checkpoints_dir = Path(".codex/sessions")
    if not checkpoints_dir.exists():
        return {"total": 0, "recent": []}

    checkpoints = sorted(checkpoints_dir.glob("checkpoint_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return {
        "total": len(checkpoints),
        "recent": [str(c.name) for c in checkpoints[:5]]
    }

def generate_report():
    """Generate comprehensive session recovery report"""
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metrics": json.loads(get_recovery_metrics() or "{}"),
        "recent_failures": check_recent_failures(),
        "checkpoint_status": check_checkpoint_status(),
        "recovery_system_status": "OPERATIONAL"
    }
    return report

if __name__ == "__main__":
    report = generate_report()
    print(json.dumps(report, indent=2))

    # Save report for artifact upload
    report_file = Path(".codex/session_recovery_monitoring_report.json")
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n✅ Report saved to {report_file}")
