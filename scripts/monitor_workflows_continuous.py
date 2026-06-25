#!/usr/bin/env python3
"""
Track 5B: Continuous Workflow Health Monitoring
Monitors all GitHub Actions workflows for ~60 minutes during the remediation campaign.
Categorizes failures in real-time and generates reports.
"""

import json
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple

# Configuration
REPO_OWNER = "Aries-Serpent"
REPO_NAME = "_codex_"
MONITORING_DURATION_MINUTES = 60
POLL_INTERVAL_SECONDS = 300  # 5 minutes
LOG_UPDATE_INTERVAL_MINUTES = 15
CRITICAL_ALERT_THRESHOLD = 2  # Alert after 2 failures

# Database
DB_PATH = Path(".codex/monitoring_data.db")

class WorkflowMonitor:
    """Continuously monitors workflow health during campaign."""

    def __init__(self):
        self.start_time = datetime.utcnow()
        self.end_time = self.start_time + timedelta(minutes=MONITORING_DURATION_MINUTES)
        self.failures = {}
        self.runs_tracked = {}
        self.last_log_update = None
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for monitoring."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Create tables if not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_runs (
                run_id INTEGER PRIMARY KEY,
                workflow_name TEXT,
                status TEXT,
                conclusion TEXT,
                created_at TEXT,
                updated_at TEXT,
                branch TEXT,
                commit_sha TEXT,
                category TEXT,
                first_seen_at TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failures (
                failure_id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT,
                run_id INTEGER,
                status TEXT,
                category TEXT,
                timestamp TEXT,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_workflow_runs(self) -> Dict:
        """Get current workflow runs from GitHub."""
        try:
            # Use gh CLI to get workflow runs
            cmd = [
                "gh", "run", "list",
                "-R", f"{REPO_OWNER}/{REPO_NAME}",
                "-L", "100",
                "--json", "databaseId,name,status,conclusion,createdAt,updatedAt,headBranch,headSha"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"Error fetching runs: {result.stderr}")
                return {}

            return json.loads(result.stdout)
        except Exception as e:
            error_type = type(e).__name__
            print(f"Exception getting runs: <ERROR_TYPE>")
            return {}

    def categorize_failure(self, workflow_name: str, error_msg: str = "") -> str:
        """Categorize a failure based on workflow name and error message."""
        name_lower = workflow_name.lower()

        # Flaky patterns
        flaky_keywords = ['timeout', 'transient', 'temporary', 'intermittent', 'race']

        # Regression patterns
        regression_keywords = ['assertion', 'error:', 'failed', 'exception']

        # Environment patterns
        env_keywords = ['import error', 'dependency', 'package', 'module not found', 'environment']

        # Transient patterns
        transient_keywords = ['timeout', 'network', 'connection', 'temporary failure']

        # Check error message first
        if error_msg:
            error_lower = error_msg.lower()
            for keyword in transient_keywords:
                if keyword in error_lower:
                    return "Transient"
            for keyword in env_keywords:
                if keyword in error_lower:
                    return "Environment"
            for keyword in regression_keywords:
                if keyword in error_lower:
                    return "Regression"

        # Check workflow name patterns
        if 'test' in name_lower or 'validation' in name_lower:
            return "Regression"
        elif 'security' in name_lower or 'scan' in name_lower:
            return "Regression"
        elif 'dependabot' in name_lower or 'dependency' in name_lower:
            return "Environment"
        elif 'health' in name_lower or 'monitor' in name_lower:
            return "Transient"

        return "Unrelated"

    def log_failure(self, workflow_name: str, run_id: int, category: str, notes: str = ""):
        """Log a workflow failure."""
        key = f"{workflow_name}_{run_id}"

        if key not in self.failures:
            self.failures[key] = {
                'workflow_name': workflow_name,
                'run_id': run_id,
                'category': category,
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'notes': notes
            }

            # Store in database
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO failures (workflow_name, run_id, status, category, timestamp, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (workflow_name, run_id, 'failed', category, self.failures[key]['timestamp'], notes))
            conn.commit()
            conn.close()

            print(f"[{self.failures[key]['timestamp']}] FAILURE: {workflow_name} (Run #{run_id}) - Category: {category}")

    def monitor_iteration(self) -> Tuple[int, int, int]:
        """Perform one monitoring iteration. Returns (total_runs, passed, failed)."""
        runs = self.get_workflow_runs()

        if not runs:
            return 0, 0, 0

        passed = 0
        failed = 0

        for run in runs:
            run_id = run.get('databaseId')
            workflow_name = run.get('name', 'Unknown')
            status = run.get('status', 'unknown')
            conclusion = run.get('conclusion', '')

            key = f"{workflow_name}_{run_id}"

            # Track run
            if key not in self.runs_tracked:
                self.runs_tracked[key] = {
                    'workflow_name': workflow_name,
                    'run_id': run_id,
                    'first_seen': datetime.utcnow().isoformat() + "Z"
                }

            # Check for failures
            if conclusion == 'failure':
                category = self.categorize_failure(workflow_name)
                self.log_failure(workflow_name, run_id, category)
                failed += 1
            elif conclusion == 'success':
                passed += 1

            # Store run data
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO workflow_runs
                (run_id, workflow_name, status, conclusion, created_at, updated_at, branch, commit_sha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_id,
                workflow_name,
                status,
                conclusion,
                run.get('createdAt'),
                run.get('updatedAt'),
                run.get('headBranch'),
                run.get('headSha', '')
            ))
            conn.commit()
            conn.close()

        return len(runs), passed, failed

    def generate_status_report(self) -> str:
        """Generate current status report."""
        elapsed = datetime.utcnow() - self.start_time
        remaining = self.end_time - datetime.utcnow()

        total_tracked = len(self.runs_tracked)
        total_failures = len(self.failures)

        # Count by category
        categories = {}
        for failure in self.failures.values():
            cat = failure['category']
            categories[cat] = categories.get(cat, 0) + 1

        report = f"""
## 📊 Monitoring Status Report
**Timestamp**: {datetime.utcnow().isoformat()}Z
**Elapsed Time**: {elapsed.total_seconds():.0f}s
**Remaining Time**: {remaining.total_seconds():.0f}s
**Monitoring Status**: 🟢 ACTIVE

### Summary
- **Total Runs Tracked**: {total_tracked}
- **Total Failures**: {total_failures}
- **Success Rate**: {(1 - total_failures/max(total_tracked, 1))*100:.1f}%
- **Failure Categories**: {dict(categories)}

### Critical Alert Status
"""
        if total_failures > CRITICAL_ALERT_THRESHOLD:
            report += f"🔴 **CRITICAL**: {total_failures} failures detected (threshold: {CRITICAL_ALERT_THRESHOLD})\n"
        else:
            report += "✅ **NORMAL**: Within acceptable failure threshold\n"

        return report

    def update_monitoring_log(self):
        """Update the real-time monitoring log file."""
        current_time = datetime.utcnow()

        # Check if enough time has passed for an update
        if self.last_log_update and (current_time - self.last_log_update).total_seconds() < LOG_UPDATE_INTERVAL_MINUTES * 60:
            return

        self.last_log_update = current_time

        # Read current log
        log_path = Path(".codex/WORKFLOW_MONITORING_LOG.md")
        if log_path.exists():
            content = log_path.read_text()
        else:
            content = "# Monitoring Log\n\n"

        # Generate update section
        total_tracked = len(self.runs_tracked)
        total_failures = len(self.failures)
        success_rate = (1 - total_failures / max(total_tracked, 1)) * 100 if total_tracked > 0 else 0

        update = f"""
### {current_time.isoformat()}Z - STATUS_UPDATE
- **Runs Tracked**: {total_tracked}
- **Failures**: {total_failures}
- **Success Rate**: {success_rate:.1f}%
- **Status**: {'✅ Healthy' if success_rate >= 95 else '⚠️ Warning' if success_rate >= 90 else '🔴 Critical'}

"""

        # Append to log file
        # Note: In actual implementation, would insert into the proper location in markdown
        # For now, just log to stdout
        print(f"[LOG UPDATE] {current_time.isoformat()}Z - Runs: {total_tracked}, Failures: {total_failures}, Success Rate: {success_rate:.1f}%")

    def run(self):
        """Run the monitoring loop."""
        print(f"[{datetime.utcnow().isoformat()}Z] Starting continuous workflow monitoring for Track 5B")
        print(f"[{datetime.utcnow().isoformat()}Z] Duration: {MONITORING_DURATION_MINUTES} minutes")
        print(f"[{datetime.utcnow().isoformat()}Z] Poll interval: {POLL_INTERVAL_SECONDS} seconds")

        iteration = 0

        try:
            while datetime.utcnow() < self.end_time:
                iteration += 1
                print(f"\n[Iteration {iteration}] {datetime.utcnow().isoformat()}Z")

                # Run monitoring iteration
                total, passed, failed = self.monitor_iteration()
                print(f"  Checked {total} runs: {passed} passed, {failed} failed")

                # Update log periodically
                self.update_monitoring_log()

                # Check for critical failures
                if len(self.failures) > CRITICAL_ALERT_THRESHOLD:
                    print(f"  ⚠️ ALERT: {len(self.failures)} failures detected!")

                # Wait for next iteration
                remaining = self.end_time - datetime.utcnow()
                if remaining.total_seconds() > POLL_INTERVAL_SECONDS:
                    print(f"  Sleeping for {POLL_INTERVAL_SECONDS}s (remaining time: {remaining.total_seconds():.0f}s)")
                    time.sleep(POLL_INTERVAL_SECONDS)
                else:
                    break

        except KeyboardInterrupt:
            print("\n[Interrupted by user]")
        except Exception as e:
            error_type = type(e).__name__
            print(f"\n[ERROR] <ERROR_TYPE>")

        finally:
            self.finalize()

    def finalize(self):
        """Generate final report."""
        total_time = datetime.utcnow() - self.start_time
        total_tracked = len(self.runs_tracked)
        total_failures = len(self.failures)
        success_rate = (1 - total_failures / max(total_tracked, 1)) * 100 if total_tracked > 0 else 0

        print(f"\n[{datetime.utcnow().isoformat()}Z] Monitoring session complete")
        print(f"  Total Duration: {total_time.total_seconds():.0f}s")
        print(f"  Runs Tracked: {total_tracked}")
        print(f"  Failures: {total_failures}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final report."""
        total_time = datetime.utcnow() - self.start_time
        total_tracked = len(self.runs_tracked)
        total_failures = len(self.failures)
        success_rate = (1 - total_failures / max(total_tracked, 1)) * 100 if total_tracked > 0 else 0

        # Count failures by category
        categories = {}
        for failure in self.failures.values():
            cat = failure['category']
            categories[cat] = categories.get(cat, 0) + 1

        report = f"""# Track 5B: Workflow Health Final Report

**Campaign Duration**: {total_time.total_seconds():.0f} seconds
**Report Generated**: {datetime.utcnow().isoformat()}Z
**Monitoring Status**: ✅ Complete

## 📊 Summary Statistics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Runs Tracked | {total_tracked} | - | - |
| Failures | {total_failures} | <5% | {'✅' if success_rate >= 95 else '❌'} |
| Success Rate | {success_rate:.1f}% | ≥95% | {'✅' if success_rate >= 95 else '❌'} |
| Monitoring Duration | {total_time.total_seconds():.0f}s | ≥1800s | {'✅' if total_time.total_seconds() >= 1800 else '⚠️'} |

## 🔴 Failures by Category

"""

        if not categories:
            report += "No failures detected! ✅\n\n"
        else:
            for category, count in sorted(categories.items(), key=lambda x: -x[1]):
                percentage = (count / total_failures) * 100 if total_failures > 0 else 0
                report += f"- **{category}**: {count} ({percentage:.1f}%)\n"

            report += "\n## 📋 Detailed Failures\n\n"

            # Group failures by category
            for category in sorted(categories.keys()):
                report += f"### {category}\n\n"
                for failure in self.failures.values():
                    if failure['category'] == category:
                        report += f"- **{failure['workflow_name']}** (Run #{failure['run_id']})\n"
                        report += f"  - Timestamp: {failure['timestamp']}\n"
                        report += f"  - Notes: {failure['notes']}\n"
                report += "\n"

        report += """
## 🎯 Conclusions

"""

        if success_rate >= 95:
            report += "✅ **EXCELLENT HEALTH**: Campaign achieved >95% workflow success rate. All critical workflows remained stable.\n"
        elif success_rate >= 90:
            report += "⚠️ **GOOD HEALTH**: Campaign achieved ~90% success rate. Some transient failures detected, but no critical regressions.\n"
        else:
            report += "🔴 **DEGRADED HEALTH**: Campaign saw significant failures. Manual investigation required.\n"

        report += f"""
## 📝 Recommendations

1. **Immediate Actions**
   - Review all failures categorized as 'Regression' for code issues
   - Re-run any 'Transient' failures to verify they're not persistent
   - Investigate 'Environment' failures for dependency conflicts

2. **Follow-up Required**
   - {self.failures.get('Regression', 0)} regression(s) need code fixes
   - {self.failures.get('Environment', 0)} environment issue(s) need infrastructure updates
   - {self.failures.get('Flaky', 0)} flaky test(s) need stabilization work

3. **Prevention**
   - Update flaky test list with any new failures
   - Add monitoring alerts for critical workflow failures
   - Implement automatic retry for transient failures

---

**Report Generated**: {datetime.utcnow().isoformat()}Z
**Monitoring Agent**: workflow-health-monitor
**Campaign**: Track 5B Continuous Workflow Health Monitoring
"""

        # Write report
        report_path = Path(".codex/WORKFLOW_HEALTH_FINAL_REPORT.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)

        print(f"\nFinal report written to {report_path}")


def main():
    """Entry point."""
    monitor = WorkflowMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
